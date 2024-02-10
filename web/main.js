// Prevent default context menu on right click
// document.addEventListener("contextmenu", (event) => event.preventDefault());

// Initialize audio elements
const rec_play = new Audio("static/sfx/rec_play.mp3");
const rec_stop = new Audio("static/sfx/rec_stop.mp3");
const processingSound = new Audio("static/sfx/processing.mp3");
processingSound.volume = 1;

// Disable dragging and right-clicking on mars image
const marsImage = document.querySelector(".img-fluid");
marsImage.draggable = false;
marsImage.ondragstart = marsImage.oncontextmenu = (e) => e.preventDefault();

$(document).ready(() => {
  // DOM elements
  const recordButton = $("#record-button");
  const transcriptionBox = $("#transcription-box");
  const askButton = $("#ask-button");
  const audioElement = $("#audio-element")[0];
  const conversation = [];
  let mediaRecorder;
  let chunks = [];
  let recording = false;

  // Disable button function
  const disableButton = (btn) => {
    btn.addClass("loading").prop("disabled", true);
  };

  // Enable button function
  const enableButton = (btn) => {
    btn.removeClass("loading").prop("disabled", false);
  };

  // Setup initial text for AI response
  const setupTypeIt = () => {
    new TypeIt("#response-text", {
      strings: [
        "Hi there! I'm MARS, your helpful AI voice assistant.",
        "How can I assist you today?",
      ],
      speed: 1,
      waitUntilVisible: true,
      cursorChar: "|",
    }).go();
  };

  // Handle click on Ask button
  const handleAskButtonClick = () => {
    disableButton(recordButton);
    disableButton(askButton);
    askButton.html("<i class='fas fa-cog fa-spin'></i>");

    // Store user input in conversation
    conversation.push({ role: "user", content: transcriptionBox.val() });
    const textData = { conversation: conversation };

    // Play processing sound
    processingSound.play();

    // Send user input to server for processing
    $.ajax({
      type: "POST",
      url: "/initiate_query",
      data: JSON.stringify(textData),
      contentType: "application/json",
      success: (data) => {
        processingSound.pause();
        processingSound.currentTime = 0;
        const fileURL = data.audio;
        $("#response-text")[0].innerHTML = "";

        // Update conversation with assistant response
        // conversation.push({ role: "assistant", content: data.text });
        new TypeIt("#response-text", {
          strings: data.text,
          speed: 1,
          waitUntilVisible: false,
          cursorChar: "|",
        }).go();

        // Play audio response
        audioElement.src = fileURL;
        audioElement.controls = true;
        audioElement.play();

        // Enable buttons after response
        enableButton(recordButton);
        enableButton(askButton);
        askButton.html("<i class='fas fa-paper-plane'></i>");
      },
    });
  };

  // Initialize MediaRecorder for audio recording
  const initializeMediaRecorder = () => {
    navigator.mediaDevices.getUserMedia({ audio: true }).then((stream) => {
      mediaRecorder = new MediaRecorder(stream);
      mediaRecorder.ondataavailable = (event) => {
        chunks.push(event.data);
      };
      mediaRecorder.onstop = () => {
        disableButton(recordButton);
        disableButton(askButton);
        recordButton.html("<i class='fas fa-sync-alt fa-spin'></i>");

        // Convert recorded audio chunks to blob
        const audioData = new Blob(chunks, { type: "audio/wav" });
        const formData = new FormData();
        formData.append("file", audioData, "audio.wav");

        // Play processing sound
        processingSound.play();

        // Send recorded audio to server for transcription
        $.ajax({
          type: "POST",
          url: "/audio_transcription",
          data: formData,
          contentType: false,
          processData: false,
          success: (data) => {
            processingSound.pause();
            processingSound.currentTime = 0;
            // Update transcription box with transcribed text
            transcriptionBox.val(data.text);
            // Enable Record button and trigger Ask button click
            enableButton(recordButton);
            recordButton.html("<i class='fas fa-microphone'></i>");
            askButton.click();
          },
        });
      };
    });
  };

  // Handle Record button click
  const handleRecordButtonClick = () => {
    if (recording) {
      rec_play.play();
      mediaRecorder.stop();
      recording = false;
    } else {
      rec_stop.play();
      recordButton.html("<i class='fas fa-stop'></i>");
      chunks = [];
      mediaRecorder.start();
      recording = true;
    }
  };

  // Handle audio play event
  const handleAudioPlay = () => {
    marsImage.classList.add("scale-down");
  };

  // Handle audio ended event
  const handleAudioEnded = () => {
    marsImage.classList.remove("scale-down");
  };

  // Event Listeners
  askButton.click(handleAskButtonClick);
  recordButton.click(handleRecordButtonClick);
  audioElement.addEventListener("play", handleAudioPlay);
  audioElement.addEventListener("ended", handleAudioEnded);

  // Initial Setup
  setupTypeIt();
  initializeMediaRecorder();
});
