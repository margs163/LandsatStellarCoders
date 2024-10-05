import aiohttp
import json
import os
from dotenv import load_dotenv
load_dotenv()

USERNAME = os.getenv("USERNAMENASA")
TOKEN = os.getenv("LOGINTOKEN")

host = "https://m2m.cr.usgs.gov/api/api/json/stable/"

async def key_generator():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(host+"login-token", json={
                "username": USERNAME,
                "token": TOKEN
            }) as response:
                result = await response.json()
                yield result['data']
    finally:
       pass