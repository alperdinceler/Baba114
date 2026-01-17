from app.utils.geo import haversine_distance_m


def test_haversine_distance_m():
    distance = haversine_distance_m(41.0, 29.0, 41.0, 29.001)
    assert distance > 0
    assert 50 < distance < 150
