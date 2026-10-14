from dataclasses import dataclass


@dataclass(frozen=True)
class Weather:
    wind_mph: float
    rain_in_per_hr: float
    snow_in_per_hr: float
