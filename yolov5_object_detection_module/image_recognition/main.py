import cv2

camera = cv2.VideoCapture(0)  # 替换为摄像头索引或视频文件路径
while True:
    success, frame = camera.read()
    if not success:
        print("无法读取视频帧！")
        break
    cv2.imshow("Video", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
camera.release()
cv2.destroyAllWindows()