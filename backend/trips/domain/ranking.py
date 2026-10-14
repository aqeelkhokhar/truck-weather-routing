from dataclasses import dataclass

from trips.domain.levels import RiskLevel


@dataclass(frozen=True)
class RouteSummary:
    route_id: str
    distance_miles: float
    duration_seconds: float
    severe_miles: float
    high_miles: float
    no_travel_miles: float
    average_risk: float

    @property
    def blocked(self):
        return self.no_travel_miles > 0

    @property
    def sort_key(self):
        return (
            self.blocked,
            self.severe_miles,
            self.high_miles,
            self.average_risk,
            self.duration_seconds,
        )


def summarize_route(route, assessed):
    total = sum(item.checkpoint.miles_covered for item in assessed)

    def miles_at(level):
        return sum(item.checkpoint.miles_covered for item in assessed if item.level == level)

    weighted = sum(item.checkpoint.miles_covered * int(item.level) for item in assessed)
    return RouteSummary(
        route_id=route.id,
        distance_miles=route.distance_miles,
        duration_seconds=route.duration_seconds,
        severe_miles=miles_at(RiskLevel.SEVERE),
        high_miles=miles_at(RiskLevel.HIGH),
        no_travel_miles=miles_at(RiskLevel.NO_TRAVEL),
        average_risk=weighted / total if total else 0.0,
    )


def rank_routes(summaries):
    return sorted(summaries, key=lambda summary: summary.sort_key)
