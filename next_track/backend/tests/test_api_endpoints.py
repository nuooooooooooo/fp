from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.config.db import get_session
from app.controllers.recommendation_controller import get_recommender
from app.next_track import app


class FakeRecommender:
    def __init__(self, predicted_song_ids: list[str]):
        self.predicted_song_ids = predicted_song_ids
        self.calls: list[dict] = []

    def predict_sequence(
        self,
        seed: list[str],
        n_predictions: int = 5,
        window_size: int = 4,
        genre: str | None = None,
        should_recommend_new_artists: bool = False,
    ) -> list[str]:
        self.calls.append(
            {
                "seed": seed,
                "n_predictions": n_predictions,
                "window_size": window_size,
                "genre": genre,
                "should_recommend_new_artists": should_recommend_new_artists,
            }
        )
        return self.predicted_song_ids


class APITestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.original_startup = list(app.router.on_startup)
        app.router.on_startup.clear()

    @classmethod
    def tearDownClass(cls) -> None:
        app.router.on_startup[:] = cls.original_startup

    def setUp(self) -> None:
        self.fake_db = object()
        self.fake_recommender = FakeRecommender(
            predicted_song_ids=["00000000-0000-0000-0000-000000000010"]
        )

        def override_get_session():
            yield self.fake_db

        def override_get_recommender():
            return self.fake_recommender

        app.dependency_overrides[get_session] = override_get_session
        app.dependency_overrides[get_recommender] = override_get_recommender
        self.client = TestClient(app)

    def tearDown(self) -> None:
        app.dependency_overrides.clear()
        self.client.close()

    def test_root_endpoint_returns_status_message(self) -> None:
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "API is running"})

    def test_hello_endpoint_returns_ok_message(self) -> None:
        response = self.client.get("/hello")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "OK"})

    def test_health_endpoint_returns_ok_status(self) -> None:
        response = self.client.get("/api/v1/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    @patch("app.controllers.genre_controller.get_all_genres")
    def test_genres_endpoint_returns_serialized_genres(self, mock_get_all_genres) -> None:
        mock_get_all_genres.return_value = [
            type("Genre", (), {"genre_id": "genre-2", "name": "Pop"})(),
            type("Genre", (), {"genre_id": "genre-1", "name": "Rock"})(),
        ]

        response = self.client.get("/api/v1/genres")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            [
                {"id": "genre-2", "name": "Pop"},
                {"id": "genre-1", "name": "Rock"},
            ],
        )
        mock_get_all_genres.assert_called_once_with(self.fake_db)

    @patch("app.controllers.recommendation_controller.get_songs_with_artists_by_ids")
    @patch("app.controllers.recommendation_controller.fetch_random_song_ids")
    def test_recommendations_endpoint_uses_random_seed_when_song_ids_are_missing(
        self,
        mock_fetch_random_song_ids,
        mock_get_songs_with_artists_by_ids,
    ) -> None:
        mock_fetch_random_song_ids.return_value = [
            "00000000-0000-0000-0000-000000000001",
            "00000000-0000-0000-0000-000000000002",
            "00000000-0000-0000-0000-000000000003",
            "00000000-0000-0000-0000-000000000004",
        ]
        mock_get_songs_with_artists_by_ids.return_value = [
            {
                "song_id": "00000000-0000-0000-0000-000000000010",
                "name": "Recommended Song",
                "youtube_id": "yt-1",
                "duration": "03:15",
                "artists": ["New Artist"],
                "genres": ["rock"],
            }
        ]

        response = self.client.post("/api/v1/recommendations")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "recommended_songs": [
                    {
                        "song_id": "00000000-0000-0000-0000-000000000010",
                        "name": "Recommended Song",
                        "youtube_id": "yt-1",
                        "duration": "03:15",
                        "artists": ["New Artist"],
                        "genres": ["rock"],
                    }
                ]
            },
        )
        mock_fetch_random_song_ids.assert_called_once_with(
            self.fake_db,
            size=4,
            genre=None,
        )
        self.assertEqual(
            self.fake_recommender.calls[0],
            {
                "seed": mock_fetch_random_song_ids.return_value,
                "n_predictions": 5,
                "window_size": 4,
                "genre": None,
                "should_recommend_new_artists": False,
            },
        )
        mock_get_songs_with_artists_by_ids.assert_called_once_with(
            self.fake_db,
            ["00000000-0000-0000-0000-000000000010"],
        )

    @patch("app.controllers.recommendation_controller.get_songs_with_artists_by_ids")
    @patch("app.controllers.recommendation_controller.fetch_random_song_ids")
    def test_recommendations_endpoint_uses_payload_values(
        self,
        mock_fetch_random_song_ids,
        mock_get_songs_with_artists_by_ids,
    ) -> None:
        mock_get_songs_with_artists_by_ids.return_value = []

        response = self.client.post(
            "/api/v1/recommendations",
            json={
                "song_ids": [
                    "00000000-0000-0000-0000-000000000101",
                    "00000000-0000-0000-0000-000000000102",
                ],
                "genre": "Hip Hop",
                "shouldRecommendNewArtists": True,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"recommended_songs": []})
        mock_fetch_random_song_ids.assert_not_called()
        self.assertEqual(
            self.fake_recommender.calls[0],
            {
                "seed": [
                    "00000000-0000-0000-0000-000000000101",
                    "00000000-0000-0000-0000-000000000102",
                ],
                "n_predictions": 5,
                "window_size": 4,
                "genre": "hip-hop",
                "should_recommend_new_artists": True,
            },
        )

