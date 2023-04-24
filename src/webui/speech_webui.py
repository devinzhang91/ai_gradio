
import tempfile
from src.webui.webui_surface import WebUISurface
from loguru import logger
import gradio as gr
import src.tools.azure_speech as azure_speech
import numpy as np
import soundfile as sf

class SpeechWebUI(WebUISurface):
    def __init__(self):
        with tempfile.TemporaryDirectory(prefix= '/tmp/ai_gradio_') as self.tmpdir:
            pass

    def reformat_freq(sr, y):
        if sr not in (
            48000,
            16000,
        ):  # Deepspeech only supports 16k, (we convert 48k -> 16k)
            raise ValueError("Unsupported rate", sr)
        if sr == 48000:
            y = (
                ((y / max(np.max(y), 1)) * 32767)
                .reshape((-1, 3))
                .mean(axis=1)
                .astype("int16")
            )
            sr = 16000
        return sr, y

    def call_asr(self, input_audio):
        sr_16k, data_16k = SpeechWebUI.reformat_freq(*input_audio)
        with tempfile.NamedTemporaryFile(suffix='.wav', dir=self.tmpdir, delete=True) as tmpfile :
            try:
                sf.write(tmpfile.name, data_16k, 16000, 'PCM_16')
                result = azure_speech.recognize_from_audio(tmpfile.name)
                logger.info("recognize_from_audio result: {}", result)
            finally:
                tmpfile.close()  # 文件关闭即删除
        return result

    def call_tts(self, input_text):
        with tempfile.NamedTemporaryFile(suffix='.wav', dir=self.tmpdir, delete=False) as tmpfile :
            try:
                tmpfile.close()  # 文件关闭，但保留文件，这里只获取了tmpfile的文件名作为参数
                result = azure_speech.synthesize_to_output(input_text, tmpfile.name)
                logger.info("recognize_from_audio result: {}", result)
                data, sr = sf.read(tmpfile.name, dtype='int16')
            except Exception as e:
                raise gr.Error("Exception: " + str(e))    
        return sr, data

    def get_gradio_block():
        with gr.Blocks() as speech_block:
            # with gr.Column():
            input_audio = gr.Audio(label='input audio',
                                   source="upload")


            input_text = gr.Textbox(label='input text',
                                    interactive=True,)

            output_text = gr.Textbox(label='output text')

            output_audio = gr.Audio(label='output audio',
                                    interactive=False,)
            with gr.Row():
                clear_button = gr.Button( value="Clear")
                submit_button = gr.Button(value="Submit")

        
        clear_button.click(lambda: None, inputs=None, outputs=[ input_text, output_text], queue=False)
        # submit_button.click(fn=SpeechWebUI.call_asr, 
        #                     inputs=[input_audio], 
        #                     outputs=[input_text],
        #                     queue=True)
        submit_button.click(fn=SpeechWebUI.call_tts, 
                    inputs=[input_text], 
                    outputs=[output_audio],
                    queue=True)
        return speech_block