from argparse import ArgumentParser
import ipaddress
import os
import cv2
import numpy as np

from .cameraParams import CameraParams


class VideoStreamArgs(ArgumentParser):
    def __init__(self) -> None:
        super().__init__()
        self.add_argument("--source", type=str, required=True, help="Source of the video. It can be an IP, a path to a device, an index.")
        self.add_argument("--port", type=int, default=4747, help="In case of source from IP, you can set here the port. Default to 8080.")
        
    
    def parse_args(self):
        args = super().parse_args()

        video_src = str(args.source)

        if is_ipv4(video_src):
            ip_port = int(args.port)
            source = f'http://{video_src}:{ip_port}/video'
        else:
            try:
                source = int(video_src)
            except:
                source = video_src
        self.data_source_ = source
        return args

    def open_video_stream(self) -> cv2.VideoCapture:
        return cv2.VideoCapture(self.data_source_)


def pre_process_image(frame, camera:CameraParams):
    brightness_adj = 0
    saturation_adj = 0
    if 'brightness' in camera.others:
        brightness_adj = camera.others['brightness']
    if 'saturation' in camera.others:
        saturation_adj = camera.others['saturation']
    

    if saturation_adj != 0 or brightness_adj != 0:
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV).astype(np.int32)
        h, s, v = cv2.split(hsv)

        v += brightness_adj
        s += saturation_adj
        
        final_hsv = cv2.merge((h, s, v))
        #clamp and cast
        final_hsv[final_hsv > 255] = 255
        final_hsv[final_hsv < 0] = 0
        final_hsv = final_hsv.astype(np.uint8)
        frame = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)

        
    return frame



def is_ipv4(string):
    try:
        ipaddress.IPv4Network(string)
        return True
    except ValueError:
        return False
