from PyQt6.QtWidgets import (QFrame, QVBoxLayout, QGroupBox, QPushButton, 
                            QSlider, QLabel, QVBoxLayout, QHBoxLayout)
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt
from PyQt6.QtCore import pyqtSignal

class ControlPanel(QFrame):
    backgroundTypeChanged = pyqtSignal(int)  # 背景类型信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        
        # 主布局
        control_layout = QVBoxLayout(self)
        control_layout.setSpacing(15)
        control_layout.setContentsMargins(15, 15, 15, 15)
        
        # 标题标签
        title_label = QLabel("OpenGL Black Hole Controls")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        control_layout.addWidget(title_label)
        
        # 添加分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        control_layout.addWidget(separator)
        
        # 背景选择部分 - 修复这里
        self.bg_group = QGroupBox("Background Type")
        bg_layout = QVBoxLayout(self.bg_group)
        bg_layout.setSpacing(8)
        bg_layout.setContentsMargins(10, 20, 10, 10)  # 增加上边距给标题空间

        # 创建按钮布局 - 修复这里
        bg_button_layout = QHBoxLayout()
        bg_button_layout.setSpacing(5)  # 减少按钮间距

        # 背景类型选择按钮 - 修复这里
        self.bg_chess_btn = QPushButton("Chess")
        self.bg_chess_btn.setCheckable(True)
        self.bg_chess_btn.setChecked(True)
        self.bg_chess_btn.setObjectName("bg_chess_btn")
        self.bg_chess_btn.setFixedHeight(30)  # 限制按钮高度
        self.bg_chess_btn.clicked.connect(lambda: self.setBackgroundType(0))
        bg_button_layout.addWidget(self.bg_chess_btn)

        self.bg_black_btn = QPushButton("Black")
        self.bg_black_btn.setCheckable(True)
        self.bg_black_btn.setObjectName("bg_black_btn")
        self.bg_black_btn.setFixedHeight(30)  # 限制按钮高度
        self.bg_black_btn.clicked.connect(lambda: self.setBackgroundType(1))
        bg_button_layout.addWidget(self.bg_black_btn)

        self.bg_stars_btn = QPushButton("Stars")
        self.bg_stars_btn.setCheckable(True)
        self.bg_stars_btn.setObjectName("bg_stars_btn")
        self.bg_stars_btn.setFixedHeight(30)  # 限制按钮高度
        self.bg_stars_btn.clicked.connect(lambda: self.setBackgroundType(2))
        bg_button_layout.addWidget(self.bg_stars_btn)

        self.bg_texture_btn = QPushButton("Texture")
        self.bg_texture_btn.setCheckable(True)
        self.bg_texture_btn.setObjectName("bg_texture_btn")
        self.bg_texture_btn.setFixedHeight(30)  # 限制按钮高度
        self.bg_texture_btn.clicked.connect(lambda: self.setBackgroundType(3))
        bg_button_layout.addWidget(self.bg_texture_btn)
        
        # 添加按钮布局到组框
        bg_layout.addLayout(bg_button_layout)
        
        control_layout.addWidget(self.bg_group)
        
        # 添加拉伸因子使控件居中
        control_layout.addStretch(1)
        
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
        
        # 添加页脚
        self.footer_label = QLabel("© 2023 OpenGL PyQt6 Demo | Dark Theme | MSAA Enabled")
        self.footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        control_layout.addWidget(self.footer_label)

    def setAspectRatio(self, ratio_text):
        """设置宽高比显示文本"""
        self.ratio_label.setText(ratio_text)
        
        # 添加这个方法
    def setBackgroundType(self, bg_type):
        """设置背景类型并发出信号"""
        # 确保只有一个按钮被选中
        if bg_type == 0:
            self.bg_chess_btn.setChecked(True)
            self.bg_black_btn.setChecked(False)
            self.bg_stars_btn.setChecked(False)
            self.bg_texture_btn.setChecked(False)
        elif bg_type == 1:
            self.bg_chess_btn.setChecked(False)
            self.bg_black_btn.setChecked(True)
            self.bg_stars_btn.setChecked(False)
            self.bg_texture_btn.setChecked(False)
        elif bg_type == 2:
            self.bg_chess_btn.setChecked(False)
            self.bg_black_btn.setChecked(False)
            self.bg_stars_btn.setChecked(True)
            self.bg_texture_btn.setChecked(False)
        elif bg_type == 3:
            self.bg_chess_btn.setChecked(False)
            self.bg_black_btn.setChecked(False)
            self.bg_stars_btn.setChecked(False)
            self.bg_texture_btn.setChecked(True)
            
        self.backgroundTypeChanged.emit(bg_type)

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
        
    def onMassChanged(self, value):
        """质量改变时处理"""
        mass = value * 1e5  # 转换为太阳质量单位 (10^5 * value)
        # 格式化显示为科学计数法
        if mass >= 1e6:
            exponent = 6
            base = mass / 1e6
            self.mass_value_label.setText(f"{base:.2f} × 10⁶")
        else:
            exponent = 5
            base = mass / 1e5
            self.mass_value_label.setText(f"{base:.2f} × 10⁵")
        self.massChanged.emit(mass)
        
    def customColorRequested(self):
        self.customColorClicked.emit()

# 为控件面板添加背景类型信号
class ControlPanelSignals(ControlPanel):
    colorSelected = pyqtSignal(float, float, float)
    customColorClicked = pyqtSignal()
    offsetChanged = pyqtSignal(float, float)
    radiusChanged = pyqtSignal(float)
    requestAspectRatioUpdate = pyqtSignal()
    massChanged = pyqtSignal(float)
    backgroundTypeChanged = pyqtSignal(int)  # 新增背景类型信号

# 合并信号类
class ControlPanel(ControlPanelSignals):
    pass