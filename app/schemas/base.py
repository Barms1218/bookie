import re
from pydantic import BaseModel, Field,field_validator 
from datetime import datetime

class TagIngestSchema(BaseModel):
    """

    Attributes: 
        name: 
        rating_value: 
    """
    name: str
    rating_value: int | None

    @field_validator("name")
    @classmethod
    def clean_up_name(cls, n: str) -> str:
        """

        Args:
            n: 

        Returns:
            
        """
        clean_text = re.sub(r'[^a-zA-Z0-9\s]', '', n) 
        return clean_text.strip().title()   
