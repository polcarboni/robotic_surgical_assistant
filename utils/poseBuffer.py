import numpy as np
import time
import json

class PoseBuffer:
    def __init__(self, memory = 1.0) -> None:
        """memory is the max amount of time data will be kept when not updated"""
        self.memory = memory
        self.last_data = None
        self.last_ts = None

    def set_new_data(self, position:np.ndarray, rotation:np.ndarray = None):
        assert not position is None

        position = position.flatten()
        if not rotation is None:
            rotation = rotation.flatten()
        data = position if rotation is None else np.concatenate((position, rotation), 0)

        # let's stringify data.
        self.last_data = json.dumps(data.tolist())
        self.last_ts = time.time()
        #print('new_data: ', self.last_data) 

    def poll_last_data(self)-> (bool, str):
        if self.last_data is None or time.time() - self.last_ts > self.memory:
            return False, ""
        return True, self.last_data
        