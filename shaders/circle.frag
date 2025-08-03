#version 430 core
out vec4 fragColor;
uniform vec3 circleColor;
uniform vec2 iResolution;  // 视口分辨率
uniform vec2 offset;       // 偏移参数
uniform float radius;      // 半径参数
uniform float MBlackHole;  // 黑洞质量（太阳质量单位）
uniform sampler2D backgroundTexture;  // 背景纹理
uniform int backgroundType; // 0: 棋盘, 1: 星空, 2: 纯色

// 物理常量
#define PI 3.141592653589
#define G0 6.673e-11
#define lightspeed 299792458.0
#define sigma 5.670373e-8
#define ly 9460730472580800.0
#define Msun 1.9891e30
#define FOV 0.5

// 计算史瓦西半径 (Schwarzschild radius)
float calculateRs(float MBlackHole) {
    return 2.0 * MBlackHole * G0 / (lightspeed * lightspeed) * Msun;
}

// 球体SDF (有符号距离函数)
// float sdSphere(vec3 p, float r) {
//     return length(p) - r;
// }
// 计算背景纹理坐标

vec2 backgroundTexCoords(vec3 rd) {
    // 将方向向量转换为球面坐标
    float u = 0.5 + atan(rd.z, rd.x) / (2.0 * PI);  // 经度 [0, 1]
    float v = 0.5 - asin(rd.y) / PI;                // 纬度 [0, 1]
    
    // 添加轻微偏移使黑洞位置不在纹理接缝处
    u += 0.25;
    if (u > 1.0) u -= 1.0;
    
    return vec2(u, v);
}

// 计算光线与球体的交点
float raySphereIntersection(vec3 ro, vec3 rd, vec3 center, float radius) {
    vec3 oc = ro - center;
    float a = dot(rd, rd);
    float b = 2.0 * dot(oc, rd);
    float c = dot(oc, oc) - radius * radius;
    float discriminant = b * b - 4.0 * a * c;
    
    if (discriminant < 0.0) {
        return -1.0;
    }
    
    return (-b - sqrt(discriminant)) / (2.0 * a);
}

// 生成随机数函数
float rand(vec2 co) {
    return fract(sin(dot(co.xy, vec2(12.9898, 78.233)) * 43758.5453));
}

// 生成棋盘格
vec3 chessboardPattern(vec2 uv, float scale) {
    uv *= scale;
    vec2 f = fract(uv);
    vec2 i = floor(uv);
    
    // 创建棋盘格
    float pattern = mod(i.x + i.y, 2.0);
    
    // 添加边框效果
    float border = 0.02;
    f = smoothstep(0.0, border, f) * smoothstep(1.0, 1.0 - border, f);
    float final = pattern * f.x * f.y;
    
    // 两种颜色
    vec3 color1 = vec3(0.8, 0.8, 0.8); // 浅色
    vec3 color2 = vec3(0.2, 0.2, 0.2); // 深色
    
    return mix(color1, color2, final);
}

// 生成星空背景
vec3 starfieldPattern(vec2 uv) {
    vec3 color = vec3(0.0);
    
    // 基础星空密度
    float density = 0.1;
    
    // 随机星点
    float star = rand(uv);
    star = pow(star, 100.0);
    
    // 不同大小的星点
    float star2 = rand(uv * 10.0);
    star2 = pow(star2, 300.0);
    
    // 添加星云效果
    vec2 q = uv * 5.0;
    vec2 p = floor(q);
    vec2 f = fract(q);
    vec2 r = p * 0.5;
    float nebula = sin(r.x + r.y * 10.0) * 0.5 + 0.5;
    
    color += star * vec3(1.0, 0.9, 0.8);
    color += star2 * vec3(1.0, 1.0, 1.0);
    color += nebula * vec3(0.3, 0.2, 0.5) * 0.1;
    
    return color;
}

void main() {
    // 使用传入的黑洞质量参数
    float Rs = calculateRs(MBlackHole);
    
    // 设置相机位置和黑洞位置
    vec3 cameraPos = vec3(0.0, 0.0, 0.0);
    vec3 blackHolePos = vec3(offset, 5.0 * Rs);  // 使用传入的偏移参数
    
    // 计算UV坐标 [-1.0, 1.0] 范围
    vec2 uv = (2.0 * gl_FragCoord.xy - iResolution.xy) / min(iResolution.x, iResolution.y);
    
    // 创建光线
    vec3 ro = cameraPos;  // 光线起点 (相机位置)
    vec3 rd = normalize(vec3(uv, 1.0));  // 光线方向
    
    // 计算光线与球体的交点
    float t = raySphereIntersection(ro, rd, blackHolePos, Rs);
    
    if (t > 0.0) {
        // 计算交点位置
        vec3 hitPoint = ro + t * rd;
        
        // 计算法线 (用于简单着色)
        vec3 normal = normalize(hitPoint - blackHolePos);
        
        // 简单光照计算
        vec3 lightDir = normalize(vec3(1.0, 1.0, -1.0));
        float diff = max(dot(normal, lightDir), 0.0);
        vec3 diffuse = circleColor * diff;  // 使用自定义颜色
        
        // 添加一点环境光
        vec3 ambient = circleColor * 0.1;
        
        // 最终颜色
        fragColor = vec4(diffuse + ambient, 1.0);
    } else {
        // 没有击中黑洞 - 显示背景
        
        vec3 bgColor;
        
        // 根据背景类型选择不同的背景
        if (backgroundType == 0) { // 棋盘背景
            // 使用屏幕空间UV
            vec2 screenUV = gl_FragCoord.xy / iResolution.xy;
            bgColor = chessboardPattern(screenUV, 15.0);
        } else if (backgroundType == 1) { // 星空背景
            vec2 screenUV = gl_FragCoord.xy / iResolution.xy;
            bgColor = starfieldPattern(screenUV);
        } else if (backgroundType == 2) { // 纯色背景
            bgColor = vec3(0.1, 0.1, 0.15);
        } else { // 默认使用纹理
            vec2 texCoords = backgroundTexCoords(rd);
            bgColor = texture(backgroundTexture, texCoords).rgb;
        }
        
        // 添加空间感效果 - 使背景变暗
        // float distanceFactor = 1.0 - smoothstep(0.0, 0.7, length(uv));
        // bgColor *= mix(0.7, 1.0, distanceFactor);
        
        fragColor = vec4(bgColor, 1.0);
    }
}