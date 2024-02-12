import numpy as np
import json
import typing



class IntrinsicParams:
    def __init__(self, fx:float, fy:float, cx:float, cy:float, skew:float=0) -> None:
        """
        Parameters
        ----------
        fx, fy:
            The focal distances
        cx, cy : 
            Center of projection in pixels            
        """
        self.fx = fx
        self.fy = fy
        self.cx = cx
        self.cy = cy
        self.skew = skew
        self.matrix = np.array([fx, skew , cx, 0, fy, cy, 0, 0, 1], dtype=np.float32).reshape((3,3))

    @classmethod
    def from_dict(cls, dict:dict):
        return cls(dict['fx'], dict['fy'], dict['cx'], dict['cy'], dict['skew'])


    def toDict(self):
        return {'fx':self.fx, 'fy':self.fy, 'cx':self.cx, 'cy':self.cy, 'skew':self.skew}

    def __str__(self):
        return "Intrinsic params:\n{}\n".format(self.matrix)

class DistortionParams:
    def __init__(self, distortion_vector:np.ndarray) -> None:
        """
        Parameters
        ----------
        [k1, k2, p1, p2, k3, k4, k5, k6, s1, s2, s3, s4, taux, tauy]

        where:
            + k1 -> k6      are radial coeffs
            + p1, p2        are tangential coeffs
            + s1 -> s4      are coeffs for the thin prism model
            + taux, tauy    are coeffs for the tilted model
        
        You can provide the firsts 4, 5, 8, 12 elements, or all of them (14)

        k1 [,k2 [, ..kn]]:
            The radial coefficients of the lens. Set all of them to 0 if you don't have distorsion.
            As note, k1 is typically negative for barrel distortions, while it is typically positive for pincushion distorsions.
        p1, p2 : 
            Tangential distortion of the lens (due to lens not perfectly parallel to image plane).
            Set to 0 if alignment is perfect.
        """
        assert distortion_vector.ndim == 1
        numel = distortion_vector.size
        assert numel in [4, 5, 8, 12, 14], "The given vector is incompatible, having {} elements.".format(numel)

        self.dist_vector = distortion_vector.astype(np.float32)

    @classmethod
    def from_dict(cls, dict:dict):
        try:
            dist_vector = np.asarray(dict['dist_vector'])
        except:
            # for backcompatibility
            dist_vector = np.array([dict['k1'], dict['k2'], dict['p1'], dict['p2'], dict['k3']])
        return cls(dist_vector)

    def toDict(self):
        return {'dist_vector':self.dist_vector.tolist()}

    def __str__(self):
        names = ['k1', 'k2', 'p1', 'p2', 'k3', 'k4', 'k5', 'k6', 's1', 's2', 's3', 's4', 'taux', 'tauy']
        res = "Distorsion params:\n"
        for idx, val in enumerate(self.dist_vector):
            res += "\t{}:\t{}\n".format(names[idx], val)
        return res
    

class CameraParams:
    def __init__(self, width:int, height:int,  intrinsics: IntrinsicParams, distortions:DistortionParams, name:str, others = {}) -> None:
        self.name = name
        self.width=width
        self.height=height
        self.intrinsics = intrinsics
        self.distortions = distortions
        self.others = others

    @classmethod
    def from_dict(cls, dict:dict):
        intrinsics = IntrinsicParams.from_dict(dict['intrinsics'])
        dist = DistortionParams.from_dict(dict['distortions'])
        try:
            others = dict['others']
        except: 
            others = {}

        return cls(dict['width'], dict['height'], intrinsics, dist, dict['name'], others)

    @classmethod
    def from_file(cls, json_file_path:str):
         # Opening JSON file
        with open(json_file_path, 'r') as openfile:
            # Reading from json file
            json_object = json.load(openfile)

        p = CameraParams.from_dict(json_object)
        print("Loaded data from {}:{}".format(json_file_path, str(p)))
        return p

    def toDict(self):
        dict = {'name':self.name, 'width':self.width, 'height':self.height, 'intrinsics':self.intrinsics.toDict() , 'distortions':self.distortions.toDict()}
        return dict

    def __str__(self):
        res = "\n-- Camera {} :--\n".format(self.name)
        res += "W x H: ({}, {})\n".format(self.width, self.height)
        res += str(self.intrinsics)
        res += str(self.distortions)
        return res
    

class ExtrinsicParams:
    def __init__(self, rot_matrix:np.ndarray, trans_vector:np.ndarray) -> None:

        assert rot_matrix.shape == (3,3)
        assert trans_vector.shape == (3,)

        self.rot_matrix = rot_matrix
        self.trans_vector = trans_vector

        rot_trans = np.hstack((rot_matrix, trans_vector.reshape(3,1)))
        self.matrix = np.vstack((rot_trans, np.array([0,0,0,1],dtype=np.float32)))

    @classmethod
    def from_dict(cls, dict:dict):
        return cls(np.asarray(dict['rot']), np.asarray(dict['trans']))

    def toDict(self):
        return {'rot':self.rot_matrix.tolist(), 'trans':self.trans_vector.tolist()}

    def __str__(self):
        return "\n-- Extrinsic params :--\n{}\n".format(self.matrix)
    

class StereoCamera:
    def __init__(self, camera_A:CameraParams, camera_B:CameraParams, extr_A_to_B:ExtrinsicParams) -> None:
        self.src = camera_A
        self.dst = camera_B
        self.extrinsics = extr_A_to_B

    @classmethod
    def from_dict(cls, dict:dict):
        src = CameraParams.from_dict(dict['src'])
        dst = CameraParams.from_dict(dict['dst'])
        return cls(src, dst, ExtrinsicParams.from_dict(dict['src_to_dst']))

    @classmethod
    def from_file(cls, json_file_path:str, verbose=False):
        # Opening JSON file
        with open(json_file_path, 'r') as openfile:
            # Reading from json file
            json_object = json.load(openfile)

        map = StereoCamera.from_dict(json_object)
        if verbose:
            print("Loaded stereoCamera data from {}:{}".format(json_file_path, str(map)))
        return map

    def toDict(self):
        return {'src':self.src.toDict(), 'dst':self.dst.toDict(), 'src_to_dst': self.extrinsics.toDict()}

    def __str__(self):
        res = "\StereoCamera Data from {} to {}:\n".format(self.src.name, self.dst.name)
        res += "-----------------------------------------"
        res += "\nSource:"
        res += str(self.src)
        res += "\nDestination:"
        res += str(self.dst)
        res += str(self.extrinsics)
        res += "-----------------------------------------\n\n"
        return res
    

if __name__ == '__main__':
     
    """
    intrinsics = IntrinsicParams(fx=587.4568, fy=592.4251, cx=337.0928, cy=224.3169)
    distortions = DistortionParams(np.asarray([-0.3651, 0.0492, 0.0008, -0.0014, 0.3062]))
    camera = CameraParams(640,480, intrinsics, distortions, "Pietro's_webcam")
    
    # Serializing json
    json_object = json.dumps(camera.toDict(), indent=4)
    # Writing to sample.json
    with open('pietro_webcam.json', "w") as outfile:
        outfile.write(json_object)
    """