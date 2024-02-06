import numpy as np
import cv2


def extract_arucos(frame, aruco_detector:cv2.aruco.ArucoDetector)->list:
    # turning the frame to grayscale-only (for efficiency)
    marker_corners, marker_IDs, reject = aruco_detector.detectMarkers(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
    results = []
    if marker_corners:
        for ids, corners in zip(marker_IDs, marker_corners):
            results.append(ArucoDetection(ids[0], corners))

    return results


class ArucoDetection:
    def __init__(self, id:int, corners:np.ndarray) -> None:
        assert corners.shape == (1, 4, 2)

        self.id = id
        self.corners = corners.copy()

        #reverting top/bottom to match tag's orientation with 3D models
        self.corners[:, :2, :] = corners[:, 2:, :].copy()
        self.corners[:, 2:, :] = corners[:, :2, :].copy()

        corners = corners.reshape(4, 2)
        self.center = np.average(corners, 0).astype(int)

        corners = corners.astype(int)
        self.top_right = corners[0].ravel()
        self.top_left = corners[1].ravel()
        self.bottom_right = corners[2].ravel()
        self.bottom_left = corners[3].ravel()