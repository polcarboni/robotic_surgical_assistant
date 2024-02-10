import cv2
import os
import sys
import signal
import time

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__))+'/../')
from utils.videoStreamUtils import VideoStreamArgs

def get_arguments():
    """Parse all the arguments provided from the CLI.
    Returns:
      A list of parsed arguments.
    """
    parser = VideoStreamArgs()
    parser.add_argument("--dst", "-d", type=str, required=True, help="Destination directory where to store pictures. If it doesn't exist yet, it will be created.")
    parser.add_argument("--cmd", "-c", type=int, default=-1, help="If you want, you can type here the PID of another camera calibration process, which will be asked to store an image \
                        whenever this process will store it.")

    # If needed, add other custom stuff here.
    return parser


def check_if_click(event, x, y, flags, param):
    global slave_process
    if event == cv2.EVENT_LBUTTONDOWN:
        save_frame()
        if slave_process > 0:
            os.kill(slave_process, signal.SIGUSR1)
            print(f'Sent {signal.SIGUSR1} to process {slave_process}')

def save_frame():
    global frame_counter
    global dst_folder
    frame_name = os.path.join(dst_folder, f'frame_{frame_counter}.png')
    res =  cv2.imwrite(frame_name, frame)
    if res:
        print(f'Stored {frame_name}')
        frame_counter += 1
    else:
        print(f'Impossible to store {frame_name}')


def sig_handler(signum, frame):
    print('An external process asked to store image.')
    save_frame()
    global next_frame_faulty
    next_frame_faulty = True


videoStreamerArgs = get_arguments()
args = videoStreamerArgs.parse_args()
dst_folder = str(args.dst)
capture = videoStreamerArgs.open_video_stream()
slave_process = int(args.cmd)
next_frame_faulty = False

# Inizializza il contatore dei frame
frame_counter = 0

if not os.path.isdir(dst_folder):
    os.mkdir(dst_folder)


print('Process PID: ', os.getpid())

signal.signal(signal.SIGUSR1, sig_handler)



# Crea una finestra per visualizzare lo stream
cv2.namedWindow("Web Stream")
cv2.setMouseCallback("Web Stream", check_if_click)

while True:
    ret, frame = capture.read()

    if not ret:
        if next_frame_faulty:
            next_frame_faulty = False
            continue
        else:
            print("Errore nella cattura del frame.")
            break

    cv2.imshow("Web Stream", frame)

    # Esci se viene premuto il tasto 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Rilascia le risorse
capture.release()
cv2.destroyAllWindows()
