from typing import ClassVar
from pydantic import BaseModel, field_validator, EmailStr, SecretStr, ConfigDict 
import string
import uuid

class UserIngestSchema(BaseModel):
    email: EmailStr
    password: SecretStr | None = None
    password_hash: str | None = None
    google_id: str | None = None
    apple_id: str | None = None

    @field_validator("password")
    @classmethod
    def password_strength(cls, p: SecretStr) -> SecretStr: #If the password is good, the validator needs to send it on
        raw: str = p.get_secret_value()
        if p and len(raw) < 8:
            raise ValueError("Password does not meet length requirements(8 or more)") 
        
        contains_special = any(char in set(string.punctuation) for char in raw)
        if not contains_special:
            raise ValueError("Password does not meet complexity requirements.")
        return p


class CurrentUser(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)
    id: uuid.UUID
    email: str

class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str 

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class UserInDB(BaseModel):
    hashed_password: str
