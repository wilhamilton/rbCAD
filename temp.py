from rbCAD import rbcad_init, build_offset_axis, build_coordinate_system
from OCC.Core.gp import gp_Pnt, gp_Dir, gp_Vec, gp_Ax1, gp_Ax2, gp_Ax3, gp_Trsf, gp, gp_Circ
        
Feature, Sketch, SketchEntity = rbcad_init("occ")

sketches = []
features = []

track_bed_width = 16
track_bed_top_width = 11
track_bed_height = 8

test_sketch = Sketch("test sketch", is_2d = True)

a = [-track_bed_width/2, 0]
b = [track_bed_width/2, 0]
c = [track_bed_top_width/2, track_bed_height]
d = [-track_bed_top_width/2, track_bed_height]

e = [-4, 1]
f = [4, 1]
g = [4, 2]
h = [-4, 2]

e2 = [-4, 4]
f2 = [4, 4]
g2 = [4, 5]
h2 = [-4, 5]

test_sketch.make_segments_from_points([a, b, c, d])
test_sketch.make_edges_from_entities()
test_sketch.make_wire_from_edges()

# hole_entities = test_sketch.make_segments_from_points([e, f, g, h])
# hole_edges = test_sketch.make_edges_from_entities(hole_entities)
# test_sketch.make_wire_from_edges(hole_edges)

# hole_entities2 = test_sketch.make_segments_from_points([e2, f2, g2, h2])
# hole_edges2 = test_sketch.make_edges_from_entities(hole_entities2)
# test_sketch.make_wire_from_edges(hole_edges2)

test_feature = Feature('track')
test_feature.add_profile_sketch(test_sketch)
test_feature.build_face()
# test_feature.extrude_profile(2)
test_feature.revolve_profile(build_offset_axis("Y", [-20, 0, 0]), 90)

plane_origin2 = gp_Pnt(0, 10, 0)
plane_normal2 = gp.DY()#gp_Dir(0, 1, 0)
# plane_major_axis = gp_Dir(0, 1, 0)

# coordinate_system2 = gp_Ax3(gp_Ax2(plane_origin2, plane_normal2))

#coordinate_system2 = test_feature.end_face_coordinate_system

coordinate_system2 = build_coordinate_system(plane="ZX")



# print("coordinate system 2 location: ", point_to_string(coordinate_system2.Location()))

test_sketch2 = Sketch("second test sketch", is_2d = True, coordinate_system=coordinate_system2)

# m = [5, 10]
# n = [0, 10]
# o = [0, 0]
# p = [10, 0]
# q = [10, 5]
m = [0, 0]
n = [10, 0]
o = [20, 5]

r = [5, 5]

test_sketch2.make_segments_from_points([m, n, o])
test_sketch2.entities.pop()

# test_arc = SketchEntity([r, r, q, m], type="arc")
# test_sketch2.add_entity(test_arc)
test_sketch2.make_edges_from_entities()
test_sketch2.make_wire_from_edges()

# test_feature2 = Feature("test2")
# test_feature2.add_profile_sketch(test_sketch2)
# test_feature2.build_face()
# test_feature2.extrude_profile(20)

sketches.append(test_sketch)
sketches.append(test_sketch2)
#features.append(track)
#features.append(tr2)

# test_feature.sweep_profile(test_sketch2.wires[0])

features.append(test_feature)
# features.append(test_feature2)

# # initialize the STEP exporter
# step_writer = STEPControl_Writer()
# Interface_Static_SetCVal("write.step.schema", "AP203")

# # transfer shapes and write file
# step_writer.Transfer(tr3.solid.Shape(), STEPControl_AsIs)
# status = step_writer.Write("output.stp")

# if status != IFSelect_RetDone:
# 	raise AssertionError("load failed")



