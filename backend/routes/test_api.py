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

# Step 1: Define your target location (latitude/longitude) and WRS-2 Path/Row
target_lat, target_lon = 34.0522, -118.2437  # Example: Los Angeles
target_path = 41  # WRS-2 Path for the target location
target_row = 36   # WRS-2 Row for the target location

ts = load.timescale()

def find_overpasses(satellite: EarthSatellite, observer: GeographicPosition, start_time: Time, end_time: Time, altitude_deg):
        t: Time
        t, events = satellite.find_events(observer, start_time, end_time, altitude_degrees=altitude_deg)
        return [(t[i].utc_iso(), events[i]) for i in range(len(events)) if events[i] == 1]

def is_valid_imaging_overpass(satellite: EarthSatellite, overpass_time, target_path, target_row, session: ClientSession, api_key: str):
        # Simulate satellite position at the overpass time
        geocentric = satellite.at(ts.utc(overpass_time)).subpoint()
        lat, lon = geocentric.latitude.degrees, geocentric.longitude.degrees

        # Lookup WRS-2 path/row based on lat/lon using predefined tables or libraries
        # Here, we use a mock function `get_wrs2_path_row` that should be replaced with a real lookup
        path, row = get_wrs2_path_row(lat, lon, session)
        
        # Check if path and row match the target values
        return path == target_path and row == target_row

async def get_wrs2_path_row(lat, lon, session: ClientSession, api_key: str):
        async with session as sess:
            async with sess.post("https://m2m.cr.usgs.gov/api/api/json/stable/scene-search", json={
                "maxResults": 1,
                "metadataType": "full",
                "datasetName": "landsat_ot_c2_l2",
                "sceneFilter": {
                    "spatialFilter": {
                        "filterType": "mbr",
                        "lowerLeft": {"latitude": lat - 0.01, "longitude": lon - 0.01},
                        "upperRight": {"latitude": lat + 0.01, "longitude": lat + 0.01}
                    }}}, headers={
                          "X-Auth-Token": api_key
                    }
                ) as response:
                result = json.loads(await response.text())
                return result

# async def main():
#       asyncio.run(get_wrs2_path_row(52.2873, 76.9674, aiohttp.ClientSession(), ))
app = FastAPI()
router = APIRouter(prefix="/predict-satellite")



@router.post("/")
async def get_satellite_acquisition_date(
      api_key: Annotated[str, Depends(key_generator)], 
      client: Annotated[aiohttp.ClientSession, Depends(get_client)], 
      location: Coordinates, 
      days_delta: int = 7,  
      altitude_deg = 60.0
      ):
    dict_result = await get_wrs2_path_row(location.latitude, location.longitude, client, api_key)
    return {"wrs_path": dict_result["data"]["results"][0]["metadata"][8]["value"], "wrs_row": dict_result["data"]["results"][0]["metadata"][9]["value"]}

app.include_router(router)

    # tle_url = 'https://celestrak.org/NORAD/elements/landsat.txt'
    # tle_data = load.tle_file(tle_url, filename="../data/tle/tle_landsat.txt")

    # # Filter to get TLE for Landsat 8 and 9
    # landsat_8 = [sat for sat in tle_data if 'LANDSAT 8' in sat.name][0]
    # landsat_9 = [sat for sat in tle_data if 'LANDSAT 9' in sat.name][0]

    # # Step 3: Create an observer location
    # ts = load.timescale()
    # observer_location = wgs84.latlon(location.latitude, location.longitude)
    # current_time = datetime.now()

    # # Define a time window for prediction
    # start_time = ts.utc(current_time.year, current_time.month, current_time.day)
    # end_time = ts.utc(current_time.year, current_time.month, current_time.day + days_delta) 

    # # Get overpasses for Landsat 8 and 9
    # overpasses_landsat8 = find_overpasses(landsat_8, observer_location, start_time, end_time)
    # overpasses_landsat9 = find_overpasses(landsat_9, observer_location, start_time, end_time)

    # # Step 6: Filter the overpasses for actual imaging opportunities
    # imaging_passes_landsat8 = [time for time, _ in overpasses_landsat8 if is_valid_imaging_overpass(landsat_8, time, target_path, target_row, client, api_key)]
    # imaging_passes_landsat9 = [time for time, _ in overpasses_landsat9 if is_valid_imaging_overpass(landsat_9, time, target_path, target_row, client, api_key)]

    # # Display the imaging passes for Landsat 8 and 9 over the specified location
    # print(f"Landsat 8 Imaging Passes: {imaging_passes_landsat8}")
    # print(f"Landsat 9 Imaging Passes: {imaging_passes_landsat9}")