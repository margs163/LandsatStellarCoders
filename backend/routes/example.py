# import os
# import zipfile
# import os
# import json
# import requests
# import sys
# import time
# import argparse
# import datetime
# import threading
# import re
# from dotenv import load_dotenv
# from datetime import datetime, date, timedelta
# import boto3
# from botocore.client import Config
# load_dotenv()
# from fastapi import APIRouter
# from ..dependencies.api_key import key_generator
# from ..dependencies.client import get_client
# from ..dependencies.current_user import user_dependency
# from ..schemas.default import Coordinates, SceneFilter
# from typing import Annotated
# from fastapi import BackgroundTasks, Depends
# from aiohttp import ClientSession
# import numpy as np
# from fastapi import HTTPException
# import rasterio


# path = "../data/landsat_scenes" # Fill a valid path to save the downloaded files
# maxthreads = 5 # Threads count for downloads
# sema = threading.Semaphore(value=maxthreads)
# label = datetime.now().strftime("%Y%m%d_%H%M%S") # Customized label using date time
# threads = []

# ACCESS_KEY = os.getenv("doceanpublickey")
# SECRET_KEY = os.getenv("doceansecretkey")
# SPACE_NAME = 'landsat-scenes-storage'
# REGION = 'fra1'  # e.g., nyc3
# ENDPOINT_URL = "https://landsat-scenes-storage.fra1.digitaloceanspaces.com"
# file_paths = []

# s3_client = boto3.client('s3',
#                          region_name=REGION,
#                          endpoint_url=ENDPOINT_URL,
#                          ws_access_key_id=ACCESS_KEY,
#                        aws_secret_access_key=SECRET_KEY,
#                          config=Config(signature_version='s3v4'))

# async def extract_pixel_value(geotiff_path, lon, lat):
#     with rasterio.open(geotiff_path) as src:
#         band_data = src.read(1)  # Read the first band
#         transform = src.transform
#         row, col = src.index(lon, lat)
#         pixel_value = band_data[row, col]
#     return pixel_value

# async def extract_surface_temperature(geotiff_path, lon, lat, metadata):
#     with rasterio.open(geotiff_path) as src:
#         band_data = src.read(1)  # Read the first band (TIR band)
#         transform = src.transform
#         row, col = src.index(lon, lat)
#         pixel_value = band_data[row, col]
        
#         # Extract relevant metadata for conversion
#         radiance_mult = metadata['RADIANCE_MULT_BAND_10']  # For Band 10
#         radiance_add = metadata['RADIANCE_ADD_BAND_10']  # For Band 10
#         k1_constant = metadata['K1_CONSTANT_BAND_10']  # For Band 10
#         k2_constant = metadata['K2_CONSTANT_BAND_10']  # For Band 10

#         # Convert DN to TOA spectral radiance
#         L_lambda = radiance_mult * pixel_value + radiance_add

#         # Convert TOA spectral radiance to temperature in Kelvin
#         temperature_kelvin = k2_constant / (np.log((k1_constant / L_lambda) + 1))
    
#     return temperature_kelvin

# def load_metadata(mtl_file_path):
#     metadata = {}
#     with open(mtl_file_path, 'r') as mtl_file:
#         for line in mtl_file:
#             if "=" in line:
#                 key, value = line.split("=")
#                 key = key.strip()
#                 value = value.strip()
#                 metadata[key] = float(value)
#     return metadata

# async def extract_surface_reflectance_and_temperature(files, lon, lat, metadata):
#     pixel_values = {}
#     for band in files:
#         band_name = os.path.basename(band)
#         if "SR_B" in band_name:  # Surface Reflectance bands
#             pixel_values[band_name] = await extract_pixel_value(band, lon, lat)
#         elif "ST_B10" in band_name:  # Surface Temperature Band 10
#             pixel_values['Surface_Temperature_B10'] = await extract_surface_temperature(band, lon, lat, metadata)
#         elif "ST_B11" in band_name:  # Surface Temperature Band 11 (optional)
#             pixel_values['Surface_Temperature_B11'] = await extract_surface_temperature(band, lon, lat, metadata)
    
#     return pixel_values

# # send http request
# async def sendRequest(url, data, apiKey = None):  
#     pos = url.rfind('/') + 1
#     endpoint = url[pos:]
#     json_data = json.dumps(data)
    
#     if apiKey == None:
#         response = requests.post(url, json_data)
#     else:
#         headers = {'X-Auth-Token': apiKey}   
#         async with ClientSession() as session:
#             async with session.post(url, json=json_data, headers=headers) as result:
#                response = result 

#     try:
#       httpStatusCode = response.status_code 
#       if response == None:
#           print("No output from service")
#           sys.exit()
#       output = await response.json()	
#       if output['errorCode'] != None:
#           print("Failed Request ID", output['requestId'])
#           print(output['errorCode'], "-", output['errorMessage'])
#           sys.exit()
#       if  httpStatusCode == 404:
#           print("404 Not Found")
#           sys.exit()
#       elif httpStatusCode == 401: 
#           print("401 Unauthorized")
#           sys.exit()
#       elif httpStatusCode == 400:
#           print("Error Code", httpStatusCode)
#           sys.exit()
#     except Exception as e: 
#           response.close()
#           print(f"Failed to parse request {endpoint} response. Re-check the input {json_data}.\n")
#     response.close()    
#     print(f"Finished request {endpoint} with request ID {output['reques\n")
    
#     return output['data']

# async def downloadFile(url):
#     sema.acquire()
#     global path
#     try:        
#         async with ClientSession() as session:
#             async with session.get(url, stream=True) as response:
#                 disposition = response.headers['content-disposition']
#                 filename = re.findall("filename=(.+)", disposition)[0].strip("\"")
#                 print(f"Downloading {filename} ...\n")
#             if path != "" and path[-1] != "/":
#                 filename = "/" + filename
#             with open(path + filename, 'wb') as file:
#                 file.write(response.content)

#             print(f"Downloaded {filename}\n")

#         space_path = f"landsat_scenes/ot_c2_l2/{filename}"
#         try:
#             s3_client.upload_file(path + filename, SPACE_NAME, space_path)
#             file_paths.append(path+filename)
#         except Exception as e:
#             print("Error uploading file: ", e)

#     except Exception as e:
#         print(f"Failed to download from {url}. {e}. Will try to re-download.")
#         sema.release()
#         runDownload(threads, url)
    
# def runDownload(threads, url):
#     thread = threading.Thread(target=downloadFile, args=(url,))
#     threads.append(thread)
#     thread.start()
    
# router = APIRouter(prefix="/download-scene")

# @router.post("/")
# async def download_scene(coordinates: Coordinates, api_key: Annotated[str, Depends(key_generator)], client: Annotated[ClientSession, Depends(get_client)], user: user_dependency):
#     serviceUrl = "https://m2m.cr.usgs.gov/api/api/json/stable/"
    
#     spatialFilter = {
#         'filterType': "mbr",
#         'lowerLeft': {'latitude': coordinates.latitude - 0.1, 'longitude': coordinates.longitude - 0.1},
#         'upperRight': {'latitude': coordinates.latitude + 0.1, 'longitude': coordinates.longitude + 0.1}
#     }
    
#     current = datetime.now()
#     acquisitionFilter = {
#         "end": str(current.date()),
#         "start": str(current.date() - timedelta(days=7))
#     }

#     payload = {
#         'datasetName': "landsat_ot_c2_l2",
#         'maxResults': 1,
#         'sceneFilter': {
#             'spatialFilter': spatialFilter,
#             'acquisitionFilter': acquisitionFilter
#         }
#     }

#     scenes = await sendRequest(serviceUrl + "scene-search", payload, api_key)
#     if scenes['recordsReturned'] == 0:
#         raise HTTPException(status_code=404, detail="No scenes found for the given coordinates and date range.")

#     sceneIds = [result['entityId'] for result in scenes['results']]
    
#     payload = {'datasetName': "landsat_ot_c2_l2", 'entityIds': sceneIds}
#     downloadOptions = await sendRequest(serviceUrl + "download-options", payload, api_key)

#     downloads = [{'entityId': product['entityId'], 'productId': product['id']} for product in downloadOptions if product['available']]

#     if downloads:
#         payload = {'downloads': downloads, 'label': datetime.now().strftime("%Y%m%d_%H%M%S")}
#         requestResults = await sendRequest(serviceUrl + "download-request", payload, api_key)
        
#         download_urls = [download['url'] for download in requestResults['availableDownloads']]
#         for url in download_urls:
#             await downloadFile(url)

#         # Load metadata from MTL file
#         mtl_file_path = [f for f in os.listdir(path) if f.endswith('MTL.txt')][0]
#         metadata = load_metadata(mtl_file_path)

#         # Extract SR and Surface Temperature values
#         downloaded_files = [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.tif')]
#         pixel_values = await extract_surface_reflectance_and_temperature(downloaded_files, coordinates.longitude, coordinates.latitude, metadata)

#         return {
#             "coordinates": coordinates,
#             "pixel_values": pixel_values
#         }
#     else:
#         raise HTTPException(status_code=404, detail="No downloadable scenes available.")

# @router.post("/")
# async def download_scene(coordinates: Coordinates, api_key: Annotated[str, Depends(key_generator)], client: Annotated[ClientSession, Depends(get_client)], user: user_dependency):
#     serviceUrl = "https://m2m.cr.usgs.gov/api/api/json/stable/"
    
#     spatialFilter =  {'filterType' : "mbr",
#                       'lowerLeft' : {'latitude' : coordinates.latitude - 0.1, 'longitude' : coordinates.longitude - 0.1},
#                       'upperRight' : { 'latitude' : coordinates.latitude + 0.1, 'longitude' : coordinates.longitude + 0.1}}
                     
#     current = datetime.now()
        
#     acquisitionFilter = {"end": date(current.year, current.month, current.day),
#                             "start": date(current.year, current.month, current.day) - timedelta(days=7)}        
        
#     payload = {'datasetName' : "landsat_ot_c2_l2", 
#                                 'maxResults' : 1,
#                                 'sceneFilter' : {
#                                                 'spatialFilter' : spatialFilter,
#                                                 'acquisitionFilter' : acquisitionFilter}}
        
    
#     scenes = sendRequest(serviceUrl + "scene-search", payload, api_key)

#     if scenes['recordsReturned'] > 0:
#         sceneIds = []
#         for result in scenes['results']:
#             sceneIds.append(result['entityId'])
        
#         payload = {'datasetName' : "landsat_ot_c2_l2", 'entityIds' : sceneIds}
                            
#         downloadOptions = await sendRequest(serviceUrl + "download-options", payload, api_key)
    
#         downloads = []
#         for product in downloadOptions:
#                 if product['available'] == True:
#                         downloads.append({'entityId' : product['entityId'],
#                                         'productId' : product['id']})
                        
#         if downloads:
#             requestedDownloadsCount = len(downloads)
#             label = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
#             payload = {'downloads' : downloads, 'label' : label}
#             requestResults = await sendRequest(serviceUrl + "download-request", payload, api_key)          
                            
#             if requestResults['preparingDownloads'] != None and len(requestResults['preparingDownloads']) > 0:
#                 payload = {'label' : label}
#                 moreDownloadUrls = sendRequest(serviceUrl + "download-retrieve", payload, api_key)
#                 downloadIds = []  
                
#                 for download in moreDownloadUrls['available']:
#                     if str(download['downloadId']) in requestResults['newRecords'] or str(download['downloadId']) in requestResults['duplicateProducts']:
#                         downloadIds.append(download['downloadId'])
#                         runDownload(threads, download['url'])
                    
#                 for download in moreDownloadUrls['requested']:
#                     if str(download['downloadId']) in requestResults['newRecords'] or str(download['downloadId']) in requestResults['duplicateProducts']:
#                         downloadIds.append(download['downloadId'])
#                         runDownload(threads, download['url'])
#             else:
#                 for download in requestResults['availableDownloads']:
#                     runDownload(threads, download['url'])
#     else:
#         print("Search found no results.\n")
    
#     print("Downloading files... Please do not close the program\n")
# #     for thread in threads:
#         thread.join()

        


     