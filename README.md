# MARS Project Documentation

<div align="center">

<h1 align="center">○</h1>

<p align="center">
    <strong>The future is here.</strong>
</p>

![GitHub license](https://img.shields.io/github/license/GeloCreativeStudio/MARS-project)
![Artificial Intelligence](https://img.shields.io/badge/Artificial-Intelligence-green)
![GitHub last commit](https://img.shields.io/github/last-commit/GeloCreativeStudio/MARS-project)

<img src="static/MARS-D3.jpg" alt="MARS Conceptual Model" width="auto" style="box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); margin-top: 10px;">

<p align="center">
    <strong>MARS</strong> utilizes state-of-the-art Language Model capabilities to seamlessly integrate Large Language Model (LLM), Text-to-Speech (TTS), and Speech-to-Text (STT) technologies. Our mission is to provide an exceptional voice AI assistant experience with fast inference speed, delivering natural and intelligent interactions akin to a real person.
</p>

</div>

---

## Table of Contents
- [Project Overview](#project-overview)
- [Project Structure](#project-structure)
- [Key Components](#key-components)
- [Features](#features)
- [Usage](#usage)
- [Future Development](#future-development)
- [License](#license)

## Project Overview

MARS is an advanced voice AI assistant developed by a collective of computer science students from EMA EMITS College Philippines. It leverages cutting-edge technologies including Large Language Models (LLMs), Text-to-Speech (TTS), and Speech-to-Text (STT) to provide a seamless and intelligent conversational experience.

## Project Structure

The project is organized as follows:

- **App:** Main Flask application for processing user requests and responses.
- **Fine-Tune:** Training data and scripts for LLM fine-tuning.
- **Knowledge Base:** Text files containing relevant information for the AI assistant.
- **Module:** System prompts and instructions for the AI assistant.
- **Static:** Static assets (images, SVGs).
- **Web:** HTML files for the user interface.

## Key Components

### 1. App.py

- **Inputs:** User requests (text or audio)
- **Processing:** 
  - Audio transcription (OpenAI Whisper API)
  - Context retrieval (Langchain for RAG)
  - Response generation (Fine-tuned OpenAI GPT-4o model)
  - Text-to-speech synthesis (OpenAI TTS API)
- **Storage:** Supabase bucket for audio file management
- **Outputs:** Text and audio responses

### 2. Fine-Tune Files

- `fine_tuning_dataset.jsonl`: General and MARS-specific training data
- `main_training_data.jsonl`: General training data
- `mars-v1.jsonl`: MARS-specific training data
- `token_counter.py`: Token counting utility

### 3. Knowledge Base

- `eecp.txt`: Information about EMA EMITS College Philippines
- `mispronoucation.txt`: Instructions for handling user mispronunciations

### 4. Module

- `prompt.py`: General AI assistant instructions
- `system_prompt.py`: System-level prompts and capabilities
- `system_prompt.txt`: System prompt text file

## Features

- **Text-to-Speech (TTS):** Natural speech synthesis using OpenAI's TTS API
- **Speech-to-Text (STT):** Accurate transcription via OpenAI's Whisper API
- **Large Language Model (LLM):** Custom fine-tuned OpenAI GPT-4o model
- **Retrieval-Augmented Generation (RAG):** Context-aware responses using Langchain
- **Audio File Management:** Efficient serving through Supabase bucket storage

## Usage

MARS offers a web interface for user interaction, with potential for expansion to other platforms. It can understand, process, and respond to a wide range of prompts, including:

- Factual questions
- Information requests
- Commands
- Natural conversational interactions

## Future Development

MARS is in active development, with planned enhancements including:

- Expanded knowledge base and domain expertise
- Advanced language understanding and generation
- Integration with additional AI technologies
- Enhanced user interface and interaction mechanisms

---

<div align="center">
<p><strong>Note:</strong> MARS is currently in its <strong>developmental</strong> phase, with ongoing refinement and enhancement efforts.</p>
<p><a href="static/conceptual-model.svg">View Conceptual Model</a></p>

MARS is licensed under the terms of the <a href="./LICENSE">MIT License</a>.

© 2024 MARS. All rights reserved.
</div>