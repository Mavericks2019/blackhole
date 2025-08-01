from PyQt6.QtWidgets import (QFrame, QVBoxLayout, QGroupBox, QPushButton, 
                            QSlider, QLabel, QVBoxLayout, QHBoxLayout)
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt
from PyQt6.QtCore import pyqtSignal

class ControlPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        
        # 主布局
        control_layout = QVBoxLayout(self)
        control_layout.setSpacing(15)
        control_layout.setContentsMargins(15, 15, 15, 15)
        
        # 标题标签
        title_label = QLabel("OpenGL Circle Controls")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        control_layout.addWidget(title_label)
        
        # 添加分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        control_layout.addWidget(separator)
        
        # 颜色控制部分
        self.color_group = QGroupBox("Circle Color")
        color_layout = QVBoxLayout(self.color_group)
        color_layout.setSpacing(8)
        
        # 颜色按钮
        self.color_buttons = {}
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
            self.color_buttons[name] = btn
            btn.clicked.connect(lambda _, c=color: self.colorSelected.emit(*c))
            color_layout.addWidget(btn)
        
        # 自定义颜色按钮
        self.custom_btn = QPushButton("Custom Color")
        self.custom_btn.clicked.connect(self.customColorRequested)
        color_layout.addWidget(self.custom_btn)
        
        control_layout.addWidget(self.color_group)
        
        # 偏移控制部分
        self.offset_group = QGroupBox("Circle Offset")
        offset_layout = QVBoxLayout(self.offset_group)
        offset_layout.setSpacing(10)
        
        # X偏移
        x_layout = QHBoxLayout()
        x_label = QLabel("X Offset:")
        x_layout.addWidget(x_label)
        self.x_slider = QSlider(Qt.Orientation.Horizontal)
        self.x_slider.setRange(-100, 100)
        self.x_slider.setValue(20)  # 默认0.2
        self.x_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.x_slider.setTickInterval(10)
        self.x_slider.valueChanged.connect(self.onOffsetChanged)
        x_layout.addWidget(self.x_slider)
        self.x_value_label = QLabel("0.20")
        x_layout.addWidget(self.x_value_label)
        offset_layout.addLayout(x_layout)
        
        # Y偏移
        y_layout = QHBoxLayout()
        y_label = QLabel("Y Offset:")
        y_layout.addWidget(y_label)
        self.y_slider = QSlider(Qt.Orientation.Horizontal)
        self.y_slider.setRange(-100, 100)
        self.y_slider.setValue(20)  # 默认0.2
        self.y_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.y_slider.setTickInterval(10)
        self.y_slider.valueChanged.connect(self.onOffsetChanged)
        y_layout.addWidget(self.y_slider)
        self.y_value_label = QLabel("0.20")
        y_layout.addWidget(self.y_value_label)
        offset_layout.addLayout(y_layout)
        
        control_layout.addWidget(self.offset_group)
        
        # 半径控制部分
        self.radius_group = QGroupBox("Circle Radius")
        radius_layout = QVBoxLayout(self.radius_group)
        radius_layout.setSpacing(10)
        
        radius_label = QLabel("Radius:")
        radius_layout.addWidget(radius_label)
        
        self.radius_slider = QSlider(Qt.Orientation.Horizontal)
        self.radius_slider.setRange(1, 100)
        self.radius_slider.setValue(20)  # 默认0.2
        self.radius_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.radius_slider.setTickInterval(5)
        self.radius_slider.valueChanged.connect(self.onRadiusChanged)
        radius_layout.addWidget(self.radius_slider)
        
        self.radius_value_label = QLabel("0.20")
        radius_layout.addWidget(self.radius_value_label)
        
        control_layout.addWidget(self.radius_group)
        
        # 宽高比信息
        self.ratio_group = QGroupBox("Aspect Ratio")
        ratio_layout = QVBoxLayout(self.ratio_group)
        
        self.ratio_label = QLabel("Current: 1.00")
        self.ratio_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ratio_layout.addWidget(self.ratio_label)
        
        ratio_info = QLabel("To maintain circle shape:\nWidth : Height = 1 : 1")
        ratio_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ratio_layout.addWidget(ratio_info)
        
        control_layout.addWidget(self.ratio_group)
        
        # 添加拉伸因子使控件居中
        control_layout.addStretch(1)
        
        # 信息面板
        self.info_group = QGroupBox("Information")
        info_layout = QVBoxLayout(self.info_group)
        
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
        info_label.setWordWrap(True)
        info_layout.addWidget(info_label)
        
        control_layout.addWidget(self.info_group)
        
        # 添加应用信息
        self.footer_label = QLabel("© 2023 OpenGL PyQt6 Demo | Dark Theme")
        self.footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        control_layout.addWidget(self.footer_label)
        
    def setAspectRatio(self, ratio_text):
        """设置宽高比显示文本"""
        self.ratio_label.setText(ratio_text)
        
    def onOffsetChanged(self):
        """偏移改变时处理"""
        x = self.x_slider.value() / 100.0
        y = self.y_slider.value() / 100.0
        
        # 更新标签显示
        self.x_value_label.setText(f"{x:.2f}")
        self.y_value_label.setText(f"{y:.2f}")
        
        # 发出信号
        self.offsetChanged.emit(x, y)
        
    def onRadiusChanged(self, value):
        """半径改变时处理"""
        radius = value / 100.0
        self.radius_value_label.setText(f"{radius:.2f}")
        self.radiusChanged.emit(radius)
        
    def customColorRequested(self):
        self.customColorClicked.emit()

# 为控件面板添加信号
class ControlPanelSignals(ControlPanel):
    colorSelected = pyqtSignal(float, float, float)
    customColorClicked = pyqtSignal()
    offsetChanged = pyqtSignal(float, float)  # 添加偏移信号
    radiusChanged = pyqtSignal(float)  # 添加半径信号
    requestAspectRatioUpdate = pyqtSignal()  # 请求更新宽高比

# 合并信号类
class ControlPanel(ControlPanelSignals):
    pass