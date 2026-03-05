from sqlmodel import Session, select
from sqlalchemy import func
import uuid
from dataclasses import dataclass

from app.models.artist import Artist
from app.models.genre import (
    ElectronicGenre,
    ExperimentalGenre,
    HipHopGenre,
    JazzFolkGenre,
    MetalGenre,
    OtherGenre,
    PopGenre,
    RockGenre,
)
from app.models.genre_song import (
    ElectronicGenreSong,
    ExperimentalGenreSong,
    HipHopGenreSong,
    JazzFolkGenreSong,
    MetalGenreSong,
    OtherGenreSong,
    PopGenreSong,
    RockGenreSong,
)
from app.models.song import Song
from app.models.song_artist import SongArtist


@dataclass(frozen=True)
class GenreJoinSpec:
    link_model: type
    genre_model: type
    link_field: str
    genre_field: str


GENRE_TO_JOIN_CONFIG: dict[str, GenreJoinSpec] = {
    "rock": GenreJoinSpec(RockGenreSong, RockGenre, "rock_id", "rock_id"),
    "pop": GenreJoinSpec(PopGenreSong, PopGenre, "pop_id", "pop_id"),
    "jazz/folk": GenreJoinSpec(JazzFolkGenreSong, JazzFolkGenre, "jazz_folk_id", "jazz_folk_id"),
    "metal": GenreJoinSpec(MetalGenreSong, MetalGenre, "metal_id", "metal_id"),
    "hip-hop": GenreJoinSpec(HipHopGenreSong, HipHopGenre, "hip_hop_id", "hip_hop_id"),
    "electronic": GenreJoinSpec(ElectronicGenreSong, ElectronicGenre, "electronic_id", "electronic_id"),
    "experimental": GenreJoinSpec(ExperimentalGenreSong, ExperimentalGenre, "experimental_id", "experimental_id"),
    "other": GenreJoinSpec(OtherGenreSong, OtherGenre, "other_id", "other_id"),
}


def _generate_genre_join_clause(spec: GenreJoinSpec, *columns):
    return select(*columns).join(
        spec.genre_model,
        getattr(spec.link_model, spec.link_field) == getattr(spec.genre_model, spec.genre_field),
    )


def _format_duration_ms(duration_ms: int) -> str:
    total_seconds = max(0, duration_ms // 1000)
    minutes, seconds = divmod(total_seconds, 60)
    return f"{minutes:02d}:{seconds:02d}"


def _parse_unique_song_uuids(song_ids: list[str]) -> list[uuid.UUID]:
    unique_song_ids: list[uuid.UUID] = []
    for song_id in dict.fromkeys(song_ids):
        try:
            unique_song_ids.append(uuid.UUID(song_id))
        except ValueError:
            continue
    return unique_song_ids


def _load_songs_by_id(db: Session, unique_song_ids: list[uuid.UUID]) -> dict[str, Song]:
    songs = db.exec(select(Song).where(Song.song_id.in_(unique_song_ids))).all()
    return {str(song.song_id): song for song in songs}


def _load_artist_names_by_song_id(db: Session, unique_song_ids: list[uuid.UUID]) -> dict[str, list[str]]:
    artist_rows = db.exec(
        select(SongArtist, Artist)
        .join(Artist, SongArtist.artist_id == Artist.artist_id)
        .where(SongArtist.song_id.in_(unique_song_ids))
    ).all()
    artist_names_by_song_id: dict[str, list[str]] = {}
    for song_artist, artist in artist_rows:
        key = str(song_artist.song_id)
        artist_names_by_song_id.setdefault(key, []).append(artist.name)
    return artist_names_by_song_id


def _load_genre_names_by_song_id(db: Session, unique_song_ids: list[uuid.UUID]) -> dict[str, set[str]]:
    genre_names_by_song_id: dict[str, set[str]] = {}
    for spec in GENRE_TO_JOIN_CONFIG.values():
        genre_rows = db.exec(
            _generate_genre_join_clause(spec, spec.link_model.song_id, spec.genre_model.name).where(
                spec.link_model.song_id.in_(unique_song_ids)
            )
        ).all()
        for genre_song_id, genre_name in genre_rows:
            key = str(genre_song_id)
            genre_names_by_song_id.setdefault(key, set()).add(genre_name)
    return genre_names_by_song_id


def _map_song_result(
    song_id: str,
    songs_by_id: dict[str, Song],
    artist_names_by_song_id: dict[str, list[str]],
    genre_names_by_song_id: dict[str, set[str]],
) -> dict | None:
    song = songs_by_id.get(song_id)
    if song is None:
        return None

    return {
        "song_id": str(song.song_id),
        "name": song.name,
        "youtube_id": song.youtube_id,
        "duration": _format_duration_ms(song.duration_ms),
        "artists": artist_names_by_song_id.get(song_id, []),
        "genres": sorted(genre_names_by_song_id.get(song_id, set())),
    }


def fetch_random_song_ids(db: Session, size: int = 4, genre: str | None = None) -> list[str]:
    """
    Return a random in-memory session as a list of song_id strings.
    """
    limit = max(1, size)

    if genre:
        spec = GENRE_TO_JOIN_CONFIG.get(genre)
        if spec is None:
            return []
        song_ids = db.exec(
            select(spec.link_model.song_id)
            .order_by(func.random())
            .limit(limit)
        ).all()
        return [str(song_id) for song_id in song_ids]

    songs = db.exec(select(Song).order_by(func.random()).limit(limit)).all()
    return [str(song.song_id) for song in songs]


def get_songs_with_artists_by_ids(db: Session, song_ids: list[str]) -> list[dict]:
    if not song_ids:
        return []

    unique_song_ids = _parse_unique_song_uuids(song_ids)
    if not unique_song_ids:
        return []

    songs_by_id = _load_songs_by_id(db, unique_song_ids)
    artist_names_by_song_id = _load_artist_names_by_song_id(db, unique_song_ids)
    genre_names_by_song_id = _load_genre_names_by_song_id(db, unique_song_ids)

    result = []
    for song_id in song_ids:
        mapped_song = _map_song_result(
            song_id,
            songs_by_id,
            artist_names_by_song_id,
            genre_names_by_song_id,
        )
        if mapped_song is not None:
            result.append(mapped_song)
    return result
