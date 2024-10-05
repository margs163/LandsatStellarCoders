from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from .connection import async_engine 
from sqlalchemy import ForeignKey
from dotenv import load_dotenv
from typing import List, Optional
import asyncio
load_dotenv()

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "user_info"

    id: Mapped[int] = mapped_column(index=True, primary_key=True)
    full_name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(nullable=False)

    selected_locations: Mapped[Optional[List['Location']]] = relationship(back_populates='selected_user', cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, full_name={self.full_name!r}, email={self.email!r})"

class Location(Base):
    __tablename__ = "selected_locations"

    id: Mapped[int] = mapped_column(index=True, primary_key=True)
    wrs_row: Mapped[int] = mapped_column(nullable=False)
    wrs_column: Mapped[int] = mapped_column(nullable=False)
    location_latitude: Mapped[float] = mapped_column(nullable=False)
    location_longitude: Mapped[float] = mapped_column(nullable=False)

    user_id: Mapped[int] = mapped_column(ForeignKey("user_info.id"))
    selected_user: Mapped['User'] = relationship(back_populates='selected_locations')

    def __repr__(self) -> str:
        return f"Location(id={self.id}, WRS_row={self.wrs_row}, WRS_column={self.wrs_column}, coordinates=({self.location_latitude}{" N" if self.location_latitude > 0 else " S"}, {self.location_longitude}{" E" if self.location_latitude > 0 else " W"}))"

async def create_tables() -> None:
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(create_tables())