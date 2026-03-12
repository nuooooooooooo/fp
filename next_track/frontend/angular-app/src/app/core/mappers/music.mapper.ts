import { Genre, GenreDto } from '../domain/genre';
import {
  Recommendation,
  RecommendationRequest,
  RecommendationRequestDto,
  RecommendationResponseDto,
  RecommendedSong,
  RecommendedSongDto,
} from '../domain/recommendation';

export function mapGenreDtoToGenre(dto: GenreDto): Genre {
  return {
    id: dto.id,
    name: dto.name,
  };
}

export function mapRecommendationRequestToDto(
  request?: RecommendationRequest
): RecommendationRequestDto | null {
  if (!request) {
    return null;
  }

  return {
    song_ids: request.songIds,
    genre: request.genre,
  };
}

export function mapRecommendedSongDtoToRecommendedSong(
  dto: RecommendedSongDto
): RecommendedSong {
  return {
    songId: dto.song_id,
    name: dto.name,
    youtubeId: dto.youtube_id,
    duration: dto.duration,
    artists: dto.artists,
    genres: dto.genres,
  };
}

export function mapRecommendationResponseDtoToRecommendation(
  dto: RecommendationResponseDto
): Recommendation {
  return {
    recommendedSongs: dto.recommended_songs.map(mapRecommendedSongDtoToRecommendedSong),
  };
}
