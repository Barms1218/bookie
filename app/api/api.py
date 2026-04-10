from fastapi import APIRouter
from app.api.endpoints import books, tags, users, models

api_router = APIRouter()
api_router.include_router(books.router)
api_router.include_router(users.router)
api_router.include_router(tags.router)
api_router.include_router(models.router)
