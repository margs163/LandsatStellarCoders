from fastapi import FastAPI, Depends, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .authorization.auth_router import router as auth_router
from .authorization.register_router import router as register_router
from .authorization.reset_password_router import router as reset_pwd_router
from .routes.metadata import router as metadata_router
from .authorization.users_router import router as users_router
from .routes.predictions import router as notification_router
from .routes.test_api import router as prediction_router
from .routes.example import router as download_router
import os
from dotenv import load_dotenv
from .routes.scene import router as scene_router
from celery import Celery
import asyncio
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):   
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your Flutter app's actual domain
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(notification_router)
app.include_router(metadata_router)
app.include_router(download_router)
app.include_router(auth_router)
app.include_router(register_router)
app.include_router(reset_pwd_router)
app.include_router(users_router)
app.include_router(prediction_router)