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
  recommendationHistory: RecommendedSong[][] = [];
  requestedSongIds: string[] = [];
  isLoading = true;
  isFetchingNextBatch = false;
  hasMoreRecommendations = true;
  errorMessage = '';
  inlineErrorMessage = '';
  featuredSong: RecommendedSong | null = null;
  featuredVideoUrl: SafeResourceUrl | null = null;
  selectedSongIndex = 0;
  historyBatchIndex = 0;
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

  get canShowPreviousSong(): boolean {
    return this.selectedSongIndex > 0 || this.historyBatchIndex > 0;
  }

  get canShowNextSong(): boolean {
    return (
      this.selectedSongIndex < this.songs.length - 1
      || this.historyBatchIndex < this.recommendationHistory.length - 1
      || this.hasMoreRecommendations
    );
  }

  refreshRecommendations(): void {
    this.loadRecommendations(
      this.genreName,
      this.appPreferencesService.shouldRecommendNewArtists
    );
  }

  private loadRecommendations(genreName: string, shouldRecommendNewArtists: boolean): void {
    this.isLoading = true;
    this.isFetchingNextBatch = false;
    this.hasMoreRecommendations = true;
    this.errorMessage = '';
    this.inlineErrorMessage = '';
    this.songs = [];
    this.recommendationHistory = [];
    this.requestedSongIds = [];
    this.historyBatchIndex = 0;
    this.selectedSongIndex = 0;
    this.featuredSong = null;
    this.featuredVideoUrl = null;
    this.isPlaying = false;

    this.musicService.getRecommendations(
      this.buildRecommendationRequest(genreName, shouldRecommendNewArtists)
    ).subscribe({
      next: (recommendation) => {
        this.inlineErrorMessage = '';
        this.setRecommendationHistory(recommendation.recommendedSongs);
        this.isLoading = false;
      },
      error: () => {
        this.errorMessage = 'Could not load recommendations for this genre.';
        this.isLoading = false;
      },
    });
  }

  showPreviousSong(): void {
    if (!this.canShowPreviousSong) {
      return;
    }

    const shouldKeepPlaying = this.isPlaying;

    if (this.selectedSongIndex > 0) {
      this.selectedSongIndex -= 1;
      this.updateFeaturedSong(shouldKeepPlaying);
      return;
    }

    const previousBatchIndex = this.historyBatchIndex - 1;
    const previousBatch = this.recommendationHistory[previousBatchIndex];

    if (!previousBatch?.length) {
      return;
    }

    this.setActiveBatch(previousBatchIndex, previousBatch.length - 1, shouldKeepPlaying);
  }

  showNextSong(): void {
    if (this.isFetchingNextBatch || !this.canShowNextSong) {
      return;
    }

    const shouldKeepPlaying = this.isPlaying;

    if (this.selectedSongIndex < this.songs.length - 1) {
      this.selectedSongIndex += 1;
      this.updateFeaturedSong(shouldKeepPlaying);
      return;
    }

    if (this.historyBatchIndex < this.recommendationHistory.length - 1) {
      this.setActiveBatch(this.historyBatchIndex + 1, 0, shouldKeepPlaying);
      return;
    }

    this.fetchNextRecommendationBatch(shouldKeepPlaying);
  }

  selectSong(index: number): void {
    if (index < 0 || index >= this.songs.length || index === this.selectedSongIndex) {
      return;
    }

    const shouldKeepPlaying = this.isPlaying;
    this.selectedSongIndex = index;
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

  private fetchNextRecommendationBatch(autoplay: boolean): void {
    if (!this.requestedSongIds.length) {
      return;
    }

    this.isFetchingNextBatch = true;
    this.inlineErrorMessage = '';

    this.musicService.getRecommendations(
      this.buildRecommendationRequest(
        this.genreName,
        this.appPreferencesService.shouldRecommendNewArtists,
        this.requestedSongIds
      )
    ).subscribe({
      next: (recommendation) => {
        this.isFetchingNextBatch = false;

        if (!recommendation.recommendedSongs.length) {
          this.hasMoreRecommendations = false;
          this.inlineErrorMessage = 'No more recommendations available right now.';
          return;
        }

        this.hasMoreRecommendations = true;
        this.inlineErrorMessage = '';
        this.appendRecommendationBatch(recommendation.recommendedSongs, autoplay);
      },
      error: () => {
        this.isFetchingNextBatch = false;
        this.inlineErrorMessage = 'Could not load more recommendations.';
      },
    });
  }

  private buildRecommendationRequest(
    genreName: string,
    shouldRecommendNewArtists: boolean,
    songIds?: string[]
  ): RecommendationRequest {
    const request: RecommendationRequest = this.isAnyGenreRoute(genreName)
      ? { shouldRecommendNewArtists }
      : { genre: genreName, shouldRecommendNewArtists };

    if (songIds?.length) {
      request.songIds = songIds;
    }

    return request;
  }

  private setRecommendationHistory(recommendedSongs: RecommendedSong[]): void {
    this.recommendationHistory = [];
    this.requestedSongIds = [];
    this.appendRecommendationBatch(recommendedSongs, false);
  }

  private appendRecommendationBatch(
    recommendedSongs: RecommendedSong[],
    autoplay: boolean
  ): void {
    this.recommendationHistory.push(recommendedSongs);
    this.requestedSongIds.push(...recommendedSongs.map((song) => song.songId));
    this.setActiveBatch(this.recommendationHistory.length - 1, 0, autoplay);
  }

  private setActiveBatch(
    batchIndex: number,
    songIndex: number,
    autoplay: boolean
  ): void {
    const batch = this.recommendationHistory[batchIndex] ?? [];

    this.historyBatchIndex = batchIndex;
    this.songs = batch;
    this.selectedSongIndex = Math.min(songIndex, Math.max(batch.length - 1, 0));
    this.updateFeaturedSong(autoplay);
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
