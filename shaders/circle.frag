#version 430 core
out vec4 fragColor;
uniform vec3 circleColor;
uniform vec2 iResolution;  // 视口分辨率
uniform vec2 offset;       // 偏移参数
uniform float radius;      // 半径参数

vec3 sdfCircle(vec2 uv, float r, vec2 off) {
    float x = uv.x - off.x;
    float y = uv.y - off.y;
    float d = length(vec2(x, y)) - r;
    return d > 0. ? vec3(0.1) : circleColor; // 背景色改为深灰色
}

void main() {
    // 计算UV坐标 [-0.5, 0.5] 范围
    vec2 uv = (gl_FragCoord.xy - 0.5 * iResolution.xy) / min(iResolution.x, iResolution.y);
    
    // 使用SDF函数渲染圆形
    vec3 col = sdfCircle(uv, radius, offset);
    
    // 输出颜色
    fragColor = vec4(col, 1.0);
}