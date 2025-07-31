import os
import numpy as np
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtOpenGL import QOpenGLShaderProgram, QOpenGLShader
from PyQt6.QtCore import Qt, QFile, QTextStream
from OpenGL import GL as gl

class GLBasicWidget(QOpenGLWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(600, 600)
        self.program = None
        self.vbo = None
        self.vao = None
        self.rotation_angle = 0.0

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
            QOpenGLShader.ShaderTypeBit.Vertex, "basic.vert"
        )
        fragment_shader = self.loadShaderFromFile(
            QOpenGLShader.ShaderTypeBit.Fragment, "basic.frag"
        )
        
        if vertex_shader and fragment_shader:
            self.program.addShader(vertex_shader)
            self.program.addShader(fragment_shader)
            
            if not self.program.link():
                raise RuntimeError("Shader program link failed: " + self.program.log())
        else:
            raise RuntimeError("Shader loading failed")

        # 顶点数据 (彩色三角形)
        vertices = np.array([
            # 位置             # 颜色
            -0.5, -0.5, 0.0,  1.0, 0.0, 0.0,
             0.5, -0.5, 0.0,  0.0, 1.0, 0.0,
             0.0,  0.5, 0.0,  0.0, 0.0, 1.0
        ], dtype=np.float32)

        # 创建VAO和VBO
        self.vao = gl.glGenVertexArrays(1)
        self.vbo = gl.glGenBuffers(1)
        
        gl.glBindVertexArray(self.vao)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, vertices.nbytes, vertices, gl.GL_STATIC_DRAW)
        
        # 位置属性
        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 6 * vertices.itemsize, gl.ctypes.c_void_p(0))
        gl.glEnableVertexAttribArray(0)
        
        # 颜色属性
        gl.glVertexAttribPointer(1, 3, gl.GL_FLOAT, gl.GL_FALSE, 6 * vertices.itemsize, gl.ctypes.c_void_p(3 * vertices.itemsize))
        gl.glEnableVertexAttribArray(1)
        
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
        gl.glBindVertexArray(0)

    def paintGL(self):
        gl.glClearColor(0.1, 0.1, 0.15, 1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        
        if not self.program or not self.vao:
            return

        self.program.bind()
        gl.glBindVertexArray(self.vao)
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, 3)
        gl.glBindVertexArray(0)
        self.program.release()

    def resizeGL(self, w, h):
        gl.glViewport(0, 0, w, h)
        
    def rotateTriangle(self):
        """旋转三角形"""
        self.rotation_angle = (self.rotation_angle + 10) % 360
        self.update()