export interface RecommendationRequest {
  songIds?: string[];
  genre?: string | null;
  shouldRecommendNewArtists?: boolean;
}

export interface RecommendedSong {
  songId: string;
  name: string;
  youtubeId: string;
  duration: string;
  artists: string[];
  genres: string[];
}

export interface Recommendation {
  recommendedSongs: RecommendedSong[];
}

export interface RecommendationRequestDto {
  song_ids?: string[];
  genre?: string | null;
  shouldRecommendNewArtists?: boolean;
}

export interface RecommendedSongDto {
  song_id: string;
  name: string;
  youtube_id: string;
  duration: string;
  artists: string[];
  genres: string[];
}

export interface RecommendationResponseDto {
  recommended_songs: RecommendedSongDto[];
}
