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
        self.scale_x = 1.0
        self.scale_y = 1.0
        self.size_factor = 1.0  # 用于控制圆的大小

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
            
        # 生成圆形顶点数据
        self.generateCircleVertices(0.5)  # 初始半径为0.5

    def generateCircleVertices(self, radius):
        # 生成圆形顶点数据
        vertices = [0.0, 0.0]  # 圆心
        for i in range(361):  # 360度+闭合点
            angle = math.radians(i)
            vertices.extend([radius * math.cos(angle), radius * math.sin(angle)])

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

        # 计算当前缩放比例
        width = self.width()
        height = self.height()
        
        # 确保圆形始终是正圆
        if width > height:
            self.scale_x = height / width
            self.scale_y = 1.0
        else:
            self.scale_x = 1.0
            self.scale_y = width / height

        gl.glClearColor(0.1, 0.1, 0.1, 1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        self.program.bind()
        self.program.setUniformValue("circleColor", *self.circleColor)
        self.program.setUniformValue("scale_x", self.scale_x)
        self.program.setUniformValue("scale_y", self.scale_y)
        
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)
        gl.glEnableVertexAttribArray(0)
        gl.glVertexAttribPointer(0, 2, gl.GL_FLOAT, False, 0, None)
        
        gl.glDrawArrays(gl.GL_TRIANGLE_FAN, 0, 362)  # 361顶点+圆心
        self.program.release()
        
    def resizeGL(self, w, h):
        gl.glViewport(0, 0, w, h)
        self.update()  # 触发重绘
        
    def setCircleColor(self, r, g, b):
        self.circleColor = [r, g, b]
        self.update()
        
    def setCircleSize(self, size_percent):
        """设置圆的大小（百分比）"""
        self.size_factor = size_percent / 100.0
        # 重新生成顶点数据（根据新的大小）
        self.generateCircleVertices(0.5 * self.size_factor)
        self.update()