from fastapi import FastAPI, Depends
from sqlmodel import SQLModel, Session, select
from fastapi.routing import APIRoute
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.db import engine, get_session
from app.models import Item



app = FastAPI(
    title="NextTrack",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Set all CORS enabled origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

@app.get("/")
def root():
    return {"message": "API is running"}

@app.get("/health")
def health():
    return {"status": "ok"}

# dummy endpoints for testing

@app.get("/hello")
def hello_world():
    return {"message": "OK"}

@app.get("/items")
def get_items(session: Session = Depends(get_session)):
    items = session.exec(select(Item)).all()
    return items

@app.post("/items")
def create_item(item: Item, session: Session = Depends(get_session)):
    session.add(item)
    session.commit()
    session.refresh(item)
    return item