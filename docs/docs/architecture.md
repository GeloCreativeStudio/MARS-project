# Architecture Overview

The Mars Assistant application follows a client-server architecture with a Flask backend and a web-based frontend. The backend is responsible for handling audio transcription, generating responses based on conversation history, and synthesizing audio output.

## Backend

The backend is written in Python using the Flask web framework. It utilizes the OpenAI API for speech-to-text transcription, natural language processing, and text-to-speech synthesis.

The main components of the backend are:

- `app.py`: The Flask application entry point, which defines the API routes and handles requests.
- `module/prompt.py`: Contains the instructions and prompts used for the language model.
- `web/app.html`: The HTML file that serves as the frontend for the application.

## Frontend

The frontend is a simple web-based interface built with HTML, CSS, and JavaScript. It provides a user-friendly interface for interacting with the backend API, allowing users to upload audio files, initiate queries, and receive audio responses.

## Data Flow

1. The user uploads an audio file to the backend through the `/audio_transcription` endpoint.
2. The backend transcribes the audio file using the OpenAI Whisper API.
3. The transcribed text is sent back to the frontend.
4. The user initiates a query by sending the conversation history to the `/initiate_query` endpoint.
5. The backend constructs a response using the OpenAI GPT-3 language model.
6. The response text is synthesized into audio using the OpenAI TTS API.
7. The response text and the URL to the synthesized audio file are sent back to the frontend.
8. The frontend displays the response text and plays the synthesized audio.