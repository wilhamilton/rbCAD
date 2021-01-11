# rbCAD
B-REP CAD program built on top of the Open CASCADE kernal and Python OCC.

https://github.com/tpaviot/pythonocc
https://www.opencascade.com/


# Usage
The software, as of v0.1 is not much more than a few functions built on top of Python OCC to meet my needs as a simple CAD editor in the style of OpenSCAD.  As development continues I will refine the GUI and add more "helper" functions to expose more functionality.

# Roadmap
Development roadmap as of 2021-01-08:

v0.2
- ~Modeling: helper functions to build axis for revolves~
- ~Modeling: allow for multiple wires to be used in face creation to create face with "holes"~
- ~Modeling: sweep face/profile along a path~

v0.3
- Modeling: patterns/arrays/mirrors/copies, etc.
- Quality: Refactor of functions into seperate files

v0.4
- Modeling: Lofting

v0.5
- Assemblies: Anchor points for relative part location

v0.6
- GUI: decouple added features from demo-gui from pyocc

v0.7
- GUI: toggle views on/off
- GUI: implement 1 button mode for zoom/rotate/pan for trackpad (no scroll wheel) usage
- GUI: more verbose debugging options/outputs from test script

v0.8
- Special features: aka hole wizard type feature creation

v0.9
- Backend: Implement OpenSCAD as an alternative backend

v1.0
- Backend: Implement JSON/YAML file types for storing files and engine to parse them


# Known Bugs
Known bugs on the master/dev branch.
- end_face_coordinate_system when doing a revolve where the end solid intersects the axis of rotation returns the wrong result.  This may be a bug in openCASCADE.

# Installation
Use Anaconda and follow the instructions for Python OCC installation.  PyQT5 required.
