import { HttpClient, HttpHeaders } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable, map } from 'rxjs';
import { environment } from '../../../../environments/environment';
import { Genre, GenreDto } from '../../domain/genre';
import {
  Recommendation,
  RecommendationRequest,
  RecommendationResponseDto,
} from '../../domain/recommendation';
import {
  mapGenreDtoToGenre,
  mapRecommendationRequestToDto,
  mapRecommendationResponseDtoToRecommendation,
} from '../../mappers/music.mapper';

@Injectable({ providedIn: 'root' })
export class MusicClient {
  readonly #apiUrl = environment.apiUrl;
  readonly #http = inject(HttpClient);
  readonly #httpOptions = {
    headers: new HttpHeaders({ 'Content-Type': 'application/json' }),
  };

  getHelloWorld(): Observable<{ message: string }> {
    return this.#http.get<{ message: string }>(`${this.#apiUrl}/hello`);
  }

  getGenres(): Observable<Genre[]> {
    return this.#http
      .get<GenreDto[]>(`${this.#apiUrl}/api/v1/genres`)
      .pipe(map((genres) => genres.map(mapGenreDtoToGenre)));
  }

  getRecommendations(request?: RecommendationRequest): Observable<Recommendation> {
    return this.#http
      .post<RecommendationResponseDto>(
        `${this.#apiUrl}/api/v1/recommendations`,
        mapRecommendationRequestToDto(request),
        this.#httpOptions
      )
      .pipe(map(mapRecommendationResponseDtoToRecommendation));
  }
}
