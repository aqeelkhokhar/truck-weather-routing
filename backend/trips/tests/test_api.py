from datetime import UTC, datetime, timedelta

import pytest
from rest_framework.test import APIClient

from trips.clients.geocoding import Location
from trips.clients.weather import snap
from trips.domain.geo import cumulative_miles
from trips.domain.models import Route
from trips.domain.sampling import sample_checkpoints
from trips.domain.weather import WeatherSeries
from trips.services import planner

HOURS = 120
NOW = datetime.now(UTC).replace(minute=0, second=0, microsecond=0)
LINE_A = ((40.0, -100.0), (40.0, -99.0), (40.0, -98.0))
LINE_B = ((40.0, -100.0), (40.5, -99.0), (40.0, -98.0))


def build_route(route_id, geometry, duration):
    return Route(route_id, geometry, cumulative_miles(geometry)[-1], duration)


def flat_series(wind):
    zeros = (0.0,) * HOURS
    return WeatherSeries(NOW, (wind,) * HOURS, zeros, zeros)


@pytest.fixture
def stub_services(monkeypatch):
    routes = [build_route("route-1", LINE_A, 7200), build_route("route-2", LINE_B, 9000)]

    def fake_forecasts(points):
        windy = {snap(point) for point in LINE_A[1:2]}
        return {snap(p): flat_series(50.0 if snap(p) in windy else 5.0) for p in points}

    monkeypatch.setattr(
        planner, "geocode", lambda query: Location(query, 40.0, -100.0 if "A" in query else -98.0)
    )
    monkeypatch.setattr(planner, "fetch_routes", lambda origin, destination: routes)
    monkeypatch.setattr(planner, "fetch_forecasts", fake_forecasts)
    return routes


def payload(**overrides):
    body = {
        "origin": "Town A",
        "destination": "Town B",
        "departure": (datetime.now(UTC) + timedelta(hours=2)).isoformat(),
        "load_lb": 20_000,
        "spacing_miles": 25,
    }
    body.update(overrides)
    return body


def post(body):
    return APIClient().post("/api/plan/", body, format="json")


@pytest.mark.django_db
def test_health_endpoint():
    assert APIClient().get("/api/health/").json() == {"status": "ok"}


def test_plan_returns_routes_with_checkpoints(stub_services):
    response = post(payload())
    assert response.status_code == 200
    body = response.json()
    assert [route["id"] for route in body["routes"]] == ["route-1", "route-2"]
    assert body["routes"][0]["checkpoints"][0]["level"] in {"LOW", "MODERATE", "HIGH", "SEVERE"}
    assert body["origin"]["name"] == "Town A"


def test_plan_recommends_route_avoiding_windy_corridor(stub_services):
    body = post(payload(spacing_miles=10)).json()
    recommended = [route for route in body["routes"] if route["recommended"]]
    assert len(recommended) == 1
    assert body["recommendation"]["route_id"] == recommended[0]["id"]
    assert body["recommendation"]["decided_by"] != "tie"


def test_plan_includes_heatmap_for_every_forecast_hour(stub_services):
    body = post(payload()).json()
    heatmap = body["heatmap"]
    assert heatmap["hours"] == 48
    assert heatmap["points"]
    assert all(len(point["levels"]) == 49 for point in heatmap["points"])


def test_heavy_load_changes_levels(stub_services, monkeypatch):
    monkeypatch.setattr(
        planner,
        "fetch_forecasts",
        lambda points: {snap(point): flat_series(40.0) for point in points},
    )
    light = post(payload(load_lb=10_000)).json()["routes"][0]["summary"]
    heavy = post(payload(load_lb=45_000)).json()["routes"][0]["summary"]
    assert light["severe_miles"] == 0
    assert heavy["severe_miles"] > 0


@pytest.mark.parametrize(
    "overrides",
    [
        {"load_lb": -1},
        {"load_lb": 500_000},
        {"spacing_miles": 15},
        {"origin": ""},
        {"destination": "town a", "origin": "Town A"},
        {"departure": "not a date"},
        {"departure": (datetime.now(UTC) + timedelta(hours=72)).isoformat()},
        {"departure": (datetime.now(UTC) - timedelta(days=2)).isoformat()},
    ],
)
def test_invalid_input_is_rejected(stub_services, overrides):
    assert post(payload(**overrides)).status_code == 400


def test_places_resolving_to_the_same_point_are_rejected(stub_services):
    response = post(payload(origin="Town B", destination="Town C"))
    assert response.status_code == 422
    assert "same place" in response.json()["detail"]


def test_spacing_defaults_to_twenty_five(stub_services):
    body = payload()
    del body["spacing_miles"]
    assert post(body).status_code == 200


def test_sample_helper_matches_planner_checkpoint_count(stub_services):
    expected = len(sample_checkpoints(stub_services[0], 25, NOW))
    body = post(payload(departure=NOW.isoformat())).json()
    assert len(body["routes"][0]["checkpoints"]) == expected
