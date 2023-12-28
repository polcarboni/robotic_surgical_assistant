import speech_recognition as sr
import time

def listen_and_print(interval=5):
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Listening...")

        while True:
            try:
                audio = recognizer.listen(source, timeout=0.1, phrase_time_limit=2)
                text = recognizer.recognize_google(audio)
                print(f"You said: {text}")
            except sr.UnknownValueError:
                print("Could not understand audio")
            except sr.RequestError as e:
                print(f"Error making the request: {e}")

            time.sleep(interval)

if __name__ == "__main__":
    listen_and_print()
