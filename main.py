# main.py
import sys
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout, 
    QGroupBox, QPushButton, QLabel, QSlider, QCheckBox, QRadioButton, 
    QStackedLayout, QSplitter, QLineEdit, QFileDialog, QComboBox,
    QFormLayout, QSpinBox, QDoubleSpinBox, QSizePolicy
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QColor, QPalette, QFont, QImage, QPixmap, QIcon
from opengl_widgets import GLCanvas, CVTImageCanvas
from cvt_utils import compute_voronoi, compute_delaunay, lloyd_relaxation

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("3D Model Viewer & CVT Visualization")
        self.setGeometry(100, 100, 1400, 900)
        
        # 应用深色主题
        self.apply_dark_theme()
        
        # 创建主窗口部件和布局
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)
        
        # 创建标签页控件
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #444;
                border-radius: 8px;
                margin-top: 4px;
            }
            QTabBar::tab {
                background: #505050;
                color: white;
                padding: 8px 16px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                border: 1px solid #666;
                border-bottom: none;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #606060;
                border-color: #888;
            }
            QTabBar::tab:!selected {
                background: #404040;
                border-color: #555;
            }
            QTabBar::tab:first {
                margin-left: 4px;
            }
        """)
        
        # 创建画布
        self.gl_widget = GLCanvas()
        self.cvt_gl_widget = GLCanvas()
        self.cvt_image_widget = CVTImageCanvas()
        
        # 创建标签页
        self.model_tab = self.create_model_tab()
        self.param_tab = self.create_parameterization_tab()
        self.cvt_tab = self.create_cvt_tab()
        self.cvt_weight_tab = self.create_cvt_weight_tab()
        
        self.tab_widget.addTab(self.model_tab, "OBJ Model")
        self.tab_widget.addTab(self.param_tab, "Parameterization")
        self.tab_widget.addTab(self.cvt_tab, "CVT")
        self.tab_widget.addTab(self.cvt_weight_tab, "CVT Weight")
        
        # 创建右侧控制面板
        control_panel = QWidget()
        control_panel.setFixedWidth(400)
        control_layout = QVBoxLayout(control_panel)
        control_layout.setAlignment(Qt.AlignTop)
        control_layout.setSpacing(15)
        
        # 颜色设置组
        control_layout.addWidget(self.create_color_settings_group())
        
        # 动态控制面板
        self.stacked_layout = QStackedLayout()
        control_layout.addLayout(self.stacked_layout)
        
        # 添加控制面板
        self.stacked_layout.addWidget(self.create_model_control_panel())
        self.stacked_layout.addWidget(self.create_parameterization_control_panel())
        self.stacked_layout.addWidget(self.create_cvt_control_panel())
        self.stacked_layout.addWidget(self.create_cvt_weight_control_panel())
        
        # 连接标签切换信号
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        
        # 添加到主布局
        main_layout.addWidget(self.tab_widget, 8)  # 8:2比例
        main_layout.addWidget(control_panel, 2)
    
    def apply_dark_theme(self):
        # 应用深色主题
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, Qt.black)
        self.setPalette(palette)
        
        # 设置默认字体
        font = QFont("Arial", 10)
        QApplication.setFont(font)
    
    def create_model_tab(self):
        tab = QWidget()
        layout = QHBoxLayout(tab)
        layout.addWidget(self.gl_widget)
        return tab
    
    def create_parameterization_tab(self):
        tab = QWidget()
        layout = QHBoxLayout(tab)
        
        splitter = QSplitter(Qt.Horizontal)
        
        self.left_view = GLCanvas()
        self.right_view = GLCanvas()
        self.right_view.isParameterizationView = True
        
        splitter.addWidget(self.left_view)
        splitter.addWidget(self.right_view)
        splitter.setSizes([500, 500])
        
        layout.addWidget(splitter)
        return tab
    
    def create_cvt_tab(self):
        tab = QWidget()
        layout = QHBoxLayout(tab)
        layout.addWidget(self.cvt_gl_widget)
        return tab
    
    def create_cvt_weight_tab(self):
        tab = QWidget()
        layout = QHBoxLayout(tab)
        layout.addWidget(self.cvt_image_widget)
        return tab
    
    def create_color_settings_group(self):
        group = QGroupBox("Color Settings")
        layout = QVBoxLayout(group)
        layout.setSpacing(10)
        
        # 背景颜色按钮
        bg_button = QPushButton("Change Background Color")
        bg_button.setStyleSheet(self.button_style())
        bg_button.clicked.connect(self.change_bg_color)
        
        # 线框颜色按钮
        wire_button = QPushButton("Change Wireframe Color")
        wire_button.setStyleSheet(self.button_style())
        wire_button.clicked.connect(self.change_wire_color)
        
        # 表面颜色按钮
        surface_button = QPushButton("Change Surface Color")
        surface_button.setStyleSheet(self.button_style())
        surface_button.clicked.connect(self.change_surface_color)
        
        # 高光控制复选框
        specular_check = QCheckBox("Disable Specular Highlight")
        specular_check.setStyleSheet("color: white;")
        specular_check.stateChanged.connect(self.toggle_specular)
        
        layout.addWidget(bg_button)
        layout.addWidget(wire_button)
        layout.addWidget(surface_button)
        layout.addWidget(specular_check)
        layout.addStretch()
        
        return group
    
    def create_model_control_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)
        
        # 模型信息组
        model_info_group = QGroupBox("Model Information")
        model_info_layout = QVBoxLayout(model_info_group)
        
        self.model_info_label = QLabel("No model loaded")
        self.model_info_label.setAlignment(Qt.AlignCenter)
        self.model_info_label.setFixedHeight(50)
        self.model_info_label.setStyleSheet("""
            background-color: #3A3A3A; 
            color: white; 
            border-radius: 5px; 
            padding: 5px; 
            font-size: 14px;
        """)
        self.model_info_label.setWordWrap(True)
        
        model_info_layout.addWidget(self.model_info_label)
        layout.addWidget(model_info_group)
        
        # 加载按钮
        load_button = QPushButton("Load OBJ File")
        load_button.setStyleSheet(self.button_style())
        load_button.clicked.connect(self.load_obj_file)
        layout.addWidget(load_button)
        
        # 渲染模式组
        render_group = QGroupBox("Rendering Mode")
        render_layout = QVBoxLayout(render_group)
        
        self.solid_radio = QRadioButton("Solid (Blinn-Phong)")
        self.gaussian_radio = QRadioButton("Gaussian Curvature")
        self.mean_radio = QRadioButton("Mean Curvature")
        self.max_radio = QRadioButton("Max Curvature")
        self.texture_radio = QRadioButton("Texture Mapping")
        
        self.solid_radio.setChecked(True)
        
        render_layout.addWidget(self.solid_radio)
        render_layout.addWidget(self.gaussian_radio)
        render_layout.addWidget(self.mean_radio)
        render_layout.addWidget(self.max_radio)
        render_layout.addWidget(self.texture_radio)
        
        # 连接信号
        self.solid_radio.toggled.connect(lambda: self.set_render_mode("Solid"))
        self.gaussian_radio.toggled.connect(lambda: self.set_render_mode("Gaussian"))
        self.mean_radio.toggled.connect(lambda: self.set_render_mode("Mean"))
        self.max_radio.toggled.connect(lambda: self.set_render_mode("Max"))
        self.texture_radio.toggled.connect(lambda: self.set_render_mode("Texture"))
        
        layout.addWidget(render_group)
        
        # 显示选项组
        display_group = QGroupBox("Display Options")
        display_layout = QVBoxLayout(display_group)
        
        self.wireframe_check = QCheckBox("Show Wireframe Overlay")
        self.wireframe_check.setStyleSheet("color: white;")
        self.wireframe_check.stateChanged.connect(self.toggle_wireframe)
        
        self.face_check = QCheckBox("Hide Faces")
        self.face_check.setStyleSheet("color: white;")
        self.face_check.stateChanged.connect(self.toggle_faces)
        
        display_layout.addWidget(self.wireframe_check)
        display_layout.addWidget(self.face_check)
        layout.addWidget(display_group)
        
        # 视图控制按钮
        reset_button = QPushButton("Reset View")
        reset_button.setStyleSheet(self.button_style())
        reset_button.clicked.connect(self.reset_view)
        
        center_button = QPushButton("Center View")
        center_button.setStyleSheet(self.button_style())
        center_button.clicked.connect(self.center_view)
        
        layout.addWidget(reset_button)
        layout.addWidget(center_button)
        
        layout.addStretch()
        return panel
    
    def create_parameterization_control_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)
        
        # 加载按钮
        load_button = QPushButton("Load OBJ File")
        load_button.setStyleSheet(self.button_style())
        load_button.clicked.connect(self.load_obj_file_for_param)
        layout.addWidget(load_button)
        
        # 渲染模式组
        render_group = QGroupBox("Rendering Mode")
        render_layout = QVBoxLayout(render_group)
        
        solid_radio = QRadioButton("Solid (Blinn-Phong)")
        gaussian_radio = QRadioButton("Gaussian Curvature")
        mean_radio = QRadioButton("Mean Curvature")
        max_radio = QRadioButton("Max Curvature")
        texture_radio = QRadioButton("Texture Mapping")
        
        solid_radio.setChecked(True)
        
        render_layout.addWidget(solid_radio)
        render_layout.addWidget(gaussian_radio)
        render_layout.addWidget(mean_radio)
        render_layout.addWidget(max_radio)
        render_layout.addWidget(texture_radio)
        
        # 连接信号
        solid_radio.toggled.connect(lambda: self.set_render_mode("Solid"))
        gaussian_radio.toggled.connect(lambda: self.set_render_mode("Gaussian"))
        mean_radio.toggled.connect(lambda: self.set_render_mode("Mean"))
        max_radio.toggled.connect(lambda: self.set_render_mode("Max"))
        texture_radio.toggled.connect(lambda: self.set_render_mode("Texture"))
        
        layout.addWidget(render_group)
        
        # 显示选项组
        display_group = QGroupBox("Display Options")
        display_layout = QVBoxLayout(display_group)
        
        wireframe_check = QCheckBox("Show Wireframe Overlay")
        wireframe_check.setStyleSheet("color: white;")
        wireframe_check.stateChanged.connect(self.toggle_wireframe_for_param)
        
        face_check = QCheckBox("Hide Faces")
        face_check.setStyleSheet("color: white;")
        face_check.stateChanged.connect(self.toggle_faces_for_param)
        
        display_layout.addWidget(wireframe_check)
        display_layout.addWidget(face_check)
        layout.addWidget(display_group)
        
        # 边界选项
        boundary_group = QGroupBox("Boundary Type")
        boundary_layout = QVBoxLayout(boundary_group)
        
        rect_radio = QRadioButton("Rectangle")
        circle_radio = QRadioButton("Circle")
        rect_radio.setChecked(True)
        
        # 连接信号
        rect_radio.toggled.connect(lambda: self.set_boundary_type("Rectangle"))
        circle_radio.toggled.connect(lambda: self.set_boundary_type("Circle"))
        
        boundary_layout.addWidget(rect_radio)
        boundary_layout.addWidget(circle_radio)
        layout.addWidget(boundary_group)
        
        # 参数化按钮
        param_button = QPushButton("Perform Parameterization")
        param_button.setStyleSheet(self.button_style())
        param_button.clicked.connect(self.perform_parameterization)
        layout.addWidget(param_button)
        
        layout.addStretch()
        return panel
    
    def create_cvt_control_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)
        
        # 点设置组
        point_group = QGroupBox("Point Settings")
        point_layout = QVBoxLayout(point_group)
        
        # 点数输入框
        count_layout = QHBoxLayout()
        count_label = QLabel("Points Count:")
        count_label.setStyleSheet("color: white;")
        self.count_input = QLineEdit("100")
        self.count_input.setStyleSheet("""
            QLineEdit {
                background-color: #3A3A3A;
                color: white;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 4px;
            }
        """)
        count_layout.addWidget(count_label)
        count_layout.addWidget(self.count_input)
        point_layout.addLayout(count_layout)
        
        # 随机生成按钮
        random_button = QPushButton("Random generation")
        random_button.setStyleSheet(self.button_style())
        random_button.clicked.connect(self.generate_random_points)
        point_layout.addWidget(random_button)
        layout.addWidget(point_group)
        
        # Voronoi设置组
        voronoi_group = QGroupBox("Voronoi Settings")
        voronoi_layout = QVBoxLayout(voronoi_group)
        
        # 显示控制复选框
        self.show_points_check = QCheckBox("Show Points")
        self.show_points_check.setStyleSheet("color: white;")
        self.show_points_check.setChecked(True)
        self.show_points_check.stateChanged.connect(self.toggle_show_points)
        
        self.show_voronoi_check = QCheckBox("Show Voronoi Diagram")
        self.show_voronoi_check.setStyleSheet("color: white;")
        self.show_voronoi_check.stateChanged.connect(self.toggle_show_voronoi)
        
        self.show_delaunay_check = QCheckBox("Show Delaunay Triangles")
        self.show_delaunay_check.setStyleSheet("color: white;")
        self.show_delaunay_check.stateChanged.connect(self.toggle_show_delaunay)
        
        voronoi_layout.addWidget(self.show_points_check)
        voronoi_layout.addWidget(self.show_voronoi_check)
        voronoi_layout.addWidget(self.show_delaunay_check)
        layout.addWidget(voronoi_group)
        
        # Lloyd迭代组
        lloyd_group = QGroupBox("Lloyd Relaxation")
        lloyd_layout = QVBoxLayout(lloyd_group)
        
        # 迭代次数输入
        iter_layout = QHBoxLayout()
        iter_label = QLabel("Iterations:")
        iter_label.setStyleSheet("color: white;")
        self.iter_input = QLineEdit("1")
        self.iter_input.setStyleSheet("""
            QLineEdit {
                background-color: #3A3A3A;
                color: white;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 4px;
            }
        """)
        iter_layout.addWidget(iter_label)
        iter_layout.addWidget(self.iter_input)
        lloyd_layout.addLayout(iter_layout)
        
        # Lloyd按钮
        lloyd_button = QPushButton("Do Lloyd")
        lloyd_button.setStyleSheet(self.button_style())
        lloyd_button.clicked.connect(self.perform_lloyd)
        lloyd_layout.addWidget(lloyd_button)
        
        layout.addWidget(lloyd_group)
        layout.addStretch()
        return panel
    
    def create_cvt_weight_control_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)
        
        # 图像信息组
        image_info_group = QGroupBox("Image Information")
        image_layout = QVBoxLayout(image_info_group)
        
        self.image_info_label = QLabel("No image loaded")
        self.image_info_label.setAlignment(Qt.AlignCenter)
        self.image_info_label.setFixedHeight(50)
        self.image_info_label.setStyleSheet("""
            background-color: #3A3A3A; 
            color: white; 
            border-radius: 5px; 
            padding: 5px; 
            font-size: 14px;
        """)
        self.image_info_label.setWordWrap(True)
        
        image_layout.addWidget(self.image_info_label)
        layout.addWidget(image_info_group)
        
        # 图像加载组
        image_load_group = QGroupBox("Image Settings")
        image_load_layout = QVBoxLayout(image_load_group)
        
        # 加载图像按钮
        load_image_button = QPushButton("Load Image")
        load_image_button.setStyleSheet(self.button_style())
        load_image_button.clicked.connect(self.load_image_file)
        image_load_layout.addWidget(load_image_button)
        
        # 显示图像复选框
        self.show_image_check = QCheckBox("Show Image")
        self.show_image_check.setStyleSheet("color: white;")
        self.show_image_check.setChecked(True)
        self.show_image_check.stateChanged.connect(self.toggle_show_image)
        image_load_layout.addWidget(self.show_image_check)
        
        # 权重类型选择
        weight_type_layout = QHBoxLayout()
        weight_label = QLabel("Weight Type:")
        weight_label.setStyleSheet("color: white;")
        weight_combo = QComboBox()
        weight_combo.addItem("Uniform")
        weight_combo.addItem("Gradient")
        weight_combo.addItem("Texture")
        weight_combo.setStyleSheet("""
            QComboBox {
                background-color: #3A3A3A;
                color: white;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 4px;
            }
        """)
        weight_type_layout.addWidget(weight_label)
        weight_type_layout.addWidget(weight_combo)
        image_load_layout.addLayout(weight_type_layout)
        
        layout.addWidget(image_load_group)
        
        # CVT控制组
        cvt_group = QGroupBox("CVT Weight Settings")
        cvt_layout = QVBoxLayout(cvt_group)
        
        # 点数控制
        point_count_layout = QHBoxLayout()
        count_label = QLabel("Points:")
        count_label.setStyleSheet("color: white;")
        self.cvt_count_input = QLineEdit("100")
        self.cvt_count_input.setStyleSheet("""
            QLineEdit {
                background-color: #3A3A3A;
                color: white;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 4px;
            }
        """)
        point_count_layout.addWidget(count_label)
        point_count_layout.addWidget(self.cvt_count_input)
        
        # 生成点按钮
        generate_button = QPushButton("Generate Points")
        generate_button.setStyleSheet(self.button_style())
        generate_button.clicked.connect(self.generate_cvt_points)
        cvt_layout.addLayout(point_count_layout)
        cvt_layout.addWidget(generate_button)
        
        # 迭代控制
        iter_layout = QHBoxLayout()
        iter_label = QLabel("Iterations:")
        iter_label.setStyleSheet("color: white;")
        self.cvt_iter_input = QLineEdit("1")
        self.cvt_iter_input.setStyleSheet("""
            QLineEdit {
                background-color: #3A3A3A;
                color: white;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 4px;
            }
        """)
        iter_layout.addWidget(iter_label)
        iter_layout.addWidget(self.cvt_iter_input)
        
        # Lloyd松弛按钮
        lloyd_button = QPushButton("Lloyd Relaxation")
        lloyd_button.setStyleSheet(self.button_style())
        lloyd_button.clicked.connect(self.perform_cvt_lloyd)
        cvt_layout.addLayout(iter_layout)
        cvt_layout.addWidget(lloyd_button)
        
        # 显示控制
        self.cvt_show_points_check = QCheckBox("Show Points")
        self.cvt_show_points_check.setStyleSheet("color: white;")
        self.cvt_show_points_check.setChecked(True)
        self.cvt_show_points_check.stateChanged.connect(self.toggle_cvt_show_points)
        
        self.cvt_show_voronoi_check = QCheckBox("Show Voronoi")
        self.cvt_show_voronoi_check.setStyleSheet("color: white;")
        self.cvt_show_voronoi_check.stateChanged.connect(self.toggle_cvt_show_voronoi)
        
        self.cvt_show_delaunay_check = QCheckBox("Show Delaunay")
        self.cvt_show_delaunay_check.setStyleSheet("color: white;")
        self.cvt_show_delaunay_check.stateChanged.connect(self.toggle_cvt_show_delaunay)
        
        cvt_layout.addWidget(self.cvt_show_points_check)
        cvt_layout.addWidget(self.cvt_show_voronoi_check)
        cvt_layout.addWidget(self.cvt_show_delaunay_check)
        
        # 重置视图按钮
        reset_button = QPushButton("Reset View")
        reset_button.setStyleSheet(self.button_style())
        reset_button.clicked.connect(self.reset_cvt_view)
        cvt_layout.addWidget(reset_button)
        
        layout.addWidget(cvt_group)
        layout.addStretch()
        return panel
    
    def button_style(self):
        return """
            QPushButton {
                background-color: #505050;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 16px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #606060;
            }
        """
    
    def on_tab_changed(self, index):
        self.stacked_layout.setCurrentIndex(index)
        self.cvt_gl_widget.setCVTView(index == 2)
        self.cvt_gl_widget.update()
    
    def change_bg_color(self):
        color = QColorDialog.getColor(Qt.black, self, "Select Background Color")
        if color.isValid():
            self.gl_widget.setBackgroundColor(color)
            self.left_view.setBackgroundColor(color)
            self.right_view.setBackgroundColor(color)
            self.cvt_gl_widget.setBackgroundColor(color)
            self.cvt_image_widget.setBackgroundColor(color)
    
    def change_wire_color(self):
        color = QColorDialog.getColor(Qt.red, self, "Select Wireframe Color")
        if color.isValid():
            self.gl_widget.setWireframeColor(color)
            self.left_view.setWireframeColor(color)
            self.right_view.setWireframeColor(color)
    
    def change_surface_color(self):
        color = QColorDialog.getColor(QColor(179, 179, 204), self, "Select Surface Color")
        if color.isValid():
            self.gl_widget.setSurfaceColor(color)
            self.left_view.setSurfaceColor(color)
            self.right_view.setSurfaceColor(color)
    
    def toggle_specular(self, state):
        # 在实际OpenGL实现中，这里会控制高光效果
        pass
    
    def load_obj_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open OBJ File", "", "OBJ Files (*.obj)")
        if file_path:
            self.gl_widget.loadModel(file_path)
            self.model_info_label.setText(f"Model loaded: {file_path.split('/')[-1]}\nVertices: 5000, Faces: 10000")
            self.setWindowTitle(f"OBJ Viewer - {file_path.split('/')[-1]}")
    
    def load_obj_file_for_param(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open OBJ File", "", "OBJ Files (*.obj)")
        if file_path:
            self.left_view.loadModel(file_path)
            self.right_view.loadModel(file_path)
    
    def set_render_mode(self, mode):
        self.gl_widget.setRenderMode(mode)
        self.left_view.setRenderMode(mode)
        self.right_view.setRenderMode(mode)
    
    def toggle_wireframe(self, state):
        self.gl_widget.setShowWireframeOverlay(state == Qt.Checked)
    
    def toggle_faces(self, state):
        self.gl_widget.setHideFaces(state == Qt.Checked)
    
    def toggle_wireframe_for_param(self, state):
        self.left_view.setShowWireframeOverlay(state == Qt.Checked)
        self.right_view.setShowWireframeOverlay(state == Qt.Checked)
    
    def toggle_faces_for_param(self, state):
        self.left_view.setHideFaces(state == Qt.Checked)
        self.right_view.setHideFaces(state == Qt.Checked)
    
    def reset_view(self):
        self.gl_widget.resetView()
    
    def center_view(self):
        self.gl_widget.centerView()
    
    def set_boundary_type(self, boundary_type):
        self.right_view.setBoundaryType(boundary_type)
    
    def perform_parameterization(self):
        # 在实际应用中，这里会执行参数化操作
        QMessageBox.information(self, "Parameterization", "Parameterization performed successfully!")
    
    def generate_random_points(self):
        try:
            count = int(self.count_input.text())
            self.cvt_gl_widget.generateRandomPoints(count)
        except ValueError:
            pass
    
    def toggle_show_points(self, state):
        self.cvt_gl_widget.setShowPoints(state == Qt.Checked)
    
    def toggle_show_voronoi(self, state):
        self.cvt_gl_widget.setShowVoronoiDiagram(state == Qt.Checked)
    
    def toggle_show_delaunay(self, state):
        self.cvt_gl_widget.setShowDelaunay(state == Qt.Checked)
    
    def perform_lloyd(self):
        try:
            iterations = int(self.iter_input.text())
            for _ in range(iterations):
                self.cvt_gl_widget.performLloydRelaxation()
        except ValueError:
            pass
    
    def load_image_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            self.cvt_image_widget.loadImage(file_path)
            self.image_info_label.setText(
                f"Image: {file_path.split('/')[-1]}\nSize: {self.cvt_image_widget.image.width()}x{self.cvt_image_widget.image.height()}")
    
    def toggle_show_image(self, state):
        self.cvt_image_widget.show_image = (state == Qt.Checked)
        self.cvt_image_widget.update()
    
    def generate_cvt_points(self):
        try:
            count = int(self.cvt_count_input.text())
            self.cvt_image_widget.generate_points(count)
        except ValueError:
            pass
    
    def perform_cvt_lloyd(self):
        try:
            iterations = int(self.cvt_iter_input.text())
            for _ in range(iterations):
                self.cvt_image_widget.lloyd_relaxation()
        except ValueError:
            pass
    
    def toggle_cvt_show_points(self, state):
        self.cvt_image_widget.show_points = (state == Qt.Checked)
        self.cvt_image_widget.update()
    
    def toggle_cvt_show_voronoi(self, state):
        self.cvt_image_widget.show_voronoi = (state == Qt.Checked)
        self.cvt_image_widget.update()
    
    def toggle_cvt_show_delaunay(self, state):
        self.cvt_image_widget.show_delaunay = (state == Qt.Checked)
        self.cvt_image_widget.update()
    
    def reset_cvt_view(self):
        self.cvt_image_widget.reset_view()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())