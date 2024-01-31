import numpy as np
import cv2

K1 = np.array([[1433.3, 0, 955.3],
               [0, 1430.7, 546.7],
               [0, 0, 1]])

K2 = np.array([[1376, 0, 956.7],
               [0, 1379.4, 545.3],
               [0, 0, 1]])

R = np.array([[1, 0, 0],
              [0, 1, 0],
              [0, 0, 1]])

T = np.array([[0.152], [0], [0]])
# x = -0.633 y = 0.133 z = 1.621

#def calcola_posizione_3d(P1, P2, K1, K2, R, T):
def calcola_posizione_3d(P1, P2):
    global K1, K2, R, T
    projMatr1 = K1 @ np.array([[1,0,0,0], [0,1,0,0], [0,0,1,0]])

    projMatr2 =  K2 @ np.concatenate((R, T), axis=1)

    # Coordinate 2D nel sistema di coordinate della prima camera
    projPoints1 = np.array([P1], dtype=np.float32)

    # Coordinate 2D nel sistema di coordinate della seconda camera
    projPoints2 = np.array([P2], dtype=np.float32)

    # Triangolazione
    points_3d_homogeneous = cv2.triangulatePoints(projMatr1, projMatr2, projPoints1.T, projPoints2.T)

    # Converti le coordinate omogenee in coordinate 3D (elimina la componente omogenea)
    points_3d = cv2.convertPointsFromHomogeneous(points_3d_homogeneous.T)

    # Stampa le coordinate 3D
    return points_3d*-1


