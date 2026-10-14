from rest_framework import status
from rest_framework.exceptions import APIException


class LocationNotFoundError(APIException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = "Location could not be found."
    default_code = "location_not_found"


class NoRouteFoundError(APIException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = "No drivable route exists between the two locations."
    default_code = "no_route_found"


class SamePlaceError(APIException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = "Origin and destination resolve to the same place."
    default_code = "same_place"


class ExternalServiceError(APIException):
    status_code = status.HTTP_502_BAD_GATEWAY
    default_detail = "An upstream service is unavailable."
    default_code = "upstream_unavailable"
