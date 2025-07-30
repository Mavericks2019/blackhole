# opengl_widgets.py
from PyQt5.QtWidgets import QOpenGLWidget, QWidget
from PyQt5.QtGui import QColor, QImage, QPainter
from PyQt5.QtCore import Qt, QPointF
import numpy as np
import math
import random
from cvt_utils import compute_voronoi, compute_delaunay, lloyd_relaxation

class GLCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(800, 600)
        self.backgroundColor = QColor(30, 30, 40)
        self.wireframeColor = QColor(255, 0, 0)
        self.surfaceColor = QColor(179, 179, 204)
        self.showWireframe = True
        self.showSurface = True
        self.specularEnabled = True
        self.renderMode = "Solid"
        
        # 用于参数化视图的标记
        self.isParameterizationView = False
        
        # 模型信息
        self.modelLoaded = False
        self.modelName = ""
        self.vertexCount = 0
        self.faceCount = 0
        
        # 显示控制
        self.showPoints = True
        self.showVoronoi = False
        self.showDelaunay = False
        
        # CVT状态
        self.cvtPoints = []
        self.cvtView = False

    def loadModel(self, file_path):
        self.modelLoaded = True
        self.modelName = file_path.split("/")[-1]
        self.vertexCount = 5000  # 模拟数据
        self.faceCount = 10000   # 模拟数据
        self.update()

    def setBackgroundColor(self, color):
        self.backgroundColor = color
        self.update()

    def setWireframeColor(self, color):
        self.wireframeColor = color
        self.update()

    def setSurfaceColor(self, color):
        self.surfaceColor = color
        self.update()

    def setShowWireframeOverlay(self, show):
        self.showWireframe = show
        self.update()

    def setHideFaces(self, hide):
        self.showSurface = not hide
        self.update()

    def setRenderMode(self, mode):
        self.renderMode = mode
        self.update()

    def setBoundaryType(self, boundary_type):
        # 模拟边界类型设置
        pass

    def setShowPoints(self, show):
        self.showPoints = show
        self.update()

    def setShowVoronoiDiagram(self, show):
        self.showVoronoi = show
        self.update()

    def setShowDelaunay(self, show):
        self.showDelaunay = show
        self.update()

    def setCVTView(self, enabled):
        self.cvtView = enabled
        self.update()

    def resetView(self):
        # 模拟重置视图
        self.update()

    def centerView(self):
        # 模拟居中视图
        self.update()

    def generateRandomPoints(self, count):
        # 模拟生成随机点
        self.cvtPoints = []
        for _ in range(count):
            x = 0.1 + 0.8 * (id(self) % 100) / 100.0
            y = 0.1 + 0.8 * (id(self) % 73) / 73.0
            self.cvtPoints.append((x, y))
        self.update()

    def performLloydRelaxation(self):
        # 模拟Lloyd松弛
        if self.cvtPoints:
            # 简单移动点以模拟效果
            self.cvtPoints = [(x + 0.01, y + 0.01) for x, y in self.cvtPoints]
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 填充背景
        painter.fillRect(self.rect(), self.backgroundColor)
        
        # 显示模型或图像
        if self.modelLoaded:
            self.drawModel(painter)
        
        # 显示CVT点
        if self.cvtPoints and self.showPoints:
            self.drawCVTPoints(painter)
        
        # 显示Voronoi图
        if self.showVoronoi:
            self.drawVoronoi(painter)
        
        # 显示Delaunay三角
        if self.showDelaunay:
            self.drawDelaunay(painter)
        
        # 显示边界
        painter.setPen(QColor(100, 100, 150))
        painter.drawRect(10, 10, self.width() - 20, self.height() - 20)
        
        # 显示状态信息
        if self.modelLoaded:
            info = f"{self.modelName}\nVertices: {self.vertexCount}, Faces: {self.faceCount}\nMode: {self.renderMode}"
            painter.setPen(QColor(255, 255, 255))
            painter.drawText(20, 30, info)

    def drawModel(self, painter):
        # 模拟绘制模型
        center_x, center_y = self.width() // 2, self.height() // 2
        radius = min(self.width(), self.height()) // 3
        
        if self.showSurface:
            # 绘制表面
            painter.setBrush(self.surfaceColor)
            painter.setPen(Qt.NoPen)
            for i in range(8):
                angle = i * math.pi / 4
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                painter.drawEllipse(int(x - 20), int(y - 20), 40, 40)
        
        if self.showWireframe:
            # 绘制线框
            painter.setPen(self.wireframeColor)
            for i in range(8):
                angle1 = i * math.pi / 4
                angle2 = (i + 1) % 8 * math.pi / 4
                x1 = center_x + radius * math.cos(angle1)
                y1 = center_y + radius * math.sin(angle1)
                x2 = center_x + radius * math.cos(angle2)
                y2 = center_y + radius * math.sin(angle2)
                painter.drawLine(int(x1), int(y1), int(x2), int(y2))
                painter.drawLine(int(x1), int(y1), center_x, center_y)

    def drawCVTPoints(self, painter):
        # 绘制CVT点
        painter.setPen(QColor(255, 255, 0))
        painter.setBrush(QColor(255, 255, 0))
        for x, y in self.cvtPoints:
            px = 20 + int(x * (self.width() - 40))
            py = 20 + int(y * (self.height() - 40))
            painter.drawEllipse(px - 3, py - 3, 6, 6)

    def drawVoronoi(self, painter):
        # 模拟绘制Voronoi图
        if not self.cvtPoints:
            return
            
        painter.setPen(QColor(0, 200, 255))
        for i, (x1, y1) in enumerate(self.cvtPoints):
            for j, (x2, y2) in enumerate(self.cvtPoints):
                if i < j:
                    # 简单绘制连线来模拟
                    px1 = 20 + int(x1 * (self.width() - 40))
                    py1 = 20 + int(y1 * (self.height() - 40))
                    px2 = 20 + int(x2 * (self.width() - 40))
                    py2 = 20 + int(y2 * (self.height() - 40))
                    
                    # 只绘制部分连线
                    if (i + j) % 3 == 0:
                        painter.drawLine(px1, py1, px2, py2)

    def drawDelaunay(self, painter):
        # 模拟绘制Delaunay三角
        if not self.cvtPoints:
            return
            
        painter.setPen(QColor(0, 255, 100))
        for i, (x1, y1) in enumerate(self.cvtPoints):
            for j, (x2, y2) in enumerate(self.cvtPoints):
                if i < j:
                    # 简单绘制连线来模拟
                    px1 = 20 + int(x1 * (self.width() - 40))
                    py1 = 20 + int(y1 * (self.height() - 40))
                    px2 = 20 + int(x2 * (self.width() - 40))
                    py2 = 20 + int(y2 * (self.height() - 40))
                    
                    # 只绘制部分连线
                    if (i + j) % 4 == 0:
                        painter.drawLine(px1, py1, px2, py2)


class CVTImageCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(800, 600)
        self.backgroundColor = QColor(30, 30, 40)
        self.pointColor = QColor(255, 255, 0)
        self.voronoiColor = QColor(0, 200, 255)
        self.delaunayColor = QColor(0, 255, 100)
        
        # 图像和CVT状态
        self.image = None
        self.image_loaded = False
        self.show_image = True
        self.points = []
        self.voronoi_cells = []
        self.delaunay_edges = []
        self.boundary_points = []
        
        # 显示控制
        self.show_points = True
        self.show_voronoi = False
        self.show_delaunay = False
        
        # 权重类型
        self.weight_type = "Uniform"
        
        # 边界点
        self.boundary_points = [
            QPointF(0.1, 0.1),  # 左下
            QPointF(0.9, 0.1),  # 右下
            QPointF(0.1, 0.9),  # 左上
            QPointF(0.9, 0.9)   # 右上
        ]
        
        # 图像边界
        self.image_bounds = [0.1, 0.9, 0.1, 0.9]  # left, right, bottom, top

    def loadImage(self, file_path):
        self.image = QImage(file_path)
        if not self.image.isNull():
            self.image_loaded = True
            self.update_image_bounds()
            self.update()
    
    def update_image_bounds(self):
        if not self.image_loaded:
            return
            
        width_ratio = self.width() / self.image.width()
        height_ratio = self.height() / self.image.height()
        
        # 计算图像显示位置，保持宽高比
        if width_ratio < height_ratio:
            # 宽度受限
            display_height = self.image.height() * width_ratio
            self.image_bounds = [
                10,  # left
                self.width() - 10,  # right
                (self.height() - display_height) / 2,  # top
                (self.height() + display_height) / 2   # bottom
            ]
        else:
            # 高度受限
            display_width = self.image.width() * height_ratio
            self.image_bounds = [
                (self.width() - display_width) / 2,  # left
                (self.width() + display_width) / 2,   # right
                10,  # top
                self.height() - 10  # bottom
            ]
    
    def generate_points(self, count):
        self.points = []
        
        # 添加边界点
        for pt in self.boundary_points:
            self.points.append(pt)
        
        # 添加随机点
        for _ in range(count):
            x = 0.1 + 0.8 * random.random()
            y = 0.1 + 0.8 * random.random()
            self.points.append(QPointF(x, y))
        
        # 计算Voronoi和Delaunay
        self.compute_voronoi_diagram()
        self.update()
    
    def compute_voronoi_diagram(self):
        if not self.points:
            return
            
        # 转换为numpy数组
        points_np = np.array([(pt.x(), pt.y()) for pt in self.points])
        
        # 计算Voronoi图
        self.voronoi_cells = compute_voronoi(points_np)
        
        # 计算Delaunay三角剖分
        self.delaunay_edges = compute_delaunay(points_np)
    
    def lloyd_relaxation(self):
        if not self.points or not self.voronoi_cells:
            return
            
        # 执行Lloyd松弛
        new_points = lloyd_relaxation(self.points, self.voronoi_cells, 
                                     self.image, self.image_bounds, self.weight_type)
        
        # 更新点集
        self.points = new_points
        
        # 重新计算Voronoi和Delaunay
        self.compute_voronoi_diagram()
        self.update()
    
    def reset_view(self):
        # 重置视图
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 填充背景
        painter.fillRect(self.rect(), self.backgroundColor)
        
        # 绘制图像
        if self.image_loaded and self.show_image:
            # 计算缩放后的图像大小
            scaled_image = self.image.scaled(
                int(self.image_bounds[1] - self.image_bounds[0]),
                int(self.image_bounds[3] - self.image_bounds[2]),
                Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            
            # 绘制图像
            painter.drawImage(
                int(self.image_bounds[0]), 
                int(self.image_bounds[2]), 
                scaled_image
            )
        
        # 绘制Voronoi图
        if self.show_voronoi and self.voronoi_cells:
            painter.setPen(QPen(self.voronoiColor, 1.5))
            for cell in self.voronoi_cells:
                # 绘制Voronoi单元
                for i in range(len(cell)):
                    x1, y1 = cell[i]
                    x2, y2 = cell[(i+1) % len(cell)]
                    
                    # 转换为屏幕坐标
                    x1_screen = self.image_bounds[0] + x1 * (self.image_bounds[1] - self.image_bounds[0])
                    y1_screen = self.image_bounds[2] + y1 * (self.image_bounds[3] - self.image_bounds[2])
                    x2_screen = self.image_bounds[0] + x2 * (self.image_bounds[1] - self.image_bounds[0])
                    y2_screen = self.image_bounds[2] + y2 * (self.image_bounds[3] - self.image_bounds[2])
                    
                    painter.drawLine(int(x1_screen), int(y1_screen), int(x2_screen), int(y2_screen))
        
        # 绘制Delaunay三角剖分
        if self.show_delaunay and self.delaunay_edges:
            painter.setPen(QPen(self.delaunayColor, 1.5))
            for edge in self.delaunay_edges:
                # 跳过边界点
                if edge[0] < 4 or edge[1] < 4:
                    continue
                    
                pt1 = self.points[edge[0]]
                pt2 = self.points[edge[1]]
                
                # 转换为屏幕坐标
                x1_screen = self.image_bounds[0] + pt1.x() * (self.image_bounds[1] - self.image_bounds[0])
                y1_screen = self.image_bounds[2] + pt1.y() * (self.image_bounds[3] - self.image_bounds[2])
                x2_screen = self.image_bounds[0] + pt2.x() * (self.image_bounds[1] - self.image_bounds[0])
                y2_screen = self.image_bounds[2] + pt2.y() * (self.image_bounds[3] - self.image_bounds[2])
                
                painter.drawLine(int(x1_screen), int(y1_screen), int(x2_screen), int(y2_screen))
        
        # 绘制点
        if self.show_points and self.points:
            painter.setPen(Qt.NoPen)
            painter.setBrush(self.pointColor)
            for i, pt in enumerate(self.points):
                # 边界点用不同颜色
                if i < 4:
                    painter.setBrush(QColor(255, 0, 0))  # 红色边界点
                else:
                    painter.setBrush(self.pointColor)
                
                # 转换为屏幕坐标
                x_screen = self.image_bounds[0] + pt.x() * (self.image_bounds[1] - self.image_bounds[0])
                y_screen = self.image_bounds[2] + pt.y() * (self.image_bounds[3] - self.image_bounds[2])
                
                painter.drawEllipse(int(x_screen - 3), int(y_screen - 3), 6, 6)
        
        # 绘制边界
        painter.setPen(QColor(100, 100, 150))
        painter.drawRect(
            int(self.image_bounds[0]), 
            int(self.image_bounds[2]), 
            int(self.image_bounds[1] - self.image_bounds[0]), 
            int(self.image_bounds[3] - self.image_bounds[2])
        )
        
        # 显示状态信息
        if self.image_loaded:
            info = f"Image: {self.image.width()}x{self.image.height()}\nPoints: {len(self.points)}"
            painter.setPen(QColor(255, 255, 255))
            painter.drawText(20, 30, info)
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.image_loaded:
            self.update_image_bounds()