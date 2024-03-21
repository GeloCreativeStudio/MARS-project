import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import requests

from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_front_end(client):
    response = client.get('/')
    assert response.status_code == 200

def test_audio_transcription(client):
    with open('tests/sample_audio.mp3', 'rb') as file:
        files = {'file': file}
        response = client.post('/audio_transcription', data=files)
        assert response.status_code == 200
        assert 'text' in response.json

def test_initiate_query(client):
    data = {
        'conversation': [
            {'role': 'user', 'content': 'Hello'}
        ]
    }
    response = client.post('/initiate_query', json=data)
    assert response.status_code == 200
    assert 'text' in response.json
    assert 'audio' in response.json

def test_audio_perception(client):
    response = client.get('/audio_perception/sample_audio.mp3')
    assert response.status_code == 200