from trips.presenters import simplify_geometry


def test_short_geometry_is_unchanged():
    geometry = tuple((float(index), 0.0) for index in range(10))
    assert simplify_geometry(geometry, limit=100) == list(geometry)


def test_long_geometry_is_reduced_and_keeps_endpoints():
    geometry = tuple((float(index), 0.0) for index in range(10_001))
    reduced = simplify_geometry(geometry, limit=500)
    assert len(reduced) <= 520
    assert reduced[0] == geometry[0]
    assert reduced[-1] == geometry[-1]
