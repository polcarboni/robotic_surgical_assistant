import cv2
import numpy as np
from multiprocessing import Process, Value
import random, time

from paho.mqtt import client as mqtt_client
from hand_estimation.utils import calcola_posizione_3d


broker = '127.0.0.1'
port = 1883
topic = "topics/hand_position"
# Generate a Client ID with the publish prefix.
client_id = f'publish-{random.randint(0, 1000)}'
# username = 'emqx'
# password = 'public'

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect to broker, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    # client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

publisher = connect_mqtt()
publisher.loop_start()

#global counter
p1x = Value('i', 0)
p1y = Value('i', 0)
p2x = Value('i', 0)
p2y = Value('i', 0)


def publish_hand_position(position):
    result = publisher.publish(topic, position)
    # result: [0, 1]
    status = result[0]
    if status != 0:
        print(f"Failed to send message to topic {topic}")

# Funzione per gestire lo stream video
def show_stream(stream_num, capture, px, py):
    colore_segmentazione_start, colore_segmentazione_end = np.array([0,0,0]), np.array([255,255,255])
    # Funzione richiamata al click del mouse
    def mouse_click_event(event, x, y, flags, param):
        nonlocal colore_segmentazione_start, colore_segmentazione_end
        if event == cv2.EVENT_LBUTTONDOWN:
            window = param[0][y-12:y+13, x-12:x+13]  # Estrae la finestra 25x25 centrata sul punto (x, y)
            b_min, g_min, r_min = window.mean(axis=(0,1)) - 15
            b_max, g_max, r_max = window.mean(axis=(0,1)) + 15
            colore_segmentazione_start = np.array([b_min, g_min, r_min])
            colore_segmentazione_end = np.array([b_max, g_max, r_max])
            # counter.value += 1
            # print(stream_num, counter.value)
            
    while True:
        # Cattura il frame dallo stream
        ret, frame = capture.read()

        # frame = cv2.resize(frame, (frame.shape[1] // 2, frame.shape[0] // 2))

        # Verifica se il frame è stato catturato correttamente
        if not ret:
            print(f"Errore nella cattura del frame per lo stream {stream_num}.")
            break

        maschera = cv2.inRange(frame, colore_segmentazione_start, colore_segmentazione_end)
        y, x = np.where(maschera > 0)

        if len(x) > 0 and len(y) > 0 and np.sum(colore_segmentazione_start)>0:
            # Calcola il centroide medio
            px.value = cX = int(np.mean(x))
            py.value = cY = int(np.mean(y))

            # Disegna il centroide sul frame
            cv2.circle(frame, (cX, cY), 5, (0, 255, 0), 3)  # Disegna un cerchio verde
        
        # Visualizza il frame
        cv2.imshow(f'Stream {stream_num}', frame)

        
        cv2.setMouseCallback(f'Stream {stream_num}', mouse_click_event, [frame])

        # Esci se viene premuto il tasto 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Rilascia le risorse
    capture.release()

def show_meaure_button(p1x, p1y,p2x, p2y):
    def on_click(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            distance = calcola_posizione_3d([p1x.value, p1y.value], [p2x.value, p2y.value])
            print('\n')
            print([p1x.value, p1y.value], [p2x.value, p2y.value])
            print(distance)

    # Carica l'immagine
    image = cv2.imread('measure.png')

    # Crea una finestra per visualizzare l'immagine
    cv2.imshow('Measure', image)

    # Associa la funzione on_click all'evento di click del mouse
    cv2.setMouseCallback('Measure', on_click)

    # Attendi finché non viene premuto il tasto 'q' per chiudere la finestra
    while True:
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

ip_camera_1 = '192.168.193.243' #reno4
ip_camera_2 = '192.168.193.241' #mi8 lite

# Inizializza i due oggetti VideoCapture per i due flussi video
cap1 = cv2.VideoCapture(f'http://{ip_camera_1}:8080/video')  # Primo dispositivo di acquisizione
cap2 = cv2.VideoCapture(f'http://{ip_camera_2}:8080/video')  # Secondo dispositivo di acquisizione
#cap2 = cv2.VideoCapture(0)
# Crea due processi per gestire i due flussi video
process1 = Process(target=show_stream, args=(1, cap1, p1x, p1y))
process2 = Process(target=show_stream, args=(2, cap2, p2x, p2y))
#process3 = Process(target=show_meaure_button, args=(p1x, p1y,p2x, p2y))

# Avvia i processi
process1.start()
process2.start()
#process3.start()

flag = True
try:
    while flag:
        time.sleep(2)
        distance = calcola_posizione_3d([p1x.value, p1y.value], [p2x.value, p2y.value])
        publish_hand_position(str(distance))
except KeyboardInterrupt:
    flag = False

# Attendi che i processi terminino (questo succederà solo se premi 'q' in una delle finestre)
process1.join()
process2.join()
#process3.join()

# Chiudi tutte le finestre
cv2.destroyAllWindows()
