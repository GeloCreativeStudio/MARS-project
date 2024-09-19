import os
import sys
import uuid
import openai
import nltk
import requests
from typing import List, Dict
from flask import Flask, jsonify, request, send_file, send_from_directory
from dotenv import load_dotenv
from module.system_prompt import mars_instructions
from loguru import logger
from marshmallow import Schema, fields, ValidationError
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from flask_caching import Cache
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_cors import CORS
from supabase import create_client, Client
import time
import tempfile

# Load environment variables and configure logging
load_dotenv()
logger.remove()
logger.add(sys.stderr, level="INFO")
logger.add("logs/app.log", level="DEBUG" if os.environ.get("FLASK_ENV") == "development" else "INFO", rotation="1 MB")

# Constants
LLM_API_KEY = os.getenv("LLM_API_KEY")
KNOWLEDGE_BASE_DIR = os.getenv("KNOWLEDGE_BASE_DIR", "knowledge_base")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
UPLOADS_BUCKET = "uploads"
OUTPUTS_BUCKET = "outputs"

# Initialize Supabase client
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    # Test the connection using the new alpha_users table
    response = supabase.table('alpha_users').select('*').limit(1).execute()
    logger.info("Supabase client initialized and tested successfully")
except Exception as e:
    logger.error(f"Failed to initialize or test Supabase client: {str(e)}")
    raise

# Initialize Flask app and OpenAI client
app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
client = openai.OpenAI(api_key=LLM_API_KEY)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
CORS(app)

# Initialize embeddings and vector store
embeddings = OpenAIEmbeddings(openai_api_key=LLM_API_KEY)
vector_store = None

@cache.memoize(timeout=3600)
def initialize_vector_store():
    global vector_store
    try:
        documents = []
        for filename in os.listdir(KNOWLEDGE_BASE_DIR):
            if filename.endswith('.txt'):
                file_path = os.path.join(KNOWLEDGE_BASE_DIR, filename)
                try:
                    loader = TextLoader(file_path)
                    documents.extend(loader.load())
                except Exception as e:
                    logger.error(f"Error loading file {file_path}: {str(e)}")
        
        if not documents:
            logger.warning(f"No documents found in {KNOWLEDGE_BASE_DIR}")
            return

        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        texts = text_splitter.split_documents(documents)
        vector_store = FAISS.from_documents(texts, embeddings)
        logger.info("Vector store initialized")
    except Exception as e:
        logger.error(f"Error initializing vector store: {str(e)}")
        raise

# Initialize vector store
try:
    initialize_vector_store()
except Exception as e:
    logger.error(f"Failed to initialize vector store: {str(e)}")

# Helper functions
@cache.memoize(timeout=300)
def speech_to_text_conversion(file_url: str) -> str:
    try:
        # Ensure we're using the correct URL
        logger.debug(f"Attempting to download file from URL: {file_url}")
        
        # Download the file from Supabase
        response = requests.get(file_url)
        response.raise_for_status()
        
        # Log the response status and content type
        logger.debug(f"Download response status: {response.status_code}")
        logger.debug(f"Download response content type: {response.headers.get('Content-Type')}")
        
        # Create a temporary file using tempfile module
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            temp_file.write(response.content)
            temp_file_path = temp_file.name
        
        # Log the size of the downloaded file
        logger.debug(f"Downloaded file size: {os.path.getsize(temp_file_path)} bytes")
        
        # Transcribe the audio
        with open(temp_file_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(model="whisper-1", file=audio_file)
        
        # Remove the temporary file
        os.unlink(temp_file_path)
        
        return transcript.text
    except Exception as e:
        logger.error(f"Error in speech_to_text_conversion: {str(e)}")
        raise

@cache.memoize(timeout=300)
def retrieve_context(query: str, k: int = 3) -> str:
    docs = vector_store.similarity_search(query, k=k)
    return "\n".join([doc.page_content for doc in docs])

@cache.memoize(timeout=60)
def construct_response(conversation: List[Dict[str, str]]) -> str:
    try:
        query = conversation[-1]["content"]
        context = retrieve_context(query)
        augmented_conversation = [
            {"role": "system", "content": mars_instructions},
            {"role": "system", "content": f"Relevant context: {context}"},
        ] + conversation

        response = client.chat.completions.create(
            model="ft:gpt-4o-mini-2024-07-18:gelo-creative-studio:mars-v1:9viRXs1Z",
            messages=augmented_conversation,
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error in construct_response: {str(e)}")
        raise

@cache.memoize(timeout=300)
def synthesize_audio_output(text: str) -> bytes:
    try:
        response = client.audio.speech.create(model="tts-1", voice="onyx", input=text)
        return response.content
    except Exception as e:
        logger.error(f"Error in synthesize_audio_output: {str(e)}")
        raise

# Data validation schemas
class FileUploadSchema(Schema):
    file = fields.Field(required=True)

class InitiateQuerySchema(Schema):
    conversation = fields.List(fields.Dict, required=True)

# Routes
@app.route("/")
def front_end():
    return send_file("web/app.html")

@app.route("/audio_transcription", methods=["POST"])
def audio_transcription():
    try:
        file = request.files['file']
        if not file:
            return jsonify({"error": "No file provided"}), 400

        filename = f"{uuid.uuid4()}.wav"
        
        try:
            ensure_buckets_exist()
            file_content = file.read()
            
            if len(file_content) == 0:
                return jsonify({"error": "Empty file content"}), 400
            
            # Perform the upload
            logger.debug(f"Attempting to upload file: {filename}")
            logger.debug(f"File content length: {len(file_content)}")
            upload_result = supabase.storage.from_(UPLOADS_BUCKET).upload(filename, file_content)
            logger.debug(f"Upload result: {upload_result}")
            
            if upload_result:
                file_path = filename  # Use the filename directly
                file_url = supabase.storage.from_(UPLOADS_BUCKET).get_public_url(file_path)
                logger.info(f"File uploaded successfully. Public URL: {file_url}")
            else:
                raise ValueError("Upload failed")
            
            # Add a delay to ensure the file is available
            time.sleep(2)
            
            transcription = speech_to_text_conversion(file_url)
            logger.info(f"Transcribed audio: {transcription[:50]}...")
            return jsonify({"text": transcription})
        
        except Exception as upload_error:
            logger.error(f"Supabase upload or transcription error: {str(upload_error)}")
            return jsonify({"error": f"Failed to upload or process file: {str(upload_error)}"}), 500
    
    except Exception as e:
        logger.error(f"Unexpected error in audio_transcription: {str(e)}")
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

@app.route("/initiate_query", methods=["POST"])
def initiate_query():
    try:
        data = request.get_json(force=True)
        conversation = data.get("conversation")
        if not conversation:
            return jsonify({"error": "No conversation provided"}), 400

        response = construct_response(conversation)
        logger.info(f"Generated response: {response[:50]}...")
        
        audio_content = synthesize_audio_output(response)
        
        filename = f"{uuid.uuid4()}.mp3"
        
        try:
            ensure_buckets_exist()
            result = supabase.storage.from_(OUTPUTS_BUCKET).upload(filename, audio_content)
            if not result:
                raise Exception("Failed to upload audio response to Supabase")
        except Exception as upload_error:
            logger.error(f"Supabase upload error: {str(upload_error)}")
            return jsonify({"error": "Failed to upload audio response"}), 500
        
        audio_url = supabase.storage.from_(OUTPUTS_BUCKET).get_public_url(filename)
        
        logger.info(f"Uploaded audio response: {audio_url}")
        return jsonify({"text": response, "audio": audio_url})
    except Exception as e:
        logger.error(f"Error in initiate_query: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory("web", path)

@app.route('/assets/shader/<path:filename>')
def serve_shader(filename):
    return send_from_directory('web/assets/shader', filename)

@app.route('/assets/<path:filename>')
def serve_assets(filename):
    return send_from_directory('web/assets', filename)

# After initializing Supabase client
def ensure_buckets_exist():
    buckets = [UPLOADS_BUCKET, OUTPUTS_BUCKET]
    for bucket in buckets:
        try:
            supabase.storage.get_bucket(bucket)
            logger.info(f"Bucket exists: {bucket}")
        except Exception as e:
            if "Bucket not found" in str(e):
                try:
                    supabase.storage.create_bucket(bucket, public=True)
                    logger.info(f"Created bucket: {bucket}")
                except Exception as create_error:
                    logger.error(f"Error creating bucket {bucket}: {str(create_error)}")
                    raise
            else:
                logger.error(f"Error checking bucket {bucket}: {str(e)}")
                raise

# Call this function after initializing Supabase client
ensure_buckets_exist()

def test_supabase_connection():
    try:
        # Try to list buckets
        buckets = supabase.storage.list_buckets()
        logger.info(f"Successfully listed buckets: {buckets}")
        return True
    except Exception as e:
        logger.error(f"Failed to connect to Supabase: {str(e)}")
        return False

# Call this after initializing the Supabase client
if test_supabase_connection():
    logger.info("Supabase connection test passed")
else:
    logger.error("Supabase connection test failed")