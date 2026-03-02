from sqlmodel import SQLModel, Field, Relationship
import uuid
from .song_artist import SongArtist


class Artist(SQLModel, table=True):
    artist_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(min_length=1, max_length=255)
    songs: list['Song'] = Relationship(back_populates="artists", link_model=SongArtist)
