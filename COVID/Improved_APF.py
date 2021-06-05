"""
Artificial Potential Field Method in path planning
resolve unreachable target and remaining local minimal problem
"""
from COVID.Original_APF import APF, Vector2d
import matplotlib.pyplot as plt
import math
from matplotlib.patches import Circle
import random
import math
from COVID.models import *
from geopy.geocoders import Nominatim





def millerToXY(lon, lat):
    """
    Convert longitude and latitude into xy coordinates
    :param lon: longitude
    :param lat: latitude
    :return: xy coordinates
    """
    xy_coordinate = []
    L = 6381372 * math.pi * 2  # Earth circumference
    W = L  # Plane unfolded, the circumference is the x-axis
    H = L / 2  # The y-axis is about half the circumference
    mill = 2.3  # A constant in the Miller projection, the range is approximately between plus and minus 2.3
    x = lon * math.pi / 180  # Convert longitude from degrees to radians
    y = lat * math.pi / 180
    # 将纬度从度数转换为弧度
    y = 1.25 * math.log(math.tan(0.25 * math.pi + 0.4 * y))  # Here is the conversion of Miller projection
    # The radians are converted to the actual distance, and the unit of the conversion result is kilometers.
    x = (W / 2) + (W / (2 * math.pi)) * x
    y = (H / 2) - (H / (2 * mill)) * y
    xy_coordinate.append(int(round(x)))
    xy_coordinate.append(int(round(y)))
    return xy_coordinate


def check_vec_angle(v1: Vector2d, v2: Vector2d):
    '''
    Coordinate angle
    :param v1:
    :param v2:
    :return: angle
    '''
    v1_v2 = v1.deltaX * v2.deltaX + v1.deltaY * v2.deltaY
    angle = math.acos(v1_v2 / (v1.length * v2.length)) * 180 / math.pi
    return angle


class APF_Improved(APF):
    def __init__(self, start: (), goal: (), obstacles: [], k_att: float, k_rep: float, rr: float,
                 step_size: float, max_iters: int, goal_threshold: float, is_plot=False):
        self.start = Vector2d(start[0], start[1])
        self.current_pos = Vector2d(start[0], start[1])
        self.goal = Vector2d(goal[0], goal[1])
        self.obstacles = [Vector2d(OB[0], OB[1]) for OB in obstacles]
        self.k_att = k_att
        self.k_rep = k_rep
        self.rr = rr  # repulsion force range
        self.step_size = step_size
        self.max_iters = max_iters
        self.iters = 0
        self.goal_threashold = goal_threshold
        self.path = list()
        self.is_path_plan_success = False
        self.is_plot = is_plot
        self.delta_t = 0.01

    def repulsion(self):
        """
        Repulsion calculation, improvement of repulsion function, solving unreachable problems
        :return: Repulsion
        """
        rep = Vector2d(0, 0)  # Total repulsion of all obstacles
        for obstacle in self.obstacles:
            # obstacle = Vector2d(0, 0)
            obs_to_rob = self.current_pos - obstacle
            rob_to_goal = self.goal - self.current_pos
            if obs_to_rob.length > self.rr:  # Beyond the obstacle repulsion influence range
                pass
            else:
                rep_1 = Vector2d(obs_to_rob.direction[0], obs_to_rob.direction[1]) * self.k_rep * (
                        1.0 / obs_to_rob.length - 1.0 / self.rr) / (obs_to_rob.length ** 2) * (rob_to_goal.length ** 2)
                rep_2 = Vector2d(rob_to_goal.direction[0], rob_to_goal.direction[1]) * self.k_rep * (
                            (1.0 / obs_to_rob.length - 1.0 / self.rr) ** 2) * rob_to_goal.length
                rep += (rep_1 + rep_2)
        return rep


def function(start_coor,goal_coor):
    k_att, k_rep = 1.0, 0.8
    rr = 3
    step_size, max_iters, goal_threashold = .2, 500, .2  # It takes 4.37s to find a path for 1000 times with a step length of 0.5, and 21s to find a path for 1000 times with a step length of 0.1
    step_size_ = 2
    datas = Point.objects.values_list("longitude", "latitude")
    point_start = millerToXY(float(start_coor[0]), float(start_coor[1]))
    point_goal = millerToXY(float(goal_coor[0]), float(goal_coor[1]))
    obs = []
    # point_all = []
    for data in datas:
        # point = []
        separate = list(data)
        point = millerToXY(float(separate[0]), float(separate[1]))
        obs.append(point)
    max_x = 0
    max_y = 0
    min_x = 1000000000
    min_y = 1000000000
    i = 0
    for point in obs:
        x = point[0]
        y = point[1]

        if x < 25579916:
            print("xxxxxxxxxxxxx")
            print(i)
        i += 1
        max_x = max(x, max_x)
        max_y = max(y, max_y)
        min_x = min(x, min_x)
        min_y = min(y, min_y)

    max_x = max(max_x, point_start[0], point_goal[0])
    min_x = min(min_x, point_start[0], point_goal[0])
    max_y = max(max_y, point_start[1], point_goal[1])
    min_y = min(min_y, point_start[1], point_goal[1])
    multi = 20
    start = point_start
    start[0] = multi * float(start[0] - min_x) / float(max_x - min_x)
    start[1] = multi * float(start[1] - min_y) / float(max_y - min_y)
    goal = point_goal
    goal[0] = multi * float(goal[0] - min_x) / float(max_x - min_x)
    goal[1] = multi * float(goal[1] - min_y) / float(max_y - min_y)
    for point in obs:
        point[0] = multi * float(point[0] - min_x) / float(max_x - min_x)
        point[1] = multi * float(point[1] - min_y) / float(max_y - min_y)
    # print("===============")
    # print(obs)
    # Set and draw the start and end points

    is_plot = True
    if is_plot:
        fig = plt.figure(figsize=(7, 7))
        subplot = fig.add_subplot(111)
        subplot.set_xlabel('X-distance: m')
        subplot.set_ylabel('Y-distance: m')
        subplot.plot(start[0], start[1], '*r')
        subplot.plot(goal[0], goal[1], '*r')
        print("===========================")
    # Obstacle setting and drawing
    # obs = [[1, 4], [2, 4], [3, 3], [6, 1], [6, 7], [10, 6], [11, 12], [14, 14]]
    # print('obstacles: {0}'.format(obs))
    for i in range(0):
        obs.append([random.uniform(2, goal[1] - 1), random.uniform(2, goal[1] - 1)])

    if is_plot:
        for OB in obs:
            circle = Circle(xy=(OB[0], OB[1]), radius=rr, alpha=0.3)
            subplot.add_patch(circle)
            subplot.plot(OB[0], OB[1], 'xk')

    # t1 = time.time()
    # for i in range(1000):

    # path plan
    if is_plot:
        apf = APF_Improved(start, goal, obs, k_att, k_rep, rr, step_size, max_iters, goal_threashold, is_plot)
    else:
        apf = APF_Improved(start, goal, obs, k_att, k_rep, rr, step_size, max_iters, goal_threashold, is_plot)
    print('####')
    apf.path_plan(subplot)
    if apf.is_path_plan_success:
        path = apf.path
        path_ = []
        i = int(step_size_ / step_size)
        while (i < len(path)):
            path_.append(path[i])
            i += int(step_size_ / step_size)

        if path_[-1] != path[-1]:  # Add the last point
            path_.append(path[-1])
        print('planed path points:{}'.format(path_))
        print('path plan success')
        if is_plot:
            px, py = [K[0] for K in path_], [K[1] for K in path_]  # Path point x coordinate list, y coordinate list
            subplot.plot(px, py, '^k')
            plt.show()
    else:
        print('path plan failed')
    # t2 = time.time()
    # print('Time to find 1000 times:{}, one time to find the path:{}'.format(t2-t1, (t2-t1)/1000))


# if __name__ == '__main__':
# Related parameter settings


# function()
