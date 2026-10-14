from dataclasses import dataclass
from datetime import timedelta

from trips.clients.geocoding import geocode
from trips.clients.routing import fetch_routes
from trips.clients.weather import fetch_forecasts, snap
from trips.constants import FORECAST_HOURS
from trips.domain.models import AssessedCheckpoint
from trips.domain.ranking import decisive_criterion, rank_routes, summarize_route
from trips.domain.risk import assess_weather
from trips.domain.sampling import sample_checkpoints
from trips.errors import SamePlaceError


@dataclass(frozen=True)
class RoutePlan:
    route: object
    assessed: list
    summary: object


@dataclass(frozen=True)
class TripPlan:
    origin: object
    destination: object
    plans: list
    recommended_id: str
    decided_by: str
    all_blocked: bool
    heatmap: dict


def assess_route(route, checkpoints, forecasts, load_lb):
    assessed = []
    for checkpoint in checkpoints:
        series = forecasts[snap((checkpoint.lat, checkpoint.lon))]
        weather = series.at(checkpoint.eta)
        assessed.append(AssessedCheckpoint(checkpoint, weather, assess_weather(weather, load_lb)))
    return RoutePlan(route, assessed, summarize_route(route, assessed))


def build_heatmap(plans, forecasts, load_lb, now):
    points = dict.fromkeys(
        snap((item.checkpoint.lat, item.checkpoint.lon)) for plan in plans for item in plan.assessed
    )
    rows = []
    base_time = None
    for point in points:
        series = forecasts[point]
        base = series.index_at(now)
        base_time = series.start + timedelta(hours=base)
        levels = [
            int(assess_weather(series.at_index(min(base + hour, series.hours - 1)), load_lb))
            for hour in range(FORECAST_HOURS + 1)
        ]
        rows.append({"lat": point[0], "lon": point[1], "levels": levels})
    return {"base_time": base_time, "hours": FORECAST_HOURS, "points": rows}


def plan_trip(request, now):
    origin = geocode(request["origin"])
    destination = geocode(request["destination"])
    if (origin.lat, origin.lon) == (destination.lat, destination.lon):
        raise SamePlaceError
    routes = fetch_routes((origin.lat, origin.lon), (destination.lat, destination.lon))
    spacing = request["spacing_miles"]
    sampled = [sample_checkpoints(route, spacing, request["departure"]) for route in routes]
    forecasts = fetch_forecasts(
        [(point.lat, point.lon) for checkpoints in sampled for point in checkpoints]
    )
    plans = [
        assess_route(route, checkpoints, forecasts, request["load_lb"])
        for route, checkpoints in zip(routes, sampled, strict=True)
    ]
    ranked = rank_routes([plan.summary for plan in plans])
    decided_by = decisive_criterion(ranked[0], ranked[1]) if len(ranked) > 1 else "only_route"
    return TripPlan(
        origin=origin,
        destination=destination,
        plans=plans,
        recommended_id=ranked[0].route_id,
        decided_by=decided_by,
        all_blocked=all(summary.blocked for summary in ranked),
        heatmap=build_heatmap(plans, forecasts, request["load_lb"], now),
    )
