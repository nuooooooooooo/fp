from sqlmodel import Session, select

from app.models.genre import Genre


def get_all_genres(db: Session) -> list[Genre]:
    return db.exec(select(Genre).order_by(Genre.name)).all()
