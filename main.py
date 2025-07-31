import sys
import math
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QSlider, QLabel, QGroupBox, QColorDialog, QFrame)
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtGui import QSurfaceFormat, QColor, QPalette, QFont
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
        self.aspect_ratio = 1.0  # 宽高比

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
        uniform float aspect_ratio;  // 宽高比
        void main() {
            // 根据宽高比调整x坐标以保持正圆
            gl_Position = vec4(position.x * aspect_ratio, position.y, 0.0, 1.0);
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

        # 计算当前宽高比
        width = self.width()
        height = self.height()
        self.aspect_ratio = height / width if width > height else 1.0

        gl.glClearColor(0.1, 0.1, 0.1, 1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        self.program.bind()
        self.program.setUniformValue("circleColor", *self.circleColor)
        self.program.setUniformValue("aspect_ratio", self.aspect_ratio)
        
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)
        gl.glEnableVertexAttribArray(0)
        gl.glVertexAttribPointer(0, 2, gl.GL_FLOAT, False, 0, None)
        
        gl.glDrawArrays(gl.GL_TRIANGLE_FAN, 0, 362)  # 361顶点+圆心
        self.program.release()

    def resizeGL(self, w, h):
        # 更新宽高比
        self.aspect_ratio = h / w if w > h else 1.0
        gl.glViewport(0, 0, w, h)
        
    def setCircleColor(self, r, g, b):
        self.circleColor = [r, g, b]
        self.update()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OpenGL Circle Demo - Dark Theme")
        self.setGeometry(100, 100, 900, 700)
        
        # 创建深色调色板
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.ColorRole.Window, QColor(45, 45, 55))
        dark_palette.setColor(QPalette.ColorRole.WindowText, QColor(220, 220, 220))
        dark_palette.setColor(QPalette.ColorRole.Base, QColor(35, 35, 45))
        dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(45, 45, 55))
        dark_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(220, 220, 220))
        dark_palette.setColor(QPalette.ColorRole.ToolTipText, QColor(220, 220, 220))
        dark_palette.setColor(QPalette.ColorRole.Text, QColor(220, 220, 220))
        dark_palette.setColor(QPalette.ColorRole.Button, QColor(65, 65, 75))
        dark_palette.setColor(QPalette.ColorRole.ButtonText, QColor(220, 220, 220))
        dark_palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(110, 110, 170))
        dark_palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Link, QColor(100, 150, 200))
        
        # 创建主窗口中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_widget.setPalette(dark_palette)
        central_widget.setAutoFillBackground(True)
        
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
        control_panel.setStyleSheet("""
            background-color: #2d2d3a;
            border-radius: 8px;
            border: 1px solid #3a3a4a;
        """)
        control_layout = QVBoxLayout(control_panel)
        control_layout.setSpacing(15)
        control_layout.setContentsMargins(15, 15, 15, 15)
        
        # 标题标签
        title_label = QLabel("OpenGL Circle Controls")
        title_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #d0d0ff;
            padding: 10px 0;
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        control_layout.addWidget(title_label)
        
        # 添加分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("background-color: #3a3a4a;")
        control_layout.addWidget(separator)
        
        # 颜色控制部分
        color_group = QGroupBox("Circle Color")
        color_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #a0a0c0;
                border: 1px solid #3a3a4a;
                border-radius: 5px;
                margin-top: 1ex;
                background-color: rgba(40, 40, 50, 180);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #c0c0ff;
            }
        """)
        color_layout = QVBoxLayout(color_group)
        color_layout.setSpacing(8)
        
        # 颜色按钮
        colors = [
            ("Red", (1.0, 0.0, 0.0)),
            ("Green", (0.0, 1.0, 0.0)),
            ("Blue", (0.0, 0.0, 1.0)),
            ("Yellow", (1.0, 1.0, 0.0)),
            ("Purple", (0.6, 0.0, 0.8)),
            ("Cyan", (0.0, 1.0, 1.0)),
            ("White", (1.0, 1.0, 1.0)),
            ("Orange", (1.0, 0.5, 0.0))
        ]
        
        for name, color in colors:
            btn = QPushButton(name)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: rgb({int(color[0]*255)}, {int(color[1]*255)}, {int(color[2]*255)});
                    color: {'black' if (color[0]*0.299 + color[1]*0.587 + color[2]*0.114) > 0.7 else 'white'};
                    border: 1px solid #555;
                    border-radius: 5px;
                    padding: 8px;
                    font-weight: bold;
                    min-height: 30px;
                }}
                QPushButton:hover {{
                    border: 2px solid #fff;
                }}
                QPushButton:pressed {{
                    background-color: rgba({int(color[0]*255)}, {int(color[1]*255)}, {int(color[2]*255)}, 200);
                }}
            """)
            btn.clicked.connect(lambda _, c=color: self.canvas.setCircleColor(*c))
            color_layout.addWidget(btn)
        
        # 自定义颜色按钮
        custom_btn = QPushButton("Custom Color")
        custom_btn.setStyleSheet("""
            QPushButton {
                background-color: #505060;
                color: #e0e0ff;
                border: 1px solid #666677;
                border-radius: 5px;
                padding: 8px;
                font-weight: bold;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #606070;
                border: 2px solid #8888aa;
            }
            QPushButton:pressed {
                background-color: #404050;
            }
        """)
        custom_btn.clicked.connect(self.chooseCustomColor)
        color_layout.addWidget(custom_btn)
        
        control_layout.addWidget(color_group)
        
        # 尺寸控制部分
        size_group = QGroupBox("Circle Size")
        size_group.setStyleSheet(color_group.styleSheet())
        size_layout = QVBoxLayout(size_group)
        size_layout.setSpacing(10)
        
        size_label = QLabel("Adjust circle size:")
        size_label.setStyleSheet("color: #c0c0d0;")
        size_layout.addWidget(size_label)
        
        # 尺寸滑块
        size_slider = QSlider(Qt.Orientation.Horizontal)
        size_slider.setRange(1, 200)
        size_slider.setValue(100)
        size_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        size_slider.setTickInterval(10)
        size_slider.valueChanged.connect(self.adjustCircleSize)
        size_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #3a3a4a;
                height: 8px;
                background: #404050;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #a0a0c0;
                border: 1px solid #5a5a6a;
                width: 18px;
                margin: -4px 0;
                border-radius: 9px;
            }
            QSlider::handle:horizontal:hover {
                background: #b0b0d0;
                border: 1px solid #7a7a8a;
            }
            QSlider::sub-page:horizontal {
                background: #6a6a8a;
                border-radius: 4px;
            }
        """)
        size_layout.addWidget(size_slider)
        
        self.size_value_label = QLabel("Size: 100%")
        self.size_value_label.setStyleSheet("font-weight: bold; color: #d0d0ff;")
        size_layout.addWidget(self.size_value_label)
        
        control_layout.addWidget(size_group)
        
        # 宽高比信息
        ratio_group = QGroupBox("Aspect Ratio")
        ratio_group.setStyleSheet(color_group.styleSheet())
        ratio_layout = QVBoxLayout(ratio_group)
        
        self.ratio_label = QLabel("Current: 1.00")
        self.ratio_label.setStyleSheet("font-weight: bold; color: #d0d0ff; font-size: 14px;")
        self.ratio_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ratio_layout.addWidget(self.ratio_label)
        
        ratio_info = QLabel("To maintain circle shape:\nWidth : Height = 1 : 1")
        ratio_info.setStyleSheet("color: #c0c0d0;")
        ratio_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ratio_layout.addWidget(ratio_info)
        
        control_layout.addWidget(ratio_group)
        
        # 添加拉伸因子使控件居中
        control_layout.addStretch(1)
        
        # 信息面板
        info_group = QGroupBox("Information")
        info_group.setStyleSheet(color_group.styleSheet())
        info_layout = QVBoxLayout(info_group)
        
        info_label = QLabel(
            "<b>OpenGL Circle Demo</b><br><br>"
            "This demo shows an OpenGL 4.3 core profile circle rendered using PyQt6.<br><br>"
            "<b>Features:</b><br>"
            "- Modern OpenGL pipeline<br>"
            "- GLSL 430 shaders<br>"
            "- Vertex Buffer Object (VBO)<br>"
            "- Aspect ratio correction<br>"
            "- Interactive controls"
        )
        info_label.setStyleSheet("color: #c0c0d0;")
        info_label.setWordWrap(True)
        info_layout.addWidget(info_label)
        
        control_layout.addWidget(info_group)
        
        # 添加应用信息
        footer_label = QLabel("© 2023 OpenGL PyQt6 Demo | Dark Theme")
        footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_label.setStyleSheet("color: #9090a0; font-size: 10px; margin-top: 10px;")
        control_layout.addWidget(footer_label)
        
        main_layout.addWidget(control_panel, 1)  # 控制面板占据1/4空间
        
        # 监听窗口大小变化
        self.canvas.resized.connect(self.updateAspectRatio)

    def updateAspectRatio(self):
        """更新宽高比显示"""
        width = self.canvas.width()
        height = self.canvas.height()
        aspect = width / height
        self.ratio_label.setText(f"Current: {aspect:.2f}")
        self.ratio_label.setToolTip(f"Canvas size: {width} x {height}")

    def chooseCustomColor(self):
        # 使用深色主题的颜色对话框
        color = QColorDialog.getColor(options=QColorDialog.ColorDialogOption.DontUseNativeDialog)
        if color.isValid():
            r = color.red() / 255.0
            g = color.green() / 255.0
            b = color.blue() / 255.0
            self.canvas.setCircleColor(r, g, b)

    def adjustCircleSize(self, value):
        self.size_value_label.setText(f"Size: {value}%")
        # 提示用户需要进一步实现
        print(f"Circle size adjusted to {value}% (implementation required)")
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.updateAspectRatio()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 设置深色主题
    app.setStyle("Fusion")
    app.setPalette(MainWindow().palette())  # 应用深色调色板
    
    # 设置应用字体
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())