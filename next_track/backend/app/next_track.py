from fastapi import FastAPI, Depends
from sqlmodel import SQLModel, Session, select
from fastapi.routing import APIRouter
from fastapi.middleware.cors import CORSMiddleware
from app.config.config import settings
from app.config.db import engine, get_session
from app.config.initialize_db import initialize_db
from app.controllers.recommendation_controller import (
    router as recommendation_router,
    bootstrap_recommender,
)
import app.models  



# initializes the app
app = FastAPI(
    title="NextTrack",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# sets up the router with the API version prefix
api_router = APIRouter(prefix=settings.API_V1_STR)


# sets all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# creates the database tables when the app starts
@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)
    initialize_db(song_limit=100) # populates the db with the datasets
    with Session(engine) as session:
        bootstrap_recommender(app, session)

#  root endpoint
@app.get("/")
def root():
    return {"message": "API is running"}

@api_router.get("/health")
def health():
    return {"status": "ok"}

# dummy endpoints for testing

@app.get("/hello")
def hello_world():
    return {"message": "OK"}


api_router.include_router(recommendation_router)
app.include_router(api_router)
