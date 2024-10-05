import uuid

from fastapi import FastAPI, APIRouter
from fastapi_users import FastAPIUsers

from .database import User
from .manager import get_user_manager
from .backend import auth_backend

fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)

router = APIRouter()
router.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)