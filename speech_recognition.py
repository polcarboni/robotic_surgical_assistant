import speech_recognition as sr
import time

pinze = ["pinze", "vince", "pinzi", "pinza", "pinse"]

def listen_and_print(interval=0.5):
    recognizer = sr.Recognizer()
    recognizer.dynamic_energy_threshold=True

    with sr.Microphone() as source:
        print("Listening...")

        while True:
            try:
                audio = recognizer.listen(source, timeout=10, phrase_time_limit=3)
                text = recognizer.recognize_google(audio, language="it-IT")
                print(f"You said: {text}")
                
                # TOOL 1
                if "cucchiaio" in text:
                    print("CUCCHIAIO")
                # TOOL 2
                for i in pinze:
                    if i in text:
                        print("PINZE")
            
            except sr.UnknownValueError:
                #print("Could not understand audio")
                pass
            except sr.RequestError as e:
                print(f"Error making the request: {e}")

            time.sleep(interval)

if __name__ == "__main__":
    listen_and_print()
