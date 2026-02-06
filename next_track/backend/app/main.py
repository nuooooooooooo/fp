from fastapi import FastAPI, Depends
from sqlmodel import SQLModel, Session, select
from fastapi.routing import APIRouter
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.db import engine, get_session
from app.models.models import Item



# Initializes the app
app = FastAPI(
    title="NextTrack",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# sets up the router with the API version prefix
api_router = APIRouter(prefix=settings.API_V1_STR)


# Sets all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Creates the database tables when the app starts
@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

#  Root endpoint
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

@api_router.get("/items")
def get_items(session: Session = Depends(get_session)):
    items = session.exec(select(Item)).all()
    return items

@api_router.post("/items")
def create_item(item: Item, session: Session = Depends(get_session)):
    session.add(item)
    session.commit()
    session.refresh(item)
    return item

app.include_router(api_router)