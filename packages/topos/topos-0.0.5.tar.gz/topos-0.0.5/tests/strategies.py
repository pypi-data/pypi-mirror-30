import numpy as np
import numpy.random as npr
from math import pi
from hypothesis.strategies import integers, floats, composite, tuples, lists

# In this file we define a number of strategies representing
# particular data types. Defining them here in one place will
# help keep ourselves consistent.

# A "real" number in the range of +- 1 million
real = floats(min_value=-1e6, max_value=1e6)

# A "radial" number - the R in polar coordinates
R = floats(min_value=0.1, max_value=1e6)

# An angle, the T in polar coordinates
T = floats(min_value=0, max_value=(2*pi - 0.0001))

# A cylindrical coordinate - for mesh gen reasons we represent them as (T, Z, R)
cylin = tuples(T, real, R)
cylindrical = lists(cylin, min_size=4, max_size=512)

cart = tuples(real, real, real)
cartesian = lists(cart, min_size=4, max_size=512)

# A "size" a non negative integer representing the length of arrays etc.
size = integers(min_value=1, max_value=512)

# A strategy representing an arbitrary array of faces
@composite
def faces(draw):
    num = draw(size)
    return npr.randint(1, 256, size=(num, 4))
