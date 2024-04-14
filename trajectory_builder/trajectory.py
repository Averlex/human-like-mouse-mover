import pytweening
import random
from datetime import datetime
from base_functions import *


class HumanCurve:
    """
    Generates a human-like mouse curve starting at given source point, and finishing in a given destination point. \n
    """
    def __init__(self, from_point, to_point, **kwargs):
        """
        Base constructor, taking start and end points as well as some optional parameters for curve building
        :param from_point: start point, x and y float coords
        :param to_point: end point, x and y float coords
        :keyword knots_count: number of additional points for curve construction. Default = 2
        :keyword target_points: total count of points on the curve. Default = 100
        :keyword interp_step: number of curve's parts to apply linear interpolation to. Default = random.choice(range(5, 20)
        :keyword offset_boundary_x, offset_boundary_y: offsets from the actual boundaries. Default = 100
        :keyword left_boundary, right_boundary, down_boundary, up_boundary: actual boundaries, not used explicitly
        :keyword distortion_mean, distortion_stdev: distortion distribution params (mean and standard deviation). Default = 1
        :keyword distortion_frequency: self-explanatory though requires some testing. Default = 0.5
        """
        self.fromPoint = from_point
        self.toPoint = to_point

        # For better random probably
        seed_core = (datetime.now().microsecond - self.fromPoint[1] ** self.toPoint[0]) + \
                    (self.fromPoint[0] & self.toPoint[1])
        random.seed(seed_core)

        self.points = self.generate_curve(**kwargs)

    def generate_curve(self, **kwargs):
        """
        Generates a curve according to the parameters specified below. \n
        You can override any of the below parameters. If no parameter is passed, the default value is used
        """
        # Args extraction
        offset_boundary_x = kwargs.get("offset_boundary_x", 100)
        offset_boundary_y = kwargs.get("offset_boundary_y", 100)
        interp_step = kwargs.get("interp_step", random.choice(range(5, 20)))
        left_boundary = kwargs.get("left_boundary", min(self.fromPoint[0], self.toPoint[0])) - offset_boundary_x
        right_boundary = kwargs.get("right_boundary", max(self.fromPoint[0], self.toPoint[0])) + offset_boundary_x
        down_boundary = kwargs.get("down_boundary", min(self.fromPoint[1], self.toPoint[1])) - offset_boundary_y
        up_boundary = kwargs.get("up_boundary", max(self.fromPoint[1], self.toPoint[1])) + offset_boundary_y
        knots_count = kwargs.get("knots_count", 2)
        distortion_mean = kwargs.get("distortion_mean", 1)
        distortion_stdev = kwargs.get("distortion_stdev", 1)
        distortion_frequency = kwargs.get("distortion_frequency", 0.5)
        tween = kwargs.get("tweening", pytweening.easeOutQuad)
        target_points = kwargs.get("target_points", 100)

        # Get internal knots
        internal_knots = self.generate_internal_knots(left_boundary, right_boundary,
                                                      down_boundary, up_boundary, knots_count)
        # Get curve actual points
        points = self.generate_points(internal_knots)

        x_coords = [points[i] for i in range(len(points)) if i % 2 == 0]
        y_coords = [points[i] for i in range(len(points)) if i % 2 == 1]

        # Get unique point indices and append the end point (excluding start point and end point)
        random_points_indx = list(set(random.choices(range(1, len(x_coords) - 1), k=interp_step)))
        random_points_indx.append(len(x_coords) - 1)
        random_points_indx.sort()

        # Result of applying interpolation and prev_indx to tie the line with
        int_points = []
        prev_indx = 0
        # Interpolation itself
        for indx in random_points_indx:
            # Choosing whether to skip this point or not
            skip = random.choice([True, False])
            if not skip:
                # Elements to fill with
                elem_num = random.randrange(1 + (indx - prev_indx) // 2, indx - prev_indx + 2)
                int_ys = [(y_coords[indx] - y_coords[prev_indx]) / elem_num * elem + y_coords[prev_indx] for elem in range(elem_num)]
                int_xs = [(x_coords[indx] - x_coords[prev_indx]) / elem_num * elem + x_coords[prev_indx] for elem in range(elem_num)]

                int_points.extend(list(map(lambda x, y: (x, y), int_xs, int_ys)))
            else:
                int_points.extend(list(map(lambda x, y: (x, y), x_coords[prev_indx:indx], y_coords[prev_indx:indx])))
            prev_indx = indx

        # Distortion accordingly to params
        int_points = self.distort_points(int_points, distortion_mean, distortion_stdev, distortion_frequency)
        # Tweening
        int_points = self.tween_points(int_points, tween, target_points)

        return int_points

    @staticmethod
    def generate_internal_knots(left_boundary, right_boundary, down_boundary, up_boundary, knots_count):
        """
        Generates the internal knots used during generation of Bezier curve points or any interpolation function.
        The points are taken at random from a surface delimited by given boundaries.
        Exactly knots_count internal knots are randomly generated.
        """
        if not (is_numeric(left_boundary) and is_numeric(right_boundary) and
                is_numeric(down_boundary) and is_numeric(up_boundary)):
            raise ValueError("Boundaries must be numeric")
        if not isinstance(knots_count, int) or knots_count < 0:
            raise ValueError("knots_count must be non-negative integer")
        if left_boundary > right_boundary:
            raise ValueError("left_boundary must be less than or equal to right_boundary")
        if down_boundary > up_boundary:
            raise ValueError("down_boundary must be less than or equal to up_boundary")

        knots_x = np.random.choice(range(left_boundary, right_boundary), size=knots_count)
        knots_y = np.random.choice(range(down_boundary, up_boundary), size=knots_count)
        knots = list(zip(knots_x, knots_y))
        return knots

    def generate_points(self, knots):
        """
        Generates Bezier curve points on a curve, according to the internal knots passed as parameter.
        """
        if not is_list_of_points(knots):
            raise ValueError("knots must be valid list of points")

        mid_pts_cnt = max(abs(self.fromPoint[0] - self.toPoint[0]),
                          abs(self.fromPoint[1] - self.toPoint[1]),
                          2)
        knots = [self.fromPoint] + knots + [self.toPoint]
        return BezierCurve.curve_points(mid_pts_cnt, knots)

    @staticmethod
    def distort_points(points, distortion_mean, distortion_stdev, distortion_frequency):
        """
        Distorts the curve described by (x,y) points, so that the curve is not ideally smooth.
        Distortion happens by randomly, according to normal distribution, adding an offset to some of the points.
        """
        if not(is_numeric(distortion_mean) and is_numeric(distortion_stdev) and is_numeric(distortion_frequency)):
            raise ValueError("Distortions must be numeric")
        if not is_list_of_points(points):
            raise ValueError("points must be valid list of points")
        if not (0 <= distortion_frequency <= 1):
            raise ValueError("distortionFrequency must be in range [0,1]")

        distorted = []
        for i in range(1, len(points)-1):
            x, y = points[i]
            delta_y = np.random.normal(distortion_mean, distortion_stdev) if \
                random.random() < distortion_frequency else 0
            delta_x = np.random.normal(distortion_mean, distortion_stdev) if \
                random.random() < distortion_frequency else 0
            sign_y = random.choice([-1, 1])
            sign_x = random.choice([-1, 0, 1])
            distorted += (x + delta_x * sign_x, y + delta_y * sign_y),
        distorted = [points[0]] + distorted + [points[-1]]
        return distorted

    @staticmethod
    def tween_points(points, tween, target_points):
        """
        Chooses a number of points(targetPoints) from the list(points) according to tweening function(tween).
        This function in fact controls the velocity of mouse movement
        """
        if not is_list_of_points(points):
            raise ValueError("points must be valid list of points")
        if not isinstance(target_points, int) or target_points < 2:
            raise ValueError("target_points must be an integer greater or equal to 2")

        # tween is a function that takes a float 0..1 and returns a float 0..1
        res = []
        for i in range(target_points):
            index = int(tween(float(i)/(target_points-1)) * (len(points)-1))
            res += points[index],
        return res
