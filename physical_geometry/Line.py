"""
A Line.

A specific type of edge.
"""
from physical_geometry import Edge


class Line(Edge):
    """A straight line edge."""

    def __init__(self, v1, v2):
        """Create a new line."""
        super(Line, self).__init__(v1, v2)
        self.slope = self.v2 - self.v1

    def get_point(self, t):
        """Calculate a (parametric) point on the line."""
        return self.v1 + t*self.slope

    def on_edge(self, point):
        """Calculate if the supplied point falls on the line."""
        temp = (point - self.v1) / self.slope
        if temp[0] == temp[1] and temp[1] == temp[2]:
            return True
        else:
            return False
