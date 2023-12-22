import json
import torch
from transformers import WhisperProcessor, WhisperForConditionalGeneration, WhisperTokenizer, AutoFeatureExtractor, \
    WhisperModel
from transformers import pipeline, AutomaticSpeechRecognitionPipeline

import librosa
import soundfile as sf
from typing import List
from fastapi import FastAPI, UploadFile, File, Request

from pydantic import BaseModel
from io import BytesIO
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
import base64
import wave
from ast import literal_eval
import logging

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # @todo set production origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# load model and processor
processor = WhisperProcessor.from_pretrained("openai/whisper-medium")

model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-medium")
feature_extractor = AutoFeatureExtractor.from_pretrained("openai/whisper-medium")

model.config.forced_decoder_ids = processor.get_decoder_prompt_ids(language="french", task="transcribe")

device = "cuda:0" if torch.cuda.is_available() else "cpu"
tokenizer = WhisperTokenizer.from_pretrained("openai/whisper-medium", language="french")

pipe = pipeline(
    "automatic-speech-recognition",
    feature_extractor=feature_extractor,
    tokenizer=tokenizer,
    model=model,
    chunk_length_s=30,
    device='cpu'
)
class ASRRequest(BaseModel):
    data: str  # Base64 encoded audio data
    params: str  # Base64 encoded audio parameters (e.g., sample rate, channels)
    
class Transcription(BaseModel):  # pour la réponse
    transcription: str

def speech_to_text(wav_file):
    # audio_input, _ = librosa.load(audio_file.file, sr=16_000)
    input_audio, sr = librosa.load(wav_file, sr=16_000)
    prediction = pipe(input_audio.copy(), batch_size=16)['text']
    return prediction

@app.post("/speech_to_text/", response_model=Transcription)
async def transcriptions(request_body: ASRRequest):
    print("request", base64.b64decode(request_body.params))

    #logging.info("request", request_body.data)
    
    # Decode base64 encoded audio data and parameters
    audio_data = base64.b64decode(request_body.data)

    nchannels = 1
    sampwidth = 2
    framerate = 16000
    nframes = 73728
    comptype = 'NONE'
    compname = 'not compressed'

    # Create a WAV file and set the parameters
    audio_file_name = 'audio.wav'
    wave_write = wave.open(audio_file_name, "wb")
    wave_write.setnchannels(nchannels)
    wave_write.setsampwidth(sampwidth)
    wave_write.setframerate(framerate)
    wave_write.setnframes(nframes)
    wave_write.setcomptype(comptype, compname)
  
    wave_write.writeframes(audio_data)
    wave_write.close()

    #data, samplerate = sf.read(audioFileName, format='wav')
    #audio_content64 = (resquest_body['data'])
    print(audio_file_name)

    
    transcription = speech_to_text(audio_file_name)
    print(transcription)
    return jsonable_encoder({"transcription": transcription})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)