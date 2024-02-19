import numpy as np
import cv2 
import os

from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

MARGIN = 10  # pixels
FONT_SIZE = 1
FONT_THICKNESS = 1
HANDEDNESS_TEXT_COLOR = (88, 205, 54) # vibrant green

PALM_POINTS = [0, 1, 5, 17]

#tracking from https://developers.google.com/mediapipe/solutions/vision/hand_landmarker

class HandDetector:
    def __init__(self, model_asset_path='hand_landmarker.task') -> None:
        assert os.path.isfile(model_asset_path)
        base_options = python.BaseOptions(model_asset_path='hand_landmarker.task')
        options = vision.HandLandmarkerOptions(base_options=base_options,
                                            num_hands=1, min_hand_detection_confidence=0.25)
        self.detector = vision.HandLandmarker.create_from_options(options)
    
    def detect(self, frame):
       rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
       image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
       return self.detector.detect(image)


def get_hand_central_point(detection_result, image_w, image_h):
  #returns pixel coordinates of JUST the first hand detected. Return None if detection is empty.

  res = detection_result.hand_landmarks
  if len(res) == 0:
     return None
  points = res[0]

  avg_x = 0.0
  avg_y = 0.0
  for i in PALM_POINTS:
     avg_x += points[i].x
     avg_y += points[i].y

  avg_x = round(avg_x * image_w / len(PALM_POINTS))
  avg_y = round(avg_y * image_h / len(PALM_POINTS))
  return (avg_x, avg_y)


def draw_landmarks_on_image(image, detection_result):
  #image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
  hand_landmarks_list = detection_result.hand_landmarks
  handedness_list = detection_result.handedness
  annotated_image = np.copy(image)

  # Loop through the detected hands to visualize.
  for idx in range(len(hand_landmarks_list)):
    hand_landmarks = hand_landmarks_list[idx]
    handedness = handedness_list[idx]

    # Draw the hand landmarks.
    hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
    hand_landmarks_proto.landmark.extend([
      landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in hand_landmarks
    ])
    solutions.drawing_utils.draw_landmarks(
      annotated_image,
      hand_landmarks_proto,
      solutions.hands.HAND_CONNECTIONS,
      solutions.drawing_styles.get_default_hand_landmarks_style(),
      solutions.drawing_styles.get_default_hand_connections_style())

    # Get the top left corner of the detected hand's bounding box.
    height, width, _ = annotated_image.shape
    x_coordinates = [landmark.x for landmark in hand_landmarks]
    y_coordinates = [landmark.y for landmark in hand_landmarks]
    text_x = int(min(x_coordinates) * width)
    text_y = int(min(y_coordinates) * height) - MARGIN

    # Draw handedness (left or right hand) on the image.
    cv2.putText(annotated_image, f"{handedness[0].category_name}",
                (text_x, text_y), cv2.FONT_HERSHEY_DUPLEX,
                FONT_SIZE, HANDEDNESS_TEXT_COLOR, FONT_THICKNESS, cv2.LINE_AA)

  return annotated_image#cv2.cvtColor(annotated_image, cv2.COLOR_RGB2BGR)