from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy
import os
from dotenv import load_dotenv
from fastapi_users.authentication import CookieTransport

cookie_transport = CookieTransport(cookie_max_age=86400)

SECRET = os.getenv("secret")

cookie_transport = CookieTransport(cookie_max_age=86400)

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=86400)

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)