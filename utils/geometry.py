import numpy as np
import cv2

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
    marker_points = np.array([[-marker_size / 2,marker_size / 2, 0],
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


def get_distance_from_stereo(p1, p2, k1, k2, delta_rot, delta_pos):
    """Using a stereocamera, infer the distance of a given point

    Args:
        p1 : pixel coordinates of the point as seen from camera1
        p2 : pixel coordinates of the point as seen from camera2
        k1 : camera1 intrinsics 
        k2 : camera2 intrinsics 
        delta_rot : rotation matrix from camera1 to camera2
        delta_pos : position different from camera1 to camera2

    Returns:
        float: distance of that point.
    """

    projMatr1 = k1 @ np.array([[1,0,0,0], [0,1,0,0], [0,0,1,0]])
    projMatr2 =  k2 @ np.concatenate((delta_rot, np.expand_dims(delta_pos, -1)), axis=1)

    # Coordinate 2D nel sistema di coordinate della prima camera
    projPoints1 = np.array([p1], dtype=np.float32)

    # Coordinate 2D nel sistema di coordinate della seconda camera
    projPoints2 = np.array([p2], dtype=np.float32)

    # Triangolazione
    points_3d_homogeneous = cv2.triangulatePoints(projMatr1, projMatr2, projPoints1.T, projPoints2.T)

    # Converti le coordinate omogenee in coordinate 3D (elimina la componente omogenea)
    points_3d = cv2.convertPointsFromHomogeneous(points_3d_homogeneous.T)

    # Stampa le coordinate 3D
    return (points_3d*-1).flatten()


def transform_point(frame_pos:np.ndarray, frame_rot:np.ndarray, point_pos:np.ndarray, point_rot=np.eye(3)):
    assert point_pos.shape == (1,3)
    assert point_rot.shape == (3,3)
    assert frame_pos.shape == (1,3)
    assert frame_rot.shape == (3,3)

    point_matrix = np.concatenate((point_rot, point_pos.T), 1)
    point_matrix = np.concatenate((point_matrix, np.asarray([[0., 0., 0., 1.]])), 0)

    transform_matrix = np.concatenate((frame_rot, frame_pos.T), 1)
    transform_matrix = np.concatenate((transform_matrix, np.asarray([[0., 0., 0., 1.]])), 0)

    result = np.matmul(transform_matrix, point_matrix)
    #print(result)
    new_pos = result[:3, -1]
    new_rot = result[:3, :3]

    return new_pos, new_rot

