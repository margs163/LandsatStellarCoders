from pydantic import BaseModel, Field

class Coordinates(BaseModel):
    latitude: float = Field()
    longitude: float = Field()

class SceneFilter(BaseModel):
    start_date: str
    end_date: str