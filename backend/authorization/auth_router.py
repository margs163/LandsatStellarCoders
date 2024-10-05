import uuid

from fastapi import FastAPI
from fastapi import APIRouter
from fastapi_users import FastAPIUsers

from .backend import auth_backend
from .manager import get_user_manager
from .database import User

fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)

router = APIRouter()
router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)