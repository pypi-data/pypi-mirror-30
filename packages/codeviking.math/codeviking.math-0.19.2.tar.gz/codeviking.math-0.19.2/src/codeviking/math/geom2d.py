"""

This module contains types useful in 2D geometry.


"""

from typing import NamedTuple, Sequence, Tuple, TypeVar, Union
from copy import copy
from math import sqrt

from codeviking.math.interval import RI, RICompat

V2Compat = Union['V2', Tuple[float, float]]
__V2 = NamedTuple('__V2', (('x', float), ('y', float)))

__all__ = ['V2', 'ClipLine', 'Box2', 'Segment2', 'Shape2', 'ConvPoly2', 'Tri2']


# noinspection PyAttributeOutsideInit,PyAttributeOutsideInit
class V2(__V2):
    """
    2D Euclidean vector type.

    Several operations are supported.  In the following, *u* is a V2,
    *v* is either a V2 or a tuple of length 2, and *a* is a number.

    *  *u* == *v* : standard equality test.
    *  *u* + *v* :        vector addition
    *  *u* - *v* :        vector subtraction
    *  *u* * *a* or *a* * *u* :        scalar multiplication
    *  *u* / *a* :        scalar division
    *  *u* // *a* :        scalar floor division
    *  *u* @ *v* :        dot product
    """

    @property
    def length(self) -> float:
        """
        Euclidean length of this vector.
        """
        if not hasattr(self, '_length'):
            self._length = sqrt(self.x ** 2 + self.y ** 2)
        return self._length

    def __eq__(self, other: V2Compat) -> bool:
        return self.x == other[0] and self.y == other[1]

    def __add__(self, other: V2Compat) -> 'V2':
        assert isinstance(other, tuple)
        return V2(self.x + other[0], self.y + other[1])

    def __neg__(self) -> 'V2':
        return V2(-self.x, -self.y)

    def __sub__(self, other: V2Compat) -> 'V2':
        assert isinstance(other, tuple)
        return V2(self.x - other[0], self.y - other[1])

    def __mul__(self, scalar) -> 'V2':
        return V2(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar) -> 'V2':
        return V2(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar) -> 'V2':
        return V2(self.x / scalar, self.y / scalar)

    def __floordiv__(self, scalar) -> 'V2':
        """Scalar floor division."""
        return V2(self.x // scalar, self.y // scalar)

    def __matmul__(self, other: V2Compat) -> float:
        """Dot product"""
        assert isinstance(other, tuple)
        return self.x * other[0] + self.y * other[1]

    def dot(self, other: V2Compat) -> float:
        """Dot product (other can be a V2 or a tuple)."""
        assert isinstance(other, tuple)
        return self.x * other[0] + self.y * other[1]

    def rdot(self, other: V2Compat) -> float:
        """Dot product of the right-facing normal vector with other."""
        assert isinstance(other, tuple)
        return self.y * other[0] - self.x * other[1]

    def ldot(self, other: V2Compat) -> float:
        """Dot product of the left-facing normal vector with other."""
        assert isinstance(other, tuple)
        return self.x * other[1] - self.y * other[0]

    @property
    def rnormal(self) -> 'V2':
        """right-handed normal vector (points to the right of this direction
        vector.
        """
        return V2(self.y, -self.x)

    @property
    def lnormal(self) -> 'V2':
        """left-handed normal vector (points to the right of this direction
        vector.
        """
        return V2(-self.y, self.x)

    @property
    def unit(self) -> 'V2':
        """Returns a normalized version of this vector (unit vector)."""
        if not hasattr(self, '_unit'):
            self._unit = V2(self.x / self.length, self.y / self.length)
        return self._unit

    def __str__(self) -> str:
        return "({0},{1})".format(self.x, self.y)


__Box2 = NamedTuple('__BBox', (('xr', RI), ('yr', RI)))


class Box2(__Box2):
    """
    Axis-aligned bounding box.
    :members:
    :undoc-members:
    :inherited-members:

    .. attribute:: xr, yr

        x and y intervals (instances of class RI) of this bounding box.  These
        attributes are read-only.

    .. describe::  p in box

         True if the point p lies inside box.   p can be a V2 or tuple.
         A p is inside box if box.xr.min <= p.x <= box.xr.max and box.yr.min
         <= p.y <= box.yr.max

    """

    def __new__(cls, xr: RICompat, yr: RICompat):
        if not isinstance(xr, RI):
            xr = RI(*xr)
        if not isinstance(yr, RI):
            yr = RI(*yr)
        # noinspection PyArgumentList
        return super(Box2, cls).__new__(cls, xr, yr)

    def __contains__(self, p: V2Compat) -> bool:
        return p[0] in self.xr and p[1] in self.yr

    def expand(self, item: Union['Box2', V2Compat]) -> 'Box2':
        """
        return a Box2 that contains both this box and item.

        :param item: can be either a V2, a Box2, or a tuple of length 2
        """
        if isinstance(item, Box2):
            return Box2(self.xr.expand(item.xr), self.yr.expand(item.yr))
        if not isinstance(item, V2):
            item = V2(*item)
        if item in self:
            return self
        if self.is_empty:
            return Box2(RI(item.x, item.x), RI(item.y, item.y))
        return Box2(self.xr.expand(item.x), self.yr.expand(item.y))

    @property
    def is_empty(self) -> bool:
        """
        return True if this box is empty.
        """
        return self.xr.is_empty or self.yr.is_empty

    @property
    def bbox(self) -> 'Box2':
        return self

    def intersects(self, other: 'Box2') -> bool:
        return self.xr.intersects(other.xr) and self.yr.intersects(other.yr)

    def intersection(self, other: 'Box2'):
        return Box2(self.xr.intersection(other.xr),
                    self.yr.intersection(other.yr))


Box2.empty = Box2(RI.empty, RI.empty)


class Shape2:
    """
    This is an interface for a generic 2d shape.  It only supports one
    operation:

    .. describe p in shape::

        True if the point p lies inside this shape.

    subclasses need to implement the __contains__ member function.
    """

    def __contains__(self, p: V2Compat) -> bool:
        pass


__Tri2 = NamedTuple('__Tri2', (('v0', V2), ('v1', V2), ('v2', V2),
                               ('n0', V2), ('n1', V2), ('n2', V2),
                               ('bbox', Box2)))


# noinspection PyUnresolvedReferences
class Tri2(__Tri2, Shape2):
    """
    2d Triangle.
    Vertices must be supplied in counter clockwise (CCW) order.

    .. attribute:: v0, v1, v2

        Triangle vertices in counter clockwise order.  These are read-only
        attributes

    .. attribute:: n0, n1, n2

        Outward-facing edge normal vectors.  These are read-only attributes

    .. describe:: p in triangle

        True if point *p* lies inside *triangle*.  *p* can be a V2 or a
        tuple.

    """

    def __new__(cls,
                v0: V2Compat,
                v1: V2Compat,
                v2: V2Compat):
        if not isinstance(v0, V2):
            v0 = V2(*v0)
        if not isinstance(v1, V2):
            v1 = V2(*v1)
        if not isinstance(v2, V2):
            v2 = V2(*v2)
        ax, ay = [v0.x, v1.x, v2.x], [v0.y, v1.y, v2.y]

        # noinspection PyArgumentList
        return super(Tri2, cls).__new__(cls, v0, v1, v2,
                                        (v1 - v0).rnormal,
                                        (v2 - v1).rnormal,
                                        (v0 - v2).rnormal,
                                        Box2(RI(min(ax), max(ax)),
                                             RI(min(ay), max(ay))))

    def __contains__(self, p: V2Compat) -> bool:
        if not isinstance(p, V2):
            p = V2(*p)
        if p not in self.bbox:
            return False
        if self.n0.dot(p - self.v0) > 0:
            return False
        if self.n1.dot(p - self.v1) > 0:
            return False
        if self.n2.dot(p - self.v2) > 0:
            return False
        return True


_ConvPoly2 = NamedTuple('_ConvPoly2', (('vertices', Sequence[V2]),
                                       ('onorms', Sequence[V2]),
                                       ('bbox', Box2)))


class ClipLine(NamedTuple('ClipLine', (('a', V2), ('b', V2), ('n', V2)))):
    pass


"""
sa - which side of clipping line is point a on.
sb - which side of clipping line is point b on.
i - intersection point with clipping line.
"""
ClipResult = NamedTuple('ClipResult',
                        (('sa', float), ('sb', float), ('i', V2Compat)))


# noinspection PyAttributeOutsideInit


class Segment2(NamedTuple('Segment', (('a', float), ('b', float)))):
    @property
    def v(self):
        if not hasattr(self, '_v'):
            self._v = self.b - self.a
        return self._v

    def point(self, alpha):
        """Calculate a point on the segment that is a fraction alpha between a
         and b.  point(0) == a   point(1) == b  point(0.5) == midpoint of a,
         b."""
        return V2(self.a.x + alpha * self.v.x, self.a.y + alpha * self.v.y)

    def side(self, point):
        """Which side of this line segment is point on?
            > 0 => point is on the right side.
            < 0 => point is on the left side.
        """
        d = point - self.a
        self.v.rdot(d)

    def intersect(self, other, epsilon_sqr=1e-8):
        e = self.a - other.a
        k = self.v.rdot(other.v)
        k2 = k * k
        slen2 = self.v.dot(self.v)
        olen2 = other.v.dot(other.v)
        if k2 > epsilon_sqr * slen2 * olen2:
            s = e.ldot(other.v) / k
            if s < 0 or s > 1:
                return None
            t = e.ldot(other.v)
            if t < 0 or t > 1:
                return None
            return self.point(s)

        # line segments are parallel
        lene2 = e.dot(e)
        k = e.self.v
        k2 = k * k
        if k2 > epsilon_sqr * slen2 * lene2:
            # lines through segments are not colinear
            return None
        # lines through segments are colinear.  We need to see if the
        # segments overlap
        s0 = self.v.dot(e) / slen2
        s1 = s0 + self.v.dot(other.v) / slen2
        smin = min(s0, s1)
        smax = max(s0, s1)
        sinter = RI(0, 1).intersection(RI(smin, smax))
        if sinter.is_point:
            return self.a + sinter.min * self.v
        return Segment2(self.a + sinter.min * self.v,
                        self.a + sinter.max * self.v)


# noinspection PyAttributeOutsideInit
class ConvPoly2(_ConvPoly2, Shape2):
    """
    2d Convex Polygon
    Vertices must be supplied in counter clockwise (CCW) order.

    .. attribute:: vertices

        Triangle vertices in counter clockwise order.

    .. attribute:: onorms

        Outward-facing edge normal vectors.

    .. describe:: p in poly

        True if point *p* lies inside *poly*.  *p* can be a V2 or a tuple.


    """

    def __new__(cls, vertices: Sequence[V2Compat]):
        n = len(vertices)
        vertices = tuple((p if isinstance(p, V2) else V2(*p)) for p in vertices)
        ax, ay = ([p.x for p in vertices], [p.y for p in vertices])
        bbox = Box2(RI(min(ax), max(ax)), RI(min(ay), max(ay)))
        onorms = tuple((vertices[(i + 1) % n] - vertices[i]).rnormal
                       for i in range(n))
        # noinspection PyArgumentList
        return super(ConvPoly2, cls).__new__(cls,
                                             vertices,
                                             onorms,
                                             bbox)

    def __contains__(self, p):
        if not isinstance(p, V2):
            p = V2(*p)
        if p not in self.bbox:
            return False
        for i in range(len(self.vertices)):
            if self.onorms[i].dot(p - self.vertices[i]) > 0:
                return False
        return True

    def vertex(self, idx):
        return self.vertices[idx % len(self.vertices)]

    @property
    def segments(self):
        if not hasattr(self, '_segments'):
            self._segments = tuple(Segment2(self.vertices[i + 1],
                                            self.vertices[i]) for i in
                                   range(len(self.vertices)))
        return self._segments

        # def intersection(self, other: ConvPoly2):
        #     output_list = list(other.vertices)
        #     for (p, n) in self.clip_edges():
        #         input_list = copy(output_list)
        #         output_list.clear()
        #         s = input_list[-1]
        #         for e in input_list:
        #             if n.dot(e - p) > 0:
