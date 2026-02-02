import { inject, Injectable } from '@angular/core';
import { MusicClient } from './api/music.client';
import { Router } from '@angular/router';

@Injectable({
  providedIn: 'root'
})
export class MusicService {
  
  private readonly musicClient: MusicClient = inject(MusicClient);
  private readonly router = inject(Router);

  getHelloWorld() {
    return this.musicClient.getHelloWorld();
  }
}
