from src.webui.webui_surface import WebUISurface
from loguru import logger
import gradio as gr
from src.tools.google_search import GoogleSearchEngine
from src.tools.bing_search import BingSearchEngine

class SearchWebUI(WebUISurface):
    def __init__(self):
        pass

    def search_google(keyword):
        try:
            json = GoogleSearchEngine.call_google_search(keyword)
            return GoogleSearchEngine.parse_google_search_info(json)
        except Exception as e:
            raise gr.Error("Exception: " + str(e))
        
    def search_bing(keyword):
        try:
            json = BingSearchEngine.call_bing_search(keyword)
            return BingSearchEngine.parse_bing_search_result(json)
        except Exception as e:
            raise gr.Error("Exception: " + str(e))

    def get_gradio_block():
        with gr.Blocks() as google_block:
            with gr.Column():
                with gr.Row():
                    with gr.Column(scale=4):
                        in_keyword = gr.Textbox(
                            label="Keyword",
                            )
                    with gr.Column(scale=1):
                        clear_button = gr.Button( value="Clear")
                        search_button = gr.Button(value="Search")
        

                search_result = gr.Dataframe(
                                headers=["title", "snippet", "link"],
                                datatype=["str", "str", "str"],
                                col_count=(3, "fixed"),
                                wrap=True,
                                )
        
        clear_button.click(lambda: None, None, in_keyword, queue=False)
        search_button.click(fn=SearchWebUI.search_bing, 
                            inputs=[in_keyword], 
                            outputs=[search_result],
                            queue=True,
                            show_progress=True,
                            scroll_to_output=True,)
        return google_block
