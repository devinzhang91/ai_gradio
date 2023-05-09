import requests
import io
from loguru import logger
import yaml
import soundfile as sf
import numpy as np


with open('../config.yaml',mode='r') as f:
    result = yaml.load(f, Loader=yaml.FullLoader)
    gradio_config = result['gradio']
    server_name = gradio_config['server_name']
    server_port = gradio_config['server_port']

# 替换为您要发送文件的目标URL
url = "http://" + server_name + ":" + str(server_port) + "/call_tts/"
# 替换为您要保存的wav文件的路径
file_path = './file/test_call_tts.wav'
# 替换为您要合成的文本
json = {"text": "今天天气不错，又是摸鱼的一天。", "voice_name": "zh-CN-XiaoxiaoNeural"}

response = requests.post(url, json=json)

# 检查响应是否有效
if response.status_code == 200:
    # 创建一个文件来保存音频数据
    with open(file_path, 'wb') as f:
        f.write(response.content)

else:
    print("Error: Unable to fetch audio stream, error code :" + str(response.status_code))