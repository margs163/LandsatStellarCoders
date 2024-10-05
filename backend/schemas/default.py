from pydantic import BaseModel, Field
import datetime

class Coordinates(BaseModel):
    latitude: float = Field("Latitude of a certain location", gt=-90, lt=90)
    longitude: float = Field("Longitude of a certain location", gt=-180, lt=180)

class SceneFilter(BaseModel):
    dataset: str = Field(default="landsat_ot_c2_l2"),
    cloudMin: int | None = Field(default=None),
    cloudMax: int | None = Field(default=None),
    startDate: datetime.date | None = Field(default=None),
    endDate: datetime.date | None = Field(default=None),
    season: list[int] | None = Field(default=None)