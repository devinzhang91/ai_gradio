import requests
from loguru import logger
import yaml

class GoogleSearchEngine:
    with open('config.yaml',mode='r') as f:
        result = yaml.load(f, Loader=yaml.FullLoader)
        google_config = result['google']
        API_KEY = google_config['key']
        API_CX = google_config['cx']
        API_URL = google_config['url']

    def call_google_search(keyword, start=1, num=10):
        # Google自定义搜索API
        # https://www.googleapis.com/customsearch/v1?key={YOUR_KEY}&q={SEARCH_WORDS}&cx={YOUR_CX}&start={10}&num={10}
        payload = {'cx': GoogleSearchEngine.API_CX, 
                'key': GoogleSearchEngine.API_KEY,
                'start': str(start),
                'num': str(num),
                'q': keyword}
        logger.debug(f"payload={payload}")
        response = requests.get(GoogleSearchEngine.API_URL, params=payload)
        # print(response.json())
        return response.json()

    def parse_google_search_result(json):
        # 解析Google自定义搜索API返回的json数据
        result = []
        try:
            items = json['items']
            for item in items:
                result.append([item['title'], item['snippet'], item['link']])

        except Exception as e:
            logger.error(f"parse_google_search_result error: {e}")
            raise
        print(result)
        return result
            
    def parse_google_search_info(json):
        # 解析Google自定义搜索API返回的json数据
        result = []
        try:
            items = json['items']
            for item in items:
                description = ''
                try:
                    # print("metatags:", item['pagemap']['metatags'])
                    for metatag in item['pagemap']['metatags']:
                        try:
                            description += metatag['og:description']
                        except:
                            pass
                        try:
                            description += metatag['dc:description']
                        except:
                            pass
                        try:
                            description += metatag['citation_abstract']
                        except:
                            pass
                except Exception as e:
                    logger.error(f"json parse error: {e}")
                    pass
                try:
                    result.append([item['title'], item['snippet'], description])
                except:
                    result.append([item['title'], item['snippet'], ''])

        except Exception as e:
            logger.error(f"parse_google_search_result error: {e}")
            raise
        # print(result)
        return result
