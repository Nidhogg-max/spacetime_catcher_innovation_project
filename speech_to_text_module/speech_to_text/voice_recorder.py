import sounddevice as sd
import numpy as np
import wavio
import time
from datetime import datetime

def record_audio(filename, duration=None, samplerate=44100):
    """录制音频并保存为WAV文件"""
    # 设置录音参数
    channels = 1
    
    print(f"开始录音...")
    # 录制音频
    recording = sd.rec(int(duration * samplerate) if duration else None,
                      samplerate=samplerate, channels=channels, dtype='int16')
    
    try:
        while duration is None:  # 如果没有指定持续时间，等待用户按Ctrl+C停止
            sd.wait()
    except KeyboardInterrupt:
        pass
    finally:
        if duration is None:
            sd.stop()
    
    # 保存录音
    wavio.write(filename, recording, samplerate, sampwidth=2)
    print(f"录音已保存到: {filename}")

def main():
    print("简单录音程序")
    print("按Ctrl+C停止录音")
    
    try:
        while True:
            # 生成文件名（使用时间戳）
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"recording_{timestamp}.wav"
            
            try:
                # 开始新的录音
                record_audio(filename, duration=None)
                print("\n准备开始新的录音...")
                time.sleep(1)  # 稍微暂停一下，让用户有时间决定是否继续
            except KeyboardInterrupt:
                print("\n程序已退出")
                break
            except Exception as e:
                print(f"录音出错: {str(e)}")
                break
    
    except Exception as e:
        print(f"程序出错: {str(e)}")

if __name__ == "__main__":
    main()
