from celery import Celery
import smtplib
from email.message import EmailMessage
from datetime import datetime
import os
from ..celery_app import celery_app
from dotenv import load_dotenv
from fastapi import HTTPException
load_dotenv()

SMTP_HOST = "smtp@gmail.com"
SMTP_PORT = 465
SMTP_USER = os.getenv("emailfrom")
SMTP_PWD = os.getenv("smtp_pwd")

redis_url = os.getenv("REDISSTRING2")

def get_email_template_landsat(email: str, data: dict):
    list_dates = []
    for satell in data.values():
        for dicty in satell:
            for key, value in dicty.items():
                if key == "LandsatAcquisitionDate":
                    list_dates.append(datetime.fromisoformat(value))

    earliest = [diction for diction in satell for satell in data.values() if datetime.fromisoformat(diction["LandsatAcquisitionDate"]) == min(*list_dates)][0]

    email = EmailMessage()
    email['Subject'] = "Landsat Acquisition"
    email['From'] = SMTP_USER
    email['To'] = email
    email.set_content(
    '<div style="display: flex; align-items: center; justify-content: center;">'
    '<h1>Hello! This is a notification email from Landsat!</h1>'
    '<h2>Landsat Satelite is Acquiring data! Here is the acquisition information:</h1>'
    '<ul>'
        f'<li>Acquisition satellite: {earliest["LandsatSatellite"]}</li>'
        f'<li>Acquisition date: {earliest["LandsatAcquisitionDate"]}</li>'
        f'<li>WRS Path: {earliest["WRS2Path"]}</li>'
        f'<li>WRS Row: {earliest["WRS2Row"]}</li>'
        f'<li>Location latitude: {earliest["LocationLatitude"]}</li>'
        f'<li>Location longitude: {earliest["LocationLongitude"]}</li>' 
    '</ul>'
    '</div>',
    subtype='html'
    )
    return email

@celery_app.task
def send_landsat_acquisition_email(email: str, data: dict):
    try:
        email = get_email_template_landsat(email, data)
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
            server.login(SMTP_USER, SMTP_PWD)
            server.send_message(email)
    except Exception as e:
        raise HTTPException(400, detail=f"failed to send email, {e}")