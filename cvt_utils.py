# cvt_utils.py
import numpy as np
from scipy.spatial import Voronoi, Delaunay
from PyQt5.QtCore import QPointF
from PyQt5.QtGui import QImage
import random
import math

def compute_voronoi(points):
    """计算Voronoi图"""
    if len(points) < 3:
        return []
    
    # 添加虚拟点以确保所有单元都是有限的
    min_coords = np.min(points, axis=0)
    max_coords = np.max(points, axis=0)
    bounding_box = np.array([
        [min_coords[0] - 1, min_coords[1] - 1],
        [min_coords[0] - 1, max_coords[1] + 1],
        [max_coords[0] + 1, min_coords[1] - 1],
        [max_coords[0] + 1, max_coords[1] + 1]
    ])
    
    # 组合原始点和边界点
    all_points = np.vstack([points, bounding_box])
    
    # 计算Voronoi图
    vor = Voronoi(all_points)
    
    # 只保留原始点的单元
    regions = []
    for region_idx in vor.point_region[:len(points)]:
        region = vor.regions[region_idx]
        if -1 in region:
            continue  # 跳过无限区域
        
        # 获取区域的顶点
        vertices = [vor.vertices[i] for i in region]
        regions.append(vertices)
    
    return regions

def compute_delaunay(points):
    """计算Delaunay三角剖分"""
    if len(points) < 3:
        return []
    
    tri = Delaunay(points)
    edges = set()
    
    # 从三角剖分中提取所有边
    for simplex in tri.simplices:
        for i in range(3):
            edge = tuple(sorted([simplex[i], simplex[(i+1) % 3]]))
            edges.add(edge)
    
    return list(edges)

def lloyd_relaxation(points, voronoi_cells, image, image_bounds, weight_type="Uniform"):
    """执行Lloyd松弛算法"""
    new_points = points.copy()
    
    # 只处理非边界点（前4个点是边界点）
    for i in range(4, len(points)):
        cell = voronoi_cells[i]
        if not cell:
            continue
        
        # 计算单元重心
        centroid = np.mean(cell, axis=0)
        
        if weight_type != "Uniform" and image is not None:
            # 使用图像灰度进行加权
            weighted_centroid = np.zeros(2)
            total_weight = 0.0
            
            # 遍历单元内的点
            for sample in cell:
                # 转换为图像坐标
                u = (sample[0] - image_bounds[0]) / (image_bounds[1] - image_bounds[0])
                v = (sample[1] - image_bounds[2]) / (image_bounds[3] - image_bounds[2])
                
                # 确保在图像范围内
                u = max(0.0, min(1.0, u))
                v = max(0.0, min(1.0, v))
                
                # 获取图像像素
                img_x = int(u * (image.width() - 1))
                img_y = int((1.0 - v) * (image.height() - 1))  # 翻转Y轴
                
                # 获取像素灰度值
                pixel = image.pixel(img_x, img_y)
                gray = (pixel >> 16) & 0xFF  # 简单灰度计算
                
                # 计算权重
                if weight_type == "Gradient":
                    # 基于灰度梯度计算权重
                    weight = gray / 255.0
                else:  # Texture
                    # 基于灰度值计算权重
                    weight = 1.0 - (gray / 255.0)
                
                # 累加加权坐标
                weighted_centroid[0] += weight * sample[0]
                weighted_centroid[1] += weight * sample[1]
                total_weight += weight
            
            if total_weight > 0:
                centroid = weighted_centroid / total_weight
        
        # 更新点位置
        new_points[i] = QPointF(centroid[0], centroid[1])
    
    return new_points