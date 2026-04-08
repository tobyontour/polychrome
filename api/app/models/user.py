from pydantic import BaseModel, SecretStr
from datetime import datetime
import secrets

class User(BaseModel):
    username: str
    password: SecretStr
    email: str
    created_at: datetime = datetime.now()
    updated_at: datetime | None = None

    def validate_password(self, password: str) -> bool:
        return secrets.compare_digest(self.password.get_secret_value(), password)