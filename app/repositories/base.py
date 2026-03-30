from typing import Any, Generic, List, Optional, Type, TypeVar
from pydantic import BaseModel
from sqlalchemy.orm import Session

# Define TypeVars to act as placeholders
ModelType = TypeVar("ModelType")           # For SQLAlchemy Models
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel) # For Pydantic 'Create'
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel) # For Pydantic 'Update'

class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.id == id).first()

    def create(self, db: Session, *, obj_in: CreateSchemaType):
        db_obj = self.model(**obj_in.dict())
        db.add(db_obj)
        db.commit()
        return db_obj
