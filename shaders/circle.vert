#version 430 core
layout(location = 0) in vec2 position;
uniform float scale_x;
uniform float scale_y;
void main() {
    // 根据宽高比调整坐标以保持正圆
    gl_Position = vec4(position.x * scale_x, position.y * scale_y, 0.0, 1.0);
}