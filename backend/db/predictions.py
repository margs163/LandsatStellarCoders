from sqlalchemy import select
from ..authorization.database import get_async_session
from ..authorization.database import Predictions, User
from fastapi import HTTPException

async def insert_prediction(user_id: str, predictions: list[Predictions], ) -> bool:
    async with anext(get_async_session) as session:
        async with session():
            result = await session.execute(select(User).filter_by(id=user_id))
            user: User = result.scalars().first()

            if user:
                user.user_predictions = predictions
            else:
                raise(HTTPException(400, "Could not select user from database!"))

            await session.commit()

            ids = [prediction.id for prediction in predictions]
            return {"inserted_ids": ids}


async def select_predictions(prediction_ids: list[str]):
    async with anext(get_async_session) as session:
        async with session():
            result = await session.execute(select(Predictions).where(Predictions.id.in_(prediction_ids)))
            predictions = result.scalars().all()
            return predictions
        
async def delete_predictions(user_id: str, prediction_id: str):
    async with anext(get_async_session) as session:
        async with session():
            result = await session.execute(select(User).filter_by(id=user_id))
            user = result.scalars().first()
            if user:
                await session.delete(user)
                await session.commit()
            else:
                raise HTTPException(status_code=400, detail="Could not select user from database")