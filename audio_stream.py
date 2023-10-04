import pyaudio
import requests
import wave
import threading

# URL dello stream audio web
url = 'http://192.168.43.1:8080/video'

# Configurazione del lettore audio
chunk = 1024  # Dimensione del chunk audio
rate = 44100  # Frequenza di campionamento (può variare in base allo stream)
channels = 1  # Numero di canali audio (1 per mono, 2 per stereo)

# Inizializza il lettore audio PyAudio
audio_player = pyaudio.PyAudio()

# Crea un oggetto stream per la riproduzione audio
stream = audio_player.open(
    format=pyaudio.paInt16,
    channels=channels,
    rate=rate,
    output=True
)

# Funzione per leggere l'audio dallo stream web
def play_stream():
    response = requests.get(url, stream=True)
    for chunk in response.iter_content(chunk_size=chunk):
        if chunk:
            stream.write(chunk)

# Avvia la riproduzione audio in un thread separato
audio_thread = threading.Thread(target=play_stream)
audio_thread.start()

# Attendi che l'utente prema Enter per interrompere la riproduzione
input("Premi Enter per interrompere la riproduzione audio...")

# Ferma la riproduzione audio
stream.stop_stream()
stream.close()

# Chiudi l'oggetto PyAudio
audio_player.terminate()

