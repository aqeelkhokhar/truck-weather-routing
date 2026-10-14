from datetime import UTC, datetime

import pytest

from trips.domain.levels import RiskLevel
from trips.domain.models import AssessedCheckpoint, Checkpoint, Route
from trips.domain.ranking import RouteSummary, rank_routes, summarize_route
from trips.domain.weather import Weather

CALM = Weather(0, 0, 0)
NOW = datetime(2026, 11, 1, tzinfo=UTC)


def assessed(miles, level):
    checkpoint = Checkpoint(0, 0.0, 0.0, 0.0, NOW, miles)
    return AssessedCheckpoint(checkpoint, CALM, level)


def summary(route_id, *, severe=0.0, high=0.0, no_travel=0.0, average=0.0, duration=3600.0):
    return RouteSummary(route_id, 100.0, duration, severe, high, no_travel, average)


def test_summarize_route_weights_by_miles_covered():
    route = Route("r1", (), 100.0, 5400.0)
    items = [
        assessed(20, RiskLevel.SEVERE),
        assessed(30, RiskLevel.HIGH),
        assessed(50, RiskLevel.LOW),
    ]
    result = summarize_route(route, items)
    assert result.severe_miles == 20
    assert result.high_miles == 30
    assert result.average_risk == pytest.approx((20 * 3 + 30 * 2) / 100)
    assert result.duration_seconds == 5400.0


def test_summarize_route_flags_no_travel_as_blocked():
    route = Route("r1", (), 10.0, 600.0)
    result = summarize_route(route, [assessed(10, RiskLevel.NO_TRAVEL)])
    assert result.blocked


def test_fewest_severe_miles_wins_first():
    ranked = rank_routes([summary("a", severe=5, high=0), summary("b", severe=0, high=90)])
    assert ranked[0].route_id == "b"


def test_fewest_high_miles_breaks_severe_tie():
    ranked = rank_routes([summary("a", high=30), summary("b", high=10)])
    assert ranked[0].route_id == "b"


def test_lowest_average_risk_breaks_high_tie():
    ranked = rank_routes([summary("a", average=1.4), summary("b", average=0.6)])
    assert ranked[0].route_id == "b"


def test_shortest_duration_is_final_tiebreaker():
    ranked = rank_routes([summary("a", duration=7200), summary("b", duration=3600)])
    assert ranked[0].route_id == "b"


def test_blocked_route_ranks_after_unblocked_even_if_cleaner():
    ranked = rank_routes([summary("a", no_travel=1), summary("b", severe=50, high=50)])
    assert ranked[0].route_id == "b"
