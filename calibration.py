import cv2
import ipaddress
import argparse
import os


def get_arguments():
    """Parse all the arguments provided from the CLI.
    Returns:
      A list of parsed arguments.
    """
    parser = argparse.ArgumentParser()


    parser.add_argument("--source", "-s", type=str, required=True, help="Source of the video. It can be an IP, a path to a device, an index.")
    parser.add_argument("--port", "-p", type=int, default=8080, help="In case of source from IP, you can set here the port. Default to 8080.")

    parser.add_argument("--dst", "-d", type=str, required=True, help="Destination directory where to store pictures. If it doesn't exist yet, it will be created.")


    return parser.parse_args()


def is_ipv4(string):
    try:
        ipaddress.IPv4Network(string)
        return True
    except ValueError:
        return False



def save_frame(event, x, y, flags, param):
    global frame_counter
    global dst_folder
    if event == cv2.EVENT_LBUTTONDOWN:
        frame_name = os.path.join(dst_folder, f'frame_{frame_counter}.png')
        res =  cv2.imwrite(frame_name, frame)
        if res:
            print(f'Stored {frame_name}')
            frame_counter += 1
        else:
            print(f'Impossible to store {frame_name}')
        




args = get_arguments()
video_source = str(args.source)
dst_folder = str(args.dst)

if is_ipv4(video_source):
    ip_port = int(args.source)
    source = f'http://{video_source}:{ip_port}/video'
else:
    try:
        source = int(video_source)
    except:
        source = video_source



capture = cv2.VideoCapture(source)
# Inizializza il contatore dei frame
frame_counter = 0


if not os.path.isdir(dst_folder):
    os.mkdir(dst_folder)

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
