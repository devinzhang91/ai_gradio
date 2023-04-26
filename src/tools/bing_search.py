import requests
from loguru import logger
import yaml

class BingSearchEngine():

    with open('config.yaml',mode='r') as f:
        result = yaml.load(f, Loader=yaml.FullLoader)
        bing_config = result['bing']
        API_KEY = bing_config['key']
        API_URL = bing_config['endpoint']


    def __init__(self) -> None:
        pass


    def call_bing_search(keyword, start=1, num=10):
        # Construct a request
        mkt = 'zh-CN'
        params = { 'q': keyword, 'mkt': mkt }
        headers = { 'Ocp-Apim-Subscription-Key':  BingSearchEngine.API_KEY }

        # logger.debug(f"headers={headers}, params={params}")
        
        # Call the API
        try:
            response = requests.get(BingSearchEngine.API_URL, headers=headers, params=params)
            response.raise_for_status()
            # logger.debug(response.json())
        except Exception as e:
            logger.error(f"call_bing_search error: {e}")
            raise e
        return response.json()

    def parse_bing_search_result(json):
        # 解析Bing自定义搜索API返回的json数据
        result = []
        try:
            pages = json['webPages']
            items = pages['value']
            for item in items:
                result.append([item['name'], item['snippet'], item['url']])
            logger.info(result)
        except Exception as e:
            logger.error(f"parse_bing_search_result error: {e}")
            raise e
        return result
    