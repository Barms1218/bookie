from operator import index
from sqlalchemy import select, or_, func, update 
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import contains_eager, selectinload 
from sqlalchemy.ext.asyncio import AsyncSession
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
	
	async def upsert_tags(self, new_tag: schemas.TagIngestSchema) -> models.Tag:
		"""
		Checks if the tag names are already the database. Returns those if so,
		otherwise, inserts.
		Args:
		    schemas: Pydantic schemas with the name of a tag 

		Returns: rows from the tags table with a name and its associated id
		    
		"""
		stmt = (insert(models.Tag).values(new_tag.model_dump()))

		upsert_stmt = stmt.on_conflict_do_update(
				index_elements=['name'],
				set_={"name": stmt.excluded.name}
				)

		result = await self.db.execute(upsert_stmt)

		return result.scalar_one()

	async def get_all_tags(self) -> list[models.Tag]:
		stmt = select(models.Tag)

		result = await self.db.execute(stmt)

		return list(result.scalars().all())
