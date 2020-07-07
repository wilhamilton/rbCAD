#!/usr/bin/env python

# Copyright 2009-2016 Thomas Paviot (tpaviot@gmail.com)
##
# This file is part of pythonOCC.
##
# pythonOCC is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
##
# pythonOCC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
##
# You should have received a copy of the GNU Lesser General Public License
# along with pythonOCC.  If not, see <http://www.gnu.org/licenses/>.

import logging
import os
import sys
import traceback

from OCC import VERSION
from Display.backend import load_backend, get_qt_modules
from Display.OCCViewer import OffscreenRenderer

# import any CAD related libraries here
from OCC.Core.gp import gp_Pnt
from OCC.Core.GC import GC_MakeArcOfCircle, GC_MakeSegment
from OCC.Core.GeomAPI import GeomAPI_PointsToBSpline
from OCC.Core.TColgp import TColgp_Array1OfPnt
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeWire
from OCC.Core.BRepOffsetAPI import BRepOffsetAPI_MakePipe

from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeSphere, BRepPrimAPI_MakeBox




log = logging.getLogger(__name__)


# https://stackoverflow.com/questions/28836078/how-to-get-the-line-number-of-an-error-from-exec-or-execfile-in-python
class InterpreterError(Exception): pass

def my_exec(cmd, globals=None, locals=None, description='source string'):
    try:
        exec(cmd, globals, locals)
    except SyntaxError as err:
        print('Syntax error in file.')
        error_class = err.__class__.__name__
        detail = err.args[0]
        line_number = err.lineno
        print("%s at line %d of %s: %s" % (error_class, line_number, description, detail))
    except Exception as err:
        print('Exception during file execution.')
        error_class = err.__class__.__name__
        detail = err.args[0]
        cl, exc, tb = sys.exc_info()
        line_number = traceback.extract_tb(tb)[-1][1]
        print("%s at line %d of %s: %s" % (error_class, line_number, description, detail))
    else:
        return
    raise InterpreterError("%s at line %d of %s: %s" % (error_class, line_number, description, detail))


def check_callable(_callable):
    if not callable(_callable):
        raise AssertionError("The function supplied is not callable")


def init_display(backend_str=None,
                 size=(1024, 768),
                 display_triedron=True,
                 background_gradient_color1=[206, 215, 222],
                 background_gradient_color2=[128, 128, 128]):
    """ This function loads and initialize a GUI using either wx, pyq4, pyqt5 or pyside.
    If ever the environment variable PYTHONOCC_OFFSCREEN_RENDERER, then the GUI is simply
    ignored and an offscreen renderer is returned.
    init_display returns 4 objects :
    * display : an instance of Viewer3d ;
    * start_display : a function (the GUI mainloop) ;
    * add_menu : a function that creates a menu in the GUI
    * add_function_to_menu : adds a menu option

    In case an offscreen renderer is returned, start_display and add_menu are ignored, i.e.
    an empty function is returned (named do_nothing). add_function_to_menu just execute the
    function taken as a paramter.

    Note : the offscreen renderer is used on the travis side.
    """
    print("rbCAD display")

    if os.getenv("PYTHONOCC_OFFSCREEN_RENDERER") == "1":
        # create the offscreen renderer
        offscreen_renderer = OffscreenRenderer()

        def do_nothing(*kargs, **kwargs):
            """ takes as many parameters as you want,
            ans does nothing
            """
            pass

        def call_function(s, func):
            """ A function that calls another function.
            Helpfull to bypass add_function_to_menu. s should be a string
            """
            check_callable(func)
            log.info("Execute %s :: %s menu fonction" % (s, func.__name__))
            func()
            log.info("done")

        # returns empty classes and functions
        return offscreen_renderer, do_nothing, do_nothing, call_function
        
    used_backend = load_backend(backend_str)
    log.info("GUI backend set to: %s", used_backend)

    # Qt based simple GUI
    if 'qt' in used_backend:
        from Display.qtDisplay import qtViewer3d
        QtCore, QtGui, QtWidgets, QtOpenGL = get_qt_modules()

        class MainWindow(QtWidgets.QMainWindow):

            def __init__(self, *args):
                QtWidgets.QMainWindow.__init__(self, *args)
                self.canva = qtViewer3d(self)
                self.setWindowTitle("pythonOCC-%s 3d viewer ('%s' backend)" % (VERSION, used_backend))
                self.setCentralWidget(self.canva)
                if sys.platform != 'darwin':
                    self.menu_bar = self.menuBar()
                else:
                    # create a parentless menubar
                    # see: http://stackoverflow.com/questions/11375176/qmenubar-and-qmenu-doesnt-show-in-mac-os-x?lq=1
                    # noticeable is that the menu ( alas ) is created in the
                    # topleft of the screen, just
                    # next to the apple icon
                    # still does ugly things like showing the "Python" menu in
                    # bold
                    self.menu_bar = QtWidgets.QMenuBar()
                self._menus = {}
                self._menu_methods = {}
                # place the window in the center of the screen, at half the
                # screen size
                self.centerOnScreen()
                self.run_file = None
                self.statusBar().showMessage("No File Loaded")
                # self.build_gui_items()

            def build_gui_items(self):
                print('build gui items')
                clear_button = QtWidgets.QPushButton('Clear Display', self)
                clear_button.setToolTip('Click to clear all items on the display.')
                clear_button.move(20, size[1] - clear_button.height() - 20)
                clear_button.clicked.connect(self.clear_button_click)

                run_file_button = QtWidgets.QPushButton('Run File', self)
                run_file_button.setToolTip('Load and run a file.')
                run_file_button.move(40+clear_button.width(), size[1] - clear_button.height() - 20)
                run_file_button.clicked.connect(self.run_file_button_click)

                view_reset_button = QtWidgets.QPushButton('Reset View', self)
                view_reset_button.setToolTip('Click to reset model view.')
                view_reset_button.move(run_file_button.x()+run_file_button.width()+20, size[1] - clear_button.height() - 20)
                view_reset_button.clicked.connect(self.view_reset_button_click)

            def clear_button_click(self):
                print('Clearing Screen')
                display.EraseAll()
                display.display_triedron()

            def run_file_button_click(self):
                print('load and run file')
                print(self.run_file)
                display.display_triedron()
                if(self.run_file is not None):
                    self.execute_file()

            def execute_file(self):

                # print(lcl_dict)
                try:
                    my_exec(open(self.run_file).read(), globals())

                    for temp_wire in display_wires:
                        display.DisplayShape(temp_wire, update=True)

                    for temp_shape in display_shapes:
                        print(temp_shape)
                        display.DisplayShape(temp_shape, update=True)
                except:
                    print('code failed')

                # print(lcl_dict)
                


            def view_reset_button_click(self):
                display.ResetView()
                display.FitAll()

            def set_run_file(self, file):
                self.run_file = file

            def centerOnScreen(self):
                '''Centers the window on the screen.'''
                resolution = QtWidgets.QApplication.desktop().screenGeometry()
                x = (resolution.width() - self.frameSize().width()) / 2
                y = (resolution.height() - self.frameSize().height()) / 2
                self.move(x, y)

            def add_menu(self, menu_name):
                _menu = self.menu_bar.addMenu("&" + menu_name)
                self._menus[menu_name] = _menu

            def add_function_to_menu(self, menu_name, _callable):
                check_callable(_callable)
                try:
                    _action = QtWidgets.QAction(_callable.__name__.replace('_', ' ').lower(), self)
                    # if not, the "exit" action is now shown...
                    _action.setMenuRole(QtWidgets.QAction.NoRole)
                    _action.triggered.connect(_callable)

                    self._menus[menu_name].addAction(_action)
                except KeyError:
                    raise ValueError('the menu item %s does not exist' % menu_name)
            
        # following couple of lines is a tweak to enable ipython --gui='qt'
        app = QtWidgets.QApplication.instance()  # checks if QApplication already exists
        if not app:  # create QApplication if it doesnt exist
            app = QtWidgets.QApplication(sys.argv)
        win = MainWindow()
        win.resize(size[0] -1, size[1] -1)
        # win.show()
        win.centerOnScreen()
        win.canva.InitDriver()
        win.resize(size[0], size[1])
        win.canva.qApp = app
        display = win.canva._display

        win.build_gui_items()

        win.show()

        def add_menu(*args, **kwargs):
            win.add_menu(*args, **kwargs)

        def add_function_to_menu(*args, **kwargs):
            win.add_function_to_menu(*args, **kwargs)

        def start_display():
            win.raise_()  # make the application float to the top
            app.exec_()

    if display_triedron:
        print("displaying triedron")
        display.display_triedron()

    if background_gradient_color1 and background_gradient_color2:
    # background gradient
        display.set_bg_gradient_color(background_gradient_color1, background_gradient_color2)

    return display, start_display, add_menu, add_function_to_menu, win


if __name__ == '__main__':
    display, start_display, add_menu, add_function_to_menu = init_display("qt-pyqt5")
    from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeSphere, BRepPrimAPI_MakeBox

    def sphere(event=None):
        display.DisplayShape(BRepPrimAPI_MakeSphere(100).Shape(), update=True)

    def cube(event=None):
        display.DisplayShape(BRepPrimAPI_MakeBox(1, 1, 1).Shape(), update=True)

    def quit(event=None):
        sys.exit()

    add_menu('primitives')
    add_function_to_menu('primitives', sphere)
    add_function_to_menu('primitives', cube)
    add_function_to_menu('primitives', quit)
    start_display()
