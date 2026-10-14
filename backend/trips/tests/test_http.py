from trips.clients.http import adapter
from trips.constants import HTTP_RETRIES, HTTP_RETRY_STATUSES


def test_session_retries_transient_failures():
    assert adapter.max_retries.total == HTTP_RETRIES
    assert set(adapter.max_retries.status_forcelist) == set(HTTP_RETRY_STATUSES)


def test_session_does_not_retry_rate_limits():
    assert 429 not in adapter.max_retries.status_forcelist
