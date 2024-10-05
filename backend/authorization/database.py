from typing import AsyncGenerator, List, Optional
import uuid

from fastapi import Depends
from fastapi_users.db import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Boolean, Float, ForeignKey
from fastapi_users_db_sqlalchemy.generics import GUID

from dotenv import load_dotenv
import os
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

class Base(DeclarativeBase):
    pass


class User(SQLAlchemyBaseUserTableUUID, Base):
    selected_locations: Mapped[Optional[List["Location"]]] = relationship(
        back_populates="user_owner", cascade="all, delete-orphan"
        )

class Location(DeclarativeBase):
    __tablename__ = "location"

    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default_factory=uuid.uuid4)
    wrs_row: Mapped[int] = mapped_column(Integer, nullable=False)
    wrs_column: Mapped[int] = mapped_column(Integer, nullable=False)

    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user_owner: Mapped["User"] = relationship(back_populates="selected_locations")


engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)