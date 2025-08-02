#version 430 core
out vec4 fragColor;
uniform vec3 circleColor;
uniform vec2 iResolution;  // 视口分辨率
uniform vec2 offset;       // 偏移参数
uniform float radius;      // 半径参数
uniform float MBlackHole;  // 黑洞质量（太阳质量单位）

// 物理常量
const float kPi              = 3.141592653589;
const float kGravityConstant = 6.673e-11;
const float kSpeedOfLight    = 299792458.0;
const float kSigma           = 5.670373e-8;
const float kLightYear       = 9460730472580800.0;
const float kSolarMass       = 1.9884e30;

// 计算史瓦西半径 (Schwarzschild radius)
float calculateRs(float MBlackHole) {
    return 2.0 * MBlackHole * kGravityConstant / (kSpeedOfLight * kSpeedOfLight) * kSolarMass;
}

// 球体SDF (有符号距离函数)
// float sdSphere(vec3 p, float r) {
//     return length(p) - r;
// }

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

void main() {
    // 使用传入的黑洞质量参数
    float Rs = calculateRs(MBlackHole);
    
    // 设置相机位置和黑洞位置
    vec3 cameraPos = vec3(0.0, 0.0, 7.0 * Rs);
    vec3 blackHolePos = vec3(offset, 5.0 * Rs);  // 使用传入的偏移参数
    
    // 计算UV坐标 [-1.0, 1.0] 范围
    vec2 uv = (2.0 * gl_FragCoord.xy - iResolution.xy) / min(iResolution.x, iResolution.y);
    
    // 创建光线
    vec3 ro = cameraPos;  // 光线起点 (相机位置)
    vec3 rd = normalize(vec3(uv, -1.0));  // 光线方向
    
    // 计算光线与球体的交点
    float t = raySphereIntersection(ro, rd, blackHolePos, Rs);
    
    if (t > 0.0) {
        // 计算交点位置
        vec3 hitPoint = ro + t * rd;
        
        // 计算法线 (用于简单着色)
        vec3 normal = normalize(hitPoint - blackHolePos);
        
        // 简单光照计算
        vec3 lightDir = normalize(vec3(1.0, 1.0, 1.0));
        float diff = max(dot(normal, lightDir), 0.0);
        vec3 diffuse = circleColor * diff;  // 使用自定义颜色
        
        // 添加一点环境光
        vec3 ambient = circleColor * 0.1;
        
        // 最终颜色
        fragColor = vec4(diffuse + ambient, 1.0);
    } 
    // else {
    //     // 背景色 - 深空
    //     vec3 bgColor = vec3(0.05, 0.02, 0.03);
        
    //     // 添加一些星星
    //     float stars = 0.0;
    //     // 使用随机数函数生成星星
    //     if (rand(uv) > 0.99) {
    //         stars = pow(rand(uv * 2.0), 8.0); // 更亮的星星
    //     }
        
    //     fragColor = vec4(bgColor + vec3(stars), 1.0);
    // }
}