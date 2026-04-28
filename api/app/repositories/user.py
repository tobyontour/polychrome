from ..models.user import User
from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from . import Base
from ..config import get_session
from argon2 import PasswordHasher

password_hasher = PasswordHasher()

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


class SqlUser(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    nameline: Mapped[str] = mapped_column(String, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_login: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    info_text: Mapped[str | None] = mapped_column(String, nullable=True)

    def to_model(self) -> User:
        return User(
            username=self.username,
            nameline=self.nameline,
            password=None,
            email=self.email,
            created_at=self.created_at,
            updated_at=self.updated_at,
            last_login=self.last_login,
            info_text=self.info_text)

    def from_model(self, user: User) -> None:
        assert user.password is not None
        self.username = user.username
        self.nameline = user.nameline
        self.password = user.password.get_secret_value()
        self.email = user.email
        self.created_at = user.created_at
        self.updated_at = user.updated_at
        self.last_login = user.last_login
        self.info_text = user.info_text

class SqlUserRepository(UserRepository):

    def hash_password(self, password: str) -> str:
        return password_hasher.hash(password)

    def verify_password(self, password: str, hashed_password: str) -> bool:
        return password_hasher.verify(password, hashed_password)

    def get_user(self, username: str) -> User | None:
        with get_session() as session:
            user = session.query(SqlUser).filter(SqlUser.username == username).first()
            if user is None:
                return None
            return user.to_model()

    def create_user(self, user: User) -> None:
        assert user.password is not None
        with get_session() as session:
            sql_user = SqlUser()
            sql_user.from_model(user)
            sql_user.password = self.hash_password(user.password.get_secret_value())
            session.add(sql_user)
            session.commit()

    def update_user(self, user: User) -> None:
        with get_session() as session:
            sql_user = session.query(SqlUser).filter(SqlUser.username == user.username).first()
            if sql_user is None:
                return None
            old_hashed_password = sql_user.password
            sql_user.from_model(user)
            if user.password is None:
                sql_user.password = old_hashed_password
            else:
                sql_user.password = self.hash_password(user.password.get_secret_value())
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