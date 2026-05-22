from vosk import Model, KaldiRecognizer, SetLogLevel
import pyaudio
import wave
import json
import os
import time
from datetime import datetime
import audioop
import jieba
import jieba.posseg as pseg

# 设置日志级别
SetLogLevel(-1)

# 初始化语音识别模型
try:
    model = Model("model")
except Exception as e:
    print(f"错误：无法加载语音模型 - {str(e)}")
    print("请确保model文件夹存在且包含正确的模型文件")
    import sys
    sys.exit(1)

def convert_to_text(audio_file):
    """将录音文件转换为文字"""
    try:
        wf = wave.open(audio_file, "rb")
        # 创建识别器实例
        recognizer = KaldiRecognizer(model, wf.getframerate())
        
        # 读取整个音频文件
        audio_data = wf.readframes(wf.getnframes())
        
        # 进行识别
        if recognizer.AcceptWaveform(audio_data):
            result = json.loads(recognizer.Result())
        else:
            result = json.loads(recognizer.FinalResult())
            
        text = result.get('text', '')
        
        # 如果没有识别出内容
        if not text.strip():
            return "无法识别音频内容"
            
        # 对识别结果进行后处理
        text = post_process_recognition(text)
        
        return text
    except Exception as e:
        print(f"\n❌ 错误详情: {str(e)}")  # 添加详细错误信息
        return f"识别服务出错: {str(e)}"

def post_process_recognition(text):
    """对语音识别结果进行后处理，处理同音字问题"""
    # 同音字映射词典
    sound_alike_map = {
        '比': ['笔', '币'],
        '必': ['笔'],
        '壁': ['笔'],
        '避': ['笔'],
        '闭': ['笔'],
        '毕': ['笔'],
        '彼': ['笔'],
        '陪': ['杯'],
        '北': ['杯'],
        '被': ['杯'],
        '背': ['杯'],
        '钥匙': ['要是', '要是', '要死', '咬死'],
        '药': ['要', '咬', '钥'],
        '衣': ['一', '医'],
        '裤': ['哭', '酷'],
        '袜': ['挖', '瓦'],
        '帽': ['猫', '毛'],
        '伞': ['散', '三'],
        '包': ['抱', '胞'],
        '带': ['戴', '呆'],
        '手机': ['收集', '首级'],
        '钱包': ['前包', '千包'],
        '眼镜': ['演讲', '燕见'],
        '钱': ['前', '千'],
    }
    
    # 替换可能的同音字
    words = list(jieba.cut(text))
    for i, word in enumerate(words):
        for similar, replacements in sound_alike_map.items():
            if word in replacements:
                words[i] = similar
                break
    
    return ' '.join(words)

def extract_keywords(text, top_k=3):
    """从文本中提取关键词，专注于识别物品名词"""
    try:
        if not isinstance(text, str):
            print(f"错误：输入文本类型错误，期望字符串，实际为 {type(text)}")
            return []
        if not text.strip():
            print("警告：输入文本为空")
            return []
            
        # 使用结巴分词进行分词
        import jieba.posseg as pseg
        words = pseg.cut(text)
        
        # 按类别组织的物品词典
        common_items = {
            # 文具用品（扩展更多常见文具）
            '笔', '铅笔', '钢笔', '圆珠笔', '水笔', '中性笔', '记号笔', '毛笔', 
            '马克笔', '荧光笔', '粉笔', '蜡笔', '彩笔', '画笔', '笔芯', '笔盒',
            '橡皮', '橡皮擦', '尺子', '直尺', '三角尺', '量角器', '圆规',
            '文具盒', '铅笔盒', '笔袋', '笔筒', '文件夹', '活页本', '夹子',
            '订书机', '订书钉', '图钉', '回形针', '曲别针', '胶水', '胶带',
            '剪刀', '美工刀', '削笔刀', '便利贴', '便签', '贴纸',
            
            # 书本类（扩展更多种类）
            '书', '书本', '课本', '教材', '教科书', '练习册', '作业本', 
            '笔记本', '本子', '日记本', '记事本', '手账本', '素描本',
            '画册', '相册', '图册', '杂志', '期刊', '报纸', '字典',
            '词典', '图书', '漫画', '小说', '诗集', '文集',
            
            # 电子设备（扩展更多设备）
            '手机', '电话', '座机', '平板', 'iPad', '电脑', '笔记本', '显示器',
            '键盘', '鼠标', '耳机', '音响', '音箱', '蓝牙', '充电器', '数据线',
            '充电宝', '移动电源', '电池', 'U盘', '硬盘', '内存卡', 'SD卡',
            '相机', '摄像机', '录音笔', '打印机', '扫描仪', '投影仪',
            '路由器', '遥控器', '游戏机', '手柄', 'switch', 'xbox', 'ps',
            
            # 更多类别保持不变...
            # 电子设备
            '电视', '显示器', '打印机', '扫描仪',
            '耳机', '音响', '充电器', '鼠标', '键盘', '手表', '智能手环',
            '充电宝', '数据线', 'U盘', '硬盘', '相机', '摄像机', '游戏机',
            '路由器', '遥控器', '电池', '插座', '电源', '适配器',
            
            # 个人物品
            '钱包', '钥匙', '眼镜', '墨镜', '帽子', '围巾', '手套',
            '包', '背包', '公文包', '手提包', '钱包', '皮夹',
            '雨伞', '太阳伞', '梳子', '镜子', '口红', '化妆品',
            '香水', '护肤品', '面霜', '防晒霜', '面膜',
            
            # 证件文件
            '身份证', '银行卡', '信用卡', '会员卡', '门禁卡',
            '学生证', '工作证', '驾驶证', '护照', '票据',
            '发票', '合同', '文件', '资料', '证书',
            
            # 文具办公
            '笔', '铅笔', '钢笔', '圆珠笔', '记号笔', '荧光笔',
            '本子', '笔记本', '日记本', '便签', '日历', '记事本',
            '书', '杂志', '报纸', '字典', '教材', '课本',
            '尺子', '胶水', '剪刀', '订书机', '图钉', '回形针',
            
            # 生活用品
            '水杯', '保温杯', '茶杯', '咖啡杯', '餐具', '饭盒',
            '牙刷', '牙膏', '毛巾', '浴巾', '纸巾', '卫生纸',
            '肥皂', '沐浴露', '洗发水', '护发素', '梳子',
            
            # 衣物鞋帽
            '外套', '衣服', '裤子', '裙子', '西装', '夹克',
            '衬衫', '毛衣', '羽绒服', 'T恤', '内衣', '袜子',
            '鞋子', '运动鞋', '皮鞋', '拖鞋', '靴子', '凉鞋',
            
            # 首饰配件
            '项链', '戒指', '手链', '耳环', '胸针', '手表',
            '发卡', '发带', '皮带', '领带', '领结', '袖扣',
            
            # 运动用品
            '球', '篮球', '足球', '羽毛球', '乒乓球', '网球',
            '球拍', '跳绳', '瑜伽垫', '哑铃', '护具', '运动包',
            
            # 工具
            '螺丝刀', '扳手', '锤子', '钳子', '尺子', '卷尺',
            '剪刀', '美工刀', '胶带', '打火机', '手电筒', '雨伞',
            
            # 乐器
            '吉他', '钢琴', '小提琴', '笛子', '口琴', '萨克斯',
            
            # 玩具
            '玩具', '积木', '拼图', '玩偶', '毛绒玩具', '模型',
            
            # 其他
            '钥匙', '遥控器', '电池', '充电器', '数据线', '耳机',
            '纸巾', '口罩', '雨伞', '打火机', '创可贴', '药'
        }
        
        # 寻物相关的动词和短语
        search_verbs = {
            '找', '找找', '寻找', '查找', '搜索', '看看',
            '放在哪', '在哪里', '去哪了', '放哪了'
        }
        
        # 收集所有词和词性
        words_with_flags = list(words)
        
        # 首先查找物品名词
        items = []
        for word, flag in words_with_flags:
            # 如果是物品词典中的词，直接添加
            if word in common_items:
                items.append(word)
                continue
                
            # 检查是否是名词
            if flag.startswith('n'):  # 各类名词
                items.append(word)
        
        # 如果没有找到物品，尝试其他策略
        if not items:
            # 检查是否包含寻物动词，如果有，查找其后的词
            for i, (word, flag) in enumerate(words_with_flags):
                if word in search_verbs and i + 1 < len(words_with_flags):
                    next_word, next_flag = words_with_flags[i + 1]
                    if next_flag.startswith('n') and len(next_word) > 1:
                        items.append(next_word)
        
        # 过滤掉非物品词
        stop_words = {
            '一下', '这个', '那个', '什么', '谁', '哪个', '时候', 
            '东西', '地方', '位置', '今天', '明天', '昨天', '时间',
            '帮忙', '帮我', '请问', '麻烦', '知道', '告诉', '看看'
        }
        
        filtered_items = []
        for item in items:
            if (len(item) > 1 and 
                item not in stop_words and 
                not any(item.endswith(x) for x in ['吗', '呢', '啊', '吧', '里', '的'])):
                filtered_items.append(item)
        
        # 确保不返回重复项
        filtered_items = list(dict.fromkeys(filtered_items))
        
        if not filtered_items:
            print("\n⚠️ 未能识别出物品名称")
            return []
            
        return filtered_items[:top_k]
        
    except Exception as e:
        print(f"\n❌ 关键词提取出错: {str(e)}")
        return []

def main():
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    SILENCE_THRESHOLD = 400  # 适中的静音阈值
    SILENCE_CHUNKS = 40  # 保持不变
    MIN_AUDIO_LENGTH = 15  # 保持不变
    DISPLAY_VOLUME = True
    
    print("\n🎤 离线中文语音识别程序已启动...")
    print("✨ 请开始说话，声音响度超过阈值时会自动开始记录")
    print("💡 按 Ctrl+C 可以退出程序")
    
    # 检查模型文件是否存在
    if not os.path.exists("model"):
        print("\n⚠️ 未找到语音模型，正在下载中文模型...")
        print("这可能需要几分钟时间，请耐心等待...")
        try:
            import wget
            model_url = "https://alphacephei.com/vosk/models/vosk-model-small-cn-0.22.zip"
            wget.download(model_url, "model.zip")
            import zipfile
            with zipfile.ZipFile("model.zip", 'r') as zip_ref:
                zip_ref.extractall(".")
            os.rename("vosk-model-small-cn-0.22", "model")
            os.remove("model.zip")
            print("\n✅ 模型下载完成！")
        except Exception as e:
            print(f"\n❌ 模型下载失败: {str(e)}")
            print("请手动下载模型并解压到 'model' 文件夹中")
            return
    
    p = pyaudio.PyAudio()
    
    try:
        stream = p.open(format=FORMAT,
                       channels=CHANNELS,
                       rate=RATE,
                       input=True,
                       frames_per_buffer=CHUNK)
        
        print("\n正在监听...")
        if DISPLAY_VOLUME:
            print("当前音量: ", end='', flush=True)
        
        silent_chunks = 0
        audio_started = False
        frames = []
        active_frames = 0
        volume_display_counter = 0
        
        while True:
            try:
                data = stream.read(CHUNK, exception_on_overflow=False)
                rms = audioop.rms(data, 2)  # 获取音量大小
                
                # 显示音量级别
                if DISPLAY_VOLUME:
                    volume_display_counter += 1
                    if volume_display_counter >= 5:  # 每5个chunk更新一次显示
                        volume_level = min(rms // 100, 10)  # 将音量映射到0-10的范围
                        print(f"\r当前音量: {'█' * volume_level}{' ' * (10-volume_level)} [{rms:4d}]", end='', flush=True)
                        volume_display_counter = 0
                
                if not audio_started and rms > SILENCE_THRESHOLD:
                    if DISPLAY_VOLUME:
                        print()  # 换行，避免与音量显示冲突
                    print("\n检测到声音，开始录制...")
                    audio_started = True
                    frames = [data]
                    silent_chunks = 0
                    active_frames = 1
                    current_time = datetime.now().strftime("%H:%M:%S")
                    print(f"[{current_time}] 正在录制...")
                
                elif audio_started:
                    frames.append(data)
                    if rms > SILENCE_THRESHOLD:
                        active_frames += 1
                        silent_chunks = 0
                    else:
                        silent_chunks += 1
                        if silent_chunks > SILENCE_CHUNKS and active_frames > MIN_AUDIO_LENGTH:
                            if DISPLAY_VOLUME:
                                print()  # 换行，避免与音量显示冲突
                            current_time = datetime.now().strftime("%H:%M:%S")
                            print(f"[{current_time}] 检测到静音，录制结束")
                            
                            # 保存音频文件
                            audio_filename = f"recording_{int(time.time())}.wav"
                            wf = wave.open(audio_filename, 'wb')
                            wf.setnchannels(CHANNELS)
                            wf.setsampwidth(p.get_sample_size(FORMAT))
                            wf.setframerate(RATE)
                            wf.writeframes(b''.join(frames))
                            wf.close()
                            
                            print(f"已保存录音文件: {audio_filename}")
                            
                            # 将录音转换为文字
                            print("\n正在转换语音为文字...")
                            text = convert_to_text(audio_filename)
                            if text.startswith(("错误：", "警告：")):
                                print(f"识别失败: {text}")
                            else:
                                print(f"\n📝 识别结果: {text}")
                                
                                # 提取关键词
                                print("\n正在分析关键内容...")
                                keywords = extract_keywords(text)
                                if keywords:
                                    print("\n🔑 提取的关键词:")
                                    for i, keyword in enumerate(keywords, 1):
                                        print(f"  {i}. {keyword}")
                                print("\n" + "="*50)
                            
                            # 删除临时录音文件
                            try:
                                os.remove(audio_filename)
                            except:
                                pass
                            
                            # 重置状态
                            audio_started = False
                            frames = []
                            active_frames = 0
                            print("\n正在监听新的声音...")
                    
            except Exception as e:
                print(f"\n❌ 错误: {str(e)}")
                break
                
    except KeyboardInterrupt:
        print("\n程序已退出")
    except Exception as e:
        print(f"发生错误: {str(e)}")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

if __name__ == "__main__":
    main()
