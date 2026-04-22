from fastapi import HTTPException
from google import genai
from google.genai import types
from app.database.unit_of_work import UnitOfWork
from pydantic import TypeAdapter
import app.schemas as schemas
import json
import httpx
import uuid


# Mocking the IDs
user_id = uuid.uuid4()

test_user_profile = [
    schemas.TopBooksSchema(
        title="The Fellowship of the Ring",
        authors=["J.R.R. Tolkien"],
        overall_rating=5,
        book_tags=[
            schemas.BookTag(name="Epic Fantasy", rating_value=5),
            schemas.BookTag(name="World Building", rating_value=5),
            schemas.BookTag(name="Hero's Journey", rating_value=4),
            schemas.BookTag(name="Linguistics", rating_value=3)
        ]
    ),
    schemas.TopBooksSchema(
        title="Empire of Silence",
        authors=["Christopher Ruocchio"],
        overall_rating=5,
        book_tags=[
            schemas.BookTag(name="Space Opera", rating_value=5),
            schemas.BookTag(name="Science Fantasy", rating_value=5),
            schemas.BookTag(name="First Person Narrative", rating_value=4),
            schemas.BookTag(name="Philosophical Sci-Fi", rating_value=5)
        ]
    ),
    schemas.TopBooksSchema(
        title="Red Rising",
        authors=["Pierce Brown"],
        overall_rating=5,
        book_tags=[
            schemas.BookTag(name="Dystopian", rating_value=5),
            schemas.BookTag(name="High Stakes", rating_value=5),
            schemas.BookTag(name="Revolution", rating_value=5),
            schemas.BookTag(name="Fast Paced", rating_value=4)
        ]
    ),
    schemas.TopBooksSchema(
        title="The Eye of the World",
        authors=["Robert Jordan"],
        overall_rating=4,
        book_tags=[
            schemas.BookTag(name="Epic Fantasy", rating_value=5),
            schemas.BookTag(name="Complex Magic System", rating_value=5),
            schemas.BookTag(name="Chosen One", rating_value=3),
            schemas.BookTag(name="Vast Lore", rating_value=5)
        ]
    ),
    schemas.TopBooksSchema(
        title="The Hobbit",
        authors=["J.R.R. Tolkien"],
        overall_rating=4,
        book_tags=[
            schemas.BookTag(name="Adventure", rating_value=5),
            schemas.BookTag(name="Whimsical", rating_value=4),
            schemas.BookTag(name="Dragon", rating_value=5)
        ]
    )
]

class AIService:
    def __init__(self, api_key: str, client: httpx.AsyncClient, uow: UnitOfWork):
        self.api_key: str =api_key
        self.client: httpx.AsyncClient =client
        self.genai=genai.Client(api_key=self.api_key)
        self.uow: UnitOfWork =uow

    async def suggest_tags_for_book(self, description: str) -> list[str]:
        response = await self.genai.aio.models.generate_content(
                model="gemini-1.5-flash",
                contents=f"Description of the book: {description}",
                config=types.GenerateContentConfig(
                    system_instruction="Analyze this book description and return 3-5 tags in a JSON list of strings.",
                    response_mime_type="application/json"
                    )
                )
        content = response.text

        if not content:
            return ["General"]


        try:
            return json.loads(content) 
        except json.JSONDecodeError:
            return ["General"]


    async def generate_book_suggestion(self, user_id: uuid.UUID):
        row = await self.uow.books.build_user_profile(id=user_id)
        
        user_profile: list[schemas.TopBooksSchema] = [
        schemas.TopBooksSchema(
            title=user_book.book.title, 
            authors=user_book.book.authors,
            overall_rating=user_book.overall_rating,
            book_tags=[
                schemas.BookTag(
                    name=bt.tag.name,        
                    rating_value=bt.rating_value
                )
                for bt in user_book.book_tags
            ]
        )
        for user_book in row  
        ]
        user_data = [test.model_dump(exclude_none=True) for test in test_user_profile]

        context_payload = [schema.model_dump_json(exclude_none=True) for schema in user_profile]
        system_msg = (
            "You are a sophisticated book recommendation engine. "
            "Analyze the provided reading history where 4-5 stars indicate strong preference. "
            "Provide 3 suggestions for new books NOT in the list. The suggestions must not include a title from the list."
            "Each suggestion must include a reason linking back to  the user's favorite tags and authors."
        )
        response = await self.genai.aio.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=f"User's top Books History: {user_data}",
                    config=types.GenerateContentConfig(
                        system_instruction=system_msg,
                        response_mime_type="application/json",
                        response_schema={
                        "type": "ARRAY",
                        "items": {
                            "type": "OBJECT",
                            "properties": {
                                "title": {"type": "STRING"},
                                "author": {"type": "STRING"},
                                "reason": {"type": "STRING"},
                                "confidence_score": {"type": "NUMBER"}
                                },
                            "required": ["title", "author", "reason"]
                            } 
                        }
                    )
                )

        content = response.text

        if not content:
            return []

        try:
            raw_json =  json.loads(content)
            adapter = TypeAdapter(list[schemas.BookRecommendation])
            validated_recs = adapter.validate_python(raw_json)
            async with self.uow:
                inserted = await self.uow.books.save_book_recommendations(user_id=user_id, recs=validated_recs)
                return inserted

        except json.JSONDecodeError:
            return []

