

from OCC.Core.gp import gp_Pnt, gp_Dir, gp_Vec, gp_Ax1, gp_Ax2, gp_Ax3, gp_Trsf
from OCC.Core.GC import GC_MakeArcOfCircle, GC_MakeSegment, GC_MakeArcOfEllipse, GC_MakeCircle, GC_MakeEllipse
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


display_wires = []
display_shapes = []

sketches = []
features = []

# def make_wire_from_points(list_of_points):
    # points = []
    # segments = []
    # edges = []
    
    # wire_builder = BRepBuilderAPI_MakeWire()
    
    # #make points from list of points
    # for temp_point in list_of_points:
        # # print(temp_point)
        # points.append(gp_Pnt(temp_point[0], temp_point[1], temp_point[2]))
        
    # #make segments from points
    # for i in range(len(points)):
        # #print(str(i) + ": making segment between")
        # # print(len(points))
        # if(i == len(points)-1):
            # segments.append(GC_MakeSegment(points[i], points[0]))
        # else:
            # segments.append(GC_MakeSegment(points[i], points[i+1]))

    # #make edges from segments
    # for temp_segment in segments:
        # temp_edge = BRepBuilderAPI_MakeEdge(temp_segment.Value())
        # edges.append(temp_edge)
        # wire_builder.Add(temp_edge.Edge())
    
    # return wire_builder, edges, segments, points
    
    
def rbcad_init(backend="occ"):
    '''Set all of the functions to be used based on the backends.'''
    if backend is "occ":
        SketchEntity = SketchEntity_OCC
        Sketch = Sketch_OCC
        Feature = Feature_OCC
    else:
        return False, False, False
        '''
        SketchEntity = SketchEntity_openSCAD
        Sketch = Sketch_openSCAD
        Feature = Feature_openSCAD
        '''

    return Feature, Sketch, SketchEntity



class SketchEntity_OCC:
    ''' SketchEntity - an individual component (segment, arc, etc.) that can exist in a sketch and be used to produce a path or loop for making features.
        
        Each entity type is nominally input as a set of 2D points (or scalars mapped onto a vector).
        
        Entity Type         point[0]    point[1]    point[2]    point[3]    point[4]    point[5]
        segment             start       end
        arc                 start       end         point on arc
        arc                 center      radius      start       end
        elliptical_arc      center      s1          s2          start       end
        circle              center      radius
        ellipse             center      s1          s2
    
    '''
    
    def __init__(self, points, type='segment', is_2d=True, name=None):
        ''' Create a sketch entity.  There are different types of sketch entity that can exist: segment, arc, elliptical arc, circle, and ellipse.
            When creating the entity the option to enter it as 2D (and let the sketch that contains it handle where it is in 3D space).
            By default, the sketch entity is "2D" and exists on the plane defined by the parent sketch.  
            
            For some entity types, the one or more of the points is used to store a scalar value.  These scalar values are always referred to from the points_2d array.
        '''

        self.points_2d = points
        self.type = type
        self.is_2d = is_2d
        self.name = name
        
        self.coordinate_system = None
        
        
        if is_2d is True:
            self.points_3d = []
        else:
            self.points_3d = points
        
    def build_entity(self, transform = None):
        ''' Build a sketch entity for a sketch.  
            Converts from a 2D representation to a true 3D representation.
        '''
        if transform is None and self.is_2d is True:
            return False
        else:
            self.transform = transform
            self.transform_points(transform)

        build_fuction = self.entity_build_switcher(self.type)
        return build_fuction()
            
            
    def transform_points(self, coordinate_system=None):
        ''' Converter all points of the entity from their 2D representation to a 3D represenation by applying a transform.
            The transform is stored at the gp_Ax3 object (which can be used for generating axis for circles/ellipses/arcs) and is then converted to the gp_Trsf object.
        
            https://dev.opencascade.org/doc/refman/html/classgp___ax3.html
            https://dev.opencascade.org/doc/refman/html/classgp___trsf.html
        '''
        if coordinate_system is not None:
            self.coordinate_system = coordinate_system
            
        if self.is_2d is True:
            # we need to convert 2d points to 3d and then move
            self.build_points_3d_from_2d()
            
        transform_object = gp_Trsf()
        transform_object.SetTransformation(self.coordinate_system)
            
        for point in self.points_3d:
            #do transform on point by point basis
            point.Transform(transform_object)
            
    def build_points_3d_from_2d(self, points_list=None):
        ''' Converts all of the 2D points for the sketch entity (x, y) into a 3D point (x, y, z).
            For entities that don't use all of their points (some points are repurposed for scalar values,
            a list of points to be converted can be used.
        '''
        
        self.points_3d = []
        
        if points_list is None:
            points_list = self.points_2d
            
        for point in points_list:
            self.points_3d.append(gp_Pnt(point[0], point[1], 0))
            
    def entity_build_switcher(self, x):
        ''' Select the correct build function based on entity type.
        '''
        return {
            'segment': self.build_segment,
            'arc': self.build_arc,
            'elliptical_arc': self.build_elliptical_arc,
            'circle': self.build_circle,
            'ellipse': self.build_ellipse
        }.get(x, self.build_segment)
        
    def build_segment(self):
        ''' Build a segment between two points.
        
            https://dev.opencascade.org/doc/refman/html/class_g_c___make_segment.html
        '''
        return GC_MakeSegment(self.points_3d[0], self.points_3d[1])
        
    def build_arc(self):
        # https://dev.opencascade.org/doc/refman/html/class_g_c___make_arc_of_circle.html
        
        if len(self.points_2d) > 3:
            # build arc by building circle first
            temp_circle = GC_MakeCircle(self.points_3d[0], self.points_2d[1][0])
            
            return GC_MakeArcOfCircle(temp_circle, self.points_3d[2], self.points_3d[3])
        else:
            # build an arc by using 3 points
            
            return GC_MakeArcOfCircle(self.points_3d[0], self.points_3d[1], self.points_3d[2])
        
    
    def build_elliptical_arc(self):
        ''' Build an elliptical arc.
            Arc is defined by the ellipse and the 2 points on the ellipse that are the endpoints of the arc.
            
            https://dev.opencascade.org/doc/refman/html/class_g_c___make_arc_of_ellipse.html
        '''
        
        temp_ellipse = self.build_ellipse()
        
        return GC_MakeArcOfEllipse(temp_ellipse, self.points_3d[3], self.points_3d[4], True)
    
    
    def build_circle(self):
        # the points used to build a circle, the first point is the center of circle, second point the first value is used for circle radius
        return GC_MakeCircle(self.points_3d[0], self.points_2d[1][0])
    
    def build_ellipse(self):
        ''' Build an ellipse from the points provided.  First we need to build the appropriate axis for the ellipse and then actually build the ellipse.
        
            ellipse center :    points_3d[0]
            ellipse s1 :        points_3d[1]
            ellipse s2:         points_3d[2]
            
            the major and minor axis are stored as a 2d directino vector and its magnitude is the radius 
            
            https://dev.opencascade.org/doc/refman/html/class_g_c___make_ellipse.html
            https://dev.opencascade.org/doc/refman/html/classgp___ax2.html
        '''
        
        
        return GC_MakeEllipse(self.points_3d[1], self.points_3d[2], self.points_3d[0])
        
        
        

class Sketch_OCC:
    '''Sketch - Store all items related to making paths or profiles that can then be used to create a 3D shape.

    Can be used to store points, edges, etc. and contains methods to convert them into paths.  Methods to transform all sketch items as a group are also implemented.

    Mostly, a sketch is just a handy container. 
    
    Goal of a sketch it to build a OpenCASCADE Wire.  The wire can then be used as the profile for a face for an extrude, revolve, or sweep (eventually loft). or as the path
    for a sweep operation.
    
    The Wire itself is made up of Edges.  Edges can be built from any BoundedCurve (Bezier, BSPline, TrimmedCurve (Segment, Arc)) or conic (circle, ellipse)
    
    see: https://dev.opencascade.org/doc/refman/html/package_gc.html for base sketch funciton types of 3d components
    '''

    def __init__(self, name, is_2d=False, coordinate_system=None):
        '''Create a new empty sketch.'''
        self.name = name
        # self.points = []
        self.entities = []
        self.edges = []
        self.wires = []
        self.meta = {}
        
        self.is_2d = is_2d
        
        if coordinate_system is None:
            # build a transform that is the origin (centered at 0,0,0, normal is z-axis, major axis is x-axis
            plane_origin = gp_Pnt(0, 0, 0)
            plane_normal = gp_Dir(0, 0, 1)
            plane_major_axis = gp_Dir(1, 0, 0)
            
            coordinate_system = gp_Ax3(gp_Ax2(plane_origin, plane_normal, plane_major_axis))
            # plane_transform = gp_Trsf()
            # plane_transform.SetTransformation(plane_transform_coordinate_system)
            
        self.coordinate_system = coordinate_system
        
        
        # self.points_2d = []
        # self.2d_segments = []

    # def add_wire(self, wire):
        # '''Adds a wire to the wires list.'''
        # self.wires.append(wire)

    def move_sketch(self, translation, end_point = None):
        print('Move the sketch by translation')
        

        if type(translation) is int or type(translation) is float:
            distance_to_translate = translation
            translation = gp_Trsf()
            
            translation.SetTranslation(gp_Vec(0, 0, distance_to_translate))
        elif end_point is not None and isinstance(translation, gp_Pnt):
            start_point = translation
            translation = gp_Trsf()
            translation.SetTranslation(start_point, end_point)
        elif isinstance(translation, gp_Vec):
            translation_vector = translation
            translation = gp_Trsf()
            translation.SetTranslation(translation_vector)
        
        self.coordinate_system.Transform(translation)
        

    def rotate_sketch(self, rotation, angle = None):
        print('rotate the sketch')

        if angle is None:
            print('Using provided rotation matrix')
        else:
            print('Using provided axis and angle for rotation')


    def add_meta(self, key, value):
        self.meta[key] = value

    # def add_point(self, point):
        # if (type(point) == list):
            # point = gp_Pnt(point[0], point[1], point[2])

        # self.points.append(point)

    # def add_points(self, points):
        # for pnt in points:
            # self.add_point(pnt)

    # def print_points(self):
        # for pnt in self.points:
            # print(pnt.Coord())

    def make_segments_from_points(self, points):
        for i in range(len(points)):
            # #print(str(i) + ": making segment between")
            # # print(len(points))
            if(i == len(points)-1):
                self.entities.append(SketchEntity_OCC([points[i], points[0]]))
            else:
                self.entities.append(SketchEntity_OCC([points[i], points[i+1]]))
                # self.entities.append(GC_MakeSegment(self.points[i], self.points[i+1]))

    # def make_edges_from_segments(self):
        # for segment in self.entities:
            # new_edge = BRepBuilderAPI_MakeEdge(segment.Value())
            # self.edges.append(new_edge)

    def make_wire_from_edges(self, edge_list=None):
        wire_builder = BRepBuilderAPI_MakeWire()
        
        if edge_list is None:
            for edge in self.edges:
                wire_builder.Add(edge.Edge())
        else:
            for edge in edge_list:
                wire_builder.Add(edge.Edge())

        self.wires.append(wire_builder)

    # def make_wire_from_points(self, points):
        # self.add_points(points)
        # self.make_segments_from_points()
        # self.make_edges_from_segments()
        # self.make_wire_from_edges()
    
    def add_entity(self, sketch_entity):
        self.entities.append(sketch_entity)
        
    def make_edges_from_entities(self, entity_list=None):
        ''' Build edges from sketch entities.
        
            https://dev.opencascade.org/doc/refman/html/class_b_rep_builder_a_p_i___make_edge.html
            https://dev.opencascade.org/doc/refman/html/class_geom___curve.html
            
        '''
        if entity_list is None:
            entity_list = self.entities

        for entity in entity_list:
            
            built_entity = entity.build_entity(self.coordinate_system)
            
            new_edge = BRepBuilderAPI_MakeEdge(built_entity.Value())
            self.edges.append(new_edge)
            

class Feature_OCC:
    def __init__(self, name):
        self.name = name
        self.profile_sketch = None
        self.profile_face = None
        self.solid = None
        self.color = None
        
        self.path_sketch = None

    def add_profile_sketch(self, sketch):
        self.profile_sketch = sketch
        # self.profile_face = BRepBuilderAPI_MakeFace(self.profile_sketch.wires[0].Wire())
        
    def build_face(self, wire_builder_list=None):
        ''' Build a face from all of the wires in a sketch. 
        
            The first wire in the wire list is the outer profile of the face, any additional wires are holes in the face.
        
            https://dev.opencascade.org/doc/refman/html/class_b_rep_builder_a_p_i___make_face.html
        '''
        
        if wire_builder_list is None:
            wire_builder_list = self.profile_sketch.wires

        profile_wire_builder = wire_builder_list.pop(0)
        print(profile_wire_builder)
        self.profile_face = BRepBuilderAPI_MakeFace(profile_wire_builder.Wire())
        
        for hole_wire_builder in wire_builder_list:
            self.profile_face.Add(hole_wire_builder.Wire())
        
    def extrude_profile(self, extrude_vector):
        if type(extrude_vector) is int or type(extrude_vector) is float:
            # get the normal axis for the face sketch and use that for the direction
            sketch_normal = self.profile_sketch.coordinate_system.Direction()
            vector = gp_Vec(sketch_normal)
            vector.Scale(extrude_vector)
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

    # def sweep_profile(self, path_sketch):

class Part:

    def __init__(self, name):
        self.features = []

    def add_feature(self, feature):
        self.features.append(feature)
        
Feature, Sketch, SketchEntity = rbcad_init("occ")

track_bed_width = 16
track_bed_top_width = 11
track_bed_height = 5

test_sketch = Sketch("test sketch", is_2d = True)

a = [-track_bed_width/2, 0]
b = [track_bed_width/2, 0]
c = [track_bed_top_width/2, track_bed_height]
d = [-track_bed_top_width/2, track_bed_height]

test_sketch.make_segments_from_points([a, b, c, d])
test_sketch.make_edges_from_entities()
test_sketch.make_wire_from_edges()

test_feature = Feature('track')
test_feature.add_profile_sketch(test_sketch)
test_feature.build_face()
test_feature.extrude_profile(10)

'''
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
# wire1, edges, seg

# display.DisplayShape(track.solid.Shape(), update=True)
# display_wires.append(tb_sketch.wires[0])
# display_shapes.append(track.solid.Shape())
'''
sketches.append(test_sketch)
#features.append(track)
#features.append(tr2)
features.append(test_feature)

# # initialize the STEP exporter
# step_writer = STEPControl_Writer()
# Interface_Static_SetCVal("write.step.schema", "AP203")

# # transfer shapes and write file
# step_writer.Transfer(tr3.solid.Shape(), STEPControl_AsIs)
# status = step_writer.Write("output.stp")

# if status != IFSelect_RetDone:
# 	raise AssertionError("load failed")



