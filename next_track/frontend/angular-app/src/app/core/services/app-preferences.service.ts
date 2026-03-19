import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class AppPreferencesService {
  private readonly diverseArtistsStorageKey = 'next-track-diverse-artists';
  private readonly shouldRecommendNewArtistsSubject = new BehaviorSubject<boolean>(true);

  readonly shouldRecommendNewArtists$ = this.shouldRecommendNewArtistsSubject.asObservable();

  constructor() {
    if (typeof window === 'undefined') {
      return;
    }

    const storedValue = localStorage.getItem(this.diverseArtistsStorageKey);

    if (storedValue === null) {
      localStorage.setItem(this.diverseArtistsStorageKey, 'true');
      return;
    }

    this.shouldRecommendNewArtistsSubject.next(storedValue !== 'false');
  }

  get shouldRecommendNewArtists(): boolean {
    return this.shouldRecommendNewArtistsSubject.value;
  }

  setShouldRecommendNewArtists(shouldRecommendNewArtists: boolean): void {
    this.shouldRecommendNewArtistsSubject.next(shouldRecommendNewArtists);

    if (typeof window !== 'undefined') {
      localStorage.setItem(
        this.diverseArtistsStorageKey,
        String(shouldRecommendNewArtists)
      );
    }
  }

  toggleShouldRecommendNewArtists(): void {
    this.setShouldRecommendNewArtists(!this.shouldRecommendNewArtists);
  }
}
