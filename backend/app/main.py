from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import auth_router
from app.api.routes import router
from app.core.config import settings
from app.core.database import close_mongo_connection, connect_to_mongo
from app.services.classifier import classifier


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    classifier.load()
    yield
    await close_mongo_connection()


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")
app.include_router(auth_router, prefix="/api")
