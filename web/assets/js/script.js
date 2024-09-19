let sketch = function(p) {
  let audio, amp, fft;
  let isPressed = true;
  let myShader;
  let angle = 0.0;
  let jitter = 0.0;

  const BASE_URL = window.location.origin;

  p.preload = function() {
    audio = p.loadSound(`${BASE_URL}/assets/audio/intro.mp3`);
    myShader = p.loadShader(`${BASE_URL}/assets/shader/vertex.vert`, `${BASE_URL}/assets/shader/fragment.vert`);
  }

  p.setup = function() {
    let canvas = p.createCanvas(p.windowWidth, p.windowHeight, p.WEBGL);
    canvas.parent('p5-sketch-container');
    p.frameRate(60);

    p.shader(myShader);

    amp = new p5.Amplitude();
    fft = new p5.FFT();
  }

  p.draw = function() {
    p.background(0);

    p.drawingContext.filter = 'blur(1px)';

    fft.analyze();

    const volume = amp.getLevel();
    let freq = fft.getCentroid();

    freq *= 0.001;

    if (p.second() % 2 == 0) {
      jitter = p.random(0, 0.1);
      jitter += jitter;
    }

    angle = angle + jitter;

    p.rotateX(p.sin(freq) + angle * 0.1);
    p.rotateY(p.cos(volume) + angle * 0.1);

    const mapF = p.map(freq, 0, 1, 0, 20);
    const mapV = p.map(volume, 0, 0.2, 0, 0.5);

    myShader.setUniform('uTime', p.frameCount);
    myShader.setUniform('uFreq', mapF);
    myShader.setUniform('uAmp', mapV);

    p.sphere(100, 400, 400);
  }

  p.windowResized = function() {
    p.resizeCanvas(p.windowWidth, p.windowHeight);
  }
};

// Initialize p5.js sketch
new p5(sketch);

// ... (rest of the code) ...
