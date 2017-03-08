

class Sketch :
    
    def __init__(self, name, plane):
        self.setName(name)
        self.setPlane(plane)
        self.vertices = []
        self.edges = []
        self.paths = []
        self.profiles = []
        
        
    def setName(self, name):
        self.name = name
        
    def setPlane(self, plane):
        self.plane = plane
        
    def addVertex(self, vertex):
        
        found = False
        
        for tempVertex in self.vertices:
            if vertex == tempVertex :
                found = True
                vertex = tempVertex
                break
            
        if not found :
            self.vertices.append(vertex)
            
        return vertex
        
        
        
    def addEdge(self, edge):
        
        found = False
        
        for tempEdge in self.edges :
            if tempEdge == edge :
                found = True
                edge = tempEdge
                break
            
        if not found :
            self.edges.append(edge)
        
        return edge
        
    def findPaths(self):
        pass
    
    def findProfiles(self):
        pass