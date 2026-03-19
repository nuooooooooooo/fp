from collections import defaultdict
from datetime import datetime
from sqlmodel import Session, select
from sqlalchemy import func
from app.models import SongSession
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
from app.models.artist import Artist
from app.models.song_artist import SongArtist


GENRE_JOIN_CONFIG = [
    (RockGenreSong, RockGenre, "rock_id", "rock_id"),
    (PopGenreSong, PopGenre, "pop_id", "pop_id"),
    (JazzFolkGenreSong, JazzFolkGenre, "jazz_folk_id", "jazz_folk_id"),
    (MetalGenreSong, MetalGenre, "metal_id", "metal_id"),
    (HipHopGenreSong, HipHopGenre, "hip_hop_id", "hip_hop_id"),
    (ElectronicGenreSong, ElectronicGenre, "electronic_id", "electronic_id"),
    (ExperimentalGenreSong, ExperimentalGenre, "experimental_id", "experimental_id"),
    (OtherGenreSong, OtherGenre, "other_id", "other_id"),
]


def load_sessions_from_db(db: Session) -> dict[str, list[str]]:
    """
    Load all training sessions from the database, ordered by listened_at.
    Returns a dict: session_id (str) -> [song_id (str), ...] in order.
    Skips sessions with fewer than 2 songs.
    """
    rows = db.exec(
        select(SongSession).order_by(
            SongSession.session_id, SongSession.listened_at
        )
    ).all()

    sessions: dict[str, list[str]] = defaultdict(list)
    for row in rows:
        sessions[str(row.session_id)].append(str(row.song_id))

    return {sid: songs for sid, songs in sessions.items() if len(songs) >= 2}


def load_sessions_signature(db: Session) -> tuple[int, datetime | None]:
    """
    Return a lightweight fingerprint of training data.
    Changes when rows are added/removed or listened_at max changes.
    """
    count_value, max_listened_at = db.exec(
        select(func.count(SongSession.session_id), func.max(SongSession.listened_at))
    ).one()
    return int(count_value or 0), max_listened_at


def load_song_genres_from_db(db: Session) -> dict[str, set[str]]:
    """
    Return song_id -> normalized genre names (lowercase).
    """
    song_genres: dict[str, set[str]] = defaultdict(set)

    for link_model, genre_model, link_field, genre_field in GENRE_JOIN_CONFIG:
        genre_rows = db.exec(
            select(link_model.song_id, genre_model.name)
            .join(genre_model, getattr(link_model, link_field) == getattr(genre_model, genre_field))
        ).all()
        for song_id, genre_name in genre_rows:
            normalized_genre = str(genre_name).strip().lower()
            if normalized_genre:
                song_genres[str(song_id)].add(normalized_genre)

    return song_genres


def load_song_artists_from_db(db: Session) -> dict[str, set[str]]:
    """
    Return song_id -> normalized artist names (lowercase).
    """
    artist_rows = db.exec(select(SongArtist.song_id, SongArtist.artist_id)).all()

    song_artists: dict[str, set[str]] = defaultdict(set)

    artist_names_by_id = {
        str(artist.artist_id): str(artist.name).strip().lower()
        for artist in db.exec(select(Artist)).all()
        if str(artist.name).strip()
    }

    for song_id, artist_id in artist_rows:
        normalized_artist = artist_names_by_id.get(str(artist_id))
        if normalized_artist:
            song_artists[str(song_id)].add(normalized_artist)

    return song_artists
