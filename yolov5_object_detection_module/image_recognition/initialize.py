# initialize.py
import sys
import os
import torch
from .config import DEFAULT_MODEL_PATH, OUTPUT_DIR, TARGET_DIR

# 动态添加 yolov5 文件夹到模块搜索路径
yolov5_path = os.path.join(os.path.dirname(__file__), "yolov5")
sys.path.append(yolov5_path)

def load_model_classes(model_path):
    try:
        print(f"尝试加载模型文件: {model_path}")
        checkpoint = torch.load(model_path, map_location='cpu', weights_only=False)
        model = checkpoint['model']
        class_names = model.names
        print(f"成功加载模型类别: {class_names}")
        return class_names
    except Exception as e:
        print(f"加载模型时出错: {e}")
        raise


def create_directories(base_dir, class_names):
    """
    在基础路径下创建所有必要文件夹。
    :param base_dir: 基础路径
    :param class_names: 类别列表（如 ['person', 'bicycle', 'car', ...]）
    """
    # 创建目标类别文件夹
    for class_name in class_names:
        target_folder = os.path.join(base_dir, "targets", class_name)
        os.makedirs(target_folder, exist_ok=True)
        print(f"已创建目录: {target_folder}")


if __name__ == "__main__":
    # 检查权重文件是否存在
    if not os.path.exists(DEFAULT_MODEL_PATH):
        print(f"错误：权重文件未找到，请确保路径 {DEFAULT_MODEL_PATH} 存在！")
        exit(1)

    print(f"所有存储目录将创建在: {OUTPUT_DIR}")

    # 加载模型类别
    try:
        class_names = load_model_classes(DEFAULT_MODEL_PATH)

        # 创建所有必要文件夹
        create_directories(OUTPUT_DIR, class_names)
        print(f"初始化完成：所有存储目录已创建在 {OUTPUT_DIR} 下。")
    except Exception as e:
        print(f"初始化失败: {e}")