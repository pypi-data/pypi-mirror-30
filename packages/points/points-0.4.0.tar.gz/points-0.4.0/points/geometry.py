"""Contains functions for manipulating Euclidian vectors."""

from math import cos, sin, radians
from .vectors import Vector
from .matrices import Matrix

def round_vectors(func):
    """This decorator takes a function which handles vectors, and makes it round
    its values once complete."""

    def new(*args, trim=None, **kwargs):
        result = func(*args, **kwargs)
        if trim:
            for arg in args:
                if isinstance(arg, Vector):
                    arg._values = [round(val, trim) for val in arg._values]
        return result
    new.__doc__, new.__name__ = func.__doc__, func.__name__
    return new


def allow_degrees(func):
    """This decorator takes a function which takes an angle, and makes it able
    to take it in degrees as well as in radians. The angle argument should be
    the first positional argument."""

    def new(*args, degrees=False, **kwargs):
        if degrees: args = [radians(args[0])] + list(args[1:])
        return func(*args, **kwargs)
    new.__doc__, new.__name__ = func.__doc__, func.__name__
    return new


def translate_vectors(translation, *vectors):
    """Translates some vectors in space. The vectors will be changed in place.

    :param tuple translation: The translation values.
    :param \*vectors: The vectors to translate.
    :raises TypeError: if non-vectors are given.
    :raises ValueError: if the vectors given don't match the dimension of the\
    translation."""

    for v in vectors:
        if not isinstance(v, Vector):
            raise TypeError("Cannot translate {} - not a vector".format(v))
        if len(v._values) != len(translation):
            raise ValueError("Cannot translate {} - wrong dimension".format(v))
    for vector in vectors:
        vector._values = [val + d for val, d in zip(vector._values, translation)]


@round_vectors
@allow_degrees
def rotate_2d_vectors(angle, *vectors, point=None):
    """Rotates 2 dimensional vectors.

    :param float angle: The angle in radians.
    :param iter point: A point to rotate around. The origin is the default.
    :param int trim: if given, the vector values will be rounded to this number\
    of decimal places at the end.
    :param bool degrees: if `True``, the angle given will be interpreted as\
    being in degrees, not radians.
    :param \*vectors: The vectors to rotate.
    :raises TypeError: if non-vectors are given.
    :raises ValueError: if the vectors given don't match the dimension of the\
    rotation."""

    for v in vectors:
        if not isinstance(v, Vector):
            raise TypeError("Cannot rotate {} - not a vector".format(v))
        if len(v._values) != 2:
            raise ValueError("Cannot rotate {} - not 2D".format(v))
    if point:
        if len(point) != 2:
            raise ValueError("point {} is not 2D".format(point))
        dx, dy = point
        translate_vectors((-dx, -dy), *vectors)
    matrix = Matrix([cos(angle), -sin(angle)], [sin(angle), cos(angle)])
    for vector in vectors:
        vector._values = (matrix @ vector)._values
    if point: translate_vectors((dx, dy), *vectors)


@round_vectors
@allow_degrees
def rotate_3d_vectors(angle, dimension, *vectors, point=None):
    """Rotates 3 dimensional vectors.

    :param float angle: The angle in radians.
    :param int dimension: 0, 1, or 2, depending on which axis to rotate around.
    :param int trim: if given, the vector values will be rounded to this number\
    of decimal places at the end.
    :param bool degrees: if `True``, the angle given will be interpreted as\
    being in degrees, not radians.
    :param \*vectors: The vectors to rotate.
    :raises TypeError: if non-vectors are given.
    :raises ValueError: if the vectors given don't match the dimension of the\
    rotation."""

    for v in vectors:
        if not isinstance(v, Vector):
            raise TypeError("Cannot rotate {} - not a vector".format(v))
        if len(v._values) != 3:
            raise ValueError("Cannot rotate {} - not 3D".format(v))
    if point:
        if len(point) != 3:
            raise ValueError("point {} is not 3D".format(point))
        dx, dy, dz = point
        translate_vectors((-dx, -dy, -dz), *vectors)
    if dimension == 0:
        matrix = Matrix(
         [1, 0, 0], [0, cos(angle), -sin(angle)], [0, sin(angle), cos(angle)]
        )
    elif dimension == 1:
        matrix = Matrix(
         [cos(angle), 0, sin(angle)], [0, 1, 0], [-sin(angle), 0, cos(angle)]
        )
    elif dimension == 2:
        matrix = Matrix(
         [cos(angle), -sin(angle), 0], [sin(angle), cos(angle), 0], [0, 0, 1]
        )
    else:
        raise ValueError("{} is not a valid dimensions".format(dimension))
    for vector in vectors:
        vector._values = (matrix @ vector)._values
    if point: translate_vectors((dx, dy, dz), *vectors)


@round_vectors
def align_vectors_to_plane(axis, coaxis, vector, *vectors):
    """Rotates some vectors around an axis, until a given vector lies in the
    plane of that axis with a second coaxis.

    :param int axis: The axis to rotate around.
    :param int coaxis: The second axis of the plane to land on.
    :param Vector vector: The vector to align to the plane.
    :param \*vectors: The other vectors along for the ride."""

    if axis not in (0, 1, 2):
        raise ValueError("{} is not a valid axis".format(axis))
    if coaxis not in (0, 1, 2) or coaxis == axis:
        raise ValueError("{} is not a valid coaxis".format(coaxis))
    coaxis_vector = Vector(*[1 if i == coaxis else 0 for i in range(3)])
    flattened_vector = Vector(
     *[0 if i == axis else val for i, val in enumerate(vector._values)]
    )
    angle = coaxis_vector.angle_with(flattened_vector)
    rotate_3d_vectors(angle, axis, vector, *vectors)
