#*************************************************************************#
#   Description :                                                         #
#                 Script for creating waypoints on the edges              #
#                 which covers whole area                                 #
#                 in optimal manner for given parameter                   #
#   Parameters :                                                          #
#                < List of GPS points covering Parameters >               #
#                                                                         #
#**************************V - 1.0****************************************#
#   Date : 19-October-2018   By: Gautam  & Atul                           #
#   Initial draft of the script                                           #
#                                                                         #
#*************************************************************************#


import numpy as np
from scipy.interpolate import splprep, splev
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, Point
import matplotlib.pyplot as plt

class global_path_coverage:
    def __init__(self,sep=1):
        self.latitudes = []
        self.longitudes = None
        self.waypoint_order = []
        self.poly = None
        
        
    def set_polygons(self,coordinates):
        
        self.poly = Polygon(coordinates)
        
        
    def generate_waypoint(self,coordinates):
        self.set_polygons(coordinates)
        minx, miny, maxx, maxy = self.poly.bounds
        self.longitudes = np.arange(minx, maxx+0.00001,0.00001)
        for point in coordinates :
            if point[1] not in self.latitudes:
                self.latitudes.append(point[1])

        for lng in range(len(self.longitudes)):
            count = 0
            for lat in self.latitudes:
                point = Point(self.longitudes[lng],lat)
                if self.poly.boundary.contains(point) and count is not 2:
                    self.waypoint_order.append([lat,self.longitudes[lng]])
                    count = count+1
        return self.waypoint_order


# c1 = global_path_coverage()
# c1.generate_waypoint([[12.35874, 76.59436], [12.35894, 76.59436], [12.35894, 76.59416], [12.35874, 76.59416]])
# print len(c1.waypoint_order)
