"""
Sketch.

Sketches are only useful for creating new paths and profiles.

They will
be used when the CAD system is more complete.
"""


class Sketch:
    """The Sketch Class."""

    def __init__(self, name, plane):
        """Initialize a new sketch."""
        self.set_name(name)
        self.set_plane(plane)
        self.vertices = []
        self.edges = []
        self.paths = []
        self.profiles = []

    def setName(self, name):
        """Set the name of the sketch."""
        self.name = name

    def set_plane(self, plane):
        """Set the plane the sketch is on."""
        self.plane = plane

    def add_vertex(self, vertex):
        """Add a new vertex to the sketch."""
        found = False

        for tempVertex in self.vertices:
            if vertex == tempVertex:
                found = True
                vertex = tempVertex
                break

        if not found:
            self.vertices.append(vertex)

        return vertex

    def add_edge(self, edge):
        """Add a new edge to the sketch."""
        found = False

        for tempEdge in self.edges:
            if tempEdge == edge:
                found = True
                edge = tempEdge
                break

        if not found:
            self.edges.append(edge)

        return edge

    def find_paths(self):
        """Process the sketch to find any paths."""
        pass

    def find_profiles(self):
        """Process the sketch to find any profiles."""
        pass
