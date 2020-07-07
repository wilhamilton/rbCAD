

from OCC.Core.gp import gp_Pnt
from OCC.Core.GC import GC_MakeArcOfCircle, GC_MakeSegment
from OCC.Core.GeomAPI import GeomAPI_PointsToBSpline
from OCC.Core.TColgp import TColgp_Array1OfPnt
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeWire
from OCC.Core.BRepOffsetAPI import BRepOffsetAPI_MakePipe

from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeSphere, BRepPrimAPI_MakeBox


display_wires = []
display_shapes = []

def make_wire_from_points(list_of_points):
    points = []
    segments = []
    edges = []
    
    wire_builder = BRepBuilderAPI_MakeWire()
    
    #make points from list of points
    for temp_point in list_of_points:
        # print(temp_point)
        points.append(gp_Pnt(temp_point[0], temp_point[1], temp_point[2]))
        
    #make segments from points
    for i in range(len(points)):
        #print(str(i) + ": making segment between")
        # print(len(points))
        if(i == len(points)-1):
            segments.append(GC_MakeSegment(points[i], points[0]))
        else:
            segments.append(GC_MakeSegment(points[i], points[i+1]))

    #make edges from segments
    for temp_segment in segments:
        temp_edge = BRepBuilderAPI_MakeEdge(temp_segment.Value())
        edges.append(temp_edge)
        wire_builder.Add(temp_edge.Edge())
    
    return wire_builder, edges, segments, points

class Sketch:
    def __init__(self, name):
        self.name = name
        self.points = []
        self.segments = []
        self.edges = []
        self.wires = []
        self.meta = {}

    def add_wire(self, wire):
        self.wires.append(wire)

    def move_sketch(self, transform):
        print('Move the sketch by transform')

    def add_meta(self, key, value):
        self.meta[key] = value

    def add_point(self, point):
        if (type(point) == list):
            point = gp_Pnt(point[0], point[1], point[2])

        self.points.append(point)

    def add_points(self, points):
        for pnt in points:
            self.add_point(pnt)

    def print_points(self):
        for pnt in self.points:
            print(pnt)

class Feature:
    def __init__(self, name):
        self.name = name
        self.sketch = None

    def add_sketch(self, sketch):
        self.sketch = sketch

track_bed_width = 16
track_bed_top_width = 11
track_bed_height = 5

tb_bottom_left = gp_Pnt(-track_bed_width/2, 0, 0)
tb_bottom_right = gp_Pnt(track_bed_width/2, 0, 0)

a = [-track_bed_width/2, 0, 0]
b = [track_bed_width/2, 0, 0]
c = [track_bed_top_width/2, 0, track_bed_height]
d = [-track_bed_top_width/2, 0, track_bed_height]

tb_sketch = Sketch("tb")

tb_sketch.add_points([a, b, c, d])

tb_sketch.print_points()

wire1, edges, segments, points = make_wire_from_points([a, b, c, d])


# display.DisplayShape(wire1.Wire(), update=True)
display_wires.append(wire1.Wire())