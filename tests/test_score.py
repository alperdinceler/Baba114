from app.core.config import get_settings
from app.services.hotspots_finder import compute_crowd_score


def test_compute_crowd_score():
    settings = get_settings()
    score = compute_crowd_score(poi_count=10, ratings_total_sum=200, avg_rating=4.5)
    expected = (
        settings.hotspot_weights.w_poi_count * 10
        + settings.hotspot_weights.w_ratings_total * 200
        + settings.hotspot_weights.w_avg_rating * 4.5
    )
    assert score == expected
