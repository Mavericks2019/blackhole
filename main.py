import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QColorDialog,QLabel,QFrame,QGroupBox)
from PyQt6.QtGui import QPalette, QColor, QFont
from PyQt6.QtCore import Qt

# 从其他文件导入组件
from gl_circle_widget import GLCircleWidget
from control_panel import ControlPanel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OpenGL Circle Demo - Dark Theme")
        self.setGeometry(100, 100, 900, 700)
        
        # 创建深色调色板
        dark_palette = self.createDarkPalette()
        
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
        self.control_panel = ControlPanel()
        self.applyControlPanelStyles()
        main_layout.addWidget(self.control_panel, 1)  # 控制面板占据1/4空间
        
        # 连接信号
        self.control_panel.colorSelected.connect(self.canvas.setCircleColor)
        self.control_panel.customColorClicked.connect(self.chooseCustomColor)
        self.control_panel.sizeChanged.connect(self.adjustCircleSize)
        # 新增：连接宽高比更新请求信号
        self.control_panel.requestAspectRatioUpdate.connect(self.updateAspectRatio)
        
        # 初始更新宽高比
        self.updateAspectRatio()

    def createDarkPalette(self):
        """创建深色调色板"""
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
        return dark_palette

    def applyControlPanelStyles(self):
        """应用控制面板的样式"""
        # 控制面板样式
        self.control_panel.setStyleSheet("""
            background-color: #2d2d3a;
            border-radius: 8px;
            border: 1px solid #3a3a4a;
        """)
        
        # 标题样式
        self.control_panel.findChild(QLabel, None).setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #d0d0ff;
            padding: 10px 0;
        """)
        
        # 分隔线样式
        for separator in self.control_panel.findChildren(QFrame):
            if separator.frameShape() == QFrame.Shape.HLine:
                separator.setStyleSheet("background-color: #3a3a4a;")
        
        # 组框样式
        group_style = """
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
        """
        
        for group in self.control_panel.findChildren(QGroupBox):
            group.setStyleSheet(group_style)
            
            # 特定组内标签样式
            for label in group.findChildren(QLabel):
                if "Size:" in label.text() or "Current:" in label.text():
                    label.setStyleSheet("font-weight: bold; color: #d0d0ff;")
                else:
                    label.setStyleSheet("color: #c0c0d0;")
        
        # 按钮样式
        colors = {
            "Red": (1.0, 0.0, 0.0),
            "Green": (0.0, 1.0, 0.0),
            "Blue": (0.0, 0.0, 1.0),
            "Yellow": (1.0, 1.0, 0.0),
            "Purple": (0.6, 0.0, 0.8),
            "Cyan": (0.0, 1.0, 1.0),
            "White": (1.0, 1.0, 1.0),
            "Orange": (1.0, 0.5, 0.0)
        }
        
        for name, color in colors.items():
            btn = self.control_panel.color_buttons.get(name)
            if btn:
                text_color = 'black' if (color[0]*0.299 + color[1]*0.587 + color[2]*0.114) > 0.7 else 'white'
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: rgb({int(color[0]*255)}, {int(color[1]*255)}, {int(color[2]*255)});
                        color: {text_color};
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
        
        # 自定义按钮样式
        self.control_panel.custom_btn.setStyleSheet("""
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
        
        # 滑块样式
        self.control_panel.size_slider.setStyleSheet("""
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
        
        # 信息标签样式
        for label in self.control_panel.info_group.findChildren(QLabel):
            label.setStyleSheet("color: #c0c0d0;")
        
        # 页脚样式
        self.control_panel.footer_label.setStyleSheet("color: #9090a0; font-size: 10px; margin-top: 10px;")

    def updateAspectRatio(self):
        """更新宽高比显示"""
        width = self.canvas.width()
        height = self.canvas.height()
        
        if width == 0 or height == 0:
            return
            
        if width > height:
            aspect = width / height
            ratio_text = f"Current: {aspect:.2f} : 1"
        else:
            aspect = height / width
            ratio_text = f"Current: 1 : {aspect:.2f}"
        
        self.control_panel.setAspectRatio(ratio_text)

    def chooseCustomColor(self):
        # 使用深色主题的颜色对话框
        color = QColorDialog.getColor(options=QColorDialog.ColorDialogOption.DontUseNativeDialog)
        if color.isValid():
            r = color.red() / 255.0
            g = color.green() / 255.0
            b = color.blue() / 255.0
            self.canvas.setCircleColor(r, g, b)

    def adjustCircleSize(self, value):
        self.control_panel.setSizeValue(value)
        # 调用新的setCircleSize方法
        self.canvas.setCircleSize(value)
        # 提示用户需要进一步实现
        print(f"Circle size adjusted to {value}% (implementation required)")
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.updateAspectRatio()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 设置深色主题
    app.setStyle("Fusion")
    window = MainWindow()
    app.setPalette(window.palette())  # 应用深色调色板
    
    # 设置应用字体
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    window.show()
    sys.exit(app.exec())