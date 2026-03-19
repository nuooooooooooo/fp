import { Component, DestroyRef, ElementRef, ViewChild, inject, OnInit } from '@angular/core';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';
import { ActivatedRoute } from '@angular/router';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { combineLatest } from 'rxjs';
import { MusicService } from '../../core/services/music.service';
import { RecommendedSong, RecommendationRequest } from '../../core/domain/recommendation';
import { AppPreferencesService } from '../../core/services/app-preferences.service';
import { getYoutubeEmbedUrl } from '../../core/utils/helpers/youtube.helper';

const ANY_GENRE_ROUTE_SEGMENT = 'any-genre';

@Component({
  selector: 'app-genre',
  standalone: true,
  templateUrl: './genre.component.html',
  styleUrl: './genre.component.scss',
})
export class GenreComponent implements OnInit {
  @ViewChild('playerFrame') playerFrame?: ElementRef<HTMLIFrameElement>;

  private readonly route = inject(ActivatedRoute);
  private readonly musicService = inject(MusicService);
  private readonly destroyRef = inject(DestroyRef);
  private readonly sanitizer = inject(DomSanitizer);
  private readonly appPreferencesService = inject(AppPreferencesService);
  private readonly playerOrigins = new Set([
    'https://www.youtube-nocookie.com',
    'https://www.youtube.com',
  ]);
  private readonly handlePlayerMessage = (event: MessageEvent): void => {
    if (!this.playerOrigins.has(event.origin)) {
      return;
    }

    const payload = this.parsePlayerMessage(event.data);

    if (!payload) {
      return;
    }

    if (payload.event === 'onStateChange') {
      this.syncPlaybackState(payload.info);
    }
  };

  genreName = '';
  songs: RecommendedSong[] = [];
  isLoading = true;
  errorMessage = '';
  featuredSong: RecommendedSong | null = null;
  featuredVideoUrl: SafeResourceUrl | null = null;
  selectedSongIndex = 0;
  isPlaying = false;

  constructor() {
    window.addEventListener('message', this.handlePlayerMessage);
    this.destroyRef.onDestroy(() => {
      window.removeEventListener('message', this.handlePlayerMessage);
    });
  }

  ngOnInit(): void {
    combineLatest([
      this.route.paramMap,
      this.appPreferencesService.shouldRecommendNewArtists$,
    ])
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe(([params, shouldRecommendNewArtists]) => {
        const genreName = params.get('genre') ?? '';
        this.genreName = genreName;
        this.loadRecommendations(genreName, shouldRecommendNewArtists);
      });
  }

  get genreDisplayName(): string {
    return this.isAnyGenreRoute(this.genreName) ? 'Any genre' : this.genreName;
  }

  get genreDescription(): string {
    return this.isAnyGenreRoute(this.genreName)
      ? 'Recommendations across all genres.'
      : '';
  }

  private loadRecommendations(genreName: string, shouldRecommendNewArtists: boolean): void {
    this.isLoading = true;
    this.errorMessage = '';
    this.songs = [];
    this.selectedSongIndex = 0;
    this.featuredSong = null;
    this.featuredVideoUrl = null;
    this.isPlaying = false;

    const request: RecommendationRequest = this.isAnyGenreRoute(genreName)
      ? { shouldRecommendNewArtists }
      : { genre: genreName, shouldRecommendNewArtists };

    this.musicService.getRecommendations(request).subscribe({
      next: (recommendation) => {
        this.songs = recommendation.recommendedSongs;
        this.updateFeaturedSong();
        this.isLoading = false;
      },
      error: () => {
        this.errorMessage = 'Could not load recommendations for this genre.';
        this.isLoading = false;
      },
    });
  }

  showPreviousSong(): void {
    if (this.selectedSongIndex <= 0) {
      return;
    }

    const shouldKeepPlaying = this.isPlaying;
    this.selectedSongIndex -= 1;
    this.updateFeaturedSong(shouldKeepPlaying);
  }

  showNextSong(): void {
    if (this.selectedSongIndex >= this.songs.length - 1) {
      return;
    }

    const shouldKeepPlaying = this.isPlaying;
    this.selectedSongIndex += 1;
    this.updateFeaturedSong(shouldKeepPlaying);
  }

  togglePlayback(): void {
    if (!this.featuredVideoUrl) {
      return;
    }

    this.postPlayerCommand(this.isPlaying ? 'pauseVideo' : 'playVideo');
  }

  registerPlayerListeners(): void {
    this.postPlayerEvent('listening');
    this.postPlayerCommand('addEventListener', 'onStateChange');
  }

  private updateFeaturedSong(autoplay = false): void {
    this.featuredSong = this.songs[this.selectedSongIndex] ?? null;
    this.isPlaying = autoplay;
    this.featuredVideoUrl = this.featuredSong?.youtubeId
      ? this.sanitizer.bypassSecurityTrustResourceUrl(
          getYoutubeEmbedUrl(
            this.featuredSong.youtubeId,
            typeof window !== 'undefined' ? window.location.origin : undefined,
            autoplay
          )
        )
      : null;
  }

  private postPlayerCommand(
    command: 'playVideo' | 'pauseVideo' | 'addEventListener',
    argument?: string
  ): void {
    this.playerFrame?.nativeElement.contentWindow?.postMessage(
      JSON.stringify({
        event: 'command',
        func: command,
        args: argument ? [argument] : [],
      }),
      'https://www.youtube-nocookie.com'
    );
  }

  private postPlayerEvent(eventName: 'listening'): void {
    this.playerFrame?.nativeElement.contentWindow?.postMessage(
      JSON.stringify({
        event: eventName,
      }),
      'https://www.youtube-nocookie.com'
    );
  }

  private parsePlayerMessage(data: unknown): { event?: string; info?: number } | null {
    if (typeof data !== 'string') {
      return null;
    }

    try {
      return JSON.parse(data) as { event?: string; info?: number };
    } catch {
      return null;
    }
  }

  private syncPlaybackState(state?: number): void {
    this.isPlaying = state === 1;
  }

  private isAnyGenreRoute(genreName: string): boolean {
    return genreName.toLowerCase() === ANY_GENRE_ROUTE_SEGMENT;
  }
}
