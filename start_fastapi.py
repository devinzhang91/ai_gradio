# Description: This is a simple example of how to use Gradio with FastAPI.
from loguru import logger
import gradio as gr
import yaml as yaml
from src.webui.scholarly_webui import ScholarlyWebUI
from src.webui.search_webui import SearchWebUI
from src.webui.playground_webui import PlaygroundWebUI
from src.webui.chatbot_webui import ChatBotWebUI
from src.webui.speech_webui import SpeechWebUI

from src.routers.azure_speech_router import AzureSpeechRouter
from src.routers.search_router import SearchRouter
from src.routers.openai_gpt_router import OpenAiGPTRouter

import uvicorn
from fastapi import FastAPI
from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel

WEBUI_PATH = "/"
app = FastAPI()
# include the router
app.include_router(AzureSpeechRouter.router)
app.include_router(SearchRouter.router)
app.include_router(OpenAiGPTRouter.router)

@app.get("/help")
def help():
    return {"message": "This is ai gradio webui."}

class AppConf:
    with open('config.yaml',mode='r') as f:
        result = yaml.load(f, Loader=yaml.FullLoader)
        gradio_config = result['gradio']
        server_name = gradio_config['server_name']
        server_port = gradio_config['server_port']

with gr.Blocks() as gradio_app:
    gradio_app.queue(concurrency_count=30)
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


try:
    # Run the add
    app = gr.mount_gradio_app(app, gradio_app, path=WEBUI_PATH)
    uvicorn.run(app, host=AppConf.server_name, port=AppConf.server_port)

except RuntimeError as e:
    logger.error(e)
    gradio_app.close()
    
# Run this from the terminal as you would normally start a FastAPI app: `uvicorn run:app`
# and navigate to http://localhost:8000/gradio in your browser.