import time
import logging
from deepface import DeepFace
import uvicorn
from fastapi import FastAPI
import requests
from fastapi.middleware.cors import CORSMiddleware
from speech_recognition import speech_to_text

app = FastAPI()

origins = [
    "http://localhost:3000/",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # @todo set production origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/face_recognizer")
def face_recognizer():
    # load img from local url get-image/img/currentImg.png using deepface

    # result = DeepFace.verify(img1_path="../get-image/db/jordan.png", img2_path="../get-image/db/jordan_1.png", enforce_detection=False)
    result = DeepFace.find(img_path="../get-image/img/currentImg.png", db_path="../get-image/db",
                           enforce_detection=False)
    text = result[0].get("identity")[0].split("/")[3].split(".")[0]

    print(result[0].get("identity")[0].split("/")[3].split(".")[0])

    return {"result": text}


@app.get("/emotion_recognizer")
def emotion_recognizer():
    # load img from local url get-image/img/currentImg.png using deepface
    text = ''

    result = DeepFace.analyze(img_path="../get-image/img/currentImg.png", actions=['emotion'], enforce_detection=False)

    print(result[0])

    if result[0].get("dominant_emotion") == "happy":
        text = "vous êtes heureux"
    elif result[0].get("dominant_emotion") == "sad":
        text = "vous êtes triste"
    elif result[0].get("dominant_emotion") == "angry":
        text = "vous êtes en colère"
    elif result[0].get("dominant_emotion") == "surprise":
        text = "vous êtes surpris"
    elif result[0].get("dominant_emotion") == "neutral":
        text = "vous êtes neutre"
    elif result[0].get("dominant_emotion") == "fear":
        text = "vous avez peur"
    return {"result": text}


app.include_router(speech_to_text.router)

if __name__ == "__main__":
    uvicorn.run("main:app", host='0.0.0.0', port=4557, reload=True, workers=3)
