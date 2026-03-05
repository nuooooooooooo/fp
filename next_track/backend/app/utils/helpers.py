
import datetime


def get_datetime_now():
    return datetime.datetime.now(datetime.timezone.utc)

def normalize_genre_name(genre: str | None) -> str | None:
    if genre is None:
        return None

    normalized = " ".join(genre.strip().lower().replace("_", " ").split())
    if not normalized:
        return None

    aliases = {
        "hip hop": "hip-hop",
        "hiphop": "hip-hop",
        "jazz folk": "jazz/folk",
        "jazzfolk": "jazz/folk",
    }
    return aliases.get(normalized, normalized)

    