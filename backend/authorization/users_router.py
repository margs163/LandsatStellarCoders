import uuid

from fastapi import FastAPI, APIRouter
from fastapi_users import FastAPIUsers

from .database import User
from .schema import UserRead, UserUpdate
from .backend import auth_backend
from .manager import get_user_manager

fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)

router = FastAPI()
router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)