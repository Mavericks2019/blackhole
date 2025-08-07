from PyQt6.QtWidgets import (QFrame, QVBoxLayout, QLabel, QGroupBox)
from PyQt6.QtCore import Qt

class MultiPassControlPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        
        # 主布局
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # 标题标签
        title_label = QLabel("Multi-Pass Rendering Controls")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #d0d0ff;")
        layout.addWidget(title_label)
        
        # 添加分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("background-color: #3a3a4a;")
        layout.addWidget(separator)
        
        # 信息面板
        info_group = QGroupBox("Multi-Pass Rendering Demo")
        info_layout = QVBoxLayout(info_group)
        
        info_label = QLabel(
            "<b>Two-Pass Rendering Technique:</b><br><br>"
            "This demo demonstrates a multi-pass rendering technique:<br>"
            "1. <b>First Pass</b>: Renders a square to a framebuffer texture<br>"
            "2. <b>Second Pass</b>: Renders a circle using the first pass texture<br><br>"
            "<b>Technical Details:</b><br>"
            "- OpenGL Framebuffer Objects (FBO)<br>"
            "- Texture Rendering<br>"
            "- Shader Uniforms<br>"
            "- Multi-pass rendering pipeline"
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #c0c0d0;")
        info_layout.addWidget(info_label)
        
        layout.addWidget(info_group)
        
        # 添加应用信息
        footer_label = QLabel("© 2023 OpenGL PyQt6 Multi-Pass Demo")
        footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_label.setStyleSheet("color: #9090a0; font-size: 10px;")
        layout.addWidget(footer_label)
        
        # 添加拉伸因子
        layout.addStretch(1)