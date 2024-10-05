from fastapi import Depends
from fastapi_users import FastAPIUsers
from typing import Annotated
from ..authorization.manager import get_user_manager
from ..authorization.backend import auth_backend
from ..authorization.database import User

fast_api_users = FastAPIUsers(
    get_user_manager,
    [auth_backend]
)

user_dependency = Annotated[User, Depends(fast_api_users.current_user(active=True))]
