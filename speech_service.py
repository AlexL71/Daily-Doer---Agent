# speech_service.py
from google.cloud import speech
from google.oauth2 import service_account
import os
import config

async def audio_to_text(audio_file_path):
    if not os.path.exists(config.SPEECH_SA_KEY_PATH):
        print(f"Service account key file not found at: {config.SPEECH_SA_KEY_PATH}")
        return None
    try:
        speech_credentials = service_account.Credentials.from_service_account_file(config.SPEECH_SA_KEY_PATH)
        client = speech.SpeechAsyncClient(credentials=speech_credentials)
    except Exception as e:
        print(f"Error loading service account credentials or initializing SpeechClient: {e}")
        return None

    try:
        with open(audio_file_path, "rb") as audio_file:
            content = audio_file.read()

        audio = speech.RecognitionAudio(content=content)
        speech_config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.OGG_OPUS,
            sample_rate_hertz=48000,
            language_code="en-US", 
            enable_automatic_punctuation=True,
        )
        
        # print("Sending audio to Google Speech-to-Text (with explicit sample rate)...") # Optional debug
        response = await client.recognize(config=speech_config, audio=audio)
        # print(f"FULL STT RESPONSE: {response}") # Optional debug
        # print("Received response from Google Speech-to-Text.") # Optional debug

        transcript = ""
        if response.results:
            for result in response.results:
                if result.alternatives:
                    transcript += result.alternatives[0].transcript + " "
        
        if not transcript.strip():
            # print("STT Result: No transcript returned or transcript is empty.") # Optional debug
            pass # Return empty string if no transcript

        return transcript.strip()
    except Exception as e:
        print(f"Google Speech-to-Text error: {e}")
        return None