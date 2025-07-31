#version 430 core
out vec4 fragColor;
uniform vec3 circleColor;
void main() {
    fragColor = vec4(circleColor, 1.0);
}