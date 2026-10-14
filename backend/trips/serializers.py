from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers

from trips.constants import (
    DEFAULT_SPACING_MILES,
    FORECAST_HOURS,
    MAX_LOAD_LB,
    PAST_DEPARTURE_GRACE_HOURS,
    SPACING_CHOICES_MILES,
)


class TripRequestSerializer(serializers.Serializer):
    origin = serializers.CharField(max_length=200)
    destination = serializers.CharField(max_length=200)
    departure = serializers.DateTimeField()
    load_lb = serializers.IntegerField(min_value=0, max_value=MAX_LOAD_LB)
    spacing_miles = serializers.ChoiceField(
        choices=SPACING_CHOICES_MILES, default=DEFAULT_SPACING_MILES
    )

    def validate_departure(self, value):
        now = timezone.now()
        earliest = now - timedelta(hours=PAST_DEPARTURE_GRACE_HOURS)
        latest = now + timedelta(hours=FORECAST_HOURS)
        if not earliest <= value <= latest:
            raise serializers.ValidationError(
                f"Departure must be within the next {FORECAST_HOURS} hours."
            )
        return value

    def validate(self, attrs):
        if attrs["origin"].strip().lower() == attrs["destination"].strip().lower():
            raise serializers.ValidationError("Origin and destination must differ.")
        return attrs
