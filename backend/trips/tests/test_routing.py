import re

import pytest
import responses

from trips.clients.routing import fetch_routes, osrm_path
from trips.errors import NoRouteFoundError

ORIGIN = (40.0, -100.0)
DESTINATION = (40.0, -98.0)
OSRM_URL = re.compile(r"https://router\.project-osrm\.org/route/v1/driving/.*")


def osrm_route(latitude_shift, duration):
    coordinates = [[-100.0 + step * 0.1, 40.0 + latitude_shift * step] for step in range(21)]
    return {
        "distance": 170_000,
        "duration": duration,
        "geometry": {"coordinates": coordinates},
    }


def payload(*routes):
    return {"code": "Ok", "routes": list(routes)}


def test_osrm_path_orders_longitude_first():
    assert osrm_path([ORIGIN, DESTINATION]) == "-100.0,40.0;-98.0,40.0"


@responses.activate
def test_three_alternatives_are_returned_sorted_by_duration():
    responses.add(
        responses.GET,
        OSRM_URL,
        json=payload(osrm_route(0.0, 9000), osrm_route(0.05, 6000), osrm_route(-0.05, 7000)),
    )
    routes = fetch_routes(ORIGIN, DESTINATION)
    assert [route.id for route in routes] == ["route-1", "route-2", "route-3"]
    assert [route.duration_seconds for route in routes] == [6000, 7000, 9000]
    assert len(responses.calls) == 1


@responses.activate
def test_missing_alternatives_are_filled_with_detours():
    responses.add(responses.GET, OSRM_URL, json=payload(osrm_route(0.0, 6000)))
    responses.add(responses.GET, OSRM_URL, json=payload(osrm_route(0.3, 7000)))
    responses.add(responses.GET, OSRM_URL, json=payload(osrm_route(-0.3, 8000)))
    routes = fetch_routes(ORIGIN, DESTINATION)
    assert len(routes) == 3


@responses.activate
def test_detour_identical_to_primary_is_discarded():
    responses.add(responses.GET, OSRM_URL, json=payload(osrm_route(0.0, 6000)))
    responses.add(responses.GET, OSRM_URL, json=payload(osrm_route(0.0, 6100)))
    routes = fetch_routes(ORIGIN, DESTINATION)
    assert len(routes) == 1


@responses.activate
def test_no_route_raises():
    responses.add(responses.GET, OSRM_URL, json={"code": "NoRoute", "routes": []})
    with pytest.raises(NoRouteFoundError):
        fetch_routes(ORIGIN, DESTINATION)


@responses.activate
def test_routes_are_cached():
    responses.add(
        responses.GET,
        OSRM_URL,
        json=payload(osrm_route(0.0, 9000), osrm_route(0.05, 6000), osrm_route(-0.05, 7000)),
    )
    fetch_routes(ORIGIN, DESTINATION)
    fetch_routes(ORIGIN, DESTINATION)
    assert len(responses.calls) == 1
