from fastapi import FastAPI

from app.api.routes.areas import router as area_router
from app.api.routes.hotspots import router as hotspot_router
from app.api.routes.listings import router as listing_router
from app.core.logging import setup_logging


def create_app() -> FastAPI:
    setup_logging()
    app = FastAPI(title="Hotspot Dentist Listings API")
    app.include_router(area_router)
    app.include_router(hotspot_router)
    app.include_router(listing_router)
    return app


app = create_app()
