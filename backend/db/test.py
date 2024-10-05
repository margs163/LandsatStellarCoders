import asyncio
from .connection import async_session
from .tables import User, Location

async def create_users():
    async with async_session() as session:
            Daniyal = User(
                full_name="Aldanov Daniyal", 
                email="aldanovdaniyal@gmail.com", 
                hashed_password="qwerty1234", 
                selected_locations=[Location(wrs_row=123, wrs_column=102, location_latitude=12.42, location_longitude=-12.43)])
            Adiya = User(
                full_name="Aldanova Adiya", 
                email="adiya@gmail.com", 
                hashed_password="pwd1234", 
                selected_locations=[Location(wrs_row=240, wrs_column=212, location_latitude=-18.02, location_longitude=78.14)])

            session.add_all([Daniyal, Adiya])
            await session.commit()

if __name__ == "__main__":
    asyncio.run(create_users())