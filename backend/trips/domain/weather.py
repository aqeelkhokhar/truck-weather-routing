from dataclasses import dataclass
from datetime import datetime

from trips.constants import SECONDS_PER_HOUR


@dataclass(frozen=True)
class Weather:
    wind_mph: float
    rain_in_per_hr: float
    snow_in_per_hr: float


@dataclass(frozen=True)
class WeatherSeries:
    start: datetime
    winds_mph: tuple
    rain_in_per_hr: tuple
    snow_in_per_hr: tuple

    @property
    def hours(self):
        return len(self.winds_mph)

    def index_at(self, moment):
        offset_hours = round((moment - self.start).total_seconds() / SECONDS_PER_HOUR)
        return min(max(offset_hours, 0), self.hours - 1)

    def at_index(self, index):
        return Weather(
            wind_mph=self.winds_mph[index],
            rain_in_per_hr=self.rain_in_per_hr[index],
            snow_in_per_hr=self.snow_in_per_hr[index],
        )

    def at(self, moment):
        return self.at_index(self.index_at(moment))
