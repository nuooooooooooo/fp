from sqlmodel import SQLModel, Field
from datetime import datetime, timezone
from sqlalchemy import DateTime
from ..utils.helpers import get_datetime_now
import uuid

class SongSession(SQLModel, table=True):
    song_id: uuid.UUID = Field(default=None, foreign_key="song.song_id", primary_key=True)
    session_id: uuid.UUID = Field(default=None, foreign_key="session.session_id", primary_key=True)
    listened_at: datetime | None = Field(
        default_factory=get_datetime_now,
        sa_type=DateTime(timezone=True), 
    )