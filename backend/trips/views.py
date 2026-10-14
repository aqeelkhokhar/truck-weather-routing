from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response

from trips.presenters import present_trip
from trips.serializers import TripRequestSerializer
from trips.services.planner import plan_trip


@api_view(["GET"])
def health(request):
    return Response({"status": "ok"})


@api_view(["POST"])
def plan(request):
    serializer = TripRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    trip = plan_trip(serializer.validated_data, timezone.now())
    return Response(present_trip(trip))
