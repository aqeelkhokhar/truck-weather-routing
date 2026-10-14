import requests

from trips.constants import HTTP_TIMEOUT_SECONDS
from trips.errors import ExternalServiceError


def get_json(url, params=None, headers=None):
    try:
        response = requests.get(url, params=params, headers=headers, timeout=HTTP_TIMEOUT_SECONDS)
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError) as error:
        raise ExternalServiceError from error
