

class Feature :
    
    def __init__(self):
        '''build a feature'''
        self.vertices = []
        self.edges = []
        self.faces = []
    
    def setStartProfile(self, profile):
        self.startProfile = profile
        
    def setEndProfile(self, profile):
        self.endProfile = profile
        
    def setPath(self, path):
        self.path = path
    
    def generate(self):
        