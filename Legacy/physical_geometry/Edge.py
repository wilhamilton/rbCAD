
import numpy as np

class Edge(object) :
    
    def __init__(self, v1, v2):
        self.set_start_vertex(v1)
        self.set_end_vertex(v2)
    
    
    def set_start_vertex(self,vertex):
        self.v1 = vertex
        
    def set_end_vertex(self, vertex):
        self.v2 = vertex
        
    def set_next_edge(self, nextEdge):
        self.next = nextEdge
        
    def set_previous_edge(self, previousEdge):
        self.previousEdge = previousEdge
        
    def set_partner_edge(self, partnerEdge):
        self.partnerEdge = partnerEdge
        
    def get_point(self, t):
        '''override'''
        return np.array([0,0,0])
    
    def on_edge(self, point):
        return False
    
    def __str__(self):
        return "v1: " + np.array_str(self.v1) + "\nv2: " + np.array_str(self.v2) + "\n"
    
    def tostring(self):
        return self.__str__()
