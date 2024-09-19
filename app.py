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

# Load environment variables and configure logging
load_dotenv()
logger.remove()
logger.add(sys.stderr, level="INFO")
logger.add("logs/app.log", level="DEBUG" if os.environ.get("FLASK_ENV") == "development" else "INFO", rotation="1 MB")

# Constants
LLM_API_KEY = os.getenv("LLM_API_KEY")
KNOWLEDGE_BASE_DIR = os.getenv("KNOWLEDGE_BASE_DIR", "knowledge_base")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")  # Updated this line
UPLOADS_BUCKET = "uploads"
OUTPUTS_BUCKET = "outputs"

# After loading environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    logger.error("SUPABASE_URL or SUPABASE_ANON_KEY is missing from environment variables")
    raise EnvironmentError("Supabase configuration is incomplete")

# Initialize Supabase client
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    logger.info("Supabase client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Supabase client: {str(e)}")
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
        # Download the file from Supabase
        response = requests.get(file_url)
        response.raise_for_status()
        
        # Create a temporary file
        temp_file = f"/tmp/{uuid.uuid4()}.wav"
        with open(temp_file, "wb") as f:
            f.write(response.content)
        
        # Transcribe the audio
        with open(temp_file, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(model="whisper-1", file=audio_file)
        
        # Remove the temporary file
        os.remove(temp_file)
        
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

        # Generate a unique filename
        filename = f"{uuid.uuid4()}.wav"
        
        # Upload to Supabase
        _, error = supabase.storage.from_(UPLOADS_BUCKET).upload(filename, file.read())
        if error:
            raise Exception(f"Error uploading to Supabase: {error}")
        
        # Get public URL
        file_url = supabase.storage.from_(UPLOADS_BUCKET).get_public_url(filename)
        
        logger.info(f"Uploaded audio file: {file_url}")
        transcription = speech_to_text_conversion(file_url)
        logger.info(f"Transcribed audio: {transcription[:50]}...")
        return jsonify({"text": transcription})
    except Exception as e:
        logger.error(f"Error in audio_transcription: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/initiate_query", methods=["POST"])
def initiate_query():
    try:
        data = request.get_json(force=True)
        conversation = data.get("conversation")
        if not conversation:
            return jsonify({"error": "No conversation provided"}), 400

        response = construct_response(conversation)
        logger.info(f"Generated response: {response[:50]}...")
        
        # Generate audio
        audio_content = synthesize_audio_output(response)
        
        # Generate a unique filename
        filename = f"{uuid.uuid4()}.mp3"
        
        # Upload to Supabase
        _, error = supabase.storage.from_(OUTPUTS_BUCKET).upload(filename, audio_content)
        if error:
            raise Exception(f"Error uploading to Supabase: {error}")
        
        # Get public URL
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