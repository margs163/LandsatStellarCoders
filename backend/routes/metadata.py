from fastapi import APIRouter, Depends
from ..schemas.default import Coordinates
from ..dependencies.current_user import user_dependency
from ..schemas.default import SceneFilter
from ..dependencies.api_key import key_generator
from ..dependencies.client import get_client
from typing import Annotated
import aiohttp
from datetime import datetime, date, timedelta

router = APIRouter(prefix="/metadata")
current_time = datetime.now()

@router.post("/")
async def get_metada(
    location: Coordinates,
    user: user_dependency,
    client: Annotated[aiohttp.ClientSession, Depends(get_client)], 
    api_key: Annotated[str, Depends(key_generator)],
    scene_filter: SceneFilter = SceneFilter(
           cloudMin=0, 
           cloudMax=100, 
           startDate=date(current_time.year, current_time.month, current_time.day) - timedelta(days=7),
           endDate=date(current_time.year, current_time.month, current_time.day),
           season=[0])
        ):

    bbox = [location.longitude - 0.1, location.latitude - 0.1, location.longitude + 0.1, location.latitude + 0.1]
    scene_filter = {
        "maxResults": 1,
        "metadataType": "summary",
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
    async with client as sess:
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
                   result = await response.json()
                   metada_list = result["data"]["metadata"]
                   metadata = {metada_list[index]["fieldName"]: metada_list[index]["value"] for index in [2, 3, 6, 7, 14, 15, 18, 19, 31]}
                   return metadata.update({"landsat_image": image_link})

                          
