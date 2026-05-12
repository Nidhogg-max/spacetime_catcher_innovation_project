from image_recognition import VideoStreamProcessor
# detector.py 或 example.py
import sys
import os
import torch

# 动态添加 yolov5 文件夹到模块搜索路径
yolov5_path = os.path.join(os.path.dirname(__file__), "yolov5")
if not os.path.exists(yolov5_path):
    print(f"未找到 yolov5 文件夹，请确保 {yolov5_path} 存在！")
    sys.exit(1)
sys.path.append(yolov5_path)

def load_model(model_path):
    try:
        print(f"尝试加载模型文件: {model_path}")
        model = torch.hub.load(
            'yolov5',          # 使用本地 yolov5 文件夹
            'custom',
            path=model_path,
            source='local',    # 强制使用本地源码
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
processor = VideoStreamProcessor()
processor.process_video_stream(target_object="cell phone")  # 示例：过滤目标物体“cell phone”