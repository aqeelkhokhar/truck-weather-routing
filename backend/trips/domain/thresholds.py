from dataclasses import dataclass

from trips.domain.levels import RiskLevel


@dataclass(frozen=True)
class Band:
    level: RiskLevel
    minimum: float
    inclusive: bool = True

    def reached_by(self, value):
        return value >= self.minimum if self.inclusive else value > self.minimum


WIND_BANDS = (
    Band(RiskLevel.NO_TRAVEL, 55),
    Band(RiskLevel.SEVERE, 45),
    Band(RiskLevel.HIGH, 35),
    Band(RiskLevel.MODERATE, 25),
)

RAIN_BANDS = (
    Band(RiskLevel.NO_TRAVEL, 1.00, inclusive=False),
    Band(RiskLevel.SEVERE, 0.50),
    Band(RiskLevel.HIGH, 0.25),
    Band(RiskLevel.MODERATE, 0.10),
)

SNOW_BANDS = (
    Band(RiskLevel.NO_TRAVEL, 3.0, inclusive=False),
    Band(RiskLevel.SEVERE, 2.0),
    Band(RiskLevel.HIGH, 1.0),
    Band(RiskLevel.MODERATE, 0.5),
)


@dataclass(frozen=True)
class LoadRule:
    wind_minimum: float
    wind_maximum: float
    load_minimum_lb: float | None
    level: RiskLevel

    def applies_to(self, wind_mph, load_lb):
        if not self.wind_minimum <= wind_mph < self.wind_maximum:
            return False
        return self.load_minimum_lb is None or load_lb > self.load_minimum_lb


LOAD_RULES = (
    LoadRule(55, float("inf"), None, RiskLevel.NO_TRAVEL),
    LoadRule(45, 55, 30_000, RiskLevel.NO_TRAVEL),
    LoadRule(35, 45, 40_000, RiskLevel.SEVERE),
)
