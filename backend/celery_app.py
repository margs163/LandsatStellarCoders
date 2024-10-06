from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Celery
celery_app = Celery("tasks", broker=os.getenv("REDISSTRING2"))