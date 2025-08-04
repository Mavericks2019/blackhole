import math
import os
import numpy as np
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtOpenGL import QOpenGLShaderProgram, QOpenGLShader
from PyQt6.QtCore import Qt, QFile, QTextStream, QPoint
from PyQt6.QtGui import QSurfaceFormat, QMouseEvent, QImage
from OpenGL import GL as gl

class GLCircleWidget(QOpenGLWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(600, 600)
        
        # 配置MSAA抗锯齿
        fmt = QSurfaceFormat()
        fmt.setSamples(4)  # 4倍多重采样
        fmt.setVersion(4, 3)
        fmt.setProfile(QSurfaceFormat.OpenGLContextProfile.CoreProfile)
        self.setFormat(fmt)
        
        self.program = None
        self.vao = None  # 添加顶点数组对象(VAO)
        self.vbo = None
        self.circleColor = [1.0, 0.0, 0.0]  # 默认红色
        self.offset = [0.2, 0.2]  # 默认偏移
        self.radius = 0.2  # 默认半径
        self.blackHoleMass = 1.49e7  # 默认黑洞质量 (太阳质量单位)
        self.background_texture = None  # 添加背景纹理
        self.chess_texture = None       # 添加棋格纹理 (iChannel1)
        self.backgroundType = 0  # 0: 棋盘, 1: 星空, 2: 纯色, 3: 纹理
        self.chess_texture_resolution = [64.0, 64.0, 0.0]  # 棋格纹理分辨率 (宽, 高, 深度)
        
        # 添加 iMouse 变量 (类似Shadertoy的实现)
        self.iMouse = [0.0, 0.0, 0.0, 0.0]  # [current_x, current_y, click_x, click_y]
        self.mousePressed = False  # 跟踪鼠标按下状态
        self.setMouseTracking(True)  # 启用鼠标跟踪
        self.lastMousePos = QPoint()  # 添加变量记录上次鼠标位置

    def setBackgroundType(self, bg_type):
        self.backgroundType = bg_type
        self.update()

    def createChessTexture(self):
        """创建棋格纹理 (iChannel1)"""
        # 创建 64x64 的棋格纹理
        size = 64
        texture_data = np.zeros((size, size, 4), dtype=np.uint8)
        
        # 定义棋格颜色
        color1 = [220, 220, 220, 255]  # 浅色
        color2 = [80, 80, 100, 255]    # 深色
        
        # 创建棋格图案
        tile_size = size // 8
        for y in range(size):
            for x in range(size):
                tile_x = x // tile_size
                tile_y = y // tile_size
                
                if (tile_x + tile_y) % 2 == 0:
                    texture_data[y, x] = color1
                else:
                    texture_data[y, x] = color2
        
        # 创建OpenGL纹理
        self.chess_texture = gl.glGenTextures(1)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.chess_texture)
        
        # 设置纹理参数
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_REPEAT)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
        
        # 上传纹理数据
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, size, size, 0, 
                       gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, texture_data)
        
        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)

    def loadShaderFromFile(self, shader_type, file_path):
        """从文件加载着色器"""
        if not os.path.exists(file_path):
            print(f"Shader file not found: {file_path}")
            return None
            
        shader = QOpenGLShader(shader_type, self)
        file = QFile(file_path)
        if file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text):
            stream = QTextStream(file)
            shader_source = stream.readAll()
            file.close()
            
            if not shader.compileSourceCode(shader_source):
                print(f"Shader compilation error: {shader.log()}")
                return None
            return shader
        return None

    def initializeGL(self):
        # 配置OpenGL 4.3核心模式 (已经在构造函数中设置过，这里确保)
        fmt = self.format()
        fmt.setVersion(4, 3)
        fmt.setProfile(fmt.OpenGLContextProfile.CoreProfile)
        self.setFormat(fmt)

        # 创建着色器程序
        self.program = QOpenGLShaderProgram(self)
        
        # 从文件加载着色器
        vertex_shader = self.loadShaderFromFile(
            QOpenGLShader.ShaderTypeBit.Vertex, "shaders/circle.vert"
        )
        fragment_shader = self.loadShaderFromFile(
            QOpenGLShader.ShaderTypeBit.Fragment, "shaders/circle.frag"
        )
        
        if vertex_shader and fragment_shader:
            self.program.addShader(vertex_shader)
            self.program.addShader(fragment_shader)
            
            if not self.program.link():
                raise RuntimeError("Shader program link failed: " + self.program.log())
        else:
            raise RuntimeError("Shader loading failed")
            
        # 生成VAO和VBO
        self.vao = gl.glGenVertexArrays(1)
        gl.glBindVertexArray(self.vao)
        
        # 生成全屏矩形顶点数据
        self.generateScreenQuad()
        
        # 创建棋格纹理
        self.createChessTexture()
        
        # 解绑VAO
        gl.glBindVertexArray(0)

    def generateScreenQuad(self):
        """生成覆盖整个视口的矩形顶点数据"""
        # 全屏矩形顶点数据（两个三角形组成）
        vertices = [
            -1.0, -1.0,  # 左下
             1.0, -1.0,  # 右下
             1.0,  1.0,  # 右上
             
            -1.0, -1.0,  # 左下
             1.0,  1.0,  # 右上
            -1.0,  1.0   # 左上
        ]
        
        # 创建或更新VBO
        if not self.vbo:
            self.vbo = gl.glGenBuffers(1)
        
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, 
                       (gl.GLfloat * len(vertices))(*vertices),
                       gl.GL_STATIC_DRAW)
        
        # 设置顶点属性指针
        gl.glEnableVertexAttribArray(0)
        gl.glVertexAttribPointer(0, 2, gl.GL_FLOAT, False, 0, None)

    def paintGL(self):
        if not self.program or not self.vao or not self.vbo:
            return

        # 清除背景
        gl.glClearColor(0.1, 0.1, 0.1, 1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        # 使用着色器程序
        self.program.bind()
        
        # 设置统一变量
        self.program.setUniformValue("circleColor", *self.circleColor)
        self.program.setUniformValue("iResolution", self.width(), self.height())
        self.program.setUniformValue("offset", *self.offset)
        self.program.setUniformValue("radius", self.radius)
        self.program.setUniformValue("MBlackHole", self.blackHoleMass)
        self.program.setUniformValue("backgroundType", self.backgroundType)  # 设置背景类型
        
        # 传递 iMouse 变量 (类似Shadertoy)
        self.program.setUniformValue("iMouse", *self.iMouse)
        
        # 传递棋格纹理分辨率 (iChannelResolution[1])
        self.program.setUniformValue("iChannelResolution", 
                                self.chess_texture_resolution[0],
                                self.chess_texture_resolution[1],
                                self.chess_texture_resolution[2])
        
        # 绑定棋格纹理 (iChannel1) 到纹理单元1
        if self.chess_texture:
            gl.glActiveTexture(gl.GL_TEXTURE1)
            gl.glBindTexture(gl.GL_TEXTURE_2D, self.chess_texture)
            self.program.setUniformValue("iChannel1", 1)
        
        # 绑定背景纹理（如果存在）到纹理单元0
        if self.background_texture:
            gl.glActiveTexture(gl.GL_TEXTURE0)
            gl.glBindTexture(gl.GL_TEXTURE_2D, self.background_texture)
            self.program.setUniformValue("backgroundTexture", 0)
        
        # 绑定VAO
        gl.glBindVertexArray(self.vao)
        
        # 绘制两个三角形（6个顶点）
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, 6)
        
        # 解绑VAO
        gl.glBindVertexArray(0)
        
        # 解绑纹理
        if self.background_texture:
            gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
        
        # 释放着色器程序
        self.program.release()
        
    def resizeGL(self, w, h):
        # 设置视口大小
        gl.glViewport(0, 0, w, h)
        # 触发重绘以更新宽高比
        self.update()
        
    def mousePressEvent(self, event: QMouseEvent):
        """鼠标按下事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.mousePressed = True
            pos = event.position()
            self.lastMousePos = event.pos()  # 记录初始位置
            
            # 更新 iMouse 的 z 和 w 分量 (按下时的坐标)
            self.iMouse[2] = pos.x()
            self.iMouse[3] = self.height() - pos.y()  # 翻转Y坐标
            
            # 更新当前坐标
            self.iMouse[0] = pos.x()
            self.iMouse[1] = self.height() - pos.y()
            
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        """鼠标释放事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.mousePressed = False
            
            # 重置按下坐标
            self.iMouse[2] = 0.0
            self.iMouse[3] = 0.0
            
            # 更新当前坐标
            pos = event.position()
            self.iMouse[0] = pos.x()
            self.iMouse[1] = self.height() - pos.y()
            
            self.update()

    def mouseMoveEvent(self, event: QMouseEvent):
        """鼠标移动事件"""
        if not self.mousePressed:
            # 未按下时不更新视角
            return
            
        pos = event.position()
        currentPos = event.pos()
        
        # 计算鼠标移动增量
        delta = currentPos - self.lastMousePos
        self.lastMousePos = currentPos
        
        # 更新当前坐标
        self.iMouse[0] = pos.x()
        self.iMouse[1] = self.height() - pos.y()  # 翻转Y坐标
        
        # 根据移动增量更新按下坐标
        self.iMouse[2] += delta.x()
        self.iMouse[3] -= delta.y()  # Y轴方向相反
        
        self.update()
        
    def setCircleColor(self, r, g, b):
        """设置圆形颜色"""
        self.circleColor = [r, g, b]
        self.update()
        
    def setCircleOffset(self, x, y):
        """设置圆形偏移位置"""
        self.offset = [x, y]
        self.update()
        
    def setCircleRadius(self, radius):
        """设置圆形半径"""
        self.radius = radius
        self.update()
        
    def setBlackHoleMass(self, mass):
        """设置黑洞质量（太阳质量单位）"""
        self.blackHoleMass = mass
        self.update()