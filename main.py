
import numpy as np
from Segment import Segment


def update (v1, v2):
    v1[0] = v2[0]
    v1[1] = v2[1]
    v1[2] = v2[2]

v1 = np.array([0,0,0])

v2 = np.array([1,1,1])

s = Segment(v1, v2)

print(s.tostring())

print(s.onEdge(np.array([.5,.5,.5])))


update(v1, [-1,-1,-1])

print(s.tostring())



