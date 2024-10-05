import uuid
from typing import Optional
from .backend import SECRET as secret_rsa

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, UUIDIDMixin

from .database import User, get_user_db
from fastapi_users.password import PasswordHelper
from pwdlib import PasswordHash, exceptions
from pwdlib.hashers.argon2 import Argon2Hasher

password_hash = PasswordHash((
    Argon2Hasher(),
))
password_helper = PasswordHelper(password_hash)

SECRET = secret_rsa


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db, password_helper)