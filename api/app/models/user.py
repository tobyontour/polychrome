from pydantic import BaseModel
from datetime import datetime
import secrets

class User(BaseModel):
    username: str
    password: str
    email: str
    created_at: datetime = datetime.now()
    updated_at: datetime | None = None

    def validate_password(self, password: str) -> bool:
        return secrets.compare_digest(self.password, password)