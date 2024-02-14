import cv2
import os
from cv2 import aruco
import numpy as np
import math
from scipy.spatial.transform import Rotation as R

from utils.videoStreamUtils import VideoStreamArgs, pre_process_image
from utils.cameraParams import CameraParams
from utils.poseBuffer import PoseBuffer
from utils.arucoDetection import ArucoDetection, extract_arucos
from utils.geometry import estimatePoseSingleMarkers, transform_point
from utils.mqttPeriodicPublisher import PeriodicPublisher

def get_arguments():
    """Parse all the arguments provided from the CLI.
    Returns:
      A list of parsed arguments.
    """
    parser = VideoStreamArgs()
    parser.add_argument("--params", "-p", type=str, required=True, help="Calibration parameters of your camera, point here the path of the .json file.\
                         They will be used to undistort the image.")
    
    parser.add_argument("--mqtt", type=str, default='', help="If you intend to activate a periodic MQTT publisher, set here the relative .json setting file.")
    
    # If needed. add other custom stuff here.
    return parser



def main():
    videoStreamerArgs = get_arguments()
    args = videoStreamerArgs.parse_args()

    #open camera
    capture = videoStreamerArgs.open_video_stream()
    w= int(capture.get(3))
    h = int(capture.get(4))
    
    cam_params_path = str(args.params)
    assert os.path.isfile(cam_params_path)
    assert cam_params_path.endswith('.json')
    cameraParams = CameraParams.from_file(cam_params_path)
    assert cameraParams.width == w
    assert cameraParams.height == h
    mtx = cameraParams.intrinsics.matrix
    dist_vec = cameraParams.distortions.dist_vector

    mqtt_settings = str(args.mqtt) if args.mqtt != '' else None

    # dictionary to specify type of the marker
    marker_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
    marker_size = 0.025     # 25mm
    param_markers = aruco.DetectorParameters()
    aruco_detector = cv2.aruco.ArucoDetector(marker_dict, param_markers)

    # ID 0 is for tweezers, ID 1 is for spoon.
    available_tool_ids = [0, 1]
    
    buffers = {}
    mqtt_publishers = []
    for t in available_tool_ids:
        b = PoseBuffer()
        buffers[t] = b

        if not mqtt_settings is None:
            pub = PeriodicPublisher(mqtt_settings, f'tool/{t}', b)
            mqtt_publishers.append(pub)
    
    base_frame_to_camera__rot = np.asarray([[-1., 0., 0.], 
                                            [0., 1., 0.], 
                                            [0., 0., -1.]])
    camera_heigth_from_table__m = 1.1
    base_frame_to_camera__pos = np.asarray([[.6, -1.3, 0.83 + camera_heigth_from_table__m]])


    # Crea una finestra per visualizzare lo stream
    cv2.namedWindow("Web Stream")
    while True:
        ret, frame = capture.read()

        if not ret:
            print("Errore nella cattura del frame.")
            break

        # if you want, you can modify saturation, bightness etc
        frame = pre_process_image(frame, cameraParams)

        detected_arucos = extract_arucos(frame, aruco_detector)
        for a in detected_arucos:

            rvecs, tvecs, _ = estimatePoseSingleMarkers(a.corners, marker_size, mtx, dist_vec)
            frame = render_aruco(frame, a, show_center=False)
            cv2.drawFrameAxes(frame, mtx, dist_vec, rvecs[0].flatten(), tvecs[0].flatten(), 0.03)

            if a.id in available_tool_ids:

                rot_matrix, _ = cv2.Rodrigues(rvecs[0])

                res_pos, res_rot = transform_point(base_frame_to_camera__pos, base_frame_to_camera__rot, tvecs[0].T, rot_matrix)
                print(res_pos)
                quaternion = R.from_matrix(res_rot).as_quat()
                buffers[a.id].set_new_data(res_pos, quaternion)

        cv2.imshow("Web Stream", frame)

        # Esci se viene premuto il tasto 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Rilascia le risorse
    capture.release()
    cv2.destroyAllWindows()
    for p in mqtt_publishers:
        p.stop()



def render_aruco(frame, aruco:ArucoDetection, 
                 show_contour=True, show_id=True,
                 show_center=True):
    if show_contour:
        cv2.polylines(
                    frame, [aruco.corners.astype(np.int32)], True, (0, 0, 255), 1, cv2.LINE_AA
                )
    if show_id:
        cv2.putText(frame, f"id: {aruco.id}", aruco.top_right, 
                    cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2, cv2.LINE_AA)
    
    if show_center:
        cv2.circle(frame, aruco.center, radius=5, color=(0, 0, 255), thickness=2)

    return frame
    


if __name__ == '__main__':
    main()
    
    # python detect_arucos.py --source 2 --params settings/pietro_webcam.json --mqtt settings/mqtt_pub_settings.json