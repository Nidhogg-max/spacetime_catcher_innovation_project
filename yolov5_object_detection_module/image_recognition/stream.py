import cv2
import os
import shutil
from .detector import ObjectDetector  # 注意前面的点号
from .config import VIDEO_URL, TARGET_DIR, OUTPUT_DIR  # 注意前面的点号

class VideoStreamProcessor:
    def __init__(self):
        # 初始化目标检测器
        self.detector = ObjectDetector()

    def process_video_stream(self, target_object=None):
        """处理视频流并进行目标检测"""
        cap = cv2.VideoCapture(VIDEO_URL)
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # 目标检测
            processed_frame, detected_objects = self.detector.detect_objects(frame, target_object)

            # 显示检测结果
            cv2.imshow("Detection", processed_frame)

            # 保存检测到的目标图像
            for obj in detected_objects.values():
                target_folder = os.path.join(TARGET_DIR, obj)
                os.makedirs(target_folder, exist_ok=True)
                filename = os.path.join(target_folder, f"last_frame_{obj}.jpg")
                cv2.imwrite(filename, processed_frame)

            # 按键处理
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('i'):
                self.set_target_object(target_object)

        cap.release()
        cv2.destroyAllWindows()

    def set_target_object(self, target_object):
        """设置目标物体并复制最新图像到输出目录"""
        if target_object:
            target_folder = os.path.join(TARGET_DIR, target_object)
            source_file = os.path.join(target_folder, f"last_frame_{target_object}.jpg")
            if os.path.exists(source_file):
                output_path = os.path.join(OUTPUT_DIR, f"last_frame_{target_object}_output.jpg")
                shutil.copy(source_file, output_path)
                print(f"{target_object} 图像已保存到 {output_path}")
            else:
                print(f"没有找到目标物体 {target_object} 的图像文件！")