from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import threading
import vosk
import pyaudio
import json
import os

# Initialize Flask app and SocketIO
app = Flask(__name__)
socketio = SocketIO(app)

# Set up Vosk model
MODEL_PATH = "vosk-model-small-en-us-0.15"  # Update with the model you downloaded
model = vosk.Model(MODEL_PATH)

# Audio settings
chunk_size = 4000
rate = 16000
mic = pyaudio.PyAudio()

# Function to handle speech-to-text in background
def recognize_speech_background():
    stream = mic.open(format=pyaudio.paInt16, channels=1, rate=rate, input=True, frames_per_buffer=chunk_size)
    recognizer = vosk.KaldiRecognizer(model, rate)

    while True:
        data = stream.read(chunk_size)
        if recognizer.AcceptWaveform(data):
            result = recognizer.Result()
            result_json = json.loads(result)
            if "text" in result_json:
                socketio.emit('transcript', {'text': result_json['text']})

@app.route("/")
def index():
    return render_template("index.html")

@socketio.on("start_stream")
def handle_stream():
    threading.Thread(target=recognize_speech_background, daemon=True).start()

if __name__ == "__main__":
    socketio.run(app, debug=True)
