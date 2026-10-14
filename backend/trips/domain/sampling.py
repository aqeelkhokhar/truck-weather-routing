from datetime import timedelta

from trips.domain.geo import cumulative_miles, point_at_mile
from trips.domain.models import Checkpoint


def checkpoint_miles(total_miles, spacing_miles):
    marks = []
    mile = 0.0
    while mile < total_miles:
        marks.append(mile)
        mile += spacing_miles
    marks.append(total_miles)
    return marks


def covered_miles(marks):
    covered = []
    for position, mile in enumerate(marks):
        start = 0.0 if position == 0 else (marks[position - 1] + mile) / 2
        end = marks[-1] if position == len(marks) - 1 else (mile + marks[position + 1]) / 2
        covered.append(end - start)
    return covered


def sample_checkpoints(route, spacing_miles, departure):
    totals = cumulative_miles(route.geometry)
    geometry_miles = totals[-1]
    marks = checkpoint_miles(geometry_miles, spacing_miles)
    spans = covered_miles(marks)
    checkpoints = []
    for index, mile in enumerate(marks):
        lat, lon = point_at_mile(route.geometry, totals, mile)
        elapsed = route.duration_seconds * (mile / geometry_miles if geometry_miles else 0.0)
        checkpoints.append(
            Checkpoint(
                index=index,
                mile=mile,
                lat=lat,
                lon=lon,
                eta=departure + timedelta(seconds=elapsed),
                miles_covered=spans[index],
            )
        )
    return checkpoints
