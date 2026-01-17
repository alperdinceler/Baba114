from pydantic import BaseModel, Field


class HotspotRunRequest(BaseModel):
    area_id: int
    grid_step_m: int = Field(default=500, ge=100)
    top_n: int = Field(default=20, ge=1)


class DentistRunRequest(BaseModel):
    area_id: int
