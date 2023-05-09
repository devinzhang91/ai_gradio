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

# 替换为您要发送文件的目标URL
url = "http://" + server_name + ":" + str(server_port) + "/call_openai_chat/"
clear_url = "http://" + server_name + ":" + str(server_port) + "/clear_chat_history/"

def check_response(response):
    # 检查响应
    if response.status_code == 200:
        print(f'请求成功, json: {response.text}')
    else:
        print(f'请求失败，状态码：{response.status_code}, json: {response.text}')


data = {
    "prompt": "塞尔达最新作品是什么？",
    "engine": chatbot_engine_list[0],
    "temperature": 0.1,
    "top_p": 0.5,
    "max_tokens": 100,
    "is_correlation": True,
    "is_search": False,
    "device_id": 0
}

# 第一次对话
response = requests.post(url, json=data)
check_response(response)

# 第二次对话
data['prompt'] = "我可以在android上玩吗?"
response = requests.post(url, json=data)
check_response(response)

# 清除对话历史
response = requests.post(url, json=data)

# 新的对话， 第一次对话
data['prompt'] = "什么是增程式混合动力汽车?"
response = requests.post(url, json=data)
check_response(response)

# 第二次对话
data['prompt'] = "它需要加油吗?"
response = requests.post(url, json=data)
check_response(response)