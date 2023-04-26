from src.tools.bing_search import BingSearchEngine
from src.tools.google_search import GoogleSearchEngine
from loguru import logger
import tempfile
import os
# fastapi router
from fastapi import APIRouter
from pydantic import BaseModel

class SearchRouter():
    router = APIRouter()

    def __init__(self) -> None:
        pass


    @router.post("/bing_search/")
    async def fastapi_bing_search(keyword: str):
        json = BingSearchEngine.call_bing_search(keyword)
        return BingSearchEngine.parse_bing_search_result(json)
        

    @router.post("/google_search/")
    async def fastapi_bing_search(keyword: str):
        json = GoogleSearchEngine.call_google_search(keyword)
        return GoogleSearchEngine.parse_google_search_info(json)
        