from pydantic import BaseModel, field_validator, EmailStr, SecretStr, Optional
import string
import datetime
import uuid

class UserIngestSchema(BaseModel):
    name: str  
    email: EmailStr
    password: Optional[SecretStr] = None
    google_id: Optional[str] = None
    apple_id: Optional[str] = None

    @field_validator("name")
    @classmethod
    def no_empty_name(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Name cannot be blank")
        return v

    @field_validator("password")
    @classmethod
    def password_strength(cls, p: SecretStr) -> SecretStr: #If the password is good, the validator needs to send it on
        raw: str = p.get_secret_value()
        if len(raw) < 8:
            raise ValueError("Password does not meet length requirements(8 or more)") 
        
        contains_special = any(char in set(string.punctuation) for char in raw)
        if not contains_special:
            raise ValueError("Password does not meet complexity requirements.")
        return p


class User:
    def __init__(self, id: uuid.UUID, name: str, 
                 email: str, date_joined: datetime.datetime):
        self.name = name
        self.email = email
        self.id = id,
        self.date_joined = date_joined
        

