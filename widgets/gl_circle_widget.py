import math
import os
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtOpenGL import QOpenGLShaderProgram, QOpenGLShader
from PyQt6.QtCore import Qt, QFile, QTextStream
from PyQt6.QtGui import QSurfaceFormat, QVector3D
from OpenGL import GL as gl

class GLCircleWidget(QOpenGLWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(600, 600)
        
        # 配置MSAA抗锯齿
        fmt = QSurfaceFormat()
        fmt.setSamples(4)  # 4倍多重采样
        fmt.setVersion(4, 3)
        fmt.setProfile(QSurfaceFormat.OpenGLContextProfile.CoreProfile)
        self.setFormat(fmt)
        
        self.program = None
        self.vao = None  # 添加顶点数组对象(VAO)
        self.vbo = None
        self.circleColor = [1.0, 0.0, 0.0]  # 默认红色
        self.offset = [0.2, 0.2]  # 默认偏移
        self.radius = 0.2  # 默认半径
        self.blackHoleMass = 1.49e7  # 默认黑洞质量 (太阳质量单位)
        
        # 添加相机控制参数
        self.cameraDistance = 10.0  # 相机到原点的距离
        self.cameraRotationX = 0.0  # 绕X轴的旋转角度（弧度）
        self.cameraRotationY = 0.0  # 绕Y轴的旋转角度（弧度）
        self.lastMousePos = None  # 记录上一次鼠标位置

    def loadShaderFromFile(self, shader_type, file_path):
        """从文件加载着色器"""
        if not os.path.exists(file_path):
            print(f"Shader file not found: {file_path}")
            return None
            
        shader = QOpenGLShader(shader_type, self)
        file = QFile(file_path)
        if file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text):
            stream = QTextStream(file)
            shader_source = stream.readAll()
            file.close()
            
            if not shader.compileSourceCode(shader_source):
                print(f"Shader compilation error: {shader.log()}")
                return None
            return shader
        return None

    def initializeGL(self):
        # 配置OpenGL 4.3核心模式 (已经在构造函数中设置过，这里确保)
        fmt = self.format()
        fmt.setVersion(4, 3)
        fmt.setProfile(fmt.OpenGLContextProfile.CoreProfile)
        self.setFormat(fmt)

        # 创建着色器程序
        self.program = QOpenGLShaderProgram(self)
        
        # 从文件加载着色器
        vertex_shader = self.loadShaderFromFile(
            QOpenGLShader.ShaderTypeBit.Vertex, "shaders/circle.vert"
        )
        fragment_shader = self.loadShaderFromFile(
            QOpenGLShader.ShaderTypeBit.Fragment, "shaders/circle.frag"
        )
        
        if vertex_shader and fragment_shader:
            self.program.addShader(vertex_shader)
            self.program.addShader(fragment_shader)
            
            if not self.program.link():
                raise RuntimeError("Shader program link failed: " + self.program.log())
        else:
            raise RuntimeError("Shader loading failed")
            
        # 生成VAO和VBO
        self.vao = gl.glGenVertexArrays(1)
        gl.glBindVertexArray(self.vao)
        
        # 生成全屏矩形顶点数据
        self.generateScreenQuad()
        
        # 解绑VAO
        gl.glBindVertexArray(0)

    def generateScreenQuad(self):
        """生成覆盖整个视口的矩形顶点数据"""
        # 全屏矩形顶点数据（两个三角形组成）
        vertices = [
            -1.0, -1.0,  # 左下
             1.0, -1.0,  # 右下
             1.0,  1.0,  # 右上
             
            -1.0, -1.0,  # 左下
             1.0,  1.0,  # 右上
            -1.0,  1.0   # 左上
        ]
        
        # 创建或更新VBO
        if not self.vbo:
            self.vbo = gl.glGenBuffers(1)
        
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, 
                       (gl.GLfloat * len(vertices))(*vertices),
                       gl.GL_STATIC_DRAW)
        
        # 设置顶点属性指针
        gl.glEnableVertexAttribArray(0)
        gl.glVertexAttribPointer(0, 2, gl.GL_FLOAT, False, 0, None)

    def paintGL(self):
        if not self.program or not self.vao or not self.vbo:
            return

        # 清除背景
        gl.glClearColor(0.1, 0.1, 0.1, 1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        # 使用着色器程序
        self.program.bind()
        
        # 计算相机位置
        cameraPos = QVector3D(
            self.cameraDistance * math.sin(self.cameraRotationY) * math.cos(self.cameraRotationX),
            self.cameraDistance * math.sin(self.cameraRotationX),
            self.cameraDistance * math.cos(self.cameraRotationY) * math.cos(self.cameraRotationX)
        )
        
        # 设置统一变量
        self.program.setUniformValue("circleColor", *self.circleColor)
        self.program.setUniformValue("iResolution", self.width(), self.height())
        self.program.setUniformValue("offset", *self.offset)
        self.program.setUniformValue("radius", self.radius)
        self.program.setUniformValue("MBlackHole", self.blackHoleMass)  # 传递黑洞质量
        self.program.setUniformValue("cameraPos", cameraPos)  # 传递相机位置
        self.program.setUniformValue("cameraRotationX", self.cameraRotationX)
        self.program.setUniformValue("cameraRotationY", self.cameraRotationY)
        
        # 绑定VAO
        gl.glBindVertexArray(self.vao)
        
        # 绘制两个三角形（6个顶点）
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, 6)
        
        # 解绑VAO
        gl.glBindVertexArray(0)
        
        # 释放着色器程序
        self.program.release()
        
    def resizeGL(self, w, h):
        # 设置视口大小
        gl.glViewport(0, 0, w, h)
        # 触发重绘以更新宽高比
        self.update()
        
    def setCircleColor(self, r, g, b):
        """设置圆形颜色"""
        self.circleColor = [r, g, b]
        self.update()
        
    def setCircleOffset(self, x, y):
        """设置圆形偏移位置"""
        self.offset = [x, y]
        self.update()
        
    def setCircleRadius(self, radius):
        """设置圆形半径"""
        self.radius = radius
        self.update()
        
    def setBlackHoleMass(self, mass):
        """设置黑洞质量（太阳质量单位）"""
        self.blackHoleMass = mass
        self.update()
        
    # 添加鼠标事件处理
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.lastMousePos = event.position()
            
    def mouseMoveEvent(self, event):
        if self.lastMousePos is not None and event.buttons() & Qt.MouseButton.LeftButton:
            # 计算鼠标移动距离
            currentPos = event.position()
            dx = currentPos.x() - self.lastMousePos.x()
            dy = currentPos.y() - self.lastMousePos.y()
            
            # 更新旋转角度
            self.cameraRotationY += dx * 0.01
            self.cameraRotationX += dy * 0.01
            
            # 限制X轴旋转角度在[-π/2, π/2]之间，避免翻转
            self.cameraRotationX = max(-math.pi/2, min(math.pi/2, self.cameraRotationX))
            
            self.lastMousePos = currentPos
            self.update()  # 触发重绘
            
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.lastMousePos = None
            
    def wheelEvent(self, event):
        # 滚轮控制相机距离
        delta = event.angleDelta().y() / 120.0  # 获取滚轮变化量
        self.cameraDistance = max(1.0, min(100.0, self.cameraDistance - delta * 0.5))
        self.update()