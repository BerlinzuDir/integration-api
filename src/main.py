from fastapi import FastAPI

from src.api.api import router as api_router
from mangum import Mangum

app = FastAPI()

app.include_router(api_router, prefix="/api")
handler = Mangum(app)
