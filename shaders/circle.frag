#version 430 core
out vec4 fragColor;
uniform vec3 circleColor;
uniform vec2 iResolution;  // 视口分辨率
uniform vec2 offset;       // 偏移参数
uniform float radius;      // 半径参数
uniform float MBlackHole;  // 黑洞质量（太阳质量单位）
uniform sampler2D backgroundTexture;  // 背景纹理
// uniform int backgroundType; // 0: 棋盘, 1: 星空, 2: 纯色
uniform vec4 iMouse; // 添加 iMouse 变量
uniform sampler2D iChannel1;         // 棋盘格纹理 (类似Shadertoy)
uniform vec3 iChannelResolution;  // 声明为vec3数组

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

vec4 GetCamera(vec4 a)//相机系平移旋转  本部分在实际使用时uniform输入
{
    float _Theta=4.0*PI*iMouse.x/iResolution.x;
    float _Phi=0.999*PI*iMouse.y/iResolution.y+0.0005;
    float _R=0.000057;
    vec3 _Rotcen=vec3(0.0,0.0,0.0);
    vec3 _Campos;
        vec3 reposcam=vec3(
        _R * sin(_Phi) * cos(_Theta),
        _R * sin(_Phi) * sin(_Theta),
        -_R * cos(_Phi));
        _Campos = _Rotcen + reposcam;
        vec3 vecz =vec3( 0.0,0.0,1.0 );
        vec3 _X = normalize(cross(vecz, reposcam));
        vec3 _Y = normalize(cross(reposcam, _X));
        vec3 _Z = normalize(reposcam);
        a=(transpose(mat4x4(//注意glsl的矩阵和线性代数里学的矩阵差个转置
            1., 0., 0., -_Campos.x,
            0., 1., 0., -_Campos.y,
            0., 0., 1., -_Campos.z,
            0., 0., 0., 1.
        ))*a);
        a=transpose(mat4x4(
            _X.x,_X.y,_X.z,0.,
            _Y.x,_Y.y,_Y.z,0.,
            _Z.x,_Z.y,_Z.z,0.,
            0.   ,0.   ,0.   ,1.)
            )*a;  
        return a;
}

vec4 GetCameraRot(vec4 a)//摄影机系旋转，用于矢量换系   本部分在实际使用时uniform输入
{
float _Theta=4.0*PI*iMouse.x/iResolution.x;
float _Phi=0.999*PI*iMouse.y/iResolution.y+0.0005;
float _R=0.000057;
vec3 _Rotcen=vec3(0.0,0.0,0.0);
vec3 _Campos;
    vec3 reposcam=vec3(
    _R * sin(_Phi) * cos(_Theta),
    _R * sin(_Phi) * sin(_Theta),
    -_R * cos(_Phi));
    _Campos = _Rotcen + reposcam;
    vec3 vecz =vec3( 0.0,0.0,1.0 );
    vec3 _X = normalize(cross(vecz, reposcam));
    vec3 _Y = normalize(cross(reposcam, _X));
    vec3 _Z = normalize(reposcam);
    a=transpose(mat4x4(
        _X.x,_X.y,_X.z,0.,
        _Y.x,_Y.y,_Y.z,0.,
        _Z.x,_Z.y,_Z.z,0.,
        0.   ,0.   ,0.   ,1.)
        )*a;
    return a;
}

vec3 uvToDir(vec2 uv) //一堆坐标间变换
{
    return normalize(vec3(FOV*(2.0*uv.x-1.0),FOV*(2.0*uv.y-1.0)*iResolution.y/iResolution.x,-1.0));
}
vec2 PosToNDC(vec4 pos)
{
    return vec2(-pos.x/pos.z,-pos.y/pos.z*iResolution.x/iResolution.y);
}
vec2 DirToNDC(vec3 dir)
{
    return vec2(-dir.x/dir.z,-dir.y/dir.z*iResolution.x/iResolution.y);
}
vec2 DirTouv(vec3 dir)
{
    return vec2(0.5-0.5*dir.x/dir.z,0.5-0.5*dir.y/dir.z*iResolution.x/iResolution.y);
}
vec2 PosTouv(vec4 Pos)
{
    return vec2(0.5-0.5*Pos.x/Pos.z,0.5-0.5*Pos.y/Pos.z*iResolution.x/iResolution.y);
}

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

void main() {
    // 使用传入的黑洞质量参数
    fragColor = vec4(0.,0.,0.,0.);
    vec2 uv = gl_FragCoord.xy / iResolution.xy;

    float MBH = 1.49e7;//单位是太阳质量                                                                                            本部分在实际使用时uniform输入
    float Rs = 2.*MBH*G0 / lightspeed / lightspeed * Msun;//单位是米 
    Rs=Rs/ly;//现在单位是ly 
    
    // 设置相机位置和黑洞位置
    vec3 cameraPos = vec3(0.0, 0.0, 0.0);
    vec4 BHAPos = vec4(2.*Rs, 0.0, 0.0, 1.0);//黑洞世界位置                                                                        本部分在实际使用时没有
    vec3 BHRPos = GetCamera(BHAPos).xyz; //
    vec3 RayDir = uvToDir(uv);
    vec3 RayPos = vec3(0.0,0.0,0.0);
    vec3 lastRayPos;
    vec3 lastRayDir;
    vec3 PosToBH = RayPos-BHRPos;
    vec3 NPosToBH = normalize(PosToBH);
    float DistanceToBlackHole = length(PosToBH);
    RayDir=normalize(RayDir-NPosToBH*dot(PosToBH,RayDir)*(-sqrt(max(1.0-Rs/DistanceToBlackHole,0.00000000000000001))+1.0));

    float steplength;
    float lastR=length(PosToBH);
    float costheta;
    float dthe;    
    float dphirate;
    float dl;
    float Dis=length(PosToBH);
    bool flag=true;
    int count=0;

    while(flag==true){//测地raymarching
        lastRayPos = RayPos;
        lastRayDir = RayDir;
        lastR = Dis;
        costheta = length(cross(NPosToBH,RayDir));//前进方向与切向夹角
        dphirate = -1.0*costheta*costheta*costheta*(1.5*Rs/Dis);//单位长度光偏折角

        dl = 1.0;
        dl *= 0.15;
        dl *= Dis;

        RayPos += RayDir*dl;
        dthe = dl / Dis*dphirate;
        RayDir = normalize(RayDir+(dthe+dthe*dthe*dthe/3.0)*cross(cross(RayDir,NPosToBH),RayDir)/costheta);//更新方向，里面的（dthe +dthe^3/3）是tan（dthe）
        steplength = length(RayPos-lastRayPos);
                
        PosToBH = RayPos - BHRPos;
        Dis = length(PosToBH);
        NPosToBH = PosToBH/Dis;
        
        count++;
        if(Dis>(100.*Rs) && Dis>lastR && count>50){//远离黑洞
            flag = false;
            uv = DirTouv(RayDir);
            fragColor+=0.5*texelFetch(iChannel1, ivec2(vec2(fract(uv.x),fract(uv.y))*iChannelResolution.xy), 0)*(1.0-fragColor.a);            
            //fragColor += vec4(.25)*(1.0-fragColor.a);
        }
        if(Dis < 0.1 * Rs){//命中奇点
            flag = false;
        }
    }
    fragColor.a = 1.0;

}