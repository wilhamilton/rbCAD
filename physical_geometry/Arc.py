"""
An Arc.

An edge that is defined as the arc.
"""

from physical_geometry import Edge


class Arc(Edge):
    """The Arc class."""

    def __init__(self, v1, v2, center, radius):
        """Create a new arc."""
        super(Arc, self).__init__(v1, v2)
        self.set_center(center)
        self.set_radius(radius)

    def set_center(self, center):
        """Set the center point of the arc."""
        self.center = center

    def set_radius(self, radius):
        """Set the radius of the arc."""
        self.radius = radius
