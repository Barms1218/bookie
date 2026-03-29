from fastapi import FastAPI, Depends
from fastapi.datastructures import URL
from app.config import settings
from app.services import GoogleBooksService
from app.lifespan import lifespan


app = FastAPI(lifespan=lifespan)

def get_google_service():
    return GoogleBooksService(api_key=str(settings.google_api_key), client=app.state.http_client)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/search/{term}")
async def search_books(term: str, service: GoogleBooksService = Depends(get_google_service)):
    data = await service.get_book_with_term(term)
    return {"data": data }



