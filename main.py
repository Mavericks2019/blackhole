import sys
import math
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QSlider, QLabel, QGroupBox, QColorDialog, QFrame)
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtGui import QSurfaceFormat, QColor, QPalette
from PyQt6.QtOpenGL import QOpenGLShaderProgram, QOpenGLShader
from PyQt6.QtCore import Qt
from OpenGL import GL as gl

class GLCircleWidget(QOpenGLWidget):
    # 原有画布代码保持不变
    def __init__(self):
        super().__init__()
        self.setMinimumSize(600, 600)
        self.program = None
        self.vbo = None
        self.circleColor = [1.0, 0.0, 0.0]  # 默认红色

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
        self.program.setUniformValue("circleColor", *self.circleColor)
        
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)
        gl.glEnableVertexAttribArray(0)
        gl.glVertexAttribPointer(0, 2, gl.GL_FLOAT, False, 0, None)
        
        gl.glDrawArrays(gl.GL_TRIANGLE_FAN, 0, 362)  # 361顶点+圆心
        self.program.release()

    def resizeGL(self, w, h):
        gl.glViewport(0, 0, w, h)
        
    def setCircleColor(self, r, g, b):
        self.circleColor = [r, g, b]
        self.update()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OpenGL Circle Demo")
        self.setGeometry(100, 100, 900, 700)
        
        # 创建主窗口中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # 创建OpenGL画布
        self.canvas = GLCircleWidget()
        main_layout.addWidget(self.canvas, 3)  # 画板占据3/4空间
        
        # 创建右侧控制面板
        control_panel = QFrame()
        control_panel.setFrameShape(QFrame.Shape.StyledPanel)
        control_panel.setStyleSheet("background-color: #f0f0f0; border-radius: 8px;")
        control_layout = QVBoxLayout(control_panel)
        control_layout.setSpacing(15)
        control_layout.setContentsMargins(15, 15, 15, 15)
        
        # 标题标签
        title_label = QLabel("OpenGL Circle Controls")
        title_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #333;
            padding: 10px 0;
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        control_layout.addWidget(title_label)
        
        # 添加分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        control_layout.addWidget(separator)
        
        # 颜色控制部分
        color_group = QGroupBox("Circle Color")
        color_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #aaa;
                border-radius: 5px;
                margin-top: 1ex;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        color_layout = QVBoxLayout(color_group)
        
        # 颜色按钮
        colors = [
            ("Red", (1.0, 0.0, 0.0)),
            ("Green", (0.0, 1.0, 0.0)),
            ("Blue", (0.0, 0.0, 1.0)),
            ("Yellow", (1.0, 1.0, 0.0)),
            ("Purple", (0.6, 0.0, 0.8)),
            ("Cyan", (0.0, 1.0, 1.0))
        ]
        
        for name, color in colors:
            btn = QPushButton(name)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: rgb({int(color[0]*255)}, {int(color[1]*255)}, {int(color[2]*255)});
                    color: {'black' if color[0]+color[1] > 1.0 else 'white'};
                    border: 1px solid #777;
                    border-radius: 5px;
                    padding: 8px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: rgba({int(color[0]*255)}, {int(color[1]*255)}, {int(color[2]*255)}, 200);
                }}
            """)
            btn.clicked.connect(lambda _, c=color: self.canvas.setCircleColor(*c))
            color_layout.addWidget(btn)
        
        # 自定义颜色按钮
        custom_btn = QPushButton("Custom Color")
        custom_btn.setStyleSheet("""
            QPushButton {
                background-color: #fff;
                color: #333;
                border: 1px solid #777;
                border-radius: 5px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        custom_btn.clicked.connect(self.chooseCustomColor)
        color_layout.addWidget(custom_btn)
        
        control_layout.addWidget(color_group)
        
        # 尺寸控制部分
        size_group = QGroupBox("Circle Size")
        size_group.setStyleSheet(color_group.styleSheet())
        size_layout = QVBoxLayout(size_group)
        
        size_label = QLabel("Adjust circle size:")
        size_layout.addWidget(size_label)
        
        # 尺寸滑块
        size_slider = QSlider(Qt.Orientation.Horizontal)
        size_slider.setRange(1, 200)
        size_slider.setValue(100)
        size_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        size_slider.setTickInterval(10)
        size_slider.valueChanged.connect(self.adjustCircleSize)
        size_layout.addWidget(size_slider)
        
        self.size_value_label = QLabel("Size: 100%")
        size_layout.addWidget(self.size_value_label)
        
        control_layout.addWidget(size_group)
        
        # 添加拉伸因子使控件居中
        control_layout.addStretch(1)
        
        # 信息面板
        info_group = QGroupBox("Information")
        info_group.setStyleSheet(color_group.styleSheet())
        info_layout = QVBoxLayout(info_group)
        
        info_label = QLabel(
            "This demo shows an OpenGL 4.3 core profile circle rendered using PyQt6.\n\n"
            "Features:\n"
            "- Modern OpenGL pipeline\n"
            "- GLSL 430 shaders\n"
            "- Vertex Buffer Object (VBO)\n"
            "- Interactive controls"
        )
        info_label.setWordWrap(True)
        info_layout.addWidget(info_label)
        
        control_layout.addWidget(info_group)
        
        main_layout.addWidget(control_panel, 1)  # 控制面板占据1/4空间

    def chooseCustomColor(self):
        color = QColorDialog.getColor()
        if color.isValid():
            r = color.red() / 255.0
            g = color.green() / 255.0
            b = color.blue() / 255.0
            self.canvas.setCircleColor(r, g, b)

    def adjustCircleSize(self, value):
        # 这里只是示例，实际需要修改OpenGL渲染逻辑
        # 在您的原始实现中，圆的大小是固定的
        # 如果需要实现尺寸调整，需要修改顶点数据或使用变换矩阵
        self.size_value_label.setText(f"Size: {value}%")
        # 提示用户需要进一步实现
        print(f"Circle size adjusted to {value}% (implementation required)")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 设置应用样式
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())