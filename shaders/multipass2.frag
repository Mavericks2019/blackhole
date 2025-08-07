#version 430 core
in vec2 fragCoord;
out vec4 outColor;

uniform sampler2D pass1Texture;
uniform vec2 iResolution;

void main() {
    // 将坐标归一化到[0,1]
    vec2 uv = fragCoord;
    
    // 读取第一通道的纹理（方形）
    vec4 squareColor = texture(pass1Texture, uv);
    
    // 圆形参数
    vec2 center = vec2(0.7, 0.3);
    float radius = 0.2;
    
    // 计算圆形
    float dist = distance(uv, center);
    float circle = 1.0 - smoothstep(radius - 0.01, radius + 0.01, dist);
    
    // 设置颜色（绿色圆形）
    vec3 color = vec3(0.0, 1.0, 0.0) * circle;
    
    // 混合方形和圆形
    vec3 finalColor = squareColor.rgb + color;
    
    outColor = vec4(finalColor, 1.0);
}