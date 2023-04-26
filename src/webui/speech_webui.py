import tempfile
from src.webui.webui_surface import WebUISurface
from loguru import logger
import gradio as gr
from src.tools.azure_speech import AuzerSpeechEngine
import numpy as np
import soundfile as sf

class SpeechWebUI(WebUISurface):

    def __init__(self):
        pass

    def reformat_freq(sr, y):
        if sr not in (
            48000,
            16000,
        ):  # Deepspeech only supports 16k, (we convert 48k -> 16k)
            raise ValueError("Unsupported rate", sr)
        if sr == 48000:
            if(shape := y.shape[1]) == 2:   # stereo
                y = y.reshape(-1, 6)
            else:
                y = y.reshape(-1, 3)        # mono
            y = (
                ((y / max(np.max(y), 1)) * 32767)
                .mean(axis=1)
                .astype("int16")
            )
            sr = 16000
        return sr, y

    def call_asr(input_audio):
        sr_16k, data_16k = SpeechWebUI.reformat_freq(*input_audio)
        with tempfile.TemporaryDirectory(prefix= '/tmp/ai_gradio_') as tmpdir:
            with tempfile.NamedTemporaryFile(suffix='.wav', dir=tmpdir, delete=False) as tmpfile :
                try:
                    sf.write(tmpfile.name, data_16k, 16000, 'PCM_16')
                    tmpfile.close()  # 文件关闭即删除
                    result = AuzerSpeechEngine.recognize_from_audio(tmpfile.name)
                    logger.info("recognize_from_audio result: {}", result)
                finally:
                    tmpfile.close()  # 文件关闭即删除
            return result

    def call_tts(input_text):
        with tempfile.TemporaryDirectory(prefix= '/tmp/ai_gradio_') as tmpdir:
            with tempfile.NamedTemporaryFile(suffix='.wav', dir=tmpdir, delete=False) as tmpfile :
                try:
                    tmpfile.close()  # 文件关闭，但保留文件，这里只获取了tmpfile的文件名作为参数
                    result = AuzerSpeechEngine.synthesize_to_output(input_text, tmpfile.name)
                    logger.info("recognize_from_audio result: {}", result)
                    data, sr = sf.read(tmpfile.name, dtype='int16')
                except Exception as e:
                    raise gr.Error("Exception: " + str(e))    
        return sr, data

    def get_gradio_block():
        with gr.Blocks() as speech_block:
            with gr.Row():
                with gr.Column(scale=4):
                    asr_audio = gr.Audio(label='ASR audio',
                                         source="upload")
                    asr_text = gr.Textbox(label='ASR text')
                asr_button = gr.Button( value="ASR")

            with gr.Row():
                with gr.Column(scale=4):
                    tts_text = gr.Textbox(label='TTS text',
                                          interactive=True,)

                    tts_audio = gr.Audio(label='TTS audio',
                                            interactive=False,)
                tts_button = gr.Button(value="TTS")

        # clear_button.click(lambda: None, inputs=None, outputs=[ input_text, output_text], queue=False)
        asr_button.click(fn=SpeechWebUI.call_asr, 
                         inputs=[asr_audio], 
                         outputs=[asr_text],
                         queue=True)
        tts_button.click(fn=SpeechWebUI.call_tts, 
                         inputs=[tts_text], 
                         outputs=[tts_audio],
                         queue=True)# fastapi router