
from Edge import Edge

class Segment(Edge):
    
    def __init__(self, v1, v2):
        super(Segment,self).__init__(v1,v2)
        self.slope = self.v2 - self.v1
        
    def getPoint(self, t):
        return self.v1 + t*self.slope
    
    def onEdge(self, point):
        temp = ( point - self.v1 ) / self.slope
        if temp[0] == temp[1] and temp[1] == temp[2] :
            return True
        else :
            return False
        
    
        