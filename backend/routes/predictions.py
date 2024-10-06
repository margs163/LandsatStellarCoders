from fastapi import APIRouter, HTTPException
from datetime import datetime
from ..dependencies.current_user import user_dependency
from ..schemas.default import PredData
from ..routes.celery_tasks import send_landsat_acquisition_email
from celery import Celery
import os
from dotenv import load_dotenv
load_dotenv()

router = APIRouter(prefix="/send-notification")

@router.post("/")
async def send_notification(user: user_dependency, predictions: PredData, time_not: datetime = datetime(year=2024, month=10, day=6)):
    try:
        task = send_landsat_acquisition_email.delay(user.email, predictions.model_dump())
    except Exception as e:
        raise HTTPException(500, detail="failed to send an email")
    return {"message": "Email has been sent successfully!", "task_id": task.id}