import httpx
from app.dependencies import UnitOfWork
from app.schemas.journal import JournalIngestSchema, JournalPublic
from fastapi import HTTPException
from pydantic import ValidationError


class JournalService:
    def __init__(self, client: httpx.AsyncClient, uow: UnitOfWork):
        self.client = client
        self.uow = uow

        async def submit_journal(self, schema: JournalIngestSchema) -> JournalPublic:

            journal_data = schema.model_dump()
            async with self.uow.begin():
                book_title = await self.uow.books.get_book_with_id(journal_data["book_id"]).title 
                submitted_journal = await self.uow.journals.create_journal(journal_data, book_title)
               
            return submitted_journal
