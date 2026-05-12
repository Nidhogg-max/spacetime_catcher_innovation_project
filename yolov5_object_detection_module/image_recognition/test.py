from image_recognition import VideoStreamProcessor

if __name__ == "__main__":
    print("启动视频流检测...")

    processor = VideoStreamProcessor()
    processor.process_video_stream(target_object="cell phone")  # 示例：过滤目标物体“cell phone”