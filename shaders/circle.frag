#version 430 core
out vec4 fragColor;
uniform vec3 circleColor;
uniform vec2 iResolution;  // 视口分辨率
uniform vec2 offset;       // 偏移参数
uniform float radius;      // 半径参数
uniform float MBlackHole;  // 黑洞质量（太阳质量单位）
uniform sampler2D backgroundTexture;  // 背景纹理
uniform int backgroundType; // 0: 棋盘, 1: 纯黑, 2: 星空, 3: 纹理
uniform vec4 iMouse; // 添加 iMouse 变量
uniform float iTime;              // 添加 iTime 变量 (类似Shadertoy)
uniform sampler2D iChannel1;         // 棋盘格纹理 (类似Shadertoy)
uniform vec3 iChannelResolution;  // 声明为vec3数组
uniform int iFrame;           // 添加 iFrame 变量 (类似Shadertoy)

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

float softHold(float x){//使不大于一
    return 1.0-1.0/(max(x,0.0)+1.0);
}

float Vec2Theta(vec2 a,vec2 b)//两平面向量夹角,0到2pi
{
    if(dot(a,b)>0.0){
        return asin(0.999999*(a.x*b.y-a.y*b.x)/length(a)/length(b));
    }else if(dot(a,b)<0.0 && (-a.x*b.y+a.y*b.x)<0.0){
        return PI-asin(0.999999*(a.x*b.y-a.y*b.x)/length(a)/length(b));
    }else if(dot(a,b)<0.0 && (-a.x*b.y+a.y*b.x)>0.0){
        return -PI-asin(0.999999*(a.x*b.y-a.y*b.x)/length(a)/length(b));
    }
}

vec3 WavelengthToRgb(float wavelength) {
    vec3 color = vec3(0.0);

    if (wavelength < 380.0 || wavelength > 750.0) {
        return color; // 非可见光范围，返回黑色
    }

    // 根据波长计算颜色
    if (wavelength >= 380.0 && wavelength < 440.0) {
        color.r = -(wavelength - 440.0) / (440.0 - 380.0);
        color.g = 0.0;
        color.b = 1.0;
    } else if (wavelength >= 440.0 && wavelength < 490.0) {
        color.r = 0.0;
        color.g = (wavelength - 440.0) / (490.0 - 440.0);
        color.b = 1.0;
    } else if (wavelength >= 490.0 && wavelength < 510.0) {
        color.r = 0.0;
        color.g = 1.0;
        color.b = -(wavelength - 510.0) / (510.0 - 490.0);
    } else if (wavelength >= 510.0 && wavelength < 580.0) {
        color.r = (wavelength - 510.0) / (580.0 - 510.0);
        color.g = 1.0;
        color.b = 0.0;
    } else if (wavelength >= 580.0 && wavelength < 645.0) {
        color.r = 1.0;
        color.g = -(wavelength - 645.0) / (645.0 - 580.0);
        color.b = 0.0;
    } else if (wavelength >= 645.0 && wavelength <= 750.0) {
        color.r = 1.0;
        color.g = 0.0;
        color.b = 0.0;
    }

    // 亮度调整
    float factor = 0.0;
    if (wavelength >= 380.0 && wavelength < 420.0) {
        factor = 0.3 + 0.7 * (wavelength - 380.0) / (420.0 - 380.0);
    } else if (wavelength >= 420.0 && wavelength < 645.0) {
        factor = 1.0;
    } else if (wavelength >= 645.0 && wavelength <= 750.0) {
        factor = 0.3 + 0.7 * (750.0 - wavelength) / (750.0 - 645.0);
    }

    return color * factor/pow(color.r*color.r+2.25*color.g*color.g+0.36*color.b*color.b,0.5)*(0.1*(color.r+color.g+color.b)+0.9);
}

float omega(float r,float Rs){//绕黑洞公转角速度
    return sqrt(lightspeed/ly*lightspeed*Rs/ly/((2.0*r-3.0*Rs)*r*r));
}

vec3 GetBH(vec4 a,vec3 BHPos,vec3 DiskDir)//BH系平移旋转
    {
    vec3 vecz =vec3( 0.0,0.0,1.0 );
    if(DiskDir==vecz){
        DiskDir+=0.0001*(vec3(1.0,0.,0.));
    }
     vec3 _X = normalize(cross(vecz, DiskDir));
     vec3 _Y = normalize(cross(DiskDir, _X));
     vec3 _Z = normalize(DiskDir);
    a=(transpose(mat4x4(
        1., 0., 0., -BHPos.x,
        0., 1., 0., -BHPos.y,
        0., 0., 1., -BHPos.z,
        0., 0., 0., 1.
    ))*a);
    a=transpose(mat4x4(
        _X.x,_X.y,_X.z,0.,
        _Y.x,_Y.y,_Y.z,0.,
        _Z.x,_Z.y,_Z.z,0.,
        0.   ,0.   ,0.   ,1.)
        )*a;
    return a.xyz;
}

vec3 GetBHRot(vec4 a,vec3 BHPos,vec3 DiskDir)//BH系旋转
    {
    vec3 vecz =vec3( 0.0,0.0,1.0 );
    if(DiskDir==vecz){
    DiskDir+=0.0001*(vec3(1.0,0.,0.));
    }
    vec3 _X = normalize(cross(vecz, DiskDir));
    vec3 _Y = normalize(cross(DiskDir, _X));
    vec3 _Z = normalize(DiskDir);

    a=transpose(mat4x4(
        _X.x,_X.y,_X.z,0.,
        _Y.x,_Y.y,_Y.z,0.,
        _Z.x,_Z.y,_Z.z,0.,
        0.   ,0.   ,0.   ,1.)
        )*a;
    return a.xyz;
}

vec4 diskcolor(vec4 fragColor,float timerate,float steplength,vec3 RayPos,vec3 lastRayPos,vec3 RayDir,vec3 lastRayDir,vec3 WorldZ,vec3 BHPos,vec3 DiskDir,float Rs,float RIn,float ROut,float diskA,float TPeak4,float shiftMax){//吸积盘
    vec3 CamOnDisk=GetBH(vec4(0.,0.,0.,1.0),BHPos,DiskDir);//黑洞系下相机位置
    vec3 References=GetBHRot(vec4(WorldZ,1.0),BHPos,DiskDir);//用于吸积盘角度零点确定
    vec3 PosOnDisk=GetBH(vec4(RayPos,1.0),BHPos,DiskDir);//光线黑洞系下位置
    vec3 DirOnDisk=GetBHRot(vec4(RayDir,1.0),BHPos,DiskDir);//光线黑洞系下方向
    
    // 此行以下在黑洞坐标系

    float PosR=length(PosOnDisk.xy);
    float PosZ=PosOnDisk.z;
    
    vec4 color=vec4(0.);
    if(abs(PosZ)<0.5*Rs && PosR<ROut && PosR>RIn){
            color=vec4(0.05);
            color.xyz*=steplength   /Rs ;
            color.a*=steplength    /Rs;
       }
   

    return fragColor + color*(1.0-fragColor.a);
}

float RandomStep(vec2 xy, float seed)//用于光线起点抖动的随机
{
    return fract(sin(dot(xy.xy+fract(11.4514*sin(seed)), vec2(12.9898, 78.233)))* 43758.5453);
}

void main() {
    // 使用传入的黑洞质量参数
    fragColor = vec4(0.,0.,0.,0.);
    vec2 uv = gl_FragCoord.xy / iResolution.xy;

    float MBH = 1.49e7;//单位是太阳质量本部分在实际使用时uniform输入
    float Rs = 2.*MBH*G0 / lightspeed / lightspeed * Msun;//单位是米 
    Rs=Rs/ly;//现在单位是ly 
    
    // 设置相机位置和黑洞位置
    vec4 BHAPos = vec4(2.*Rs, 0.0, 0.0, 1.0);//黑洞世界位置本部分在实际使用时没有
    vec3 BHRPos = GetCamera(BHAPos).xyz; //
    vec3 RayDir=uvToDir(uv+0.5*vec2(RandomStep(uv, fract(iTime * 1.0+0.5)),RandomStep(uv, fract(iTime * 1.0)))/iResolution.xy);
    vec3 RayPos = vec3(0.0,0.0,20.*Rs);
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

    // 在main函数顶部添加这些定义
    float timerate = 0.0; // 时间因子，暂时设为0
    vec3 WorldZ = vec3(0.0, 0.0, 1.0); // 世界坐标系Z轴
    vec3 BHRDiskDir = vec3(0.0, 1.0, 1.0); // 吸积盘方向（法向量）
    float RIn = 2.0 * Rs; // 吸积盘内半径（典型值：3倍史瓦西半径）
    float ROut = 10.0 * Rs; // 吸积盘外半径（典型值：20倍史瓦西半径）
    float diskA = 0.0; // 黑洞角动量参数（0-1，0为无自旋）
    float TPeak4 = 1.0; // 温度峰值参数（无量纲）
    float shiftMax = 1.0; // 最大多普勒频移因子

    while(flag==true){//测地raymarching
        lastRayPos = RayPos;
        lastRayDir = RayDir;
        lastR = Dis;
        costheta = length(cross(NPosToBH,RayDir));//前进方向与切向夹角
        dphirate = -1.0*costheta*costheta*costheta*(1.5*Rs/Dis);//单位长度光偏折角

        if(count==0){
            dl=RandomStep(uv, fract(iTime * 1.0));//光起步步长抖动
        }else{
            dl=1.0;
        }
        dl *= 0.15;
        dl *= Dis;

        RayPos += RayDir*dl;
        dthe = dl / Dis*dphirate;
        RayDir = normalize(RayDir+(dthe+dthe*dthe*dthe/3.0)*cross(cross(RayDir,NPosToBH),RayDir)/costheta);//更新方向，里面的（dthe +dthe^3/3）是tan（dthe）
        steplength = length(RayPos-lastRayPos);
                
        PosToBH = RayPos - BHRPos;
        Dis = length(PosToBH);
        NPosToBH = PosToBH/Dis;

        fragColor=diskcolor(fragColor, timerate, steplength, RayPos, lastRayPos, RayDir, lastRayDir, 
                            WorldZ, BHRPos, BHRDiskDir, Rs, RIn, ROut, diskA, TPeak4, shiftMax);//吸积盘颜色
        
        count++;
        if(Dis>(100.*Rs) && Dis>lastR && count>50){//远离黑洞
            flag = false;
            
            // 根据背景类型选择不同的背景
            if (backgroundType == 0) { // 棋盘背景
                uv = DirTouv(RayDir);
                fragColor+=0.5*texelFetch(iChannel1, ivec2(vec2(fract(uv.x),fract(uv.y))*iChannelResolution.xy), 0)*(1.0-fragColor.a);            
            } else if (backgroundType == 1) { // 纯黑背景
                fragColor += vec4(0.0, 0.0, 0.0, 1.0) * (1.0 - fragColor.a);
            } else { // 其他背景类型暂时使用棋盘背景
                uv = DirTouv(RayDir);
                fragColor+=0.5*texelFetch(iChannel1, ivec2(vec2(fract(uv.x),fract(uv.y))*iChannelResolution.xy), 0)*(1.0-fragColor.a);
            }
        }
        if(Dis < 0.1 * Rs){//命中奇点
            flag = false;
        }
    }
    fragColor.a = 1.0;

    // float blendWeight = 1.0-pow(0.5,(iTimeDelta)/max(min((0.131*36.0/(timerate)*(omega(3.*0.00000465,0.00000465))/(omega(3.*Rs,Rs))),0.3),0.02));//本部分在实际使用时max(min((0.131*36.0/(timerate)*(omega(3.*0.00000465,0.00000465))/(omega(3.*Rs,Rs))),0.3),0.02)由uniform输入
    // blendWeight = (iFrame<2 || iMouse.z > 0.0 ) ? 1.0 : blendWeight;
    
    // vec4 previousColor = texelFetch(iChannel3, ivec2(fragCoord), 0); //获取前一帧的颜色
    // fragColor = (blendWeight)*fragColor+(1.0-blendWeight)*previousColor; //混合当前帧和前一帧

}