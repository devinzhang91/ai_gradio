from src.tools.azure_speech import AuzerSpeechEngine
from loguru import logger
import tempfile
import os
# fastapi router
from fastapi import APIRouter, UploadFile
from starlette.responses import FileResponse
from starlette.background import BackgroundTask
from pydantic import BaseModel

class AzureSpeechRouter():
    router = APIRouter()

    def __init__(self) -> None:
        pass

    @router.post("/call_asr/")
    async def fastapi_call_asr(input_audio_file: UploadFile):
        audio_bytes = input_audio_file.file.read()
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=True) as tmpfile :
            try:
                tmpfile.write(audio_bytes)
                result = AuzerSpeechEngine.recognize_from_audio(tmpfile.name)
                logger.info("recognize_from_audio result: {}", result)
            finally:
                tmpfile.close()  # 文件关闭即删除
        return {"asr": result}
        
    @router.post("/call_tts/")
    async def fastapi_call_tts(text: str):
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmpfile :
            try:
                tmpfile.close()  # 文件关闭，但保留文件，这里只获取了tmpfile的文件名作为参数
                result = AuzerSpeechEngine.synthesize_to_output(text, tmpfile.name)
                logger.info("recognize_from_audio result: {}", result)
                return FileResponse(
                    tmpfile.name,
                    filename="application.xls",
                    background=BackgroundTask(lambda: os.remove(tmpfile.name)),
                )
            except Exception as e:
                return {"tts": "error"}
            
    
