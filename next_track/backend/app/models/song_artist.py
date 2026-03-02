from sqlmodel import SQLModel, Field
import uuid

class SongArtist(SQLModel, table=True):
    song_id: uuid.UUID = Field(default=None, foreign_key="song.song_id", primary_key=True)
    artist_id: uuid.UUID = Field(default=None, foreign_key="artist.artist_id", primary_key=True)