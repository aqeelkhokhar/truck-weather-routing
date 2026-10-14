import pytest
import responses
from django.conf import settings

from trips.clients.geocoding import geocode
from trips.errors import ExternalServiceError, LocationNotFoundError

DALLAS = [{"display_name": "Dallas, Texas, United States", "lat": "32.77", "lon": "-96.79"}]


@responses.activate
def test_geocode_returns_first_match():
    responses.add(responses.GET, settings.GEOCODER_URL, json=DALLAS)
    location = geocode("Dallas")
    assert location.lat == pytest.approx(32.77)
    assert location.lon == pytest.approx(-96.79)
    assert location.name.startswith("Dallas")


@responses.activate
def test_geocode_sends_user_agent():
    responses.add(responses.GET, settings.GEOCODER_URL, json=DALLAS)
    geocode("Dallas")
    assert responses.calls[0].request.headers["User-Agent"] == settings.GEOCODER_USER_AGENT


@responses.activate
def test_geocode_is_cached():
    responses.add(responses.GET, settings.GEOCODER_URL, json=DALLAS)
    geocode("Dallas")
    geocode("  dallas ")
    assert len(responses.calls) == 1


@responses.activate
def test_geocode_unknown_place_raises():
    responses.add(responses.GET, settings.GEOCODER_URL, json=[])
    with pytest.raises(LocationNotFoundError):
        geocode("Nowhereville")


@responses.activate
def test_geocode_upstream_failure_raises():
    responses.add(responses.GET, settings.GEOCODER_URL, status=500)
    with pytest.raises(ExternalServiceError):
        geocode("Dallas")


@responses.activate
def test_upstream_failure_is_logged(caplog):
    responses.add(responses.GET, settings.GEOCODER_URL, status=403)
    with pytest.raises(ExternalServiceError):
        geocode("Dallas")
    assert "403" in caplog.text
