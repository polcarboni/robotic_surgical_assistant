from argparse import ArgumentParser
import ipaddress
import os
import cv2
import numpy as np

from .cameraParams import CameraParams


class VideoStreamArgs(ArgumentParser):
    def __init__(self, how_many_cameras=1) -> None:
        super().__init__()
        assert how_many_cameras > 0
        self.num_cameras = how_many_cameras
        if how_many_cameras == 1:
            self.add_argument("--source", type=str, required=True, help="Source of the video. It can be an IP, a path to a device, an index.")
            self.add_argument("--port", type=int, default=4747, help="In case of source from IP, you can set here the port. Default to 4747.")
        else:
            for i in range(how_many_cameras):
                self.add_argument(f"--source_{i}", type=str, required=True, help=f"Source of the video for camera {i}. It can be an IP, a path to a device, an index.")
                self.add_argument(f"--port_{i}", type=int, default=4747, help="In case of source from IP, you can set here the port. Default to 4747.")
        
    
    def parse_args(self):
        args = super().parse_args()

        self.data_sources_ = []

        if self.num_cameras == 1:
            video_src = [str(args.source)]
            ip_ports = [str(args.port)]
        else:
            video_src = [getattr(args, f'source_{i}') for i in range(self.num_cameras)]
            ip_ports = [getattr(args, f'port_{i}') for i in range(self.num_cameras)]

        for src, port in zip(video_src, ip_ports):
            if is_ipv4(src):
                source = f'http://{src}:{port}/video'
            else:
                try:
                    source = int(src)
                except:
                    source = src
            self.data_sources_.append(source)
        return args

    def open_video_stream(self) -> cv2.VideoCapture:
        streams = [cv2.VideoCapture(s) for s in self.data_sources_]
        if len(streams) == 1:
            return streams[0]
        
        return streams


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
