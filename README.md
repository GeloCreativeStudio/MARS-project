## MARS Project Documentation

This documentation outlines the structure and functionality of the MARS project. MARS is a voice AI assistant built using cutting-edge technologies like Large Language Models (LLMs), Text-to-Speech (TTS), and Speech-to-Text (STT). 

**Project Structure:**

The project is organized as follows:

* **App:** The main Flask application responsible for processing user requests and responses.
* **Fine-Tune:** Contains training data and scripts for fine-tuning the LLM.
* **Knowledge Base:** Stores text files containing information relevant to the AI assistant.
* **Module:** Contains modules related to system prompts and prompts for the AI assistant.
* **Static:** Holds static assets like images and SVGs.
* **Web:**  Contains HTML files for the user interface. 

**Code Breakdown:**

**1. App.py:**

* **Inputs:** User requests in the form of text or audio.
* **Processing:** 
    * Transcribes audio to text using the OpenAI Whisper API.
    * Retrieves context from the knowledge base using vector similarity search.
    * Constructs a response using the OpenAI Chat Completion API, incorporating the retrieved context.
    * Synthesizes the response to audio using the OpenAI TTS API.
* **Outputs:** Text and audio responses to the user.

**2. Fine-Tune Files:**

<!-- * **angelo_training_data.jsonl:**  Training data for the fine-tuned LLM focusing on Angelo Manalo. -->

* **fine_tuning_dataset.jsonl:**  Training data for the fine-tuned LLM for general knowledge and MARS-specific details.
* **main_training_data.jsonl:**  General training data for the fine-tuned LLM.
* **mars-v1.jsonl:**  Training data for the fine-tuned LLM specific to MARS.
* **token_counter.py:**  Utility script for counting tokens in the training data.

**3. Knowledge Base:**

<!-- * **angelo.txt:** Information about Angelo Manalo used for context retrieval. -->

* **eecp.txt:** Information about EMA EMITS College Philippines used for context retrieval.
* **mispronoucation.txt:**  Instructions for the AI assistant to handle potential user mispronunciations. 

**4. Module:**

* **prompt.py:** Contains general instructions for the AI assistant.
* **system_prompt.py:**  Contains system-level prompts for the AI assistant, including information about its creators and capabilities.
* **system_prompt.txt:**  Text file containing the system prompt. 

**5. Static:**

* **conceptual-model.svg:** An SVG diagram illustrating the conceptual model of MARS.
* **script/three.min.js:** The Three.js library for 3D graphics used in the web interface.

**6. Web:**

* **app.html:** Main HTML file for the web interface.
* **index.html:** HTML file for the main landing page.
<!-- * **test.html:** HTML file for testing purposes. -->
* **unavailable.html:** HTML file for the landing page when MARS is unavailable.
* **assets:** Contains CSS and JavaScript files for styling and functionality. 
<!-- * **resume/resume.html:** HTML file for Angelo Manalo's resume.  -->

**Usage:**

MARS is designed to be a voice AI assistant developed by a collective of computer science students from EMA EMITS College Philippines. Users can interact with it through a web interface or potentially other platforms. It can understand, think, and speak like a real human, enabling natural conversational interactions. MARS can respond to a wide range of prompts, including factual questions, requests for information, and commands.  

**Future Development:**

MARS is currently in development and undergoing continuous refinement. Future enhancements may include: 

* Expanded knowledge base and domain expertise. 
* More sophisticated language understanding and generation capabilities. 
* Integration with other AI technologies and services. 
* Improved user interface and interaction mechanisms. 


<div align="center">

<h1 align="center">○</h1>

<p align="center">
    <strong>The future is here.</strong><br>
</p>

![GitHub license](https://img.shields.io/github/license/GeloCreativeStudio/MARS-project)
![Artificial Intelligence](https://img.shields.io/badge/Artificial-Intelligence-green)
![GitHub last commit](https://img.shields.io/github/last-commit/GeloCreativeStudio/MARS-project)

<img src="static/MARS-D3.jpg" alt="MARS Conceptual Model" width="auto" style="box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); margin-top: 10px;">

<p align="center">
    <strong>MARS</strong> utilizes the state-of-the-art capabilities of Language Models. Its mission is to seamlessly integrate Large Language Model (LLM), Text-to-Speech (TTS), Speech-to-Text (STT) to provide an exceptional voice AI assistant experience with fast inference speed. Leveraging these cutting-edge AI technologies, MARS can deliver natural and intelligent interactions like a real person.
</p>

---

<p align="center">
    <strong>Note:</strong> MARS is currently in its <strong>developmental</strong> phase, with ongoing efforts dedicated to its refinement and enhancement.<br>
    <br><a href="static/conceptual-model.svg">View Diagram</a>
</p>

</div>

## Features

- **Text-to-Speech (TTS)**: Converts written text into natural-sounding speech.
- **Speech-to-Text (STT)**: Accurately transforms spoken language into text.
- **Large Language Model (LLM)**: Provides sophisticated language understanding and generation capabilities.


---

<div align="center">
MARS is licensed under the terms of the <a href="./LICENSE">MIT License</a>.
</div>

---

<div align="center">
© 2024 MARS. All rights reserved.
</div>

