import sqlalchemy
from sqlalchemy import select, insert, Result
from .tables import User, Location
import asyncio
from .connection import async_session, async_engine

async def select_user(email: str):
    async with async_session() as conn:
        result = await conn.execute(select(("Email: " + User.email).label("email"), Location).where(Location.user_id == User.id).order_by(User.id))
        return result.all()
    
async def main():
    result = await select_user(email="aldanovdaniyal@gmail.com")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
   