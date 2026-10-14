import logging

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from trips.constants import (
    HTTP_BACKOFF_SECONDS,
    HTTP_POOL_SIZE,
    HTTP_RETRIES,
    HTTP_RETRY_STATUSES,
    HTTP_TIMEOUT_SECONDS,
)
from trips.errors import ExternalServiceError

logger = logging.getLogger(__name__)

retry_policy = Retry(
    total=HTTP_RETRIES,
    backoff_factor=HTTP_BACKOFF_SECONDS,
    status_forcelist=HTTP_RETRY_STATUSES,
    allowed_methods=("GET",),
    raise_on_status=False,
)
adapter = HTTPAdapter(
    pool_connections=HTTP_POOL_SIZE, pool_maxsize=HTTP_POOL_SIZE, max_retries=retry_policy
)
session = requests.Session()
session.mount("https://", adapter)
session.mount("http://", adapter)


def get_json(url, params=None, headers=None):
    try:
        response = session.get(url, params=params, headers=headers, timeout=HTTP_TIMEOUT_SECONDS)
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError) as error:
        detail = getattr(getattr(error, "response", None), "text", "")[:300]
        logger.warning("Upstream request to %s failed: %s %s", url, error, detail)
        raise ExternalServiceError from error
