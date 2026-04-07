from pydantic import BaseModel, field_validator
import re

class TagIngestSchema(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def clean_up_name(cls, n: str) -> str:
        clean_text = re.sub(r'[^a-zA-Z0-9\s]', '', n) 
        return clean_text.strip().title()
