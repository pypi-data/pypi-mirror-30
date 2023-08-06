#!/usr/bin/python3

"""
This module is used to determine, whether or not a point on earth is within a given district.

Needs a GeoJSON file to get the data from. This is the only parameter, if it's run as an executable.
e.g.: python3 districtsTk.py my/favourite/cities/geo.json
"""

import argparse
import json

# Definitions:
# - A coordinate is a float representing the longitude or latitude, like 9.72839349542828 or 52.427206400296.
# - A coord-set is a list containing a longitude and a latitude (in this order).
# - A polygon is a list of coord-sets.
# - A district is a list of polygons.


class DistrictHelper:
    """
    Hold all the relevant info given in a valid 'geo.json'.
    """
    def __init__(self, geo_json):
        self.districts_dict = None
        self._read_geo_json(geo_json)

    def _read_geo_json(self, geo_json):
        self.districts_dict = dict()
        with open(geo_json, 'r') as f:
            data = json.load(f)
            for district in data['features']:
                name = district['properties']['STADTTLNAM']
                if not name:
                    continue
                self.districts_dict[name] = []
                if district['geometry']['type'] == 'MultiPolygon':
                    for subpoly in district['geometry']['coordinates']:
                        self.districts_dict[name].append(subpoly)
                else:
                    self.districts_dict[name] = district['geometry']['coordinates']

    @classmethod
    def _is_point_on_line_segment(cls, px, py, l0x, l0y, l1x, l1y):
        """Return whether the point described by px,py lies on the line-segment l0x,l0y - l1x,l1y."""
        if l0x == l1x:
            small_y, big_y = sorted((l0y, l1y))
            return px == l0x and small_y <= py <= big_y
        # m is the slope of our line.
        m = (l1y - l0y) / (l1x - l0x)
        # Now we take the equation for our line and insert the x-value of our point.
        eq = (m * (px - l0x) + l0y)
        # If eq equals py (or is very close) then the point is on the line.
        if abs(eq-py) < 0.000000001:
            # Okay, the point is on the line. Now check if it's on the line segment.
            small_x, big_x = sorted((l0x, l1x))
            return small_x <= px <= big_x
        return False

    def point_crosses_line_segment(self, px, py, l0x, l0y, l1x, l1y):
        """Draw a horizontal line from the point to the right and check whether it crosses the line.
        We have two line segments ("Strecken"), one going from our point p to the right (to infinity) and the other one
        is the given line segment.
        This is the plan:
        1. We calculate the lines ("Geraden") that contain our line segments.
        2. We calculate where these lines intersect.
        3. We check whether that point of intersection lies on both line segments. If it does, the line segments
           intersect."""
        diff_x = l1x - l0x
        diff_y = l1y - l0y
        if diff_x < 0:
            diff_x *= -1
            diff_y *= -1

        if diff_x == 0:
            # line is vertical
            small_y, big_y = sorted((l0y, l1y))
            return px < l0x and small_y < py < big_y

        if diff_y == 0:
            # line is horizontal
            small_x, big_x = sorted((l0x, l1x))
            return py == l0y and px <= big_x

        ml = diff_y / diff_x
        # y=m*x+n "Geradengleichung"
        np = py
        nl = l0y - (ml * l0x)
        x = (np - nl) / ml
        # Okay, that's not infinity, but it's close enough for our use case.
        infinity = px + 500
        is_a = self._is_point_on_line_segment(x, py, l0x, l0y, l1x, l1y)
        is_b = self._is_point_on_line_segment(x, py, px, py, infinity, py)
        return is_a and is_b

    def is_point_in_polygon(self, px, py, polygon):
        """This function gets a point and polygon. The polygon is a list of lists containing two floats each.
        It draws a line from the point to the right (to infinity) and checks how many times it intersects the polygon's
        borders.
        There are four cases:
        1. It does not intersect => point is outside
        2. The number of intersections is even => point is outside
        3. The number of intersections is odd => point is inside
        4. The number of intersections is infinite => point is exactly on a border of the polygon. We better check that
        first to avoid exceptions."""
        x = 0
        y = 1
        intersections = 0
        line_count = len(polygon)
        for i in range(line_count - 1):
            j = i + 1
            # Two points make a line segment ("Strecke").
            if self.point_crosses_line_segment(px, py, polygon[i][x], polygon[i][y], polygon[j][x], polygon[j][y]):
                intersections += 1
        return intersections % 2 != 0

    @staticmethod
    def is_point_in_polygon_fast(px, py, poly):
        j = len(poly) - 1
        odd_nodes = False
        for i in range(len(poly)):
            if ((poly[i][0] < py <= poly[j][0] or
                 poly[j][0] < py <= poly[i][0]) and (poly[i][1] <= px or poly[j][1] <= px)):
                odd_nodes ^= (
                    poly[i][1] + (py - poly[i][0]) / (poly[j][0] - poly[i][0]) * (poly[j][1] - poly[i][1]) < px)
            j = i
        return odd_nodes

    def find_district(self, lon, lat):
        for district in self.districts_dict:
            for polygon in self.districts_dict[district]:
                if self.is_point_in_polygon(lon, lat, polygon):
                    return district
        return None

    @staticmethod
    def sanitize_district(district):
        """Escape various german umlauts, as well as space and minus and return the result in lowercase."""
        replacements = {" ": "",
                        "-": "",
                        "ä": "ae",
                        "ö": "oe",
                        "ü": "ue",
                        "ß": "ss"}
        district = district.lower()
        for k, v in replacements.items():
            district.replace(k, v)
        return district


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='A script to check whether or not a point on earth is within a \
                                                        given district. Needs a GeoJSON file to get the data from.')
    parser.add_argument('geoJSON', help='Path to the GeoJSON file containing information about the districts.')
    args = parser.parse_args()

    dh = DistrictHelper(args.geoJSON)
    # fixme (aiyion): this main is not useful. Coordinates should be configurable.
    print(dh.find_district(9.709290862, 52.374701849))
