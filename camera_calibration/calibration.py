import cv2
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__))+'/../')
from utils.videoStreamUtils import VideoStreamArgs

def get_arguments():
    """Parse all the arguments provided from the CLI.
    Returns:
      A list of parsed arguments.
    """
    parser = VideoStreamArgs()
    parser.add_argument("--dst", "-d", type=str, required=True, help="Destination directory where to store pictures. If it doesn't exist yet, it will be created.")
    
    # If needed, add other custom stuff here.
    return parser


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
        

videoStreamerArgs = get_arguments()
args = videoStreamerArgs.parse_args()
dst_folder = str(args.dst)
capture = videoStreamerArgs.open_video_stream()


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
