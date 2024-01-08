import requests
import base64
import wave
import json
import soundfile as sf
import json

# Chemin vers le fichier audio WAV
audio_file_path = 'test.wav'

file = wave.open(audio_file_path, 'rb')
params = base64.b64encode(json.dumps(file.getparams()).encode())
data = base64.b64encode(file.readframes(file.getnframes()))


# Encode the audio parameters as JSON and then in base64
#encoded_audio_params = base64.b64encode(json.dumps(audio_params_dict).encode())

# URL of your FastAPI endpoint
url = 'http://10.126.7.78:8000/speech_to_text/'

print(url)
# Create the request payload
data = {
    "data": data,
    "params": params
}

# Send the POST request

headers = {"Content-Type": "application/json"}
response = requests.post(url, data=data, headers=headers)
# Encode the data as J

# Display the response
if response.status_code == 200:
    print("Request was successful")
    print(response.json())
else:
    print(f"Request failed with status code: {response.status_code}")