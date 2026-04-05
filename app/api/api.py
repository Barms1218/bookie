from fastapi import APIRouter
from app.api.endpoints import books, entries_endpoint, users 

api_router = APIRouter()
api_router.include_router(books.router)
api_router.include_router(users.router)
api_router.include_router(entries_endpoint.router)
