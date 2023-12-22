import json
import base64
import wave
import urllib.request

class MyClass:
    def __init__(self):
        self.url = 'http://10.126.7.78:8000/speech_to_text/'

    def recognize_audio(self, path):
        # Open the wave file
        with wave.open(path, 'rb') as file:
            # Encode params and data to base64
            print("audio params", file.getparams())
            params = base64.b64encode(str(file.getparams()).encode('utf-8')).decode('utf-8')
            data = base64.b64encode(file.readframes(file.getnframes())).decode('utf-8')

        # Send the POST request
        print("audio params", params)
        #print("audio data", data)
        response = self.send_audio_to_server(self.url, data, params)

        sentence = json.loads(response)['transcription']

        if sentence is None:
            sentence = "répète"
        
        return ''.join(sentence)

    def send_audio_to_server(self, url, speech_data, params):
        data = {
            "result": {
                "resultType": "Partial",
                "alts": [{"transcript": "useless", "confidence": 1}]
            },
            "data": speech_data,
            "params": params
        }
        HEADERS = {
        "Content-Type": "application/json"
        }

        req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=HEADERS, method='POST')
        with urllib.request.urlopen(req) as f:
            response = f.read().decode('utf-8')

        return response

# Exemple d'utilisation :
if __name__ == "__main__":
    my_class_instance = MyClass()
    audio_path = 'test.wav'
    result = my_class_instance.recognize_audio(audio_path)
    print(result)
