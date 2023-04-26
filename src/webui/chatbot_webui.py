from src.webui.webui_surface import WebUISurface
from loguru import logger
import gradio as gr
from src.tools.openai_gpt import OpenAiEngine
from src.tools.bing_search import BingSearchEngine

class ChatBotWebUI(WebUISurface):

    def __init__(self):
        pass

    def chatbot_openai(history,
                    engine: str = OpenAiEngine.CHATBOT_MODELS_LIST[0],
                    temperature: float = 0.2,
                    top_p: float = 0.8,
                    max_tokens: int = 4000,
                    is_search = True, 
                    is_correlation = True,
                    max_search_results: int = 5):
        try:
            tmp_history = history
            if(is_correlation == False):
                tmp_history = [history[-1]]
            if(is_search == False):
                    return OpenAiEngine.call_openai_chat(tmp_history, engine, temperature, top_p, max_tokens)
            else:
                # step1:call_openai_chat_token
                # step2:call_bing_search + parse_bing_search_result
                # step3:call_openai_chat_with_search
                new_token = OpenAiEngine.call_openai_chat_token(tmp_history, engine, max_tokens)
                json = BingSearchEngine.call_bing_search(new_token)
                bing_search_result = BingSearchEngine.parse_bing_search_result(json)
                return OpenAiEngine.call_openai_chat_with_search(tmp_history, bing_search_result, engine, temperature, top_p, max_tokens, max_search_results )
        except Exception as e:
            # raise gr.Error("Exception: " + str(e))
            return "[ERROR]::Exception: " + str(e)
            

    def get_gradio_block():
        with gr.Blocks() as openai_chatbot_block:
            with gr.Column():
                chatbot = gr.Chatbot().style(height="100%")
                with gr.Row():
                    with gr.Column(scale=5):
                        message = gr.Textbox()
                    with gr.Column(scale=1):
                        chatbot_submit_button = gr.Button(value="Submit")
                        chatbot_clear_button = gr.Button( value="Clear")
                    with gr.Column(scale=2):
                        with gr.Accordion("Prmameters", 
                                        open=False):
                            with gr.Column():
                                engine = gr.Dropdown(
                                    OpenAiEngine.CHATBOT_MODELS_LIST, 
                                    label="models", 
                                    value = OpenAiEngine.CHATBOT_MODELS_LIST[1],
                                )
                                temperature = gr.Slider(
                                    minimum=0,
                                    maximum=1.0,
                                    value=0.05,
                                    step=0.01,
                                    interactive=True,
                                    label="Temperature",
                                )
                                top_p = gr.Slider(
                                    minimum=0,
                                    maximum=1.0,
                                    value=0.2,
                                    step=0.05,
                                    interactive=True,
                                    label="Top p",
                                )
                                max_tokens = gr.Slider(
                                    minimum=1,
                                    maximum=4000,
                                    value=800,
                                    step=1,
                                    interactive=True,
                                    label="Maximum Tokens",
                                )

                                with gr.Row():
                                    is_search = gr.Checkbox(label="search", 
                                                            info="Search in network?",
                                                            value=True)
                                    max_search_results = gr.Slider(
                                        minimum=1,
                                        maximum=10,
                                        value=5,
                                        step=1,
                                        interactive=True,
                                        label="Maximum search results",
                                    )
                                    is_correlation = gr.Checkbox(label="correlation",  
                                                                info="Correlate the dialogue?", 
                                                                value=True)

                            

        def user(user_message, 
                 history, 
                 message_to_submit):
            message_to_submit.append({"role": "user", "content": f"{user_message}"})
            return "", history + [[user_message, None]]


        def bot(history, 
                message_to_submit,
                engine, 
                temperature, 
                top_p, 
                max_tokens,
                is_search, 
                is_correlation,
                max_search_results):
            print("message_to_submit: ", message_to_submit)
            bot_message = ChatBotWebUI.chatbot_openai(message_to_submit, engine, temperature, top_p, max_tokens, is_search, is_correlation, max_search_results)
            message_to_submit.append({"role": "assistant", "content": f"{bot_message}"})
            history[-1][1] = bot_message
            return history
        
        def clear(chatbot, message_to_submit):
            chatbot = []
            message_to_submit = []
            return chatbot, message_to_submit
        
        # message_to_submit = gr.State([{"role": "system", "content": f"{systemPromptTxt}"}])
        message_to_submit = gr.State([])
        message.submit(fn=user, 
                       inputs=[message, chatbot, message_to_submit], 
                       outputs=[message, chatbot], 
                       queue=False).then(fn=bot, 
                                         inputs=[chatbot, message_to_submit,engine, temperature, top_p, max_tokens, is_search, is_correlation, max_search_results], 
                                         outputs=chatbot )

        chatbot_clear_button.click(fn=clear, inputs=[chatbot, message_to_submit], outputs=[chatbot, message_to_submit], queue=False)
        chatbot_submit_button.click(fn=user, 
                                    inputs=[message, chatbot, message_to_submit], 
                                    outputs=[message, chatbot], 
                                    queue=False).then(fn=bot, 
                                                        inputs=[chatbot, message_to_submit, engine, temperature, top_p, max_tokens, is_search, is_correlation, max_search_results], 
                                                        outputs=chatbot )


        return openai_chatbot_block