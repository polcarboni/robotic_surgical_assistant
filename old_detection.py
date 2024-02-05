import cv2
import numpy as np
from multiprocessing import Process, Value


# p = [[Value('i', 0), Value('i', 0)],
#      [Value('i', 0), Value('i', 0)],
#      [Value('i', 0), Value('i', 0)]]

p = [[0, 0], [0, 0], [0, 0]]


ip_camera_1 = '192.168.193.243' #reno4
capture = cv2.VideoCapture(f'http://{ip_camera_1}:8080/video')  # Primo dispositivo di acquisizione

numero_colori = 3
threshold_segmentazione = [[np.array([0,0,0]), np.array([255,255,255])] for i in range(numero_colori)]
# colore_segmentazione_start, colore_segmentazione_end = np.array([0,0,0]), np.array([255,255,255])
# Funzione richiamata al click del mouse
click_counter = 0
def mouse_click_event(event, x, y, flags, param):
    # nonlocal colore_segmentazione_start, colore_segmentazione_end
    global threshold_segmentazione, click_counter
    if event == cv2.EVENT_LBUTTONDOWN:
        window = param[0][y-12:y+13, x-12:x+13]  # Estrae la finestra 25x25 centrata sul punto (x, y)
        b_min, g_min, r_min = window.mean(axis=(0,1)) - 15
        b_max, g_max, r_max = window.mean(axis=(0,1)) + 15
        threshold_segmentazione[click_counter][0] = np.array([b_min, g_min, r_min])
        threshold_segmentazione[click_counter][1] = np.array([b_max, g_max, r_max])
        click_counter += 1
        if click_counter == 3: click_counter = 0
        
while True:
    # Cattura il frame dallo stream
    ret, frame = capture.read()

    # frame = cv2.resize(frame, (frame.shape[1] // 2, frame.shape[0] // 2))

    # Verifica se il frame è stato catturato correttamente
    if not ret:
        print(f"Errore nella cattura del frame per lo stream.")
        break

    for i, (th_min, th_max) in enumerate(threshold_segmentazione):
        maschera = cv2.inRange(frame, th_min, th_max)
        y, x = np.where(maschera > 0)

        if len(x) > 0 and len(y) > 0 and np.sum(th_min)>0:
            # Calcola il centroide medio
            # p[i][0].value = cX = int(np.mean(x)) # coordinata x centroide i-esimo colore
            # p[i][1].value = cY = int(np.mean(y)) # coordinata y centroide i-esimo colore

            p[i][0] = cX = int(np.mean(x)) # coordinata x centroide i-esimo colore
            p[i][1] = cY = int(np.mean(y)) # coordinata y centroide i-esimo colore

            # Disegna il centroide sul frame
            cv2.circle(frame, (cX, cY), 5, (0, 255, 0), 3)  # Disegna un cerchio verde
        
        # Visualizza il frame
        cv2.imshow(f'Stream', frame)

        
        cv2.setMouseCallback(f'Stream', mouse_click_event, [frame])

        # Esci se viene premuto il tasto 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Rilascia le risorse
capture.release()


# process1 = Process(target=show_stream, args=(1, cap1, p))
# process1.start()
# process1.join()
cv2.destroyAllWindows()