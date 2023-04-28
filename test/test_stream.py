import requests
from loguru import logger
import yaml


with open('../config.yaml',mode='r') as f:
    result = yaml.load(f, Loader=yaml.FullLoader)
    gradio_config = result['gradio']
    server_name = gradio_config['server_name']
    server_port = gradio_config['server_port']

url = "http://" + server_name + ":" + str(server_port) + "/call_asr_stream/"   # 替换为您要发送文件的目标URL
file_path = '/home/devin/Downloads/bulecat.wav'  # 替换为您要发送的wav文件的路径

print(url)
print(file_path)

# 定义一个生成器函数，用于以4096字节的块读取文件
def file_stream(file_path, chunk_size=4096):
    with open(file_path, 'rb') as file:
        while True:
            data = file.read(chunk_size)
            if not data:
                break
            yield data

# 使用生成器函数创建一个文件流
stream = file_stream(file_path)

# 使用requests发送文件流
response = requests.post(url, data=stream)

# 检查响应
if response.status_code == 200:
    print(f'文件上传成功, json: {response.text}')
else:
    print(f'文件上传失败，状态码：{response.status_code}, json: {response.text}')