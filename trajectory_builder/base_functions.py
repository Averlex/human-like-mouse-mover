import numpy as np
import math


def is_numeric(val):
    """Just checks if val argument is numeric type or not"""
    return isinstance(val, (float, int, np.int32, np.int64, np.float32, np.float64))


def is_list_of_points(l):
    """Returns a sublist containing points of numeric values."""
    if not isinstance(l, list):
        return False
    try:
        is_point = lambda p: ((len(p) == 2) and is_numeric(p[0]) and is_numeric(p[1]))
        return all(map(is_point, l))
    except (KeyError, TypeError) as e:
        return False


class BezierCurve:
    """Base class used for Bezier curves building"""
    @staticmethod
    def binomial(n, k):
        """Returns the binomial coefficient "n choose k" """
        return math.factorial(n) / float(math.factorial(k) * math.factorial(n - k))

    @staticmethod
    def bernstein_polynomial_point(x, i, n):
        """Calculate the i-th component of a bernstein polynomial of degree n"""
        return BezierCurve.binomial(n, i) * (x ** i) * ((1 - x) ** (n - i))

    @staticmethod
    def bernstein_polynomial(points):
        """
        Given list of control points, returns a function, which given a point [0,1] returns
        a point in the Bezier curve described by these points
        """
        def bern(t):
            n = len(points) - 1
            x = y = 0
            for i, point in enumerate(points):
                bern = BezierCurve.bernstein_polynomial_point(t, i, n)
                x += point[0] * bern
                y += point[1] * bern
            return x, y
        return bern

    @staticmethod
    def curve_points(n, points):
        """
        Given list of control points, returns n points in the bezier curve, described by these points
        """
        curve_points = []
        bernstein_polynomial = BezierCurve.bernstein_polynomial(points)
        for i in range(n):
            t = i / (n - 1)
            curve_points += bernstein_polynomial(t)
        return curve_points
