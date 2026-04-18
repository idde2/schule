import queue
import json
import sounddevice as sd
from vosk import Model, KaldiRecognizer
import win32com.client
from ollama import Client
import threading
import time

client = Client()
speaker = win32com.client.Dispatch("SAPI.SpVoice")

model_path = r"C:\Users\Eddi\PycharmProjects\PythonProject\schule\andere\dateien\model"
model = Model(model_path)
rec = KaldiRecognizer(model, 16000)
audio_queue = queue.Queue()

chat_history = [
    {"role": "system", "content": "Du antwortest immer auf Deutsch. Die Person heißt Eddi. Dein Name ist Computer. Antworte kurz, klar und ehrlich."}
]

def ollama_query(prompt: str) -> str:
    chat_history.append({"role": "user", "content": prompt})
    r = client.chat(model="phi3:mini", messages=chat_history)
    chat_history.append(r["message"])
    return r["message"]["content"]


def callback(indata, frames, time_, status):
    audio_queue.put(bytes(indata))

def main():
    hotword = "computer"
    active = False
    cooldown = 0

    with sd.RawInputStream(
        samplerate=16000,
        blocksize=8000,
        dtype="int16",
        channels=1,
        callback=callback
    ):
        print("Bereit")

        while True:
            try:
                data = audio_queue.get(timeout=0.1)
            except queue.Empty:
                continue

            if not rec.AcceptWaveform(data):
                continue

            result = json.loads(rec.Result())
            text = result.get("text", "").lower().strip()
            if not text:
                continue

            if cooldown > time.time():
                continue

            if not active:
                if hotword in text:
                    active = True
                    cooldown = time.time() + 0.8
                    speaker.Speak("Ja Eddi")
                continue

            if "beenden" in text:
                active = False
                speaker.Speak("Alles klar")
                cooldown = time.time() + 0.8
                continue
            if "stop" in text:
                active = False
                speaker.Speak("stopt")
                quit()
            print(text)
            antwort = ollama_query(text)
            speaker.Speak(antwort)
            cooldown = time.time() + 0.8







if __name__ == "__main__":
    main()