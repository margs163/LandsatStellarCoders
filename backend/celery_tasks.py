from celery import Celery
import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv
load_dotenv()

SMTP_HOST = "smtp@gmail.com"
SMTP_PORT = 465
SMTP_USER = os.getenv("emailfrom")
SMTP_PWD = os.getenv("smtp")

redis_url = os.getenv("REDISSTRING")
celery = Celery("tasks", broker=redis_url)

def get_email_template_landsat(email: str, data: dict):
    email = EmailMessage()
    email['Subject'] = "Landsat Acquisition"
    email['From'] = SMTP_USER
    email['To'] = email
    email.set_content(
    '<div style="display: flex; align-items: center; justify-content: center;">'
    '<h1>Hello! This is a notification email from Landsat!</h1>'
    '<h2>Landsat Satelite is Acquiring data! Here is the acquisition information:</h1>'
    '<ul>'
        f'<li>Acquisition satellite: {data["satellite"]}</li>'
        f'<li>Acquisition date: {data["acq_date"]}</li>'
        f'<li>WRS Path: {data["path"]}</li>'
        f'<li>WRS Row: {data["row"]}</li>'
        f'<li>Location latitude: {data["latitude"]}</li>'
        f'<li>Location longitude: {data["longitude"]}</li>' 
    '</ul>'
    '</div>',
    subtype='html'
    )
    return email

@celery.task
def send_landsat_acquisition_email(email: str, data: dict):
    email = get_email_template_landsat(email, data)
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
        server.login(SMTP_USER, SMTP_PWD)
        server.send_message(email)