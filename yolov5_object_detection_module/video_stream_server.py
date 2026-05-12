from flask import Flask, Response
import cv2

app = Flask(__name__)

# 设置摄像头
camera = cv2.VideoCapture(0)  # 使用本地摄像头（你也可以替换为其他视频源）

def generate():
    while True:
        ret, frame = camera.read()
        if not ret:
            break
        # 对帧进行编码
        ret, jpeg = cv2.imencode('.jpg', frame)
        if not ret:
            continue
        # 将帧作为 JPEG 数据传输
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

#在PyCharm中直接运行video_stream_server.py常无法正确连接，ai认为是“防火墙或其他网络配置可能会阻止 PyCharm 与 Flask 服务器进行通信”
#在终端中运行： python video_stream_server.py