from sklearn.cluster import DBSCAN
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
import random
from diffprivlib import mechanisms

from shapely.geometry import Polygon



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


def xy_to_coor(x, y):
    '''
    Convert xy coordinates to latitude and longitude
    :param x:
    :param y:
    :return:
    '''
    lonlat_coordinate = []
    L = 6381372 * math.pi * 2
    W = L
    H = L / 2
    mill = 2.3
    lat = ((H / 2 - y) * 2 * mill) / (1.25 * H)
    lat = ((math.atan(math.exp(lat)) - 0.25 * math.pi) * 180) / (0.4 * math.pi)
    lon = (x - W / 2) * 360 / W
    lonlat_coordinate.append((round(lon, 6), round(lat, 6)))
    return lonlat_coordinate


def read_csv(file):
    data = pd.read_csv(file)
    x = data["1"]
    y = data["0"]
    points_xy = []
    for i, j in zip(x, y):
        # Convert latitude and longitude to xy coordinates
        points_xy.append(millerToXY(i, j))
    return np.array(points_xy).squeeze()


def read_csv2(file):
    data = pd.read_csv(file)
    x = data["1"]
    y = data["0"]
    points_xy = []
    for i, j in zip(x, y):
        # Convert latitude and longitude to xy coordinates
        points_xy.append([i, j])
    return np.array(points_xy).squeeze()


def get_datas(longitude, latitude):
    '''
    read data
    :param longitude:
    :param latitude:
    :return:
    '''
    points_xy = []
    for i in range(len(longitude)):
        points_xy.append(millerToXY(longitude[i], latitude[i]))
    return np.array(points_xy).squeeze()


def get_datas2(longitude, latitude):
    points_xy = []
    for i, j in zip(longitude, latitude):
        # Convert latitude and longitude to xy coordinates
        points_xy.append([round(i, 6), round(j, 6)])
    return np.array(points_xy).squeeze()


def randomcolor():
    '''
    used in dbscan to color different cluster
    :return:
    '''
    colorArr = ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F']
    color = ""
    for i in range(6):
        color += colorArr[random.randint(0, 14)]
    return "#" + color


def dbs(data, data2, eps=300, min_samples=3):
    db = DBSCAN(eps=eps, min_samples=min_samples).fit(data)
    coreSamplesMask = np.zeros_like(db.labels_, dtype=bool)
    coreSamplesMask[db.core_sample_indices_] = True
    clusterLabels = db.labels_
    uniqueClusterLabels = set(clusterLabels)
    nClusters = len(uniqueClusterLabels) - (-1 in clusterLabels)

    colors = [randomcolor() for i in range(len(clusterLabels))]
    proxy = mechanisms.LaplaceBoundedNoise(epsilon=1.1, delta=0.1, sensitivity=0.0001)

    Data_result = []
    lishandians = []
    # Data_result stores a kind of point and the corresponding convex hull polygon tuple format
    for i, cluster in enumerate(uniqueClusterLabels):
        clusterIndex = (clusterLabels == cluster)
        coreSamples = data2[clusterIndex & coreSamplesMask]
        noiseSamples = data2[clusterIndex & ~coreSamplesMask]
        newCoreSample = []
        for point in coreSamples:
            dp_x = proxy.randomise(point[0])
            dp_y = proxy.randomise(point[1])
            newCoreSample.append([point[0], point[1]])
            newCoreSample.append([dp_x, dp_y])
        if len(newCoreSample) < 3:
            for point in coreSamples:
                dp_x = proxy.randomise(point[0])
                dp_y = proxy.randomise(point[1])
                newCoreSample.append([point[0], point[1]])
                newCoreSample.append([dp_x, dp_y])
        newCoreSample = np.array(newCoreSample)
        if (len(newCoreSample) >= 6):
            #Convex hull only if the number of points is greater than 3
            polygon = Polygon([*newCoreSample, *noiseSamples])
            ConvexHull = polygon.convex_hull
            ls = list(ConvexHull.boundary.coords)
            Data_result.append((newCoreSample, ls))
            #  According to the serial number connection, a convex polygon can be obtained
        else:
            lishandians = [*noiseSamples] #The value of the discrete point cluster is -1
    return Data_result, lishandians


def convex_hull(longitude, latitude):
    coordinates = get_datas(longitude, latitude)
    coordinates2 = get_datas2(longitude, latitude)
    res, lishandians = dbs(coordinates, coordinates2)
    convex_hull = []
    discrete_points = []
    count=[]
    for points, convex in res:
        count.append(len(points)/2)
        current_convex = []
        for item in convex:
            current_convex.append(list(item))
        convex_hull.append(current_convex)
    for point in lishandians:
        points = point.tolist()
        discrete_points.append(points)
    return convex_hull, discrete_points,count


if __name__ == "__main__":
    data = read_csv("points.csv")
    print("Data:", data)
    data2 = read_csv2("points.csv")
    print("Data2:", data2)

    res, lishandians = dbs(data, data2)
    for i, j in res:
        print("point set", i, "corresponding convex hull", j)

    for i in lishandians:
        print("outlier", i)
        print(i.tolist())
