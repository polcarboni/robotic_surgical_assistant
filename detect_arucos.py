import cv2
import os
from cv2 import aruco
import numpy as np

from videoStreamUtils import VideoStreamArgs
from cameraParams import CameraParams

def get_arguments():
    """Parse all the arguments provided from the CLI.
    Returns:
      A list of parsed arguments.
    """
    parser = VideoStreamArgs()
    parser.add_argument("--params", "-p", type=str, default='', help="If you have calibration parameters \
                        of your camera, point here the path of the .json file. They will be used to undistort the image.")
    # If needed. add other custom stuff here.
    return parser


class arucoDetection:
    def __init__(self, id:int, corners:np.ndarray) -> None:
        assert corners.shape == (1, 4, 2)

        self.id = id
        self.corners = corners.copy()

        corners = corners.reshape(4, 2)
        self.center = np.average(corners, 0).astype(int)

        corners = corners.astype(int)
        self.top_right = corners[0].ravel()
        self.top_left = corners[1].ravel()
        self.bottom_right = corners[2].ravel()
        self.bottom_left = corners[3].ravel()


def main():
    videoStreamerArgs = get_arguments()
    args = videoStreamerArgs.parse_args()

    #open camera
    capture = videoStreamerArgs.open_video_stream()
    w= int(capture.get(3))
    h = int(capture.get(4))
    
    cameraParams = None
    cam_params_path = str(args.params)
    if cam_params_path != '':
        assert os.path.isfile(cam_params_path)
        assert cam_params_path.endswith('.json')
        cameraParams = CameraParams.from_file(cam_params_path)
        assert cameraParams.width == w
        assert cameraParams.height == h
        mtx = cameraParams.intrinsics.matrix
        dist_vec = cameraParams.distortions.dist_vector


    # dictionary to specify type of the marker
    marker_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
    # detect the marker
    param_markers = aruco.DetectorParameters()
    aruco_detector = cv2.aruco.ArucoDetector(marker_dict, param_markers)

    # Crea una finestra per visualizzare lo stream
    cv2.namedWindow("Web Stream")

    while True:
        ret, frame = capture.read()

        if not ret:
            print("Errore nella cattura del frame.")
            break
        
        if not cameraParams is None:
            # If the scaling parameter alpha=0, it returns undistorted image with minimum unwanted pixels. So it may even remove some pixels at image corners. 
            # If alpha=1, all pixels are retained with some extra black images.
            alpha = 0.0 # set me between 0 and 1

            newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist_vec, (w,h), alpha, (w,h))
            # undistort
            #frame = cv2.undistort(frame, mtx, dist_vec, None, newcameramtx)



        detected_arucos = extract_arucos(frame, aruco_detector)
        for a in detected_arucos:
            if not cameraParams is None:
                rvecs, tvecs, _ = estimatePoseSingleMarkers(a.corners, 0.035, mtx, dist_vec)
                print(f'rot: {rvecs}; translation: {tvecs}')
            frame = render_aruco(frame, a)

        cv2.imshow("Web Stream", frame)

        # Esci se viene premuto il tasto 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Rilascia le risorse
    capture.release()
    cv2.destroyAllWindows()



def render_aruco(frame, aruco:arucoDetection, 
                 show_contour=True, show_id=True,
                 show_center=True):
    if show_contour:
        cv2.polylines(
                    frame, [aruco.corners.astype(np.int32)], True, (0, 0, 255), 4, cv2.LINE_AA
                )
    if show_id:
        cv2.putText(frame, f"id: {aruco.id}", aruco.top_right, 
                    cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2, cv2.LINE_AA)
    
    if show_center:
        cv2.circle(frame, aruco.center, radius=5, color=(0, 0, 255), thickness=2)

    return frame
    
def estimatePoseSingleMarkers(corners, marker_size, mtx, distortion):
    '''
    This will estimate the rvec and tvec for each of the marker corners detected by:
       corners, ids, rejectedImgPoints = detector.detectMarkers(image)
    corners - is an array of detected corners for each detected marker in the image
    marker_size - is the size of the detected markers
    mtx - is the camera matrix
    distortion - is the camera distortion matrix
    RETURN list of rvecs, tvecs, and trash (so that it corresponds to the old estimatePoseSingleMarkers())
    '''
    marker_points = np.array([[-marker_size / 2, marker_size / 2, 0],
                              [marker_size / 2, marker_size / 2, 0],
                              [marker_size / 2, -marker_size / 2, 0],
                              [-marker_size / 2, -marker_size / 2, 0]], dtype=np.float32)
    trash = []
    rvecs = []
    tvecs = []
    for c in corners:
        nada, R, t = cv2.solvePnP(marker_points, c, mtx, distortion, False, cv2.SOLVEPNP_IPPE_SQUARE)
        rvecs.append(R)
        tvecs.append(t)
        trash.append(nada)
    return rvecs, tvecs, trash


def extract_arucos(frame, aruco_detector:aruco.ArucoDetector)->list:
    
    # turning the frame to grayscale-only (for efficiency)
    marker_corners, marker_IDs, reject = aruco_detector.detectMarkers(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
    results = []
    if marker_corners:
        for ids, corners in zip(marker_IDs, marker_corners):
            results.append(arucoDetection(ids[0], corners))

    return results


if __name__ == '__main__':
    main()