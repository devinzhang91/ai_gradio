# Import
from loguru import logger
import gradio as gr
import yaml as yaml
from src.webui.scholarly_webui import ScholarlyWebUI
from src.webui.search_webui import SearchWebUI
from src.webui.playground_webui import PlaygroundWebUI
from src.webui.chatbot_webui import ChatBotWebUI
from src.webui.speech_webui import SpeechWebUI

class AppConf:
    with open('config.yaml',mode='r') as f:
        result = yaml.load(f, Loader=yaml.FullLoader)
        gradio_config = result['gradio']
        server_name = gradio_config['server_name']
        server_port = gradio_config['server_port']


with gr.Blocks() as app:
    app.queue(concurrency_count=30)
    with gr.Row():
        with gr.Tab("azure speech"):
            SpeechWebUI.get_gradio_block()
        with gr.Tab("openai chatbot"):
            ChatBotWebUI.get_gradio_block()
        with gr.Tab("openai playground"):
            PlaygroundWebUI.get_gradio_block()
        with gr.Tab("search"):
            SearchWebUI.get_gradio_block()
        with gr.Tab("scholarly search"):
            ScholarlyWebUI.get_gradio_block()


if __name__=="__main__":
    try:
        # Run the add
        app.launch(server_name=AppConf.server_name, server_port=AppConf.server_port)
    except RuntimeError as e:
        logger.error(e)
        app.close()
    