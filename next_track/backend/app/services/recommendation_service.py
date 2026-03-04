"""
IR-MC: Information Retrieval Markov Chain Recommender
======================================================
Original algorithm described in:
  Tofani, A., Borges, R. & Queiroz, M. (2022).
  Dynamic session-based music recommendation using information retrieval techniques.
  User Modeling and User-Adapted Interaction, 32, 575–609.
  https://doi.org/10.1007/s11257-022-09343-w

This is a reimplementation based solely on the mathematical
formulas in the paper and the accompanying PhD thesis (Tofani, 2023).
"""

from collections import defaultdict
from typing import Optional


def _longest_common_suffix(query_prefix: list, doc_prefix: list) -> int:
    """
    Compute the Longest Common Suffix length between two sequences.

    As defined in Tofani et al. (2022), Eq. 3.3:
      longest common suffix(q, d, n) = max(longest common suffix(q[:-1], d[:-1], n) + 1)
                        if q[-1] == d[-1] and both non-empty, else 0.
    """
    length = 0
    for q_item, d_item in zip(reversed(query_prefix), reversed(doc_prefix)):
        if q_item == d_item:
            length += 1
        else:
            break
    return length


def _longest_common_suffix_weight(longest_common_suffix_length: int) -> float:
    """
    Exponential weighting scheme from Tofani et al. (2022), Eq. 3.2:
      weight = 2^longest common suffix - 1
    A match of length 0 contributes 0 (2^0 - 1 = 0).
    A match of length 1 contributes 1 (2^1 - 1 = 1).
    A match of length 2 contributes 3 (2^2 - 1 = 3), etc.
    """
    return (2 ** longest_common_suffix_length) - 1


class IRMCRecommender:
    """
    Session-based recommender using an IR-based Markov Chain (IR-MC) as proposed by Tofani et al. (2022).

    Training phase: index sessions into an inverted index (O(1) lookups).
    Prediction phase: retrieve candidate sessions via the last query item, then score candidate next-items using the longest common suffix weighting scheme.

    Parameters
    ----------
    past_items : int
        Number of preceding items in the query window considered for the longest common suffix calculation. Optimal value is 4 per Tofani et al.
    top_k : int
        Number of top recommendations to return.
    """

    def __init__(self, past_items: int = 4, top_k: int = 20):
        self.past_items = past_items
        self.top_k = top_k
        self.genre_match_boost = 2.0

        # doc_index: session_id -> ordered list of song_ids
        self._doc_index: dict[str, list[str]] = {}

        # term_index: song_id -> set of session_ids containing that song
        self._term_index: dict[str, set[str]] = defaultdict(set)

        # song_genres: song_id -> normalized genre names (lowercase)
        self._song_genres: dict[str, set[str]] = {}
        # session_genres: session_id -> normalized genre names (lowercase)
        self._session_genres: dict[str, set[str]] = {}

    def fit(
        self,
        db_sessions: dict[str, list[str]],
        song_genres: Optional[dict[str, set[str]]] = None,
    ) -> None:
        """
        Training phase
        Index sessions loaded directly from the database and build an inverted index.

        Parameters
        ----------
        db_sessions : dict mapping session_id (str) -> ordered list of song_ids (str)
            Build this with load_sessions_from_db() below.
        """
        self._song_genres = song_genres or {}

        for session_id, song_ids in db_sessions.items():
            if len(song_ids) < 2:
                continue
            self._index_session(session_id, song_ids)
            session_genres: set[str] = set()
            for song_id in song_ids:
                session_genres.update(self._song_genres.get(song_id, set()))
            self._session_genres[session_id] = session_genres

    def _index_session(self, session_id: str, song_ids: list[str]) -> None:
        """
        Incrementally add a single new session to the index.
        Because training = indexing, this enables dynamic updates
        without retraining.
        """
        self._doc_index[session_id] = song_ids
        for song_id in song_ids:
            self._term_index[song_id].add(session_id)

    def predict(
        self,
        query: list[str],
        exclude: Optional[list[str]] = None,
        genre: Optional[str] = None,
    ) -> list[str]:
        """
        Prediction phase
        ----------------
        
        Predict a list of songs given a session.

        Parameters
        ----------
        query : list of str
            Ordered list of song_ids representing a session.
            The last item is used for candidate retrieval (Markov step).
            Up to n past items are used for longest common suffix scoring.
        exclude : list of str, optional
            Song IDs to exclude from recommendations, can be used to avoid recommending songs already in the session.

        Returns
        -------
        list of str
            Top-k recommended song_ids, ordered by descending score.
        """
        if not query:
            return []

        last_item = query[-1]
        query_prefix = query[:-1]  # everything before the last item


        # Candidate selection: retrieve all sessions containing last_item
        candidate_session_ids = self._term_index.get(last_item, set())
        if genre:
            candidate_session_ids = {
                session_id
                for session_id in candidate_session_ids
                if genre in self._session_genres.get(session_id, set())
            }
        if not candidate_session_ids:
            return []

        # Limit prefix to past_items for longest common suffix computation
        query_context = query_prefix[-self.past_items:]

        scores: dict[str, float] = defaultdict(float)

        for session_id in candidate_session_ids:
            doc = self._doc_index[session_id]

            # Scan every occurrence of last_item in this session
            for pos, item in enumerate(doc):
                if item != last_item:
                    continue
                # The next item after this occurrence is the candidate
                if pos + 1 >= len(doc):
                    continue

                next_item = doc[pos + 1]

                # Compute longest common suffix between query_context and the
                # doc_prefix ending just before this occurrence
                doc_prefix = doc[max(0, pos - self.past_items):pos]
                lcs = _longest_common_suffix(query_context, doc_prefix)
                weight = _longest_common_suffix_weight(lcs)
                score = weight if weight > 0 else 1

                if genre and genre in self._song_genres.get(next_item, set()):
                    score *= self.genre_match_boost

                # weight = 0 when lcs = 0 (first-order MC, base case)
                # weight > 0 exponentially rewards longer common suffixes
                scores[next_item] += score

        # Remove excluded items
        if exclude:
            for song_id in exclude:
                scores.pop(song_id, None)

        # Return top-k sorted by descending score
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [song_id for song_id, _ in ranked[: self.top_k]]


    def predict_sequence(
        self,
        seed: list[str],
        n_predictions: int = 5,
        window_size: int = 4,
        genre: Optional[str] = None,
    ) -> list[str]:
        """
        Iteratively predict n_predictions songs using a sliding window.

        At each step the window shifts: the oldest song is excluded and the
        last predicted song is appended. Songs already in the seed are
        excluded from recommendations to avoid immediate repeats.

        Parameters
        ----------
        seed : list of str
            The starting session (ideally at least `window_size` songs).
        n_predictions : int
            How many songs to predict (default 5).
        window_size : int
            Size of the sliding context window (default 4, optimal per paper).

        Returns
        -------
        list of str
            The predicted sequence of song_ids.
        """
        window = list(seed[-window_size:])
        predicted: list[str] = []
        excluded = set(seed)

        for _ in range(n_predictions):
            top = self.predict(window, exclude=list(excluded), genre=genre)
            if not top:
                break
            next_song = top[0]
            predicted.append(next_song)
            excluded.add(next_song)
            window = window[1:] + [next_song]

        return predicted
