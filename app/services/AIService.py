from google import genai
from google.genai import types
import app.schemas as schemas
import json
import httpx

# gemini_client = genai.Client()
#
# response = client.models.generate_content(
#     model="gemini-3-flash-preview",
#     contents="Explain how AI works in a few words",
# )

class AIService:
    def __init__(self, api_key: str, client: httpx.AsyncClient):
        self.api_key=api_key
        self.client=client
        self.genai=genai.Client()

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


    async def generate_book_suggestion(self, reading_history: list[schemas.BookRecommendSchema]):
        context_payload = [r.model_dump(exclude_none=True) for r in reading_history]
        system_msg = (
            "You are a book recommendation engine. "
            "Analyze the user's rated tags and suggest 3 new books. "
            f"EXCLUDE these titles from your suggestions: {', '.join(titles)}. "
            "Return the response as a JSON list of objects with 'title', 'author', and 'reason' keys."
        )
        response = await self.genai.aio.models.generate_content(
                    model='gemini-2.0-flash',
                    contents=f"The user has chosen these tags {tag_summary} for these titles {', '.join(titles)}",
                    config=types.GenerateContentConfig(
                        system_instruction=system_msg
                        )
                )

        content = response.text

        if not content:
            return []

        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return []
