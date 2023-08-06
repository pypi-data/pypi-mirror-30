import numpy as np


class Color(object):
    def __init__(self, r, g, b):
        self.tup = (r, g, b)

    @property
    def hex(self):
        return "#%s" % "".join((chr(int(255*i)) for i in self.tup)).encode('hex')

    def __len__(self):
        return 3

    def __iter__(self):
        return iter(self.tup)

    def __get__(self, item):
        return self.tup[item]

    def __repr__(self):
        return "(%.3f, %.3f, %.3f)" % (self.tup[0], self.tup[1], self.tup[2])

    def __array__(self):
        # Matplotlib casts color tuples to Numpy arrays, so we need this method to allow for that
        return np.array(self.tup)


blue = Color(.365, .647, .855)
yellow = Color(.871, .812, .247)
green = Color(.376, .741, .408)
red = Color(.945, .345, .329)
gray = Color(.302, .302, .302)
grey = gray
orange = Color(.980, .643, .227)
pink = Color(.945, .486, .690)
brown = Color(.698, .569, .184)
purple = Color(.698, .463, .698)
