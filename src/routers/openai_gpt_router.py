from src.tools.openai_gpt import OpenAiEngine
from src.tools.bing_search import BingSearchEngine
from loguru import logger
import tempfile
import os
# fastapi router
from fastapi import APIRouter
from pydantic import BaseModel

class OpenAiGPTRouter():
    router = APIRouter()

    def __init__(self) -> None:
        pass


    class OpenAICallItem(BaseModel):
        prompt:str
        engine: str = OpenAiEngine.PLAYGROUND_MODELS_LIST[0]
        temperature: float = 0.15
        top_p: float = 0.5
        max_tokens: int = 2000
        is_correlation: bool = False
        is_search: bool = False

    @router.post("/call_openai/")
    async def fastapi_bing_search(item: OpenAICallItem):
        tmp_history = history
        if(item.is_correlation == False):
            tmp_history = [history[-1]]
        if(item.is_search == False):
                return OpenAiEngine.call_openai_chat(tmp_history, item.engine, item.temperature, item.top_p, item.max_tokens)
        else:
            # step1:call_openai_chat_token
            # step2:call_bing_search + parse_bing_search_result
            # step3:call_openai_chat_with_search
            new_token = OpenAiEngine.call_openai_chat_token(tmp_history, item.engine, item.max_tokens)
            json = BingSearchEngine.call_bing_search(new_token)
            bing_search_result = BingSearchEngine.parse_bing_search_result(json)
            return OpenAiEngine.call_openai_chat_with_search2(tmp_history, bing_search_result, item.engine, item.temperature, item.top_p, item.max_tokens, item.max_search_results )

        

    @router.post("/call_openai_chat/")
    async def fastapi_bing_search(keyword: str):
        json = BingSearchEngine.call_bing_search(keyword)
        return BingSearchEngine.parse_bing_search_result(json)
        