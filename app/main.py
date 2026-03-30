from fastapi import FastAPI 
from app.lifespan import lifespan
import uvicorn
from app.routers import books, users

app = FastAPI(lifespan=lifespan)
    
app.include_router(books.router, prefix="/books", tags=["books"])

@app.get("/")
async def root():
    return {"message": "Hello World"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

