

from OCC.Core.gp import gp_Pnt, gp_Dir, gp_Vec, gp_Ax1
from OCC.Core.GC import GC_MakeArcOfCircle, GC_MakeSegment
from OCC.Core.GeomAPI import GeomAPI_PointsToBSpline
from OCC.Core.TColgp import TColgp_Array1OfPnt
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeWire, BRepBuilderAPI_MakeFace
from OCC.Core.BRepOffsetAPI import BRepOffsetAPI_MakePipe

from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeSphere, BRepPrimAPI_MakeBox, BRepPrimAPI_MakePrism, BRepPrimAPI_MakeRevol
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Fuse, BRepAlgoAPI_Common, BRepAlgoAPI_Cut
from OCC.Core.BOPAlgo import BOPAlgo_MakeConnected

from OCC.Display.OCCViewer import rgb_color

from OCC.Core.STEPControl import STEPControl_Writer, STEPControl_AsIs
from OCC.Core.Interface import Interface_Static_SetCVal
from OCC.Core.IFSelect import IFSelect_RetDone

from OCC.Core.ShapeUpgrade import ShapeUpgrade_UnifySameDomain


display_wires = []
display_shapes = []

sketches = []
features = []

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
    '''Sketch - Store all items related to making paths or profiles that can then be used to create a 3D shape.

    Can be used to store points, edges, etc. and contains methods to convert them into paths.  Methods to transform all sketch items as a group are also implemented.

    Mostly, a sketch is just a handy container. '''

    def __init__(self, name):
        '''Create a new empty sketch.'''
        self.name = name
        self.points = []
        self.segments = []
        self.edges = []
        self.wires = []
        self.meta = {}

    def add_wire(self, wire):
        '''Adds a wire to the wires list.'''
        self.wires.append(wire)

    def move_sketch(self, transform, distance = None):
        print('Move the sketch by transform')

        if distance is None:
            print('Using provided transformation matrix')
        else:
            print('Using provided axis and distance for move')

    def rotate_sketch(self, rotation, angle = None):
        print('rotate the sketch')

        if angle is None:
            print('Using provided rotation matrix')
        else:
            print('Using provided axis and angle for rotation')


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
            print(pnt.Coord())

    def make_segments_from_points(self):
        for i in range(len(self.points)):
            #print(str(i) + ": making segment between")
            # print(len(points))
            if(i == len(self.points)-1):
                self.segments.append(GC_MakeSegment(self.points[i], self.points[0]))
            else:
                self.segments.append(GC_MakeSegment(self.points[i], self.points[i+1]))

    def make_edges_from_segments(self):
        for segment in self.segments:
            new_edge = BRepBuilderAPI_MakeEdge(segment.Value())
            self.edges.append(new_edge)

    def make_wire_from_edges(self):
        wire_builder = BRepBuilderAPI_MakeWire()
        
        for edge in self.edges:
            wire_builder.Add(edge.Edge())

        self.wires.append(wire_builder)

    def make_wire_from_points(self, points):
        self.add_points(points)
        self.make_segments_from_points()
        self.make_edges_from_segments()
        self.make_wire_from_edges()

class Feature:
    def __init__(self, name):
        self.name = name
        self.profile_sketch = None
        self.profile_face = None
        self.solid = None
        self.color = None

    def add_profile_sketch(self, sketch):
        self.profile_sketch = sketch
        self.profile_face = BRepBuilderAPI_MakeFace(self.profile_sketch.wires[0].Wire())

    def extrude_profile(self, extrude_vector):
        if (type(extrude_vector) is list):
            # vector = gp_Dir(extrude_vector)
            vector = gp_Vec(extrude_vector[0], extrude_vector[1], extrude_vector[2])
            print(vector.Coord())
        
        self.solid = BRepPrimAPI_MakePrism(self.profile_face.Face(), vector)
        print(self.solid)

    def revolve_profile(self, revolve_axis, angle = 360):
        self.revolve_axis = revolve_axis
        self.revolve_angle = 3.14159*2

        print(self.revolve_axis)
        print(self.revolve_angle)

        self.solid  = BRepPrimAPI_MakeRevol(self.profile_face.Face(), self.revolve_axis, self.revolve_angle, False)

    def combine(self, featureA, featureB):
        print('combining A and B')
        self.solid = BRepAlgoAPI_Fuse(featureA.solid.Shape(), featureB.solid.Shape())
        shape_runner = BOPAlgo_MakeConnected()
        shape_runner.AddArgument(self.solid.Shape())
        shape_runner.Perform()
    
    def union(self, featureA, featureB):
        print('generating union of A and B')
        self.solid = BRepAlgoAPI_Common(featureA.solid.Shape(), featureB.solid.Shape())

    def subtract(self, featureA, featureB):
        print('subtract B from A')
        self.solid = BRepAlgoAPI_Cut(featureA.solid.Shape(), featureB.solid.Shape())

    def set_color(self, color):
        self.color = color

    def merge_self(self):
        '''merge extra/overlapping faces and edges due to boolean operations.
           see https://tracker.dev.opencascade.org/view.php?id=26409 for more information
        '''
        temp_su = ShapeUpgrade_UnifySameDomain(self.solid.Shape())
        temp_su.Build()
        self.solid = temp_su


    # def sweep_profile(self, path_sketch):

class Part:

    def __init__(self, name):
        self.features = []

    def add_feature(self, feature):
        self.features.append(feature)

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

tb_sketch.make_wire_from_points([a, b, c, d])

tb_sketch.print_points()

track = Feature('track')

track.add_profile_sketch(tb_sketch)
track.extrude_profile([0, 10, 0])

def build_axis(base_point, direction):
    base_point = gp_Pnt(base_point[0], base_point[1], base_point[2])
    direction = gp_Dir(direction[0], direction[1], direction[2])

    return gp_Ax1(base_point, direction)

rev_axis = build_axis([50, 0, 0], [0, 0, 1])
print(rev_axis)
# track.revolve_profile(rev_axis)
#track.set_color("BLUE")

def fake_rgb(red_value, green_value, blue_value):
    red_value = red_value / 255
    green_value = green_value / 255
    blue_value = blue_value / 255
    return rgb_color(red_value, green_value, blue_value)

#track.set_color(fake_rgb(20, 20, 20))


tb_sketch2 = Sketch("tb2")
a2 = [-track_bed_width/4, 0, 0]
b2 = [track_bed_width/4, 0, 0]
c2 = [track_bed_top_width/4, 0, 2*track_bed_height]
d2 = [-track_bed_top_width/4, 0, 2*track_bed_height]
tb_sketch2.make_wire_from_points([a2, b2, c2, d2])

tr2 = Feature("track2")
tr2.add_profile_sketch(tb_sketch2)
tr2.extrude_profile([0, 5, 0])


tr3 = Feature("combine")
tr3.combine(track, tr2)
tr3.merge_self()
# wire1, edges, seg

# display.DisplayShape(track.solid.Shape(), update=True)
# display_wires.append(tb_sketch.wires[0])
# display_shapes.append(track.solid.Shape())

#sketches.append(tb_sketch)
#features.append(track)
#features.append(tr2)
features.append(tr3)

# # initialize the STEP exporter
# step_writer = STEPControl_Writer()
# Interface_Static_SetCVal("write.step.schema", "AP214")

# # transfer shapes and write file
# step_writer.Transfer(tr3.solid.Shape(), STEPControl_AsIs)
# status = step_writer.Write("output.stp")

# if status != IFSelect_RetDone:
# 	raise AssertionError("load failed")
print("eof")