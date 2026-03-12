import { inject, Injectable } from '@angular/core';
import { MusicClient } from './api/music.client';
import { Router } from '@angular/router';
import { RecommendationRequest } from '../domain/recommendation';

@Injectable({
  providedIn: 'root'
})
export class MusicService {
  
  private readonly musicClient: MusicClient = inject(MusicClient);
  private readonly router = inject(Router);

  getHelloWorld() {
    return this.musicClient.getHelloWorld();
  }

  getGenres() {
    return this.musicClient.getGenres();
  }

  getRecommendations(request?: RecommendationRequest) {
    return this.musicClient.getRecommendations(request);
  }
}
