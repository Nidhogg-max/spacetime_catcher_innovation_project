import sys
import os
import torch
from .config import MODEL_PATH  # 注意前面的点号

# 动态添加 yolov5 文件夹到模块搜索路径
yolov5_path = os.path.join(os.path.dirname(__file__), "yolov5")
sys.path.append(yolov5_path)

class ObjectDetector:
    def __init__(self):
        self.model = self._load_model()

    def _load_model(self):
        """加载 YOLOv5 模型"""
        try:
            print(f"尝试加载模型文件: {MODEL_PATH}")
            model = torch.hub.load(
                'yolov5',  # 本地 yolov5 文件夹
                'custom',
                path=MODEL_PATH,
                source='local',  # 强制使用本地源码
                force_reload=True
            )
            model.eval()
            print("模型加载成功。")
            return model
        except Exception as e:
            print(f"加载模型时出错: {e}")
            print("尝试从官方地址下载模型...")
            model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
            print("模型已下载完成。")
            return model

    def detect_objects(self, frame, target_object=None):
        """目标检测"""
        # 将 BGR 转换为 RGB
        img = frame[..., ::-1]

        # 使用 YOLOv5 进行目标检测
        results = self.model(img)
        results.render()  # 绘制检测框
        processed_frame = results.ims[0]

        # 将 RGB 转回 BGR
        processed_frame = processed_frame[..., ::-1]

        detected_objects = {}
        if len(results.xyxy[0]) > 0:
            for *box, conf, cls in results.xyxy[0]:
                class_id = int(cls.item())
                class_name = results.names[class_id]
                detected_objects[class_id] = class_name

        return processed_frame, detected_objects