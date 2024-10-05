import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
load_dotenv()

connection_str = os.getenv("DATABASE_URL")
async_engine = create_async_engine(connection_str, echo=True)
async_session = async_sessionmaker(async_engine)
