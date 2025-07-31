# 圆形着色器
CIRCLE_VERTEX_SHADER = """
#version 430 core
layout(location = 0) in vec2 position;
uniform float scale_x;
uniform float scale_y;
void main() {
    // 根据宽高比调整坐标以保持正圆
    gl_Position = vec4(position.x * scale_x, position.y * scale_y, 0.0, 1.0);
}
"""

CIRCLE_FRAGMENT_SHADER = """
#version 430 core
out vec4 fragColor;
uniform vec3 circleColor;
void main() {
    fragColor = vec4(circleColor, 1.0);
}
"""

# 基本功能着色器
BASIC_VERTEX_SHADER = """
#version 430 core
layout(location = 0) in vec3 position;
layout(location = 1) in vec3 color;
out vec3 fragColor;
void main() {
    gl_Position = vec4(position, 1.0);
    fragColor = color;
}
"""

BASIC_FRAGMENT_SHADER = """
#version 430 core
in vec3 fragColor;
out vec4 outColor;
void main() {
    outColor = vec4(fragColor, 1.0);
}
"""