
import sys
import math
from PyQt6.QtWidgets import QApplication
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtGui import QSurfaceFormat
from PyQt6.QtOpenGL import QOpenGLShaderProgram, QOpenGLShader
from OpenGL import GL as gl

class GLCircleWidget(QOpenGLWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(600, 600)
        self.program = None
        self.vbo = None

    def initializeGL(self):
        # 配置OpenGL 4.3核心模式
        fmt = QSurfaceFormat()
        fmt.setVersion(4, 3)
        fmt.setProfile(QSurfaceFormat.OpenGLContextProfile.CoreProfile)
        self.setFormat(fmt)

        # 顶点着色器 (GLSL 430)
        vertex_shader = """
        #version 430 core
        layout(location = 0) in vec2 position;
        void main() {
            gl_Position = vec4(position, 0.0, 1.0);
        }
        """

        # 片段着色器 (GLSL 430)
        fragment_shader = """
        #version 430 core
        out vec4 fragColor;
        uniform vec3 circleColor;
        void main() {
            fragColor = vec4(circleColor, 1.0);
        }
        """

        # 创建着色器程序
        self.program = QOpenGLShaderProgram(self)
        if not self.program.addShaderFromSourceCode(QOpenGLShader.ShaderTypeBit.Vertex, vertex_shader):
            print("顶点着色器错误:", self.program.log())
        
        if not self.program.addShaderFromSourceCode(QOpenGLShader.ShaderTypeBit.Fragment, fragment_shader):
            print("片段着色器错误:", self.program.log())
        
        if not self.program.link():
            raise RuntimeError("着色器链接失败: " + self.program.log())

        # 生成圆形顶点数据
        vertices = [0.0, 0.0]  # 圆心
        for i in range(361):  # 360度+闭合点
            angle = math.radians(i)
            vertices.extend([0.5 * math.cos(angle), 0.5 * math.sin(angle)])

        # 创建VBO
        self.vbo = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, 
                       (gl.GLfloat * len(vertices))(*vertices),
                       gl.GL_STATIC_DRAW)

    def paintGL(self):
        if not self.program or not self.vbo:
            return

        gl.glClearColor(0.1, 0.1, 0.1, 1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        self.program.bind()
        self.program.setUniformValue("circleColor", 1.0, 0.0, 0.0)  # 红色
        
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)
        gl.glEnableVertexAttribArray(0)
        gl.glVertexAttribPointer(0, 2, gl.GL_FLOAT, False, 0, None)
        
        gl.glDrawArrays(gl.GL_TRIANGLE_FAN, 0, 362)  # 361顶点+圆心
        self.program.release()

    def resizeGL(self, w, h):
        gl.glViewport(0, 0, w, h)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GLCircleWidget()
    window.show()
    sys.exit(app.exec())
