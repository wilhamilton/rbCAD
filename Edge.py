
import numpy as np

class Edge(object) :
    
    def __init__(self, v1, v2):
        self.v1 = v1
        self.v2 = v2
        
    def setNextEdge(self, nextEdge):
        self.next = nextEdge
        
    def setPreviousEdge(self, previousEdge):
        self.previousEdge = previousEdge
        
    def setPartnerEdge(self, partnerEdge):
        self.partnerEdge = partnerEdge
        
    def getPoint(self, t):
        '''override'''
        return np.array([0,0,0])
    
    def onEdge(self, point):
        return False
    
    def __str__(self):
        return "v1: " + np.array_str(self.v1) + "\nv2: " + np.array_str(self.v2) + "\n"
    
    def tostring(self):
        return self.__str__()