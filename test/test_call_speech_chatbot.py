import requests
from loguru import logger
import yaml
import io
import soundfile as sf
import numpy as np

with open('../config.yaml',mode='r') as f:
    result = yaml.load(f, Loader=yaml.FullLoader)
    gradio_config = result['gradio']
    server_name = gradio_config['server_name']
    server_port = gradio_config['server_port']
    openai_config = result['openai']
    chatbot_engine_list = openai_config['chatbot_models']

# 需要请求的目标URL
speech_chatbot_url = "http://" + server_name + ":" + str(server_port) + "/call_speech_chatbot/"

# 替换为您要发送的wav文件的路径
asr_file_path = './file/bulecat.wav'
tts_file_path1 = './file/answer1.wav'


# 定义一个生成器函数，用于以4096字节的块读取文件
def file_stream(asr_file_path, chunk_size=4096):
    with open(asr_file_path, 'rb') as file:
        while True:
            data = file.read(chunk_size)
            if not data:
                break
            yield data

def check_response(response):
    # 检查响应
    if response.status_code == 200:
        logger.debug(f'请求成功, json: {response.text}')
        return response.text
    else:
        logger.error(f'请求失败，状态码：{response.status_code}, json: {response.text}')
        return response.status_code
    
# 使用生成器函数创建一个文件流
stream = file_stream(asr_file_path)

# 使用requests发送文件流
response = requests.post(speech_chatbot_url, data=stream)
# 检查响应是否有效
if response.status_code == 200:
    # # 创建一个内存中的临时文件来保存音频数据
    # temp_file = io.BytesIO()

    # # 从响应中获取音频数据
    # for chunk in response.iter_content(chunk_size=8192):
    #     if chunk:
    #         temp_file.write(chunk)
    # temp_file.seek(0)
    # array = np.frombuffer(temp_file.getvalue(), dtype=np.int16)
    # sf.write(tts_file_path1, array, 16000, 'PCM_16')# 检查响应是否有效
    # 创建一个文件来保存音频数据
    with open(tts_file_path1, 'wb') as f:
        f.write(response.content)
        logger.info(f'请求成功, wav path: {tts_file_path1}')
else:
    logger.error(f'请求失败，状态码：{response.status_code}, json: {response.text}')
