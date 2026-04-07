from sqlalchemy import select, or_, func, update 
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import contains_eager, selectinload 
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import uuid
import app.schemas as schemas
import app.database.models as models

class TagRepository:
	"""
	The class that handles generic tag database functions
	Attributes: 
	    db: 
	"""
	def __init__(self, db: AsyncSession):
		self.db: AsyncSession = db
	
	async def get_or_create_tags(self, names: list[str]) -> list[models.Tag]:
		"""
		Checks if the tag names are already the database. Returns those if so,
		otherwise, inserts.
		Args:
		    schemas: Pydantic schemas with the name of a tag 

		Returns: rows from the tags table with a name and its associated id
		    
		"""
		existing_stmt = select(models.Tag).where(models.Tag.name.in_(names))
		result = await self.db.execute(existing_stmt)
		existing_tags = list(result.scalars().all())

		existing_names = [t.name for t in existing_tags]
		missing_names = [name for name in names if name not in existing_names]


		new_tags = []
		if missing_names:
			insert_stmt = (
					insert(models.Tag)
					.values([{"name": name} for name in missing_names])
					)
			insert_result = await self.db.execute(insert_stmt)
			new_tags = list(insert_result.scalars().all())

		return existing_tags + new_tags
