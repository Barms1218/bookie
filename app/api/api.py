from fastapi import APIRouter
from app.api.endpoints import books, users

api_router = APIRouter()
api_router.include_router(books.router)

