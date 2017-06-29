
import numpy as np


class Plane :
    
    def __init__(self, point = None, normal=None):
        if point is None :
            point = np.array([0,0,0])
        
        self.setPoint(point)
        
        if normal is None :
            normal = np.array([1,0,0])
            
        self.setNormal(normal)
        
    def setPoint(self, point):
        self.point = point
        
    def setNormal(self, normal):
        self.normal = normal
        
    def contains(self, point):
        ''' 
        calculates whether the point is on the plane or not 
            
            this calculation is (point-pointOnPlane) dot (normal)
            
        '''
        
        dotProduct = np.dot(point-self.point, self.normal)
        
        if dotProduct == 0 :
            return True
        else :
            return False
            
        
        