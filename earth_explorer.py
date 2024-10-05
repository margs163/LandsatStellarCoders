import requests
import os
import json
from dotenv import load_dotenv
from pprint import pprint

load_dotenv()

username = os.getenv("USERNAMENASA")
access_token = os.getenv("LOGINTOKEN")
host = "https://m2m.cr.usgs.gov/api/api/json/stable/"

payload = {
    "username": username,
    "token": access_token
}

api_key = requests.post(f'{host + 'login-token'}', json=payload).json().get('data')

landsat_c2 = requests.post(
    host + "dataset-search", headers={
    "X-Auth-Token": api_key,
    "Content-Type": "application/json"
    }, 
    json={
        "datasetName": "landsat_ot_c2_l2"
    })

with open("./landsat_c2_medet_salamaleikum.txt", 'w') as file:
    file.write(json.dumps(landsat_c2.json(), indent=4))