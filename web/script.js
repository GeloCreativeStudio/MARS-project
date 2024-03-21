let audio, amp, fft
let isPressed = true
let myShader
let angle = 0.0
let jitter = 0.0


function preload() {
  audio = loadSound('audio/intro.mp3')
  myShader = loadShader('shader/vertex.vert', 'shader/fragment.frag')
  frameRate(60)
}

function setup() {
  let canvas = createCanvas(300, 300, WEBGL);
  canvas.parent('head');
  canvas.class('canvas')

  // audio.play()

  shader(myShader);

  amp = new p5.Amplitude();
  fft = new p5.FFT();
}

function draw() {
  background(0)

  drawingContext.filter = 'blur(px)'

  console.log(audio.currentTime())
  fft.analyze()

  const volume = amp.getLevel()
  let freq = fft.getCentroid()

  freq *= 0.001

  if (second() % 2 == 0) {
    jitter = random(0, 0.1)
    jitter += jitter
  }

  angle = angle + jitter

  rotateX(sin(freq) + angle * 0.1)
  rotateY(cos(volume) + angle * 0.1)

  const mapF = map(freq, 0, 1, 0, 20)
  const mapV = map(volume, 0, 0.2, 0, 0.5)
  console.log()
  myShader.setUniform('uTime', frameCount)

  myShader.setUniform('uFreq', mapF)
  myShader.setUniform('uAmp', mapV)

  sphere(100, 400, 400)
}

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
    btn.addClass("no-click").prop("disabled", true);
  };

  // Enable button function
  const enableButton = (btn) => {
    btn.removeClass("no-click").prop("disabled", false);
  };

  // Setup initial text for AI response
  const setupTypeIt = () => {
    new TypeIt("#response-text", {
      strings: [
        // "Hi! Ako si MARS, ang kauna-unahang EECPian's AI voice chatbot. Ano ang nais mong itanong?",
      ],
      speed: 1,
      waitUntilVisible: true,
      cursorChar: "|",
    }).go();
  };


  // Declare a global variable to store the thread ID
  var thread_id = null;

  // Handle click on Ask button
  const handleAskButtonClick = () => {
    disableButton(recordButton);
    disableButton(askButton);
    askButton.html("<i class='fas fa-cog fa-spin'></i>");

    // Store user input in conversation
    conversation.push({ role: "user", content: transcriptionBox.val() });
    // Add the thread ID to the conversation if present
    if (thread_id) {
      conversation[0]["thread_id"] = thread_id;
    }
    const textData = { conversation: conversation };


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
        $("#response-text")[0].innerHTML = "";

        // Update conversation with assistant response
        new TypeIt("#response-text", {
          strings: data.text,
          speed: 1,
          waitUntilVisible: false,
          cursorChar: "|",
        }).go();

        // const fileURL = data.audio;

        // audioElement.src = fileURL;
        // audioElement.controls = true;
        // audioElement.play();

        // Load and play the audio file using p5.js
        audio = loadSound(data.audio, () => {
          audio.play();
        });

        enableButton(recordButton);
        enableButton(askButton);
        askButton.html("<i class='fas fa-paper-plane'></i>");

        // Update the thread ID with the one returned by the server
        thread_id = data.thread_id;

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
            recordButton.html("<i class='ri-mic-line'></i>");
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
      recordButton.html("<i class='ri-mic-off-line'></i>");
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
