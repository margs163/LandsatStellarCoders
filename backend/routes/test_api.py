from skyfield.api import Topos, load, EarthSatellite, wgs84, Time
from skyfield.toposlib import GeographicPosition
import pandas as pd
from datetime import datetime, timedelta, date
from aiohttp import ClientSession
from fastapi import APIRouter, Request, Depends, FastAPI
from ..schemas.default import Coordinates
from ..dependencies.api_key import key_generator
from ..dependencies.client import get_client
import aiohttp
import json
from typing import Annotated

ts = load.timescale()

def find_overpasses(satellite: EarthSatellite, observer: GeographicPosition, start_time: Time, end_time: Time, altitude_deg: float):
        t: Time
        t, events = satellite.find_events(observer, start_time, end_time, altitude_degrees=altitude_deg)
        return [(t[i].utc_iso(), events[i]) for i in range(len(events)) if events[i] == 1]

async def is_valid_imaging_overpass(satellite: EarthSatellite, overpass_time, target_path, target_row, session: ClientSession, api_key: str) -> bool:
        overpass = datetime.fromisoformat(overpass_time)
        geocentric = satellite.at(ts.utc(overpass)).subpoint()
        lat, lon = geocentric.latitude.degrees, geocentric.longitude.degrees
        result = await get_wrs2_path_row(lat, lon, session, api_key)
        return result["wrs_path"] == target_path and result["wrs_row"] == target_row

async def get_wrs2_path_row(lat, lon, session: ClientSession, api_key: str) -> dict:
        async with aiohttp.ClientSession() as sess:
            async with sess.post("https://m2m.cr.usgs.gov/api/api/json/stable/scene-search", json={
                "maxResults": 1,
                "metadataType": "full",
                "datasetName": "landsat_ot_c2_l2",
                "sceneFilter": {
                    "spatialFilter": {
                        "filterType": "mbr",
                        "lowerLeft": {"latitude": lat - 0.1, "longitude": lon - 0.1},
                        "upperRight": {"latitude": lat + 0.1, "longitude": lat + 0.1}
                    }}}, headers={
                          "X-Auth-Token": api_key
                    }
                ) as response:
                result = json.loads(await response.text())
                return {"wrs_path": int(result["data"]["results"][0]["metadata"][8]["value"]), "wrs_row": int(result["data"]["results"][0]["metadata"][9]["value"])}

router = APIRouter(prefix="/predict-satellite")

@router.post("/")
async def get_satellite_acquisition_date(
      api_key: Annotated[str, Depends(key_generator)], 
      client: Annotated[aiohttp.ClientSession, Depends(get_client)], 
      location: Coordinates, 
      days_delta: int = 7,  
      altitude_deg: float = 80
      ):
    dict_result = await get_wrs2_path_row(location.latitude, location.longitude, client, api_key)

    tle_data = load.tle_file("D:\\Landsat\\LandsatStellarCoders\\backend\\routes\\gp.php")

    # # Filter to get TLE for Landsat 8 and 9
    landsat_8 = [sat for sat in tle_data if 'LANDSAT 8' in sat.name][0]
    landsat_9 = [sat for sat in tle_data if 'LANDSAT 9' in sat.name][0]

    # # Step 3: Create an observer location
    ts = load.timescale()
    observer_location = wgs84.latlon(location.latitude, location.longitude)
    current_time = datetime.now()

    # # Define a time window for prediction
    start_time = ts.utc(2024, 9, 1)
    end_time = ts.utc(2024, 10, 1) 

    # Get overpasses for Landsat 8 and 9
    overpasses_landsat8 = find_overpasses(landsat_8, observer_location, start_time, end_time, altitude_deg)
    overpasses_landsat9 = find_overpasses(landsat_9, observer_location, start_time, end_time, altitude_deg)

    # # Step 6: Filter the overpasses for actual imaging opportunities
    imaging_passes_landsat8 = [time for time, _ in overpasses_landsat8 if await is_valid_imaging_overpass(landsat_8, time, dict_result["wrs_path"], dict_result["wrs_row"], client, api_key=api_key)]
    imaging_passes_landsat9 = [time for time, _ in overpasses_landsat9 if await is_valid_imaging_overpass(landsat_9, time, dict_result["wrs_path"], dict_result["wrs_row"], client, api_key=api_key)]

    return {"landsat_8_overpass": imaging_passes_landsat8, "landsat_9_overpass": imaging_passes_landsat9}