from argparse import ArgumentParser
import ipaddress
import os
import cv2


class VideoStreamArgs(ArgumentParser):
    def __init__(self) -> None:
        super().__init__()
        self.add_argument("--source", type=str, required=True, help="Source of the video. It can be an IP, a path to a device, an index.")
        self.add_argument("--port", type=int, default=8080, help="In case of source from IP, you can set here the port. Default to 8080.")
        
    
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



def is_ipv4(string):
    try:
        ipaddress.IPv4Network(string)
        return True
    except ValueError:
        return False
