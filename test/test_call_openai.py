import requests
from loguru import logger
import yaml


with open('../config.yaml',mode='r') as f:
    result = yaml.load(f, Loader=yaml.FullLoader)
    gradio_config = result['gradio']
    server_name = gradio_config['server_name']
    server_port = gradio_config['server_port']
    openai_config = result['openai']
    playground_engine_list = openai_config['playground_models']

# 替换为您要发送文件的目标URL
url = "http://" + server_name + ":" + str(server_port) + "/call_openai/"

data = {
    "prompt": "你好！",
    "engine": playground_engine_list[0],
    "temperature": 0.1,
    "top_p": 0.5,
    "max_tokens": 100,
    "is_correlation": True,
    "is_search": False,
    "device_id": 0
}

response = requests.post(url, json=data)


# 检查响应
if response.status_code == 200:
    print(f'请求成功, json: {response.text}')
else:
    print(f'请求失败，状态码：{response.status_code}, json: {response.text}')