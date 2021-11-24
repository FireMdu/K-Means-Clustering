from manim import VMobject
from anytree import NodeMixin


class ParentNode(VMobject):
    CONFIG = {
        'radius': 2,
        'num_children': 0,
    }

    def __init__(self, **kwargs):
        VMobject.__init__(**kwargs)

    def get_num_children(self):
        """Return the number of children the parent has"""
        return self.num_children

    def node_connect_points(self):
        """Return a dictionary of local connection points numpy array as
        values with corresponding child number as key"""
        pass

    def rotate_connect_points(self):
        """Rotate connection points in place: rotate the numpy array"""
        pass

    def get_bisector_angle(self):
        """Get angle of the bisector line from the parent if it is also a
        child"""
        pass


class MyBaseClass(object):  # Just an example of a base class
    pass


class MyClass(VMobject, NodeMixin):  # Add Node feature

    def __init__(self, name, length, width, parent=None, children=None,
                 **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.length = length
        self.width = width
        self.parent = parent
        if children:
            self.children = children






