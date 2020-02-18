#!/usr/bin/env python

##Copyright 2009-2015 Thomas Paviot (tpaviot@gmail.com)
##
##This file is part of pythonOCC.
##
##pythonOCC is free software: you can redistribute it and/or modify
##it under the terms of the GNU Lesser General Public License as published by
##the Free Software Foundation, either version 3 of the License, or
##(at your option) any later version.
##
##pythonOCC is distributed in the hope that it will be useful,
##but WITHOUT ANY WARRANTY; without even the implied warranty of
##MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##GNU Lesser General Public License for more details.
##
##You should have received a copy of the GNU Lesser General Public License
##along with pythonOCC.  If not, see <http://www.gnu.org/licenses/>.



from __future__ import print_function

import logging
import os
import sys

# from OCC.Core.gp import gp_Pnt
# from OCC.Core.GC import GC_MakeArcOfCircle, GC_MakeSegment
# from OCC.Core.GeomAPI import GeomAPI_PointsToBSpline
# from OCC.Core.TColgp import TColgp_Array1OfPnt
# from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeWire
# from OCC.Core.BRepOffsetAPI import BRepOffsetAPI_MakePipe

# from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeSphere, BRepPrimAPI_MakeBox

from PyQt5.QtWidgets import QFileDialog

from Display.SimpleGui import init_display
display, start_display, add_menu, add_function_to_menu, win = init_display()

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


def pipe():
    
    track_bed_width = 16
    track_bed_top_width = 11
    track_bed_height = 5

    tb_bottom_left = gp_Pnt(-track_bed_width/2, 0, 0)
    tb_bottom_right = gp_Pnt(track_bed_width/2, 0, 0)
    
    a = [-track_bed_width/2, 0, 0]
    b = [track_bed_width/2, 0, 0]
    c = [track_bed_top_width/2, 0, track_bed_height]
    d = [-track_bed_top_width/2, 0, track_bed_height]
    
    wire1, edges, segments, points = make_wire_from_points([a, b, c, d])
    display.DisplayShape(wire1.Wire(), update=True)
    # print(wire1)
    
    # the bspline path, must be a wire
    array2 = TColgp_Array1OfPnt(1, 3)
    array2.SetValue(1, gp_Pnt(0, 0, 0))
    array2.SetValue(2, gp_Pnt(0, 1, 2))
    array2.SetValue(3, gp_Pnt(0, 2, 3))
    bspline2 = GeomAPI_PointsToBSpline(array2).Curve()
    path_edge = BRepBuilderAPI_MakeEdge(bspline2).Edge()
    path_wire = BRepBuilderAPI_MakeWire(path_edge).Wire()

    # the bspline profile. Profile mist be a wire
    array = TColgp_Array1OfPnt(1, 5)
    array.SetValue(1, gp_Pnt(0, 0, 0))
    array.SetValue(2, gp_Pnt(1, 2, 0))
    array.SetValue(3, gp_Pnt(2, 3, 0))
    array.SetValue(4, gp_Pnt(4, 3, 0))
    array.SetValue(5, gp_Pnt(5, 5, 0))
    bspline = GeomAPI_PointsToBSpline(array).Curve()
    profile_edge = BRepBuilderAPI_MakeEdge(bspline).Edge()

    # pipe
    pipe = BRepOffsetAPI_MakePipe(path_wire, profile_edge).Shape()

    # display.DisplayShape(profile_edge, update=False)
    #display.DisplayShape(path_wire, update=False)
    # display.DisplayShape(pipe, update=True)
    display.DisplayShape(wire1.Wire(), update=True)

if __name__ == '__main__':

    def sphere(event=None):
        display.DisplayShape(BRepPrimAPI_MakeSphere(100).Shape(), update=True)

    def cube(event=None):
        display.DisplayShape(BRepPrimAPI_MakeBox(1, 1, 1).Shape(), update=True)
        
    def clear_display(event=None):
        display.EraseAll()
        
    def display_sketches(event=None):
        pipe()
        # display.DisplayShape(wire1.Wire(), update=True)

    def Quit(event=None):
        sys.exit()

    def Load_File(event=None):
        file_name, _ = QFileDialog.getOpenFileName(win,"QFileDialog.getOpenFileName()", "","All Files (*);;Python Files (*.py)")
        if(file_name):
            print(file_name)
            win.set_run_file(file_name)
            win.execute_file()

    add_menu('File')
    add_function_to_menu('File', Load_File)
    # add_function_to_menu('primitives', cube)
    add_function_to_menu('File', Quit)
    # add_function_to_menu('primitives', clear_display)
    # add_function_to_menu('primitives', display_sketches)
    
    # win.hide()
    # win.build_gui_items()
    # win.show()


    print(display)
    # pipe()
    start_display()