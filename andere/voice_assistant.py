import multiprocessing
import queue
import json
import sounddevice as sd
from vosk import Model, KaldiRecognizer


# -----------------------------
# TTS-PROZESS (lädt NUR pyttsx3)
# -----------------------------
def tts_process(tts_queue):
    import pyttsx3
    engine = pyttsx3.init()

    while True:
        text = tts_queue.get()
        if text is None:
            break
        engine.say(text)
        engine.runAndWait()


# -----------------------------
# HAUPTPROGRAMM
# -----------------------------
def main():
    model_path = r"C:\Users\Eddi\PycharmProjects\PythonProject\schule\andere\dateien\model"

    print("Lade Modell...")
    model = Model(model_path)
    print("Modell geladen!")

    rec = KaldiRecognizer(model, 16000)
    audio_queue = queue.Queue()

    # TTS-Prozess starten
    tts_queue = multiprocessing.Queue()
    tts_proc = multiprocessing.Process(target=tts_process, args=(tts_queue,), daemon=True)
    tts_proc.start()

    def speak(text):
        tts_queue.put(text)

    def callback(indata, frames, time_, status):
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

                if not listening:
                    if hotword in text:
                        print("Hotword erkannt → Assistant aktiv")
                        speak("Ja?")
                        listening = True
                    else:
                        print("Hotword nicht erkannt:", text)
                    continue

                # LISTENING-MODUS (JA/NEIN)
                if "ja" in text:
                    print("JA erkannt → True")
                    speak("Okay, verstanden.")
                    listening = False
                elif "nein" in text:
                    print("NEIN erkannt → False")
                    speak("Alles klar.")
                    listening = False
                else:
                    print("Erkannt:", text)
                    # speak(text)  <-- NICHT jedes Wort sprechen!


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
