from PyQt6.QtWidgets import (QFrame, QVBoxLayout, QGroupBox, QPushButton, 
                            QSlider, QLabel, QVBoxLayout, QHBoxLayout)
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt

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
        
        # 尺寸控制部分
        self.size_group = QGroupBox("Circle Size")
        size_layout = QVBoxLayout(self.size_group)
        size_layout.setSpacing(10)
        
        size_label = QLabel("Adjust circle size:")
        size_layout.addWidget(size_label)
        
        # 尺寸滑块
        self.size_slider = QSlider(Qt.Orientation.Horizontal)
        self.size_slider.setRange(1, 200)
        self.size_slider.setValue(100)
        self.size_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.size_slider.setTickInterval(10)
        self.size_slider.valueChanged.connect(self.onSizeChanged)
        size_layout.addWidget(self.size_slider)
        
        self.size_value_label = QLabel("Size: 100%")
        size_layout.addWidget(self.size_value_label)
        
        control_layout.addWidget(self.size_group)
        
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
        
    def setAspectRatio(self, ratio):
        # 计算宽高比并显示
        width = self.parent().canvas.width() if self.parent() else 1
        height = self.parent().canvas.height() if self.parent() else 1
        
        if width > height:
            aspect = width / height
            self.ratio_label.setText(f"Current: {aspect:.2f} : 1")
        else:
            aspect = height / width
            self.ratio_label.setText(f"Current: 1 : {aspect:.2f}")
        
    def setSizeValue(self, value):
        self.size_value_label.setText(f"Size: {value}%")
        
    def onSizeChanged(self, value):
        self.setSizeValue(value)
        self.sizeChanged.emit(value)
        
    def customColorRequested(self):
        self.customColorClicked.emit()

# 为控件面板添加信号
from PyQt6.QtCore import pyqtSignal

class ControlPanelSignals(ControlPanel):
    colorSelected = pyqtSignal(float, float, float)
    customColorClicked = pyqtSignal()
    sizeChanged = pyqtSignal(int)
    requestAspectRatioUpdate = pyqtSignal()  # 新增信号，请求更新宽高比

# 合并信号类
# 合并信号类
class ControlPanel(ControlPanelSignals):
    def setAspectRatio(self, ratio_text):
        """设置宽高比显示文本"""
        self.ratio_label.setText(ratio_text)