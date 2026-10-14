from bisect import bisect_right
from math import asin, cos, radians, sin, sqrt

EARTH_RADIUS_MILES = 3958.8


def haversine_miles(start, end):
    lat1, lon1 = map(radians, start)
    lat2, lon2 = map(radians, end)
    half_chord = sin((lat2 - lat1) / 2) ** 2 + cos(lat1) * cos(lat2) * sin((lon2 - lon1) / 2) ** 2
    return 2 * EARTH_RADIUS_MILES * asin(sqrt(half_chord))


def cumulative_miles(points):
    totals = [0.0]
    for previous, current in zip(points, points[1:], strict=False):
        totals.append(totals[-1] + haversine_miles(previous, current))
    return totals


def point_at_mile(points, totals, mile):
    if mile <= 0:
        return points[0]
    if mile >= totals[-1]:
        return points[-1]
    upper = bisect_right(totals, mile)
    lower = upper - 1
    span = totals[upper] - totals[lower]
    ratio = (mile - totals[lower]) / span if span else 0.0
    lat = points[lower][0] + (points[upper][0] - points[lower][0]) * ratio
    lon = points[lower][1] + (points[upper][1] - points[lower][1]) * ratio
    return lat, lon


MILES_PER_DEGREE_LATITUDE = 69.09


def perpendicular_offset(points, totals, mile, offset_miles):
    lat, lon = point_at_mile(points, totals, mile)
    ahead = point_at_mile(points, totals, mile + 1.0)
    behind = point_at_mile(points, totals, mile - 1.0)
    scale = cos(radians(lat))
    north = ahead[0] - behind[0]
    east = (ahead[1] - behind[1]) * scale
    length = sqrt(north**2 + east**2) or 1.0
    shift_north = -east / length * offset_miles / MILES_PER_DEGREE_LATITUDE
    shift_east = north / length * offset_miles / (MILES_PER_DEGREE_LATITUDE * scale)
    return lat + shift_north, lon + shift_east


def overlap_ratio(candidate, existing, tolerance_miles, sample_count):
    step = max(1, len(candidate) // sample_count)
    samples = candidate[::step]
    near = sum(
        1
        for sample in samples
        if min(haversine_miles(sample, vertex) for vertex in existing) <= tolerance_miles
    )
    return near / len(samples)
