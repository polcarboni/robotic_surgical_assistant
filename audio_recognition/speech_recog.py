#sudo apt-get install portaudio19-dev
#pip install pyaudio
#pip install pyalsaaudio

import speech_recognition as sr


recognizer = sr.Recognizer()

with sr.Microphone() as source:
    print("Say something:")
    audio = recognizer.listen(source)

try:
    
    text = recognizer.recognize_google(audio)
    print(f"You said: {text}")
except sr.UnknownValueError:
    print("Could not understand audio")
except sr.RequestError as e:
    print(f"Error making the request: {e}")
