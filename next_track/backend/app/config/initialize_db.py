from __future__ import annotations
import ast
import re

from collections.abc import Iterable
from datetime import datetime, timezone
import os
from pathlib import Path

import pandas
from sqlmodel import Session, select

import app.models  
from app.config.db import engine
from app.models.artist import Artist
from app.models.genre import ElectronicGenre, ExperimentalGenre, HipHopGenre, JazzFolkGenre, MetalGenre, OtherGenre, PopGenre, RockGenre
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
from app.models.session import Session as PlaySession
from app.models.song import Song
from app.models.song_artist import SongArtist
from app.models.song_session import SongSession


GENRE_MODEL_MAP = {
    "Rock": (RockGenre, RockGenreSong, "rock_id"),
    "Pop": (PopGenre, PopGenreSong, "pop_id"),
    "Jazz/Folk": (JazzFolkGenre, JazzFolkGenreSong, "jazz_folk_id"),
    "Metal": (MetalGenre, MetalGenreSong, "metal_id"),
    "Hip-Hop": (HipHopGenre, HipHopGenreSong, "hip_hop_id"),
    "Electronic": (ElectronicGenre, ElectronicGenreSong, "electronic_id"),
    "Experimental": (ExperimentalGenre, ExperimentalGenreSong, "experimental_id"),
    "Other": (OtherGenre, OtherGenreSong, "other_id"),
}

TABLES_TO_CHECK = [
    Song,
    Artist,
    SongArtist,
    PlaySession,
    SongSession,
    RockGenre,
    PopGenre,
    JazzFolkGenre,
    MetalGenre,
    HipHopGenre,
    ElectronicGenre,
    ExperimentalGenre,
    OtherGenre,
    RockGenreSong,
    PopGenreSong,
    JazzFolkGenreSong,
    MetalGenreSong,
    HipHopGenreSong,
    ElectronicGenreSong,
    ExperimentalGenreSong,
    OtherGenreSong,
]


def _normalize_text(value: object) -> str | None:
    if value is None or (isinstance(value, float) and pandas.isna(value)):
        return None
    text = str(value).strip()
    return text or None


def _parse_datetime(value: object) -> datetime | None:
    if value is None or (isinstance(value, float) and pandas.isna(value)):
        return None
    datetime = pandas.to_datetime(value, utc=True, errors="coerce")
    if pandas.isna(datetime):
        return None
    return datetime.to_pydatetime()


def _parse_supergenres(value: object) -> list[str]:
    if value is None or (isinstance(value, float) and pandas.isna(value)):
        return []

    # normalizes iterables of strings (tuples, lists, sets)
    if isinstance(value, Iterable) and not isinstance(value, (str, bytes)):
        values = [str(v).strip().strip("'\"") for v in value]
        return [v for v in values if v]

    # normalizes text representations
    text = _normalize_text(value)
    if not text:
        return []

    if text.startswith("[") and text.endswith("]"):
        try:
            literal = ast.literal_eval(text)
            if isinstance(literal, (list, tuple, set)):
                values = [str(v).strip().strip("'\"") for v in literal]
                return [v for v in values if v]
        except (SyntaxError, ValueError):
            pass

        quoted_tokens = re.findall(r"""['"]([^'"]+)['"]""", text)
        if quoted_tokens:
            values = [token.strip() for token in quoted_tokens]
            return [v for v in values if v]

    normalized = text.replace(";", ",").replace("|", ",")
    if "," in normalized:
        raw_tokens = normalized.split(",")
    else:
        raw_tokens = normalized.split()

    values = [token.strip().strip("[](){}").strip("'\"") for token in raw_tokens]
    return [v for v in values if v]


def _ensure_genre(session: Session, genre_name: str):
    genre_key = genre_name.strip()
    if genre_key not in GENRE_MODEL_MAP:
        return None, None, None

    genre_model, link_model, genre_id_field = GENRE_MODEL_MAP[genre_key]
    genre = session.exec(select(genre_model).where(genre_model.name == genre_key)).first()
    if genre is None:
        genre = genre_model(name=genre_key)
        session.add(genre)
        session.flush()
    return genre, link_model, genre_id_field


def _load_isrc_map(csv_path: Path) -> dict[str, str]:
    if not csv_path.exists():
        return {}
    dataframe = pandas.read_csv(csv_path)

    col_isrc = next(c for c in dataframe.columns if c.lower() == "isrc")
    col_youtube = next(c for c in dataframe.columns if c.lower() == "youtube_id")

    mapping: dict[str, str] = {}
    for _, row in dataframe.iterrows():
        isrc = _normalize_text(row.get(col_isrc))
        youtube = _normalize_text(row.get(col_youtube))
        if isrc and youtube:
            mapping[isrc] = youtube
    return mapping


def _all_target_tables_are_empty(session: Session) -> bool:
    for model in TABLES_TO_CHECK:
        has_rows = session.exec(select(model).limit(1)).first() is not None
        if has_rows:
            return False
    return True


def _parse_song_limit(song_limit: int | None) -> int | None:
    if song_limit is not None:
        if song_limit <= 0:
            raise ValueError("song_limit must be a positive integer")
        return song_limit

    raw_limit = os.getenv("INIT_DB_SONG_LIMIT")
    if raw_limit is None or raw_limit.strip() == "":
        return None

    parsed_limit = int(raw_limit)
    if parsed_limit <= 0:
        raise ValueError("INIT_DB_SONG_LIMIT must be a positive integer")
    return parsed_limit


def initialize_db(song_limit: int | None = None) -> None:
    parsed_song_limit = _parse_song_limit(song_limit)
    parquet_path = Path("/app/data/final_dataset.parquet")
    csv_path = Path("/app/data/isrcs.csv")
    if not parquet_path.exists():
        raise FileNotFoundError(f"Missing parquet dataset: {parquet_path}")

    isrc_to_youtube = _load_isrc_map(csv_path)
    dataframe = pandas.read_parquet(parquet_path)

    with Session(engine) as session:
        if not _all_target_tables_are_empty(session):
            return

        artists_by_name: dict[str, Artist] = {}
        songs_by_key: dict[str, Song] = {}
        sessions_by_created: dict[datetime, PlaySession] = {}
        song_artist_pairs: set[tuple] = set()
        song_session_pairs: set[tuple] = set()
        genre_song_pairs = {
            link_model: set() for _, (__, link_model, ___) in GENRE_MODEL_MAP.items()
        }
        loaded_songs_count = len(songs_by_key)

        for _, row in dataframe.iterrows():
            song_name = _normalize_text(row.get("recording_name"))
            isrc = _normalize_text(row.get("ISRC")) or "UNKNOWN"
            duration_value = row.get("duration")
            duration_ms = int(duration_value) if pandas.notna(duration_value) and int(duration_value) > 0 else 1
            youtube_id = _normalize_text(isrc_to_youtube.get(isrc)) or "UNKNOWN"

            if not song_name:
                continue

            song_key = f"{isrc}|{song_name}|{duration_ms}"
            song = songs_by_key.get(song_key)
            if song is None:
                if parsed_song_limit is not None and loaded_songs_count >= parsed_song_limit:
                    continue
                song = Song(
                    name=song_name,
                    isrc_id=isrc,
                    youtube_id=youtube_id,
                    duration_ms=duration_ms,
                )
                session.add(song)
                session.flush()
                songs_by_key[song_key] = song
                loaded_songs_count += 1

            artist_name = _normalize_text(row.get("artist_name"))
            if artist_name:
                artist = artists_by_name.get(artist_name)
                if artist is None:
                    artist = Artist(name=artist_name)
                    session.add(artist)
                    session.flush()
                    artists_by_name[artist_name] = artist

                artist_pair = (song.song_id, artist.artist_id)
                if artist_pair not in song_artist_pairs:
                    session.add(SongArtist(song_id=song.song_id, artist_id=artist.artist_id))
                    song_artist_pairs.add(artist_pair)

            created_at = _parse_datetime(row.get("created")) or datetime.now(timezone.utc)
            play_session = sessions_by_created.get(created_at)
            if play_session is None:
                play_session = PlaySession(created_at=created_at)
                session.add(play_session)
                session.flush()
                sessions_by_created[created_at] = play_session

            listened_at = _parse_datetime(row.get("listened_at")) or created_at
            listen_pair = (song.song_id, play_session.session_id)
            if listen_pair not in song_session_pairs:
                session.add(
                    SongSession(
                        song_id=song.song_id,
                        session_id=play_session.session_id,
                        listened_at=listened_at,
                    )
                )
                song_session_pairs.add(listen_pair)

            for genre_name in _parse_supergenres(row.get("supergenres")):
                genre, link_model, genre_id_field = _ensure_genre(session, genre_name)
                if genre is None:
                    continue

                pair = (song.song_id, getattr(genre, genre_id_field))
                if pair in genre_song_pairs[link_model]:
                    continue

                session.add(link_model(song_id=song.song_id, **{genre_id_field: pair[1]}))
                genre_song_pairs[link_model].add(pair)

        session.commit()
