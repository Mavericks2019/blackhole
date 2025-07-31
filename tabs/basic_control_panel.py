from PyQt6.QtWidgets import (QFrame, QVBoxLayout, QPushButton, 
                            QLabel, QVBoxLayout,QGroupBox)
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt, pyqtSignal

class BasicControlPanel(QFrame):
    rotateRequested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        
        # 主布局
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # 标题标签
        title_label = QLabel("OpenGL Basic Controls")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # 添加分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)
        
        # 控制按钮
        self.rotate_btn = QPushButton("Rotate Triangle")
        self.rotate_btn.clicked.connect(self.rotateRequested.emit)
        layout.addWidget(self.rotate_btn)
        
        # 信息面板
        info_group = QGroupBox("Information")
        info_layout = QVBoxLayout(info_group)
        
        info_label = QLabel(
            "<b>OpenGL Basic Demo</b><br><br>"
            "This demo shows a simple OpenGL 4.3 core profile triangle.<br><br>"
            "<b>Features:</b><br>"
            "- Vertex Array Object (VAO)<br>"
            "- Vertex Buffer Object (VBO)<br>"
            "- Attribute pointers<br>"
            "- Color interpolation"
        )
        info_label.setWordWrap(True)
        info_layout.addWidget(info_label)
        
        layout.addWidget(info_group)
        
        # 添加应用信息
        footer_label = QLabel("© 2023 OpenGL PyQt6 Demo | Dark Theme")
        footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(footer_label)
        
        # 添加拉伸因子
        layout.addStretch(1)