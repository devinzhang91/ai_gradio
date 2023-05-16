import requests
from loguru import logger
import yaml

with open('../config.yaml',mode='r') as f:
    result = yaml.load(f, Loader=yaml.FullLoader)
    gradio_config = result['gradio']
    server_name = gradio_config['server_name']
    server_port = gradio_config['server_port']
    openai_config = result['openai']
    chatbot_engine_list = openai_config['chatbot_models']

# 需要请求的目标URL
openai_chat_url = "http://" + server_name + ":" + str(server_port) + "/call_openai_chat/"
clear_url = "http://" + server_name + ":" + str(server_port) + "/clear_chat_history/"
asr_stream_url = "http://" + server_name + ":" + str(server_port) + "/call_asr_stream/"
tts_stream_url = "http://" + server_name + ":" + str(server_port) + "/call_tts/"

# 替换为您要发送的wav文件的路径
asr_file_path = './file/bulecat.wav'
tts_file_path1 = './file/answer1.wav'
tts_file_path2 = './file/answer2.wav'


data = {
    "prompt": "你好",
    "engine": chatbot_engine_list[0],
    "temperature": 0.1,
    "top_p": 0.5,
    "max_tokens": 256,
    "is_correlation": True,
    "is_search": False,
    "is_clear_history": False,
    "device_id": 0
}

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
response = requests.post(asr_stream_url, data=stream)
response_text : str = check_response(response)
logger.info(response_text)

#将asr的结果发送给openai_chat
data["prompt"] = response_text

# 第一次对话
response = requests.post(openai_chat_url, json=data)
response_text : str = check_response(response)
logger.info(response_text)

#将openai_chat的结果发送给tts
json = {"text": response_text, "voice_name": "zh-CN-XiaoxiaoNeural"}
response = requests.post(tts_stream_url, json=json)
# 检查响应是否有效
if response.status_code == 200:
    # 创建一个文件来保存音频数据
    with open(tts_file_path1, 'wb') as f:
        f.write(response.content)

# 第二次对话
data['prompt'] = "请帮它起一个名字"
response = requests.post(openai_chat_url, json=data)
response_text : str = check_response(response)
logger.info(response_text)

#将openai_chat的结果发送给tts
json = {"text": response_text, "voice_name": "zh-CN-XiaoxiaoNeural"}
response = requests.post(tts_stream_url, json=json)
# 检查响应是否有效
if response.status_code == 200:
    # 创建一个文件来保存音频数据
    with open(tts_file_path2, 'wb') as f:
        f.write(response.content)

# 清除对话历史
response = requests.post(clear_url, json=data)