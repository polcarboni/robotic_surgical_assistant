import cv2

# URL dello stream video web
url = 'http://192.168.43.1:8080/video'

# Crea un oggetto VideoCapture per leggere lo stream web
cap = cv2.VideoCapture(url)

# Verifica se lo stream è aperto correttamente
if not cap.isOpened():
    print("Errore nell'apertura dello stream.")
    exit()

while True:
    # Leggi un frame dallo stream
    ret, frame = cap.read()

    # Controlla se la lettura del frame è avvenuta con successo
    if not ret:
        print("Errore nella lettura del frame.")
        break

    # Visualizza il frame
    cv2.imshow('Stream Web', frame)

    # Permette di uscire dal loop quando si preme il tasto 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Rilascia le risorse
cap.release()
cv2.destroyAllWindows()