from src.webui.webui_surface import WebUISurface
from loguru import logger
import gradio as gr
from scholarly import scholarly
from scholarly import ProxyGenerator

class ScholarlyWebUI(WebUISurface):

    search_dropdown_list = ["pubs", "author"]

    def __init__(self, proxy = False):
        # Set up a ProxyGenerator object to use free proxies
        # This needs to be done only once per session
        if proxy:
            pg = ProxyGenerator()
            pg.FreeProxies()
            logger.info("Get free proxies")
            scholarly.use_proxy(pg)
            logger.info("Use proxy")
        scholarly.set_timeout(60*2)

    def search_scholarly(in_tpye, in_keyword, year_low, year_high, sort_by):

        logger.info("in_tpye: {}, in_keyword: {}, year_low: {}, year_high: {}, sort_by: {}".format(in_tpye, in_keyword, year_low, year_high, sort_by))
        if(in_tpye == ScholarlyWebUI.search_dropdown_list[0]):
            pubs_list = list(scholarly.search_pubs(in_keyword, 
                                                year_high = int(year_high), 
                                                year_low = int(year_low), 
                                                sort_by = sort_by))
            pubs_result = []
            for p in pubs_list:
                # logger.debug(p)
                try:
                    try:
                        title = p['bib']['title']
                    except:
                        title = ""
                    try:
                        author = p['bib']['author']
                    except:
                        author = ""
                    try:
                        publisher = p['bib']['publisher']
                    except:
                        publisher = ""
                    try:
                        pub_year = p['bib']['pub_year']
                    except:
                        pub_year = 0
                    try:
                        pub_url = p['pub_url']
                    except:
                        pub_url = ""
                except:
                    logger.warning("No bib")
                    # raise
                pubs_result.append([title, author, publisher, pub_year, pub_url])
            logger.debug(pubs_result)
            return pubs_result

        elif(in_tpye == ScholarlyWebUI.search_dropdown_list[1]):
            authors_list = list(scholarly.search_author(in_keyword))
            author = scholarly.fill(authors_list[0])
            pubs_list = author['publications']
            pubs_result = []
            for p in pubs_list:
                # logger.debug(p)
                try:
                    try:
                        title = p['bib']['title']
                    except:
                        title = ""
                    try:
                        author = in_keyword
                    except:
                        author = ""
                    try:
                        publisher = p['bib']['citation']
                    except:
                        publisher = ""
                    try:
                        pub_year = p['bib']['pub_year']
                    except:
                        pub_year = 0
                    try:
                        pub_url = p['citedby_url']
                    except:
                        pub_url = ""
                except:
                    logger.warning("No bib")
                    # raise
                pubs_result.append([title, author, publisher, pub_year, pub_url])
            logger.debug(pubs_result)
            return pubs_result
        else:
            raise ValueError("in_tpye.value is not correct")
    

    def get_gradio_block():
        with gr.Blocks() as scholarly_block:
            with gr.Column():
                with gr.Column():
                    with gr.Row():
                        # Input
                        with gr.Column(scale=1):
                            in_tpye = gr.Dropdown(
                                    ScholarlyWebUI.search_dropdown_list, 
                                    label="Search Type",
                                    value = ScholarlyWebUI.search_dropdown_list[0],
                                )
                        with gr.Column(scale=4):
                            in_keyword = gr.Textbox(
                                            label="Keyword",
                                            )
                    
                    with gr.Column(scale=4):
                        with gr.Accordion("Filter", 
                                        open=False):
                            with gr.Row():
                                year_low = gr.Textbox(
                                    label="year_low",
                                    lines=1,
                                    value=1990,
                                )
                                year_high = gr.Textbox(
                                    label="year_high",
                                    lines=1,
                                    value=2023,
                                )
                                sort_by = gr.Dropdown(
                                    ["relevance", "date"], 
                                    label="sort_by", 
                                    value = "relevance",
                                )
                    with gr.Column(scale=1):
                        scholarly_clear_button = gr.Button( value="Clear")
                        scholarly_search_button = gr.Button(value="Search")

                # Output
                pubs_result = gr.Dataframe(
                        headers=["title", "author", "publisher", "pub_year", "pub_url"],
                        datatype=["str", "str", "str", "number", "str"],
                        col_count=(5, "fixed"),
                        wrap=True,
                        )
        
        scholarly_clear_button.click(lambda: None, None, in_keyword, queue=False)
        scholarly_search_button.click(fn=ScholarlyWebUI.search_scholarly, 
                            inputs=[in_tpye, in_keyword, year_low, year_high, sort_by], 
                            outputs=[pubs_result],
                            queue=True,
                            show_progress=True,
                            scroll_to_output=True,)
        return scholarly_block

