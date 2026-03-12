from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.config.db import get_session
from app.schemas.genre_schema import GenreResponse
from app.services.genre_service import get_all_genres


router = APIRouter(tags=["genres"])


@router.get("/genres", response_model=list[GenreResponse])
def list_genres(db: Session = Depends(get_session)) -> list[GenreResponse]:
    return [
        GenreResponse(id=str(genre.genre_id), name=genre.name)
        for genre in get_all_genres(db)
    ]
