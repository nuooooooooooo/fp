from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.utils.helpers import normalize_genre_name


class RecommendationRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    song_ids: list[str] | None = None
    genre: str | None = None
    should_recommend_new_artists: bool = Field(
        default=False,
        alias="shouldRecommendNewArtists",
    )

    @field_validator("genre")
    @classmethod
    def normalize_genre(cls, value: str | None) -> str | None:
        return normalize_genre_name(value)

class RecommendedSong(BaseModel):
    song_id: str
    name: str
    youtube_id: str
    duration: str
    artists: list[str]
    genres: list[str]


class RecommendationResponse(BaseModel):
    recommended_songs: list[RecommendedSong]
