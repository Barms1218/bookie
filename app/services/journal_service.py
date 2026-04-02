import httpx

from app.database.unit_of_work import UnitOfWork

from app.schemas.journal import JournalIngestSchema, JournalPublic
from fastapi import HTTPException


class JournalService:
    def __init__(self, client: httpx.AsyncClient, uow: UnitOfWork):
        self.client = client
        self.uow = uow

    async def submit_journal(self, schema: JournalIngestSchema) -> JournalPublic:

        journal_data = schema.model_dump()
        async with self.uow:
            book = await self.uow.books.get_book_with_id(journal_data["user_book_id"])
            if not book:
                raise HTTPException(404, "No book with that id")

            submitted_journal = await self.uow.journals.create_journal(
                    journal_data,
                    book.title
                    )

            await self.uow.commit()

        return submitted_journal
