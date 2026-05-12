# config.py
import os

# 获取当前文件所在目录（即项目根目录）
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# 配置参数
VIDEO_URL = "http://172.20.10.10:5000/video_feed"  # 视频流地址
MODEL_PATH = os.path.join(PROJECT_ROOT, "assets", "yolov5s.pt")  # YOLOv5 模型路径
TARGET_DIR = os.path.join(PROJECT_ROOT, "output", "targets")      # 目标物体图像存储目录
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")                 # 输出图像目录




###硬路径###OUTPUT_DIR = "F:/44444/aaaaaoutput"             # 输出图像目录
###TARGET_DIR = "F:/44444"                         # 目标物体图像存储目录