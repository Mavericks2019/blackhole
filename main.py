import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QSlider,
                             QHBoxLayout, QColorDialog, QLabel, QFrame, QPushButton,
                             QGroupBox, QTabWidget, QStackedWidget, QMessageBox)
from PyQt6.QtGui import QPalette, QColor, QFont
from PyQt6.QtCore import Qt

# 从其他文件导入组件
from widgets.gl_circle_widget import GLCircleWidget
from widgets.gl_basic_widget import GLBasicWidget  # 导入基本功能演示的OpenGL组件
from widgets.multipass_widget import MultiPassWidget  # 导入多通道渲染组件
from tabs.control_panel import ControlPanel
from tabs.basic_control_panel import BasicControlPanel  # 导入基本功能演示的控制面板
from tabs.multipass_control_panel import MultiPassControlPanel  # 导入多通道渲染控制面板

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OpenGL Demo - Dark Theme")
        self.setGeometry(100, 100, 2400, 1800)
        
        # 检查着色器文件是否存在
        self.checkShaderFiles()
        
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
        
        # 创建左侧面板（包含标签页和画布）
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(15)
        
        # 创建标签页控件
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        self.tab_widget.setDocumentMode(False)  # 关闭文档模式，允许自定义样式
        
        # 添加紧凑的圆角标签页样式
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                margin-top: 4px;
            }
            QTabBar::tab {
                background: #3a3a4a;
                color: #c0c0d0;
                padding: 8px 16px;
                margin-right: 4px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                border: 1px solid #3a3a4a;
                border-bottom: none;
                font-weight: bold;
                font-size: 12px;
            }
            QTabBar::tab:selected {
                background: #505060;
                color: #ffffff;
                border-color: #5a5a6a;
            }
            QTabBar::tab:hover {
                background: #454555;
            }
            QTabBar::tab:!selected {
                margin-top: 4px;
            }
        """)
        
        # 创建圆形演示标签页
        circle_tab = QWidget()
        circle_layout = QVBoxLayout(circle_tab)
        self.circle_canvas = GLCircleWidget()
        circle_layout.addWidget(self.circle_canvas)
        self.tab_widget.addTab(circle_tab, "Black Hole Demo")
        
        # 创建基本功能演示标签页
        basic_tab = QWidget()
        basic_layout = QVBoxLayout(basic_tab)
        self.basic_canvas = GLBasicWidget()
        basic_layout.addWidget(self.basic_canvas)
        self.tab_widget.addTab(basic_tab, "Basic Demo")
        
        # 创建多通道渲染标签页
        multipass_tab = QWidget()
        multipass_layout = QVBoxLayout(multipass_tab)
        self.multipass_canvas = MultiPassWidget()
        multipass_layout.addWidget(self.multipass_canvas)
        self.tab_widget.addTab(multipass_tab, "Multi-Pass Demo")
        
        left_layout.addWidget(self.tab_widget)
        main_layout.addWidget(left_panel, 3)  # 左侧占据3/4空间
        
        # 创建右侧控制面板堆栈
        self.control_stack = QStackedWidget()
        
        # 圆形控制面板
        self.circle_control = ControlPanel()
        self.applyCircleControlStyles()
        self.control_stack.addWidget(self.circle_control)
        
        # 基本功能控制面板
        self.basic_control = BasicControlPanel()
        self.applyBasicControlStyles()
        self.control_stack.addWidget(self.basic_control)
        
        # 多通道渲染控制面板
        self.multipass_control = MultiPassControlPanel()
        self.applyMultiPassControlStyles()
        self.control_stack.addWidget(self.multipass_control)
        
        main_layout.addWidget(self.control_stack, 1)  # 控制面板占据1/4空间
        
        # 连接信号
        self.connectSignals()
        
        # 标签页切换事件
        self.tab_widget.currentChanged.connect(self.onTabChanged)
        
        # 初始更新宽高比
        self.onTabChanged(0)  # 默认选择第一个标签页
        self.connectSignals()

    def checkShaderFiles(self):
        """检查着色器文件是否存在"""
        shader_files = [
            "shaders/circle.vert", "shaders/circle.frag",
            "shaders/basic.vert", "shaders/basic.frag",
            "shaders/multipass1.vert", "shaders/multipass1.frag",
            "shaders/multipass2.vert", "shaders/multipass2.frag"
        ]
        
        missing_files = [f for f in shader_files if not os.path.exists(f)]
        
        if missing_files:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setWindowTitle("Shader Files Missing")
            msg.setText("Required shader files not found:")
            msg.setInformativeText("\n".join(missing_files))
            msg.exec()

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

    def applyCircleControlStyles(self):
        """应用圆形控制面板的样式"""
        # 控制面板样式
        self.circle_control.setStyleSheet("""
            background-color: #2d2d3a;
            border-radius: 8px;
            border: 1px solid #3a3a4a;
        """)
        
        # 标题样式
        title_label = self.circle_control.findChild(QLabel, None)
        if title_label and "OpenGL Black Hole Controls" in title_label.text():
            title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #d0d0ff; padding: 10px 0;")
        
        # 背景按钮样式
        bg_button_style = """
            QPushButton {
                background-color: #505060;
                color: #e0e0ff;
                border: 1px solid #666677;
                border-radius: 5px;
                padding: 4px;
                font-weight: bold;
                min-height: 20px;
                min-width: 60px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #606070;
                border: 2px solid #8888aa;
            }
            QPushButton:pressed {
                background-color: #404050;
                border: 2px solid #a0a0c0;
            }
            QPushButton:checked {
                background-color: #6a6a8a;
                border: 2px solid #a0a0c0;
                color: #ffffff;
                font-weight: bold;
            }
            #bg_chess_btn:checked {
                background-color: #5a7a8a;
            }
            #bg_black_btn:checked {
                background-color: #5a6a9a;
            }
            #bg_stars_btn:checked {
                background-color: #6a7a7a;
            }
            #bg_texture_btn:checked {
                background-color: #7a6a8a;
            }
        """
        
        # 应用样式到背景按钮
        self.circle_control.bg_chess_btn.setStyleSheet(bg_button_style)
        self.circle_control.bg_black_btn.setStyleSheet(bg_button_style)
        self.circle_control.bg_stars_btn.setStyleSheet(bg_button_style)
        self.circle_control.bg_texture_btn.setStyleSheet(bg_button_style)
        
        # 添加程序化反馈 - 当按钮状态改变时强制重绘
        for btn in [self.circle_control.bg_chess_btn, 
                    self.circle_control.bg_black_btn, 
                    self.circle_control.bg_stars_btn, 
                    self.circle_control.bg_texture_btn]:
            btn.clicked.connect(lambda: btn.update())

    def applyBasicControlStyles(self):
        """应用基本功能控制面板的样式"""
        # 控制面板样式
        self.basic_control.setStyleSheet("""
            background-color: #2d2d3a;
            border-radius: 8px;
            border: 1px solid #3a3a4a;
        """)
        
        # 标题样式
        title_label = self.basic_control.findChild(QLabel, None)
        if title_label and "OpenGL Basic Controls" in title_label.text():
            title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #d0d0ff; padding: 10px 0;")
        
        # 分隔线样式
        for separator in self.basic_control.findChildren(QFrame):
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
        
        for group in self.basic_control.findChildren(QGroupBox):
            group.setStyleSheet(group_style)
            
            # 标签样式
            for label in group.findChildren(QLabel):
                label.setStyleSheet("color: #c0c0d0;")
        
        # 按钮样式
        rotate_btn = self.basic_control.findChild(QPushButton, "rotate_btn")
        if rotate_btn:
            rotate_btn.setStyleSheet("""
                QPushButton {
                    background-color: #6a6a8a;
                    color: #e0e0ff;
                    border: 1px solid #8888aa;
                    border-radius: 5px;
                    padding: 12px;
                    font-weight: bold;
                    font-size: 14px;
                    min-height: 40px;
                }
                QPushButton:hover {
                    background-color: #7a7a9a;
                    border: 2px solid #a0a0c0;
                }
                QPushButton:pressed {
                    background-color: #5a5a7a;
                }
            """)
        
        # 页脚样式
        footer_label = self.basic_control.findChild(QLabel, None)
        if footer_label and "©" in footer_label.text():
            footer_label.setStyleSheet("color: #9090a0; font-size: 10px; margin-top: 10px;")
            
    def applyMultiPassControlStyles(self):
        """应用多通道渲染控制面板的样式"""
        self.multipass_control.setStyleSheet("""
            background-color: #2d2d3a;
            border-radius: 8px;
            border: 1px solid #3a3a4a;
        """)
        
        # 标题样式
        title_label = self.multipass_control.findChild(QLabel, None)
        if title_label and "Multi-Pass Rendering Controls" in title_label.text():
            title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #d0d0ff; padding: 10px 0;")
        
        # 分隔线样式
        for separator in self.multipass_control.findChildren(QFrame):
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
        
        for group in self.multipass_control.findChildren(QGroupBox):
            group.setStyleSheet(group_style)
            
            # 标签样式
            for label in group.findChildren(QLabel):
                label.setStyleSheet("color: #c0c0d0;")
        
        # 页脚样式
        footer_label = self.multipass_control.findChild(QLabel, None)
        if footer_label and "©" in footer_label.text():
            footer_label.setStyleSheet("color: #9090a0; font-size: 10px; margin-top: 10px;")

    def connectSignals(self):
        """连接所有信号"""
        # 圆形演示信号
        self.circle_control.backgroundTypeChanged.connect(self.circle_canvas.setBackgroundType)
        
        # 基本功能信号
        # self.basic_control.rotateRequested.connect(self.basic_canvas.rotateTriangle)

    def onTabChanged(self, index):
        """标签页切换事件处理"""
        # 切换到对应的控制面板
        self.control_stack.setCurrentIndex(index)
        
        # 更新宽高比（仅圆形演示需要）
        if index == 0:  # 圆形演示
            self.updateAspectRatio()

    def updateAspectRatio(self):
        """更新宽高比显示（仅圆形演示）"""
        width = self.circle_canvas.width()
        height = self.circle_canvas.height()
        
        if width == 0 or height == 0:
            return
            
        if width > height:
            aspect = width / height
            ratio_text = f"Current: {aspect:.2f} : 1"
        else:
            aspect = height / width
            ratio_text = f"Current: 1 : {aspect:.2f}"
        
        self.circle_control.setAspectRatio(ratio_text)

    def resizeEvent(self, event):
        """窗口大小改变事件"""
        super().resizeEvent(event)
        # 仅在圆形演示标签激活时更新宽高比
        if self.tab_widget.currentIndex() == 0:
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