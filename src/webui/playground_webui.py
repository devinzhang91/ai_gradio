from src.webui.webui_surface import WebUISurface
from loguru import logger
import gradio as gr
from src.tools.bing_search import BingSearchEngine
from src.tools.openai_gpt import OpenAiEngine

class PlaygroundWebUI(WebUISurface):

    def __init__(self):
        pass

    def playground_openai(prompt,
                    engine: str = OpenAiEngine.PLAYGROUND_MODELS_LIST[0],
                    temperature: float = 0.15,
                    top_p: float = 0.5,
                    max_tokens: int = 2000):
                    try:
                        return OpenAiEngine.call_openai(prompt, engine, temperature, top_p, max_tokens)
                        # return openai_gpt.call_openai_token(prompt, engine, max_tokens)
                    except Exception as e:
                        raise gr.Error("Exception: " + str(e))
            
    def get_gradio_block():
        with gr.Blocks() as openai_block:
            with gr.Row():
                with gr.Column():
                    prompt = gr.Textbox(
                        label="prompts",
                        lines=10,
                        )
                    with gr.Column():
                        with gr.Accordion("Prmameters", 
                                        open=False):
                            with gr.Row():
                                with gr.Column():
                                    engine = gr.Dropdown(
                                        OpenAiEngine.PLAYGROUND_MODELS_LIST, 
                                        label="models", 
                                        value = OpenAiEngine.PLAYGROUND_MODELS_LIST[0],
                                    )
                                    temperature = gr.Slider(
                                        minimum=0,
                                        maximum=1.0,
                                        value=0.1,
                                        step=0.01,
                                        interactive=True,
                                        label="Temperature",
                                    )
                                    top_p = gr.Slider(
                                        minimum=0,
                                        maximum=1.0,
                                        value=0.5,
                                        step=0.05,
                                        interactive=True,
                                        label="Top p",
                                    )
                                    max_tokens = gr.Slider(
                                        minimum=1,
                                        maximum=4000,
                                        value=1000,
                                        step=1,
                                        interactive=True,
                                        label="Maximum Tokens",
                                    )
                        prompt_clear_button = gr.Button( value="Clear")
                        prompt_submit_button = gr.Button(value="Submit")
        

                openai_result = gr.Textbox(
                                label="result",
                                lines=18,
                                )
        
        prompt_clear_button.click(lambda: None, None, prompt, queue=False)
        prompt_submit_button.click(fn=PlaygroundWebUI.playground_openai, 
                            inputs=[prompt, engine, temperature, top_p, max_tokens], 
                            outputs=[openai_result],
                            queue=True,
                            show_progress=True,
                            scroll_to_output=True,)
        return openai_block
    