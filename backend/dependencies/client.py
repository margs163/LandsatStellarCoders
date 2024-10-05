from typing import Annotated
from fastapi import Request
import aiohttp

async def get_client():
    try:
        client = aiohttp.ClientSession()
        yield client
    finally:
        await client.close()

# async def get_async_client(request: Request) -> aiohttp.ClientSession:
#     client: aiohttp.ClientSession = request.app.state.client
#     return client