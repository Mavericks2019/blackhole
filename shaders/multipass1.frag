#version 430 core
in vec2 fragCoord;
out vec4 outColor;

uniform vec2 iResolution;

void main() {
    // 将坐标归一化到[0,1]
    vec2 uv = fragCoord;
    
    // 方形参数
    vec2 center = vec2(0.5);
    vec2 size = vec2(0.3);
    
    // 计算方形
    vec2 d = abs(uv - center) - size;
    float square = 1.0 - smoothstep(0.0, 0.01, max(d.x, d.y));
    
    // 设置颜色（红色方形）
    vec3 color = vec3(1.0, 0.0, 0.0) * square;
    
    outColor = vec4(color, 1.0);
}