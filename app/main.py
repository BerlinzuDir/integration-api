from fastapi import FastAPI

from app.api.api import router as api_router
from mangum import Mangum

app = FastAPI()


@app.get("/")
async def root():
    return {"message`": "Hello World!"}


app.include_router(api_router, prefix="/api")
handler = Mangum(app)
