"""
Path class.

Defines a path with a start and end made up of edges (segments).
"""


class Path:
    """Class docstring."""

    '''The Path Class initializer.'''
    def __init__(self):
        """A Docstring."""
        self.segments = []
        pass

    def add_segment(self, new_edge):
        """Add a new edge (segment) to a path."""
        if self.valid_next_segment(new_edge):
            self.segments.append(new_edge)
        pass

    def valid_next_segment(self, new_edge):
        """Check to see if the new edge starts where the path ends."""
        last = self.segments[-1].v2
        if last == new_edge.v2:
            return True
        else:
            return False
        pass
