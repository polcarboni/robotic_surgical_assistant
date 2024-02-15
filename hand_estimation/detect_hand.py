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
from utils.geometry import get_distance_from_stereo, transform_point



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
    dist = None

    cv2.namedWindow("Stream_0")
    cv2.namedWindow("Stream_1")


    base_frame_to_camera__rot = np.asarray([[1., 0., 0.], 
                                            [0., 0., 1.], 
                                            [0., -1., 0.]])
    frontal_distance_from_person__m = 0.7
    lateral_distance_from_person__m = 0.8
    camera_heigth_from_floor__m = 1.3
    base_frame_to_camera__pos = np.asarray([[1.8 - lateral_distance_from_person__m , -0.1 - frontal_distance_from_person__m, camera_heigth_from_floor__m]])

    
    while True:
        positions = []
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
            distortion = single_cam_params.distortions.dist_vector
            w, h = single_cam_params.width, single_cam_params.height
            newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, distortion, (w, h), alpha, (w, h))
            frame = cv2.undistort(frame, mtx, distortion, None, newcameramtx)
            # crop the image
            x, y, w, h = roi
            frame = frame[y:y+h, x:x+w]
            

            frame = frame.astype(np.uint8)
            result = tracker.detect(frame)
            #print(result.hand_landmarks[0])
            position = get_hand_central_point(result, w, h)

            positions.append(position)

            

            if not position is None:
                cv2.circle(frame, (position), radius=5, color=(0, 255, 0), thickness=-1)

                #plot also distance text for the previous frame, if available
                if not dist is None:
                    text_pos = (position[0] + 5, position[1] + 5)
                    distance_text = "{:.3f}".format(dist)
                    cv2.putText(frame, distance_text,(text_pos), cv2.FONT_HERSHEY_DUPLEX,1, (0, 255, 0), 1, cv2.LINE_AA)

            #frame = draw_landmarks_on_image(frame, result)

            cv2.imshow(f"Stream_{i}", frame)

        assert len(positions) == 2
        dist = None
        if not (positions[0] is None or positions[1] is None):
            k1, k2 = stereoParams.src.intrinsics.matrix, stereoParams.dst.intrinsics.matrix
            delta_rot, delta_pos = stereoParams.extrinsics.rot_matrix, stereoParams.extrinsics.trans_vector
            dist_3d = get_distance_from_stereo(positions[0], positions[1], k1, k2, delta_rot.T, -delta_pos)

            fixed_rot = np.asarray([math.pi, 0, 0])
            dist_3d = np.expand_dims(dist_3d, 0)
            pos, rot = transform_point(base_frame_to_camera__pos, base_frame_to_camera__rot, dist_3d)
            #print(dist_3d, " --> ", pos)
            #print(rot)
            #fixed_pos = np.asarray([0, math.pi/2, 0])
            fixed_rot = np.asarray([0, math.pi/2, 0])
            data_buffer.set_new_data(pos, fixed_rot)

            dist = np.linalg.norm(dist_3d)



        # Esci se viene premuto il tasto 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cv2.destroyAllWindows()
    if not mqtt_settings is None:
        pub.stop()
    return


if __name__ == '__main__':
    main()
    # check that the two webcams coincide:
    # serena's webcam should be in Stream_0, Pietro's webcam in Stream_1 
    # python hand_estimation/detect_hand.py --source_0 /dev/video2 --source_1 /dev/video4 --params settings/stereo_setup.json  --mqtt settings/mqtt_pub_settings.json