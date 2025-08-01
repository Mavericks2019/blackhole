import math
import os
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtOpenGL import QOpenGLShaderProgram, QOpenGLShader
from PyQt6.QtCore import Qt, QFile, QTextStream
from OpenGL import GL as gl

class GLCircleWidget(QOpenGLWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(600, 600)
        self.program = None
        self.vbo = None
        self.circleColor = [1.0, 0.0, 0.0]  # 默认红色
        self.offset = [0.2, 0.2]  # 默认偏移
        self.radius = 0.2  # 默认半径

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
        # 配置OpenGL 4.3核心模式
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
            
        # 生成全屏矩形顶点数据
        self.generateScreenQuad()

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

    def paintGL(self):
        if not self.program or not self.vbo:
            return

        # 清除背景
        gl.glClearColor(0.1, 0.1, 0.1, 1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        # 使用着色器程序
        self.program.bind()
        
        # 设置统一变量
        self.program.setUniformValue("circleColor", *self.circleColor)
        self.program.setUniformValue("iResolution", self.width(), self.height())
        self.program.setUniformValue("offset", *self.offset)
        self.program.setUniformValue("radius", self.radius)
        
        # 绑定顶点缓冲区
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)
        gl.glEnableVertexAttribArray(0)
        gl.glVertexAttribPointer(0, 2, gl.GL_FLOAT, False, 0, None)
        
        # 绘制两个三角形（6个顶点）
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, 6)
        
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