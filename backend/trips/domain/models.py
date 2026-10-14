from dataclasses import dataclass
from datetime import datetime

from trips.domain.levels import RiskLevel
from trips.domain.weather import Weather


@dataclass(frozen=True)
class Route:
    id: str
    geometry: tuple
    distance_miles: float
    duration_seconds: float


@dataclass(frozen=True)
class Checkpoint:
    index: int
    mile: float
    lat: float
    lon: float
    eta: datetime
    miles_covered: float


@dataclass(frozen=True)
class AssessedCheckpoint:
    checkpoint: Checkpoint
    weather: Weather
    level: RiskLevel
