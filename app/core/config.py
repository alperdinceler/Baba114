from functools import lru_cache
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class GoogleSettings(BaseModel):
    api_key: str = Field(default="", description="Google API key")
    base_url: str = Field(default="https://maps.googleapis.com/maps/api", description="Base URL")
    request_timeout_s: int = Field(default=10, description="HTTP timeout in seconds")
    max_retries: int = Field(default=5, description="Max retries for rate limiting")
    backoff_base_s: float = Field(default=1.0, description="Exponential backoff base")


class HotspotWeights(BaseModel):
    w_poi_count: float = Field(default=1.0)
    w_ratings_total: float = Field(default=0.01)
    w_avg_rating: float = Field(default=1.0)


class ListingScoreWeights(BaseModel):
    w_crowd_score: float = Field(default=1.0)
    w_dentist_count: float = Field(default=1.0)
    w_rent: float = Field(default=0.001)
    w_distance: float = Field(default=0.001)


class Settings(BaseSettings):
    app_name: str = "hotspot-dentist-listings"
    env: str = "dev"

    database_url: str = Field(
        default="postgresql+psycopg2://postgres:postgres@localhost:5432/hotspot",
        description="Database URL",
    )

    google: GoogleSettings = GoogleSettings()

    grid_step_m: int = 500
    dentist_search_radius_m: int = 1500
    hotspot_top_n: int = 20

    hotspot_weights: HotspotWeights = HotspotWeights()
    listing_score_weights: ListingScoreWeights = ListingScoreWeights()

    default_poi_types: list[str] = [
        "shopping_mall",
        "transit_station",
        "bus_station",
        "train_station",
        "tourist_attraction",
        "supermarket",
        "university",
        "stadium",
        "park",
        "movie_theater",
        "beauty_salon",
        "bakery",
    ]

    class Config:
        env_file = ".env"
        env_nested_delimiter = "__"


@lru_cache
def get_settings() -> Settings:
    return Settings()
