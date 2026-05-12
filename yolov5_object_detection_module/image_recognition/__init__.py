# image_recognition/__init__.py

# 导入核心类和函数
from .stream import VideoStreamProcessor
from .detector import ObjectDetector

# 将这些类和函数暴露给外部
__all__ = ["VideoStreamProcessor", "ObjectDetector"]