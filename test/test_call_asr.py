import requests
from loguru import logger
import yaml


with open('../config.yaml',mode='r') as f:
    result = yaml.load(f, Loader=yaml.FullLoader)
    gradio_config = result['gradio']
    server_name = gradio_config['server_name']
    server_port = gradio_config['server_port']

# 替换为您要发送文件的目标URL
url = "http://" + server_name + ":" + str(server_port) + "/call_asr/"
# 替换为您要发送的wav文件的路径
file_path = './file/bulecat.wav'

with open(file_path, "rb") as file:
    files = {"input_audio_file": file}
    response = requests.post(url, files=files)

# 检查响应
if response.status_code == 200:
    print(f'文件上传成功, asr: {response.text}')
else:
    print(f'文件上传失败，状态码：{response.status_code}, asr: {response.text}')