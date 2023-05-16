from src.tools.openai_gpt import OpenAiEngine
from src.tools.bing_search import BingSearchEngine
from loguru import logger
import tempfile
import os
import soundfile as sf
# fastapi router
from fastapi import APIRouter, UploadFile, Request
from fastapi.responses import StreamingResponse
from starlette.responses import FileResponse
from starlette.background import BackgroundTask
from pydantic import BaseModel

from src.routers.azure_speech_router import AzureSpeechRouter
from src.routers.openai_gpt_router import OpenAiGPTRouter

class SpeechChatBotRouter():
    router = APIRouter()

    def __init__(self) -> None:
        pass

    #asr stream upload, openai chatbot,tts file download
    @router.post("/call_speech_chatbot/")
    async def fastapi_call_speech_chatbot(request: Request):
        asr = await AzureSpeechRouter.fastapi_call_asr_stream(request)
        logger.info("user: {}", asr)
        answer = await OpenAiGPTRouter.fastapi_call_openai_chat(OpenAiGPTRouter.OpenAICallItem(prompt=asr))
        logger.info("bot: {}", answer)
        return await AzureSpeechRouter.fastapi_call_tts(AzureSpeechRouter.TTSCallItem(text=answer))
