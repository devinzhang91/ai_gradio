from loguru import logger
import yaml
import azure.cognitiveservices.speech as speechsdk

class AuzerSpeechEngine:
    
    with open('config.yaml',mode='r') as f:
        result = yaml.load(f, Loader=yaml.FullLoader)
        speech_config = result['azure_speech']
        SPEECH_REGION = speech_config['region']
        SPEECH_KEY = speech_config['key']
        SPEECH_URL = speech_config['endpoint']
        SPEECH_VOICE = speech_config['voice']
        try:
            SPEECH_VOICE_LIST = speech_config['voice']
        except Exception as e:
            logger.error(f"speech voice config error: {e}")
            raise

    def __init__(self) -> None:
        pass


    def recognize_from_audio(filename : str  = None):
        # Call the API
        try:
            # This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
            speech_config = speechsdk.SpeechConfig(subscription=AuzerSpeechEngine.SPEECH_KEY, 
                                                region=AuzerSpeechEngine.SPEECH_REGION)
            speech_config.speech_recognition_language="zh-CN"

            if(filename):
                logger.info("filename: {}".format(filename))
                audio_config = speechsdk.audio.AudioConfig(filename=filename)
            else:
                audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)

            speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

            if(filename == None):
                logger.info("Speak into your microphone.")
            speech_recognition_result = speech_recognizer.recognize_once_async().get()

            if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
                logger.info("Recognized: {}".format(speech_recognition_result.text))
            elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
                logger.warning("No speech could be recognized: {}".format(speech_recognition_result.no_match_details))
            elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = speech_recognition_result.cancellation_details
                logger.warning("Speech Recognition canceled: {}".format(cancellation_details.reason))
                if cancellation_details.reason == speechsdk.CancellationReason.Error:
                    # if Runtime error: Failed to initialize platform (azure-c-shared).
                    # https://learn.microsoft.com/en-us/azure/cognitive-services/speech-service/quickstarts/setup-platform
                    # On Ubuntu 22.04 only, install the latest [libssl1.1](security.ubuntu.com/ubuntu/pool/main/o/openssl/)
                    logger.error("Error details: {}".format(cancellation_details.error_details))
                    logger.error("Did you set the speech resource key and region values?")
            return speech_recognition_result.text
        except Exception as e:
            logger.error(f"call_bing_search error: {e}")
            raise e

    def synthesize_to_output(text_to_speech : str,
                            filename : str  = None):
        try:
            # This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
            speech_config = speechsdk.SpeechConfig(subscription=AuzerSpeechEngine.SPEECH_KEY, 
                                                region=AuzerSpeechEngine.SPEECH_REGION)
            if(filename):
                audio_config = speechsdk.audio.AudioOutputConfig(filename=filename)
            else:
                audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)


            # The language of the voice that speaks.
            speech_config.speech_synthesis_voice_name = AuzerSpeechEngine.SPEECH_VOICE_LIST[1]

            speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

            # Get text from the console and synthesize to the default speaker.
            if(filename == None):
                print("Enter some text that you want to speak >")
                text = input()
            else:
                text = text_to_speech

            speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()

            if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                logger.info("Speech synthesized for text [{}]".format(text))
            elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = speech_synthesis_result.cancellation_details
                logger.warning("Speech synthesis canceled: {}".format(cancellation_details.reason))
                if cancellation_details.reason == speechsdk.CancellationReason.Error:
                    if cancellation_details.error_details:
                        logger.error("Error details: {}".format(cancellation_details.error_details))
                        logger.error("Did you set the speech resource key and region values?")
        except Exception as e:
            logger.error(f"call_bing_search error: {e}")
            raise e

############################################    
# import edge_tts
# import asyncio

# async def _communicate(text_to_speech, filename) -> None:
#     communicate = edge_tts.Communicate(text_to_speech, AzureSpeechConf.SPEECH_VOICE_LIST[0])
#     await communicate.save(filename)

# def edge_tts_synthesize_to_output(text_to_speech : str,
#                                   filename : str  = None):
#     try:
#         asyncio.get_event_loop().run_until_complete(_communicate())
#     except Exception as e:
#         logger.error(f"edge_tts_synthesize_to_output error: {e}")
#         raise e