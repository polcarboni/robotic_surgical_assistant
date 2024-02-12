import os
import cv2
import numpy as np
import math
import sys
from multiprocessing import Process, Value

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__))+'/../')
from utils.videoStreamUtils import VideoStreamArgs, pre_process_image
from utils.cameraParams import StereoCamera
from utils.poseBuffer import PoseBuffer
from utils.mqttPeriodicPublisher import PeriodicPublisher
from hands_tracker import *



def get_arguments():
    """Parse all the arguments provided from the CLI.
    Returns:
      A list of parsed arguments.
    """
    parser = VideoStreamArgs(how_many_cameras=2)
    parser.add_argument("--params", "-p", type=str, required=True, help="Calibration parameters of your stereo setup, point here the path of the .json file.")
    parser.add_argument("--mqtt", type=str, default='', help="If you intend to activate a periodic MQTT publisher, set here the relative .json setting file.")
    
    # If needed. add other custom stuff here.
    return parser


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



def main():
    videoStreamerArgs = get_arguments()
    args = videoStreamerArgs.parse_args()
    video_streams = videoStreamerArgs.open_video_stream()
    
    #tmp
    #video_streams = [video_streams[0]]
    
    cam_params_path = str(args.params)
    assert os.path.isfile(cam_params_path)
    assert cam_params_path.endswith('.json')
    stereoParams = StereoCamera.from_file(cam_params_path)

    mqtt_settings = str(args.mqtt) if args.mqtt != '' else None
    data_buffer = PoseBuffer()
    if not mqtt_settings is None:
        pub = PeriodicPublisher(mqtt_settings, f'hand_position', data_buffer)

    tracker = HandDetector()

    cv2.namedWindow("Stream_0")
    cv2.namedWindow("Stream_1")

    
    while True:
        for i, cap in enumerate(video_streams):
            ret, frame = cap.read()

            if not ret:
                print("Errore nella cattura del frame.")
                break

            # if you want, you can modify saturation, bightness etc
            single_cam_params = stereoParams.src if i==0 else stereoParams.dst
            frame = pre_process_image(frame, single_cam_params)

            #let's undistort the image
            
            alpha = 1.0
            mtx = single_cam_params.intrinsics.matrix
            dist = single_cam_params.distortions.dist_vector
            w, h = single_cam_params.width, single_cam_params.height
            newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), alpha, (w, h))
            dst = cv2.undistort(frame, mtx, dist, None, newcameramtx)

            # crop the image
            x, y, w, h = roi
            frame = dst[y:y+h, x:x+w]
            

            frame = frame.astype(np.uint8)
            result = tracker.detect(frame)
            #print(result.hand_landmarks[0])
            frame = draw_landmarks_on_image(frame, result)

            cv2.imshow(f"Stream_{i}", frame)

        # Esci se viene premuto il tasto 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cv2.destroyAllWindows()
    if not mqtt_settings is None:
        pub.stop()
    return


if __name__ == '__main__':
    main()