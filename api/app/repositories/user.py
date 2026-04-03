from pydantic import BaseModel
from datetime import datetime

from ..models.user import User

class UserRepository:
    def __init__(self):
        self.users = []

    def get_user(self, username: str) -> User | None:
        return next((user for user in self.users if user.username == username), None)

    def create_user(self, user: User) -> None:
        self.users.append(user)

    def update_user(self, user: User) -> None:
        self.users[self.users.index(user)] = user

    def delete_user(self, user: User) -> None:
        self.users.remove(user)

    def get_all_users(self) -> list[User]:
        return self.users

    def validate_user(self, username: str, password: str) -> bool:
        user = self.get_user(username)
        if user is None:
            return False
        return user.validate_password(password)

# Create a sqlalchemy user repository
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class SqlUser(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    email = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=True)

    def to_model(self) -> User:
        return User(
            username=self.username,
            password=self.password,
            email=self.email,
            created_at=self.created_at,
            updated_at=self.updated_at)

    def from_model(self, user: User) -> None:
        self.username = user.username
        self.password = user.password
        self.email = user.email
        self.created_at = user.created_at
        self.updated_at = user.updated_at

engine = create_engine("sqlite:///users.db")
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

