from datetime import UTC, datetime, timedelta

import pytest

from trips.domain.geo import cumulative_miles, haversine_miles, point_at_mile
from trips.domain.models import Route
from trips.domain.sampling import checkpoint_miles, covered_miles, sample_checkpoints

DEPARTURE = datetime(2026, 11, 1, 8, 0, tzinfo=UTC)
STRAIGHT_LINE = ((40.0, -100.0), (40.0, -99.0), (40.0, -98.0))


def build_route(duration_seconds=7200):
    miles = cumulative_miles(STRAIGHT_LINE)[-1]
    return Route("r1", STRAIGHT_LINE, miles, duration_seconds)


def test_haversine_one_degree_of_latitude():
    assert haversine_miles((40.0, -100.0), (41.0, -100.0)) == pytest.approx(69.09, abs=0.1)


def test_point_at_mile_midpoint_of_segment():
    totals = cumulative_miles(STRAIGHT_LINE)
    lat, lon = point_at_mile(STRAIGHT_LINE, totals, totals[1] / 2)
    assert lat == pytest.approx(40.0)
    assert lon == pytest.approx(-99.5)


def test_point_at_mile_clamps_to_ends():
    totals = cumulative_miles(STRAIGHT_LINE)
    assert point_at_mile(STRAIGHT_LINE, totals, -5) == STRAIGHT_LINE[0]
    assert point_at_mile(STRAIGHT_LINE, totals, totals[-1] + 5) == STRAIGHT_LINE[-1]


def test_checkpoint_miles_end_at_destination():
    assert checkpoint_miles(100, 25) == [0.0, 25.0, 50.0, 75.0, 100]


def test_checkpoint_miles_keeps_partial_final_stretch():
    assert checkpoint_miles(60, 25) == [0.0, 25.0, 50.0, 60]


def test_covered_miles_sum_to_route_length():
    marks = checkpoint_miles(137.5, 25)
    assert sum(covered_miles(marks)) == pytest.approx(137.5)


def test_first_and_last_checkpoints_cover_half_stretches():
    spans = covered_miles([0.0, 10.0, 20.0])
    assert spans == [5.0, 10.0, 5.0]


def test_sample_checkpoints_eta_scales_with_distance():
    route = build_route(7200)
    checkpoints = sample_checkpoints(route, 50, DEPARTURE)
    assert checkpoints[0].eta == DEPARTURE
    assert checkpoints[-1].eta == DEPARTURE + timedelta(seconds=7200)
    assert checkpoints[1].eta > checkpoints[0].eta


def test_sample_checkpoints_indexes_are_sequential():
    checkpoints = sample_checkpoints(build_route(), 25, DEPARTURE)
    assert [point.index for point in checkpoints] == list(range(len(checkpoints)))


def test_sample_checkpoints_cover_whole_route():
    route = build_route()
    checkpoints = sample_checkpoints(route, 25, DEPARTURE)
    assert sum(point.miles_covered for point in checkpoints) == pytest.approx(
        cumulative_miles(route.geometry)[-1]
    )
