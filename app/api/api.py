from fastapi import APIRouter
from endpoints import books, users

router = APIRouter(books.APIRouter)
