from fastapi import FastAPI 
from app.core.lifespan import lifespan
import uvicorn
from app.api.api import api_router 

app = FastAPI(lifespan=lifespan)
    
app.include_router(api_router)

@app.get("/")
async def root():
    return {"message": "Hello World"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

