
import numpy as np


class Vertex:
    ''' Defines a vertex, point, or vector '''
    
    def __init__(self, x, y, z):
        
        if type(x) is np.ndarray :
            self.vector = x
        else :
            self.vector = np.array([x,y,z])
        

        
        
         
            
