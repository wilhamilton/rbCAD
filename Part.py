from CoordinateSystem import CoordinateSystem

class Part :
    
    def __init__(self):
        self.name = ''
        self.coordinateSystem = CoordinateSystem()
        self.vertices = []
        self.edges = []
        self.sketches = []
        self.features = []
        self.featureRelationships = []
        self.faces = []
        
    def setName(self, name):
        self.name = name
        
        
    def rebuild(self):
        pass
    
    def addFeature(self, feature):
        self.features.append(feature)
        
    def addFeatureRelationship(self, featureRelationship):
        self.featureRelationships.append(featureRelationship)
        
    
    