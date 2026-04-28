import os
import secrets
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from .repositories import Base
# Override in production via environment.
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

AUTH_USERNAME = os.environ.get("AUTH_USERNAME", "admin")
AUTH_PASSWORD = os.environ.get("AUTH_PASSWORD", "changeme")

# Set true behind HTTPS in production.
COOKIE_SECURE = os.environ.get("COOKIE_SECURE", "").lower() in ("1", "true", "yes")

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///users.db")

engine = create_engine(DATABASE_URL)

def get_session(create_tables: bool = False) -> Session:
    if create_tables:
        Base.metadata.create_all(engine)
    return Session(engine)
