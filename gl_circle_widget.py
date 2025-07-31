import math
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtOpenGL import QOpenGLShaderProgram, QOpenGLShader
from PyQt6.QtCore import Qt
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
        self.size_factor = 1.0  # 新增：用于控制圆的大小

    def initializeGL(self):
        # 配置OpenGL 4.3核心模式
        fmt = self.format()
        fmt.setVersion(4, 3)
        fmt.setProfile(fmt.OpenGLContextProfile.CoreProfile)
        self.setFormat(fmt)

        # 顶点着色器 (GLSL 430)
        vertex_shader = """
        #version 430 core
        layout(location = 0) in vec2 position;
        uniform float scale_x;
        uniform float scale_y;
        void main() {
            // 根据宽高比调整坐标以保持正圆
            gl_Position = vec4(position.x * scale_x, position.y * scale_y, 0.0, 1.0);
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
        # 请求更新宽高比显示

    def resizeGL(self, w, h):
        # 更新宽高比
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