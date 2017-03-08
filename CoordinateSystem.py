
import numpy as np
from _overlapped import NULL

class CoordinateSystem :

    def __init__(self) :
        self.origin = np.array([0,0,0])
        self.xAxis = np.array([1,0,0])
        self.yAxis = np.array([0,1,0])
        self.zAxis = np.array([0,0,1])
        self.XY = NULL
        self.YZ = NULL
        self.XZ = NULL
        
    def rotate(self, rotationMatrix) :
        pass
        
          
    def translate(self, translationMatrix) :
        pass
    
    