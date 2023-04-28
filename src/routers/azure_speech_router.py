from src.tools.azure_speech import AuzerSpeechEngine
from loguru import logger
import tempfile
import os
# fastapi router
from fastapi import APIRouter, UploadFile, Request
from fastapi.responses import StreamingResponse
from starlette.responses import FileResponse
from starlette.background import BackgroundTask
from pydantic import BaseModel
import soundfile as sf

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
            except Exception as e:
                return {"asr": "error: " + str(e)}
            finally:
                tmpfile.close()  # 文件关闭即删除
        return {"asr": result}
        
    @router.post("/call_tts/")
    async def fastapi_call_tts(text: str):
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmpfile :
            try:
                tmpfile.close()  # 文件关闭，但保留文件，这里只获取了tmpfile的文件名作为参数
                AuzerSpeechEngine.synthesize_to_output(text, tmpfile.name)
                return FileResponse(
                    tmpfile.name,
                    filename="tts_output.wav",
                    background=BackgroundTask(lambda: os.remove(tmpfile.name)),
                )
            except Exception as e:
                return {"tts": "error: "+ str(e)}
            
    #asr stream upload
    @router.post("/call_asr_stream/")
    async def fastapi_call_asr_stream(request: Request):
        audio_size = 0
        # audio_bytes = b""
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=True) as tmpfile :
            try :
                async for chunk in request.stream():
                    # audio_bytes += chunk
                    audio_size += len(chunk)
                    tmpfile.write(chunk)
                    if len(chunk) <= 0:
                        logger.info("stream read finished audio_size: {}", audio_size)
                        break
                result = AuzerSpeechEngine.recognize_from_audio(tmpfile.name)
            except Exception as e:
                return {"asr stream": "error: " + str(e)}
            finally:
                tmpfile.close()  # 文件关闭即删除
        return {"asr stream": result}

    #tts stream download
    @router.post("/call_tts_stream/")
    async def fastapi_call_tts_stream(text: str):
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmpfile :
            try:
                tmpfile.close()  # 文件关闭，但保留文件，这里只获取了tmpfile的文件名作为参数
                AuzerSpeechEngine.synthesize_to_output(text, tmpfile.name)
                data, sr = sf.read(tmpfile.name, dtype='int16')
                return StreamingResponse(data, media_type="audio/wav", background=BackgroundTask(lambda: os.remove(tmpfile.name)))
            except Exception as e:
                return {"tts stream": "error: "+ str(e)}