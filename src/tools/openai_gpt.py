import openai
from loguru import logger
import yaml

class OpenAiEngine:
    with open('config.yaml',mode='r') as f:
        try:
            result = yaml.load(f, Loader=yaml.FullLoader)
            openai_api_config = result['openai']
            API_TYPE = openai_api_config['type']
            API_BASE = openai_api_config['base']
            API_VERSION = openai_api_config['version']
            API_KEY = openai_api_config['key']
            CONCURRENCY_MAX = 30
        except Exception as e:
            logger.error(f"openai api config error: {e}")
            raise

        try:
            openai_models_config = result['openai']['playground_models']
            PLAYGROUND_MODELS_LIST = openai_models_config
        except Exception as e:
            logger.error(f"openai models config error: {e}")
            raise

        try:
            openai_models_config = result['openai']['chatbot_models']
            CHATBOT_MODELS_LIST = openai_models_config
        except Exception as e:
            logger.error(f"openai models config error: {e}")
            raise
    
        openai.api_type = API_TYPE
        openai.api_base = API_BASE
        openai.api_version = API_VERSION
        openai.api_key = API_KEY

    def get_chat_history_as_text(messages, include_last_turn=True, approx_max_tokens=2000) -> str:
            history_text = ""
            for h in reversed(messages if include_last_turn else messages[:-1]):
                # history_text = """<|im_start|>user""" +"\n" + h["user"] + "\n" + """<|im_end|>""" + "\n" + """<|im_start|>assistant""" + "\n" + (h.get("bot") + """<|im_end|>""" if h.get("bot") else "") + "\n" + history_text
                # history_text = """<|im_start|>"""+h['role'] + h['content'] + """<|im_end|>""" +"\n" + history_text
                history_text = h['content'] +"\n" + history_text
                if len(history_text) > approx_max_tokens*4:
                    break
            logger.info(f"history_text={history_text}")
            return history_text

    def call_openai(prompt:str,
                    engine: str = PLAYGROUND_MODELS_LIST[0],
                    temperature: float = 0.15,
                    top_p: float = 0.5,
                    max_tokens: int = 2000):
        try:
            kwargs = dict(
                prompt=prompt,
                engine=engine,
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens,
                frequency_penalty=0,
                presence_penalty=0,  # 惩罚机制，-2.0 到 2.0之间，默认0，数值越小提交的重复令牌数越多，从而能更清楚文本意思
                stop=None)

            prompt = prompt.strip()
            logger.info(f"kwargs={kwargs}")
            if prompt.isspace() or len(prompt) == 0:
                raise Exception("请输入一些有意义的内容")

            response = openai.Completion.create(**kwargs)
            resp = response["choices"][0]["text"]
            logger.info(f"{response}")
            if response["choices"][0]["finish_reason"] == "content_filter":
                resp += ("\nThe generated content is filtered.")
                logger.warning("chatgpt response filtered")
        except Exception as e:
            logger.error(f"send_msg 错误:{repr(e)}")
            raise
        return resp


    def call_openai_chat(messages,
                        engine: str = CHATBOT_MODELS_LIST[0],
                        temperature: float = 0.4,
                        top_p: float = 0.80,
                        max_tokens: int = 400):
        try:
            kwargs = dict(
                engine=engine,
                messages = messages,
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens,
                frequency_penalty=0,
                presence_penalty=0, 
                stop=None)

            logger.info(f"kwargs={kwargs}")
            # if messages.length == 0:
            #     raise Exception("请输入内容!")

            response = openai.ChatCompletion.create(**kwargs)
            logger.info(f"{response}")
            resp = response['choices'][0]['message']['content']
            if response["choices"][0]["finish_reason"] == "content_filter":
                resp += ("\nThe generated content is filtered.")
                logger.warning("chatgpt response filtered")
        except Exception as e:
            logger.error(f"send_msg 错误:{repr(e)}")
            raise
        return resp


    query_prompt_template = """
        以下是到目前为止的对话历史，以及用户提出的一个新问题，需要通过在知识库中搜索来回答。
        根据对话和新问题生成查询条件。
        请勿在搜索查询词中包含引用的源文件名和文档名称，例如信息.txt或文档.pdf。
        不要在搜索查询词的 [] 或<<>>中包含任何文本。
        历史对话:
        {chat_history}
        问题:
        {question}
        查询条件:
        """

    def call_openai_token(prompt:str,
                        engine: str = PLAYGROUND_MODELS_LIST[0],
                        max_tokens: int = 500):
        prompt = OpenAiEngine.query_prompt_template.format(chat_history="", question=prompt)
        try:
            kwargs = dict(
                prompt=prompt,
                engine=OpenAiEngine.PLAYGROUND_MODELS_LIST[0],
                temperature=0.0, 
                max_tokens=max_tokens, 
                n=1, )

            prompt = prompt.strip()
            logger.info(f"kwargs={kwargs}")
            if prompt.isspace() or len(prompt) == 0:
                raise Exception("请输入一些有意义的内容")

            response = openai.Completion.create(**kwargs)
            resp = response["choices"][0]["text"]
            logger.info(f"{response}")
            if response["choices"][0]["finish_reason"] == "content_filter":
                resp += ("\nThe generated content is filtered.")
                logger.warning("chatgpt response filtered")
            logger.info(f"key words={resp}")
        except Exception as e:
            logger.error(f"send_msg 错误:{repr(e)}")
            raise
        return resp

    def call_openai_chat_token(messages,
                            engine: str = PLAYGROUND_MODELS_LIST[0],
                            max_tokens: int = 2000):
        
        prompt = OpenAiEngine.query_prompt_template.format(chat_history=OpenAiEngine.get_chat_history_as_text(messages, False), question=messages[-1]["content"])

        try:
            kwargs = dict(
                prompt=prompt,
                engine=OpenAiEngine.PLAYGROUND_MODELS_LIST[0],
                temperature=0.0, 
                max_tokens=max_tokens, 
                n=1, )

            prompt = prompt.strip()
            logger.info(f"kwargs={kwargs}")
            if prompt.isspace() or len(prompt) == 0:
                raise Exception("请输入一些有意义的内容")

            response = openai.Completion.create(**kwargs)
            resp = response["choices"][0]["text"]
            logger.info(f"{response}")
            if response["choices"][0]["finish_reason"] == "content_filter":
                resp += ("\nThe generated content is filtered.")
                logger.warning("chatgpt response filtered")
            logger.info(f"key words={resp}")
        except Exception as e:
            logger.error(f"send_msg 错误:{repr(e)}")
            raise
        return resp


    prompt_prefix = """
        <|im_start|>系统助理帮助解决他们的问题，回答要简短。
        仅回答以下来源列表中列出的事实。如果下面没有足够的信息，请说您不知道。不要生成不使用以下来源的答案。不要使用年代久远的来源信息。如果向用户提出澄清问题会有所帮助，请提出问题。
        每个来源都有一个名称，后跟冒号和实际信息，始终包括您在响应中使用的每个事实的源名称。使用方形制动器来引用源。
        例如:
        来源：
        info1.txt: 内容 <http://www.example.com/info1.txt>
        输出: 根据[info1.txt](http://www.example.com/info1.txt)，内容
        使用换行分割单独列出每个输出.
        不要合并来源，而是单独列出每个来源，例如 [info1.txt][info2.pdf].
        不要使用引用，而是始终将来源路径放在()中，例如(http://www.example.com/info1.txt)(http://www.example.com/info2.pdf)
        {follow_up_questions_prompt}
        {injected_prompt}
        来源:
        {sources}
        <|im_end|>
        {chat_history}
        """



    def call_openai_chat_with_search(messages: list,
                                    search_results,
                                    engine: str = CHATBOT_MODELS_LIST[0],
                                    temperature: float = 0.2,
                                    top_p: float = 0.80,
                                    max_tokens: int = 4000,
                                    max_search_results: int = 5):
        result_text = ""
        for result in search_results:
            result_text += result[0] + ": " + result[1] + " <" + result[2] + "> \n" 
            if result == search_results[max_search_results-1]:
                break
        prompt = OpenAiEngine.prompt_prefix.format(injected_prompt="", sources=result_text, chat_history=OpenAiEngine.get_chat_history_as_text(messages), follow_up_questions_prompt="")
        try:
            messages.append({'role': 'system', 'content': prompt})
            kwargs = dict(
                engine=engine,
                messages = messages,
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens,
                frequency_penalty=0,
                presence_penalty=0, 
                # stop=["<|im_end|>", "<|im_start|>"]
                stop=None)

            logger.info(f"kwargs={kwargs}")

            response = openai.ChatCompletion.create(**kwargs)
            logger.info(f"{response}")
            resp = response['choices'][0]['message']['content']
            if response["choices"][0]["finish_reason"] == "content_filter":
                resp += ("\nThe generated content is filtered.")
                logger.warning("chatgpt response filtered")
            resp = resp.strip('\n')
            messages.pop()
        except Exception as e:
            logger.error(f"Error:{repr(e)}")
            messages.pop()
            raise
        return resp
