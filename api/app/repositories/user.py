
from ..models.user import User
from sqlalchemy import Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from ..config import get_session

Base = declarative_base()

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

    def get_hashed_password(self, username: str) -> str | None:
        user = self.get_user(username)
        if user is None:
            return None
        return user.password

class SqlUser(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

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

class SqlUserRepository(UserRepository):

    def get_user(self, username: str) -> User | None:
        with get_session() as session:
            user = session.query(SqlUser).filter(SqlUser.username == username).first()
            if user is None:
                return None
            return user.to_model()

    def create_user(self, user: User) -> None:
        with get_session() as session:
            sql_user = SqlUser()
            sql_user.from_model(user)
            session.add(sql_user)
            session.commit()

    def update_user(self, user: User) -> None:
        with get_session() as session:
            sql_user = session.query(SqlUser).filter(SqlUser.username == user.username).first()
            if sql_user is None:
                return None
            sql_user.from_model(user)
            session.commit()

    def delete_user(self, user: User) -> None:
        with get_session() as session:
            sql_user = session.query(SqlUser).filter(SqlUser.username == user.username).first()
            if sql_user is None:
                return None
            session.delete(sql_user)
            session.commit()

    def get_all_users(self) -> list[User]:
        with get_session() as session:
            return [user.to_model() for user in session.query(SqlUser).all()]