
import numpy as np
from physical_geometry import Line

from base_geometry import Plane

def update (v1, v2):
    v1[0] = v2[0]
    v1[1] = v2[1]
    v1[2] = v2[2]

v1 = np.array([0,0,0])

v2 = np.array([1,1,1])

s = Line(v1, v2)

print(s.tostring())

print(s.on_edge(np.array([.5,.5,.5])))


update(v1, [-1,-1,-1])

print(s.tostring())


v3 = np.array([0,1,2])

p = Plane()

print(p.contains(v3))

print(p.contains(v2))


