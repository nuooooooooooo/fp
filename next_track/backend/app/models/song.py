from sqlmodel import SQLModel, Field, Relationship
import uuid
from .artist import Artist
from .song_artist import SongArtist

class Song(SQLModel, table=True):
    song_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(min_length=1, max_length=1000)
    youtube_id: str = Field(min_length=1, max_length=15)
    isrc_id: str = Field(min_length=1, max_length=15)
    duration_ms: int = Field(gt=0) #TODO check if this is the correct type for duration
    artists: list['Artist'] = Relationship(back_populates="songs", link_model=SongArtist)