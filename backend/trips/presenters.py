from trips.domain.ranking import RouteSummary


def present_location(location):
    return {"name": location.name, "lat": location.lat, "lon": location.lon}


def present_checkpoint(item):
    checkpoint = item.checkpoint
    return {
        "index": checkpoint.index,
        "mile": round(checkpoint.mile, 1),
        "lat": checkpoint.lat,
        "lon": checkpoint.lon,
        "eta": checkpoint.eta,
        "level": item.level.name,
        "weather": {
            "wind_mph": round(item.weather.wind_mph, 1),
            "rain_in_per_hr": round(item.weather.rain_in_per_hr, 2),
            "snow_in_per_hr": round(item.weather.snow_in_per_hr, 2),
        },
    }


def present_summary(summary: RouteSummary):
    return {
        "distance_miles": round(summary.distance_miles, 1),
        "duration_seconds": round(summary.duration_seconds),
        "severe_miles": round(summary.severe_miles, 1),
        "high_miles": round(summary.high_miles, 1),
        "no_travel_miles": round(summary.no_travel_miles, 1),
        "average_risk": round(summary.average_risk, 2),
        "blocked": summary.blocked,
    }


def present_route(plan, recommended_id):
    return {
        "id": plan.route.id,
        "recommended": plan.route.id == recommended_id,
        "geometry": [[round(lat, 5), round(lon, 5)] for lat, lon in plan.route.geometry],
        "summary": present_summary(plan.summary),
        "checkpoints": [present_checkpoint(item) for item in plan.assessed],
    }


def present_trip(trip):
    return {
        "origin": present_location(trip.origin),
        "destination": present_location(trip.destination),
        "recommendation": {
            "route_id": trip.recommended_id,
            "decided_by": trip.decided_by,
            "all_routes_blocked": trip.all_blocked,
        },
        "routes": [present_route(plan, trip.recommended_id) for plan in trip.plans],
        "heatmap": trip.heatmap,
    }
