from django.conf import settings
from django.core.cache import cache

from trips.clients.cache_keys import cache_key
from trips.clients.http import get_json
from trips.constants import (
    ALTERNATE_OVERLAP_LIMIT,
    DETOUR_RATIO_LIMIT,
    MAX_ROUTES,
    MAX_VIA_ATTEMPTS,
    METERS_PER_MILE,
    OVERLAP_REFERENCE_VERTICES,
    OVERLAP_SAMPLE_COUNT,
    OVERLAP_TOLERANCE_MILES,
    ROUTE_CACHE_SECONDS,
    ROUTE_KEY_PRECISION,
    VIA_OFFSET_RATIO,
    VIA_POSITIONS,
)
from trips.domain.geo import cumulative_miles, overlap_ratio, perpendicular_offset
from trips.domain.models import Route
from trips.errors import ExternalServiceError, NoRouteFoundError


def osrm_path(waypoints):
    return ";".join(f"{lon},{lat}" for lat, lon in waypoints)


def request_routes(waypoints, alternatives):
    url = f"{settings.OSRM_BASE_URL}/route/v1/driving/{osrm_path(waypoints)}"
    payload = get_json(
        url,
        params={
            "alternatives": str(MAX_ROUTES if alternatives else 0).lower(),
            "overview": "full",
            "geometries": "geojson",
            "steps": "false",
        },
    )
    if payload.get("code") == "NoRoute":
        raise NoRouteFoundError
    if payload.get("code") != "Ok":
        raise ExternalServiceError
    return [parse_route(item) for item in payload["routes"]]


def parse_route(item):
    geometry = tuple((lat, lon) for lon, lat in item["geometry"]["coordinates"])
    return Route(
        id="",
        geometry=geometry,
        distance_miles=item["distance"] / METERS_PER_MILE,
        duration_seconds=item["duration"],
    )


def decimate(geometry):
    return geometry[:: max(1, len(geometry) // OVERLAP_REFERENCE_VERTICES)]


def is_distinct(candidate, accepted):
    return all(
        overlap_ratio(
            candidate.geometry,
            decimate(route.geometry),
            OVERLAP_TOLERANCE_MILES,
            OVERLAP_SAMPLE_COUNT,
        )
        < ALTERNATE_OVERLAP_LIMIT
        for route in accepted
    )


def via_candidates(primary):
    totals = cumulative_miles(primary.geometry)
    offset_miles = totals[-1] * VIA_OFFSET_RATIO
    for position, side in VIA_POSITIONS:
        yield perpendicular_offset(
            primary.geometry, totals, totals[-1] * position, offset_miles * side
        )


def add_detour_routes(origin, destination, routes):
    shortest = min(route.distance_miles for route in routes)
    attempts = 0
    for via in via_candidates(routes[0]):
        if len(routes) >= MAX_ROUTES or attempts >= MAX_VIA_ATTEMPTS:
            break
        attempts += 1
        try:
            found = request_routes([origin, via, destination], alternatives=False)
        except (ExternalServiceError, NoRouteFoundError):
            continue
        candidate = found[0]
        within_detour = candidate.distance_miles <= shortest * DETOUR_RATIO_LIMIT
        if within_detour and is_distinct(candidate, routes):
            routes.append(candidate)
    return routes


def label_routes(routes):
    ordered = sorted(routes, key=lambda route: route.duration_seconds)
    return [
        Route(f"route-{position}", item.geometry, item.distance_miles, item.duration_seconds)
        for position, item in enumerate(ordered, start=1)
    ]


def cache_token(point):
    return ",".join(str(round(value, ROUTE_KEY_PRECISION)) for value in point)


def fetch_routes(origin, destination):
    key = cache_key("routes", cache_token(origin), cache_token(destination))
    cached = cache.get(key)
    if cached:
        return cached
    routes = request_routes([origin, destination], alternatives=True)
    if not routes:
        raise NoRouteFoundError
    routes = routes[:MAX_ROUTES]
    if len(routes) < MAX_ROUTES:
        routes = add_detour_routes(origin, destination, routes)
    labelled = label_routes(routes)
    cache.set(key, labelled, ROUTE_CACHE_SECONDS)
    return labelled
