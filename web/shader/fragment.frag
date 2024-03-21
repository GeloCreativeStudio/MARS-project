precision mediump float;

varying vec3 vNormal;

void main() {
    // Gradient from dark green to light green without y-axis rotation
    vec3 color = vec3(0.1, vNormal.x * 0.2 + 0.6, 0.0);

    gl_FragColor = vec4(color, 0.8);
}
