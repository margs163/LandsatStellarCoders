from fastapi import APIRouter, Depends
from ..schemas.default import Coordinates
from ..dependencies.current_user import user_dependency
from ..schemas.default import SceneFilter
from ..dependencies.api_key import key_generator
from ..dependencies.client import get_client
from typing import Annotated
import aiohttp

router = APIRouter(prefix="/metadata")

@router.post("/")
async def get_metada(location: Coordinates, scene_filter: SceneFilter, user: user_dependency, client: Annotated[aiohttp.ClientSession, Depends(get_client)], api_key: Annotated[str, key_generator]):
    bbox = [location.longitude - 0.01, location.latitude - 0.01, location.longitude + 0.01, location.latitude + 0.01]
    scene_filter = {
        "maxResults": 1,
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
    async with aiohttp.ClientSession() as sess:
            async with sess.post("https://m2m.cr.usgs.gov/api/api/json/stable/scene-search", 
                json=scene_filter, 
                headers={"X-Auth-Token": api_key}) as response:
                    result = await response.json()
                    return result