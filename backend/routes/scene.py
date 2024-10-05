from fastapi import APIRouter, Request, Query, HTTPException, Depends
from typing import Annotated
from dotenv import load_dotenv
import os
from ..schemas.default import Coordinates, SceneFilter
from ..dependencies.client import get_client
import datetime
import aiohttp
load_dotenv

payload = {
    "username": os.getenv("USERNAMENASA"),
    "token": os.getenv("LOGINTOKEN")
}
host = 'https://m2m.cr.usgs.gov/api/api/json/stable/'

router = APIRouter(prefix="/scene")

@router.post("/")
async def get_scene_by_location(
    request: Request, 
    coordinates: Coordinates,
    client: Annotated[aiohttp.ClientSession, Depends(get_client)],
    scene_filter: SceneFilter | None = None 
    ):

    bbox = [coordinates.longitude - 0.01, coordinates.latitude - 0.01, coordinates.longitude + 0.01, coordinates.latitude + 0.01]
    scene_filter = {
        "maxResults": 100,
        "metadataType": "full",
        "datasetName": scene_filter.dataset,
        "sceneFilter": {
            "acquisitionFilter": {
                "start": str(scene_filter.startDate),
                "end": str(scene_filter.endDate)
            },
            "cloudCoverFilter": {
                "min": scene_filter.cloudMin,
                "max": scene_filter.cloudMax,
                "includeUnknown": False
            },
            "ingestFilter": None,
            "metadataFilter": None,
            "spatialFilter": {
                "filterType": "mbr",
                "lowerLeft": {"latitude": bbox[1], "longitude": bbox[0]},
                "upperRight": {"latitude": bbox[3], "longitude": bbox[2]}
            }
        }
    }

