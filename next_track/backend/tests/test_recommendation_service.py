from __future__ import annotations

import sys
import unittest
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.services.recommendation_service import (
    IRMCRecommender,
    _longest_common_suffix,
    _longest_common_suffix_weight,
)


class RecommendationServiceTestCase(unittest.TestCase):
    def test_longest_common_suffix_and_weight(self) -> None:
        self.assertEqual(_longest_common_suffix(["a", "b", "c"], ["x", "b", "c"]), 2)
        self.assertEqual(_longest_common_suffix(["a", "b"], ["c", "d"]), 0)
        self.assertEqual(_longest_common_suffix_weight(0), 0)
        self.assertEqual(_longest_common_suffix_weight(3), 7)

    def test_fit_skips_single_item_sessions(self) -> None:
        recommender = IRMCRecommender()

        recommender.fit(
            {
                "short-session": ["only-one-song"],
                "valid-session": ["song-a", "song-b"],
            }
        )

        self.assertNotIn("short-session", recommender._doc_index)
        self.assertIn("valid-session", recommender._doc_index)

    def test_predict_ranks_candidates_by_suffix_score(self) -> None:
        recommender = IRMCRecommender(past_items=4, top_k=5)
        recommender.fit(
            {
                "session-1": ["intro", "song-a", "song-b", "song-c"],
                "session-2": ["other", "song-a", "song-b", "song-d"],
            }
        )

        result = recommender.predict(["intro", "song-a", "song-b"])

        self.assertEqual(result, ["song-c", "song-d"])

    def test_predict_honors_genre_filter(self) -> None:
        recommender = IRMCRecommender(past_items=4, top_k=5)
        recommender.fit(
            {
                "rock-session": ["context-rock", "last-song", "candidate-rock"],
                "pop-session": ["context-pop", "last-song", "candidate-pop"],
            },
            song_genres={
                "context-rock": {"rock"},
                "candidate-rock": {"rock"},
                "context-pop": {"pop"},
                "candidate-pop": {"pop"},
            },
        )

        result = recommender.predict(["context-rock", "last-song"], genre="rock")

        self.assertEqual(result, ["candidate-rock"])

    def test_predict_sequence_prefers_new_artists_when_requested(self) -> None:
        recommender = IRMCRecommender(past_items=4, top_k=5)
        recommender.fit(
            {
                "session-1": ["seed-song", "last-song", "repeat-artist-song"],
                "session-2": ["seed-song", "last-song", "repeat-artist-song"],
                "session-3": ["other-song", "last-song", "new-artist-song"],
            },
            song_artists={
                "seed-song": {"artist-a"},
                "repeat-artist-song": {"artist-a"},
                "new-artist-song": {"artist-b"},
            },
        )

        result = recommender.predict_sequence(
            seed=["seed-song", "last-song"],
            n_predictions=1,
            should_recommend_new_artists=True,
        )

        self.assertEqual(result, ["new-artist-song"])
