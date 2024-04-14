import time
from random import choices, seed, randrange
from datetime import datetime
import numpy as np
from trajectory import HumanCurve
import random
import psutil
import cv2 as cv


def get_distance(cur_x, cur_y, dest_x, dest_y, max_val=np.Inf):
    """
    Counting distance from a current position to a target point, clipping by (0, max value) range
    :return: float value of a distance
    """
    return np.clip(np.sqrt((dest_x - cur_x) ** 2 + (dest_y - cur_y) ** 2), 0, max_val)


def get_freq():
    """Getting average frequency value to further point number scaling"""
    freq = 0.
    cycles = 1000
    for times in range(cycles):
        freq += psutil.cpu_freq()[0]

    freq /= (cycles / psutil.cpu_count(True))
    return freq


class MouseMover:
    """
    mouse_move() - baseline method to use. Includes clicking and actual moving, so remove this if you intend to use curve generator only
    mouse_move_test() - visualization method including curve generation only. Uses OpenCV to draw the curves
    \n
    By default, class uses points scaling adjusted by CPU. Please, remove all related code if you don't need this feature
    """
    def __init__(self, width: int, height: int, x: float = 0, y: float = 0):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.screen = None

        # These lines are used only for visualization / debug purposes
        self.shape = (800, 1800, 3)
        self.screen = np.zeros(self.shape)
        self.prev_screen = np.zeros(self.shape)

        # Used for normalize points number by cpu frequency (since it was tested on a few PCs).
        # I advise to delete all related code
        self._freq = get_freq()
        self._canonic_freq = 50000.0  # Measured during some tests
        self._freq_ratio = self._freq / self._canonic_freq

        # Current preferred max values
        self._max_points = 120
        self._min_points = 30

        # Current preferred min values
        self._lowest_min_points = 5
        self._lowest_max_points = 17

        # Counting min points for current machine and clipping by 5 at lower border (we still want some curve,
        # not just 2 points). Same for
        self._min_points_scaled = int(np.clip(int(self._min_points * self._freq_ratio),
                                              self._lowest_min_points, self._min_points))
        self._max_points_scaled = int(np.clip(int(self._max_points * self._freq_ratio),
                                              self._lowest_max_points, self._max_points))

        print("Res points: ", self._min_points_scaled, self._max_points_scaled)

        return

    def mouse_move(self, move_func, click_func, top_left_x, top_left_y, bottom_right_x, bottom_right_y, allow_fakes: bool = False, click_thershold: int = 5):
        """
        Baseline method of moving the mouse. Includes moving itself and clicking. Method uses output since that info used by logger

        :param move_func: outer function for moving the mouse
        :param click_func same, but for clicking

        :param top_left_x: top left corner of the bounding box
        :param top_left_y: top left corner of the bounding box
        :param bottom_right_x: bottom right corner of the bounding box
        :param bottom_right_y: bottom right corner of the bounding box

        :param allow_fakes: use to imitate human excessive clicking. Clicks are performed only in a small area around the target one
        :param click_thershold: area size around the target point. Used during fake-clicking (only)

        """
        # For better random
        seed_core = datetime.now().microsecond
        seed(seed_core)

        # Box center random point
        dest_x = randrange(int(top_left_x) + 1, int(bottom_right_x) - 1)
        dest_y = randrange(int(top_left_y) + 1, int(bottom_right_y) - 1)

        res = self._generate_curve(self.x, self.y, dest_x, dest_y, self.width, self.height,
                                   self._min_points_scaled, self._max_points_scaled)

        # Actual clicks count
        click_count = 0
        # Max fake clicks count
        max_clicks = random.choices(population=range(1, 4), weights=[0.8, 0.15, 0.05], k=1)[0]
        # Distance where we allow fake clicks to happen
        distance_threshold = click_thershold

        # Adding target point so the algorithm won't skip it for sure
        if (dest_x, dest_y) not in res:
            res.append((dest_x, dest_y))
        # Points processing
        start_time = datetime.now()
        print(f"base_move - number:-1, time: {datetime.now() - start_time}, x:{self.x}, y:{self.y}")
        for indx, point in enumerate(res):
            tmp = float(np.clip(point[0], 0, self.width - 1)), float(np.clip(point[1], 0, self.height - 1))
            move_func(tmp[0], tmp[1])
            print(f"base_move - number:{indx}, time: {datetime.now() - start_time}, x:{tmp[0]}, y:{tmp[1]}")
            if get_distance(tmp[0], tmp[1], dest_x, dest_y) <= distance_threshold \
                    and click_count < max_clicks and allow_fakes:
                is_allowed = random.choices(population=[False, True], weights=[0.7, 0.3], k=1)[0]
                if is_allowed:
                    print(f"fake click - number:{indx}, time: {datetime.now() - start_time}, x:{tmp[0]}, y:{tmp[1]}")
                    click_func(tmp[0], tmp[1])
                    click_count += 1

        self.x = dest_x
        self.y = dest_y

        return

    def mouse_move_test(self, top_left_x: int, top_left_y: int, bottom_right_x: int, bottom_right_y: int):
        """
            Visualization method which uses OpenCV to draw the curves. No actual moving/clicking is performed. Screen size is locked by class attributes (default = (1800, 800))

            :param top_left_x: top left corner of the bounding box
            :param top_left_y: top left corner of the bounding box
            :param bottom_right_x: bottom right corner of the bounding box
            :param bottom_right_y: bottom right corner of the bounding box

            >>> # Usage example:
            >>> max_x = 1800
            >>> max_y = 800
            >>> mouse = MouseMover(900, 400)
            >>> for i in range(100):
            >>>     tmp_x, tmp_y = random.randint(0, max_x), random.randint(0, max_y)
            >>>     mouse.mouse_move_test(tmp_x, tmp_y, tmp_x + 20, tmp_y + 20)
            >>>     time.sleep(2)
        """
        self.screen = np.zeros(self.shape)

        seed_core = datetime.now().microsecond
        seed(seed_core)

        # Box center random point
        dest_x = randrange(int(top_left_x) + 1, int(bottom_right_x) - 1)
        dest_y = randrange(int(top_left_y) + 1, int(bottom_right_y) - 1)

        res = self._generate_curve(self.x, self.y, dest_x, dest_y, self.width, self.height,
                                   self._min_points_scaled, self._max_points_scaled)

        int_list = res

        for i in int_list:
            tmp = [int(np.clip(i[0], 0, self.shape[1] - 1)), int(np.clip(i[1], 0, self.shape[0] - 1))]

            for j in range(-2, 3):
                for k in range(-2, 3):
                    self.screen[np.clip(tmp[1] + j, 0, self.shape[0] - 1)][np.clip(tmp[0] + k, 0, self.shape[1] - 1)] \
                        = (255, 0, 207)

            self.prev_screen *= 1/3
            cv.imshow("Some curve", self.screen + self.prev_screen)
            cv.waitKey(2)

            # This line will make visualization a step-by-step animation, you will see only the most recent points
            # self.prev_screen = self.screen

        self.x = dest_x
        self.y = dest_y

        return

    @staticmethod
    def _generate_curve(cur_x, cur_y, dest_x, dest_y, width: int, height: int, min_points: int, max_points: int):
        """
        Curve generation with a set of params
        :return: Points for a target curve
        """
        # This one for curve order regulation
        knots_count = choices([1, 2, 3], k=1)[0]  # , 4, 5, 6, 7, 8, 9, 10

        # For total curve points density. USE FOR SPEED ADJUSTMENT
        # Truncating distance by view port height value
        distance = get_distance(cur_x, cur_y, dest_x, dest_y, height)
        # target_avg_points = 15 - experimental value (the default optimal one by now)
        # Possible points numbers, 20 aka max points, 5 aka min points
        max_range = range(min_points, max_points + 1)
        points_number = [num for num in max_range]
        # Scaling distance to points number range, applying random bias (-2 - +3 points per curve)
        target_points = int(distance / height * (points_number[-1] - points_number[0]) + points_number[0])
        points_num_bias = random.choices(population=range(-2, 4), weights=[0.05, 0.15, 0.5, 0.15, 0.1, 0.05], k=1)[0]
        target_points = int(np.clip(target_points + points_num_bias, points_number[0], points_number[-1]))

        print(dest_x, dest_y, target_points)

        # For noise regulation
        distortion = randrange(5, 20) / 10.
        # Curve itself. Since we use only a few points - interpolation step is set to half of the target points number
        interp_step = target_points // 2 + 1
        human_curve = HumanCurve((cur_x, cur_y), (dest_x, dest_y), knots_count=knots_count,
                                 target_points=target_points, distortion_mean=distortion,
                                 interp_step=interp_step)

        return human_curve.points


if __name__ == "__main__":
    max_x = 1800
    max_y = 800
    mouse = MouseMover(900, 400)
    for i in range(100):
        tmp_x, tmp_y = random.randint(0, max_x), random.randint(0, max_y)
        mouse.mouse_move_test(tmp_x, tmp_y, tmp_x + 20, tmp_y + 20)
        time.sleep(2)


