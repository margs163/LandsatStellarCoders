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
async def get_metada(location: Coordinates, scene_filter: SceneFilter, user: user_dependency, client: Annotated[aiohttp.ClientSession, Depends(get_client)], api_key: Annotated[str, Depends(key_generator)]):
    bbox = [location.longitude - 0.01, location.latitude - 0.01, location.longitude + 0.01, location.latitude + 0.01]
    scene_filter = {
        "maxResults": 1,
        "metadataType": "full",
        "datasetName": "landsat_ot_c2_l2",
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
                    # return result
                    global scene_id
                    scene_id = result["data"]["results"][0]["displayId"]
                    global image_link
                    image_link = result["data"]["results"][0]["browse"][0]["browsePath"]
    
    metadata_payload = {
           "datasetName": "landsat_ot_c2_l2",
           "entityId": scene_id,
           "idType": "displayId",
           "metadataType": "full"
    } 

    async with aiohttp.ClientSession() as sess:
            async with sess.post("https://m2m.cr.usgs.gov/api/api/json/stable/scene-metadata", 
                json=metadata_payload, 
                headers={"X-Auth-Token": api_key}) as response:
                   return {"metadata": await response.json(), "image": image_link}
