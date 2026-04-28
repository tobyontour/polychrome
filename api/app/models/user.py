from pydantic import BaseModel, SecretStr
from datetime import datetime

class User(BaseModel):
    username: str
    nameline: str
    password: SecretStr | None
    email: str
    created_at: datetime = datetime.now()
    updated_at: datetime | None = None
    last_login: datetime | None = None
    info_text: str | None = None
