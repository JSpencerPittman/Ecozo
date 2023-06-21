import numpy as np
from bisect import bisect_left, bisect_right


class Point(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Piecewise(object):
    def __init__(self, x=None, y=None, x_int=1, y_int=1):
        if x is None and y is None:
            raise Exception("PieceWise: Either x or y must be provided as a list.")

        self.x = x
        self.y = y

        if x is None:
            self.x = np.arange(0, len(y)*x_int, x_int)
        if y is None:
            self.y = np.arange(0, len(x)*y_int, y_int)

    def get_y(self, x):
        left_idx = bisect_left(self.x, x)
        right_idx = bisect_right(self.x, x)

        if self.x[left_idx] > x:
            left_idx -= 1

        left_point = Point(self.x[left_idx], self.y[left_idx])
        right_point = Point(self.x[right_idx], self.y[right_idx])

        slope = Piecewise.calc_slope(left_point, right_point)
        intercept = Piecewise.calc_intercept(left_point, slope)

        return slope * x + intercept

    def get_x(self, y):
        left_idx = bisect_left(self.y, y)
        right_idx = bisect_right(self.y, y)

        if self.y[left_idx] > y:
            left_idx -= 1

        left_point = Point(self.x[left_idx], self.y[left_idx])
        right_point = Point(self.x[right_idx], self.y[right_idx])

        slope = Piecewise.calc_slope(left_point, right_point)
        intercept = Piecewise.calc_intercept(left_point, slope)

        return (y - intercept) / slope

    @staticmethod
    def calc_slope(p: Point, q: Point):
        return (q.y - p.y) / (q.x - p.x)

    @staticmethod
    def calc_intercept(p: Point, slope):
        return p.y - (slope * p.x)
