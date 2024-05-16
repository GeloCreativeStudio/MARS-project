import os
import sys
import uuid
import openai
import documentation
from typing import List, Dict
from packaging import version
from flask import Flask, jsonify, request, send_file, send_from_directory
from dotenv import load_dotenv
from module.prompt import mars_instructions
from loguru import logger
from marshmallow import Schema, fields, ValidationError

# Load environment variables from .env file
load_dotenv()

# Constants
LLM_API_KEY = os.getenv("LLM_API_KEY")

# Define required and current versions
required_version = version.parse("1.1.1")

# Configure logging
logger.remove()
logger.add(sys.stderr, level="INFO")

if os.environ.get("FLASK_ENV") == "development":
    logger.add("logs/app.log", level="DEBUG", rotation="1 MB")
else:
    logger.add("logs/app.log", level="INFO", rotation="1 MB")

def check_openai_version():
    current_version = version.parse(openai.__version__)
    if current_version < required_version:
        logger.error(
            f"Error: OpenAI version {openai.__version__} is less than the required version 1.1.1"
        )
        raise ValueError(
            f"Error: OpenAI version {openai.__version__} is less than the required version 1.1.1. Please update OpenAI to the latest version."
        )
    else:
        logger.info("OpenAI version is compatible.")
    return True

try:
    check_openai_version()
except ValueError as e:
    logger.error(str(e))
    sys.exit(1)

# Initialize Flask app
app = Flask(__name__)

# Initialize OpenAI client
client = openai.OpenAI(api_key=LLM_API_KEY)

# Define folders for uploads and outputs
uploads_folder = ".uploads"
outputs_folder = ".outputs"

# Ensure folders exist
os.makedirs(uploads_folder, exist_ok=True)
os.makedirs(outputs_folder, exist_ok=True)

# Function to convert speech to text
def speech_to_text_conversion(filename: str) -> str:
    try:
        with open(filename, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1", file=audio_file
            )
            return transcript.text
    except Exception as e:
        logger.error(f"Error in speech_to_text_conversion: {str(e)}")
        raise

# Function to construct response
def construct_response(conversation: List[Dict[str, str]]) -> str:
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "system", "content": mars_instructions},
            ] + conversation,
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error in construct_response: {str(e)}")
        raise

# Function to synthesize audio output
def synthesize_audio_output(text: str, output_path: str = "") -> str:
    try:
        response = client.audio.speech.create(model="tts-1", voice="onyx", input=text)
        with open(output_path, "wb") as output:
            output.write(response.content)
        return output_path
    except Exception as e:
        logger.error(f"Error in synthesize_audio_output: {str(e)}")
        raise

# Data validation schemas
class FileUploadSchema(Schema):
    file = fields.Field(required=True)

class InitiateQuerySchema(Schema):
    conversation = fields.List(fields.Dict, required=True)

# Route for serving front-end
@app.route("/")
def front_end():
    return send_file("web/app.html")

# Route for audio transcription
@app.route("/audio_transcription", methods=["POST"])
def audio_transcription():
    try:
        schema = FileUploadSchema()
        data = schema.load(request.files)
        file = data["file"]
        recording_file = f"{uuid.uuid4()}.wav"
        recording_path = os.path.join(uploads_folder, recording_file)
        os.makedirs(os.path.dirname(recording_path), exist_ok=True)
        file.save(recording_path)
        logger.info(f"Saved audio file: {recording_path}")
        transcription = speech_to_text_conversion(recording_path)
        logger.info(f"Transcribed audio: {transcription[:50]}...")
        return jsonify({"text": transcription})
    except ValidationError as err:
        logger.error(f"Validation error: {err.messages}")
        return jsonify({"error": err.messages}), 400
    except Exception as e:
        logger.error(f"Error in audio_transcription: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500

# Route for initiating query
@app.route("/initiate_query", methods=["POST"])
def initiate_query():
    try:
        schema = InitiateQuerySchema()
        data = schema.load(request.get_json(force=True))
        conversation = data["conversation"]
        response = construct_response(conversation)
        logger.info(f"Generated response: {response[:50]}...")
        response_file = f"{uuid.uuid4()}.mp3"
        response_path = os.path.join(outputs_folder, response_file)
        os.makedirs(os.path.dirname(response_path), exist_ok=True)
        synthesize_audio_output(response, output_path=response_path)
        logger.info(f"Saved audio response: {response_path}")
        return jsonify(
            {"text": response, "audio": f"/audio_perception/{response_file}"}
        )
    except ValidationError as err:
        logger.error(f"Validation error: {err.messages}")
        return jsonify({"error": err.messages}), 400
    except Exception as e:
        logger.error(f"Error in initiate_query: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500

# Route for serving audio perception
@app.route("/audio_perception/<filename>")
def audio_perception(filename):
    try:
        return send_file(
            os.path.join(outputs_folder, filename),
            mimetype="audio/mp3",
            as_attachment=False,
        )
    except Exception as e:
        logger.error(f"Error in audio_perception: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500

# Route for serving static files
@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory("web", path)

# Main function
if __name__ == "__main__":
    logger.info("Flask app started")
    app.run(
        host=str(os.environ.get("HOST", "localhost")),
        port=int(os.environ.get("PORT", 80)),
        debug=True,
    )
