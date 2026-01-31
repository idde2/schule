import os
import sounddevice as sd
import queue
import json
from vosk import Model, KaldiRecognizer

model_path = r"C:\Users\Eddi\PycharmProjects\PythonProject\schule\andere\dateien\model"

print("Lade Modell...")
model = Model(model_path)
print("Modell geladen!")

rec = KaldiRecognizer(model, 16000)
audio_queue = queue.Queue()

def callback(indata, frames, time, status):
    audio_queue.put(bytes(indata))

hotword = "computer"
listening = False

print("Starte Mikrofon...")

with sd.RawInputStream(
    samplerate=16000,
    blocksize=8000,
    dtype='int16',
    channels=1,
    callback=callback
):
    print("Sag etwas...")

    while True:
        data = audio_queue.get()

        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            text = result.get("text", "").lower().strip()

            if not text:
                continue

            # HOTWORD-MODUS
            if not listening:
                if hotword in text:
                    print("Hotword erkannt → Assistant aktiv")
                    listening = True
                else:
                    print("Hotword nicht erkannt:", text)
                continue

            # LISTENING-MODUS (JA/NEIN)
            if "ja" in text:
                print("JA erkannt → True")
                listening = False
            elif "nein" in text:
                print("NEIN erkannt → False")
                listening = False
            else:
                print("Erkannt:", text)
