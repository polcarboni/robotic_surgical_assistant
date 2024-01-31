import cv2

def save_frame(event, x, y, flags, param):
    global frame_counter
    if event == cv2.EVENT_LBUTTONDOWN:
        frame_name = f'mi8/frame_{frame_counter}.png'
        cv2.imwrite(frame_name, frame)
        print(f'{frame_name}')
        frame_counter += 1

ip_camera = '192.168.1.199'
# Inserisci l'URL dello stream web
url = f'http://{ip_camera}:8080/video'

# Inizializza il video capture
capture = cv2.VideoCapture(url)

# Inizializza il contatore dei frame
frame_counter = 0

# Crea una finestra per visualizzare lo stream
cv2.namedWindow("Web Stream")
cv2.setMouseCallback("Web Stream", save_frame)

while True:
    ret, frame = capture.read()

    if not ret:
        print("Errore nella cattura del frame.")
        break

    cv2.imshow("Web Stream", frame)

    # Esci se viene premuto il tasto 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Rilascia le risorse
capture.release()
cv2.destroyAllWindows()
