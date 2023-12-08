import torch
from transformers import WhisperProcessor, WhisperForConditionalGeneration, WhisperTokenizer, AutoFeatureExtractor, \
    WhisperModel
from transformers import pipeline, AutomaticSpeechRecognitionPipeline

import librosa
import soundfile as sf

from typing import List
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from io import BytesIO
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware


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

class Transcription(BaseModel):  # pour la réponse
    transcription: str

def speech_to_text(wav_file):
    # audio_input, _ = librosa.load(audio_file.file, sr=16_000)
    input_audio, sr = librosa.load(wav_file, sr=16_000)
    prediction = pipe(input_audio.copy(), batch_size=16)['text']
    return prediction

@app.post("/speech_to_text/", response_model=Transcription)
async def transcriptions(file: UploadFile = File(...)):
    audio_content = BytesIO(await file.read())
    print(audio_content)
    # data, samplerate = sf.read(audio_content, format='wav')
    transcription = speech_to_text(audio_content)
    print(transcription)
    return jsonable_encoder({"transcription": transcription})


