from app.services.grid_generator import generate_grid_points


def test_generate_grid_points_basic():
    bbox = {
        "min_lat": 40.0,
        "min_lng": 29.0,
        "max_lat": 40.001,
        "max_lng": 29.001,
    }
    points = generate_grid_points(bbox, step_m=100)
    assert points
    assert all(bbox["min_lat"] <= lat <= bbox["max_lat"] for lat, _ in points)
    assert all(bbox["min_lng"] <= lng <= bbox["max_lng"] for _, lng in points)
