from fastapi import APIRouter, Depends, Request, FastAPI
from sqlmodel import Session

from app.config.db import get_session
from app.schemas.recommendation_schema import (
    RecommendationRequest,
    RecommendationResponse,
)
from app.services.recommendation_service import IRMCRecommender
from app.services.session_loader_service import (
    load_sessions_from_db,
    load_sessions_signature,
    load_song_genres_from_db,
)
from app.services.song_service import fetch_random_song_ids, get_songs_with_artists_by_ids
from app.utils.helpers import normalize_genre_name


router = APIRouter(tags=["recommendations"])


def bootstrap_recommender(app: FastAPI, db: Session) -> IRMCRecommender:
    current_signature = load_sessions_signature(db)
    recommender = IRMCRecommender(past_items=4, top_k=20)
    recommender.fit(
        load_sessions_from_db(db),
        song_genres=load_song_genres_from_db(db),
    )
    app.state.recommender = recommender
    app.state.recommender_signature = current_signature
    return recommender


def get_recommender(
    request: Request,
    db: Session = Depends(get_session),
) -> IRMCRecommender:
    current_signature = load_sessions_signature(db)
    recommender: IRMCRecommender | None = getattr(request.app.state, "recommender", None)
    cached_signature = getattr(request.app.state, "recommender_signature", None)

    if recommender is None or cached_signature != current_signature:
        recommender = bootstrap_recommender(request.app, db)
    return recommender


@router.post("/recommendations", response_model=RecommendationResponse)
def get_recommendations(
    payload: RecommendationRequest | None = None,
    db: Session = Depends(get_session),
    recommender: IRMCRecommender = Depends(get_recommender),
):
    selected_genre = normalize_genre_name(payload.genre) if payload else None

    # if no song_ids were provided, create a session with 4 random songs as seed
    if payload is None or not payload.song_ids:
        seed_song_ids = fetch_random_song_ids(db, size=4, genre=selected_genre)
    else:
        seed_song_ids = payload.song_ids

    recommended_song_ids = recommender.predict_sequence(
        seed=seed_song_ids,
        n_predictions=5,
        window_size=4,
        genre=selected_genre,
    )
    recommended_songs = get_songs_with_artists_by_ids(db, recommended_song_ids)

    return {"recommended_songs": recommended_songs}
