import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ActivatedRoute, convertToParamMap, ParamMap, provideRouter } from '@angular/router';
import { BehaviorSubject, of } from 'rxjs';
import { RecommendedSong } from '../../core/domain/recommendation';
import { AppPreferencesService } from '../../core/services/app-preferences.service';
import { MusicService } from '../../core/services/music.service';
import { GenreComponent } from './genre.component';

class MockAppPreferencesService {
  private readonly shouldRecommendNewArtistsSubject = new BehaviorSubject<boolean>(true);

  readonly shouldRecommendNewArtists$ = this.shouldRecommendNewArtistsSubject.asObservable();

  get shouldRecommendNewArtists(): boolean {
    return this.shouldRecommendNewArtistsSubject.value;
  }

  setShouldRecommendNewArtists(value: boolean): void {
    this.shouldRecommendNewArtistsSubject.next(value);
  }
}

describe('GenreComponent', () => {
  let fixture: ComponentFixture<GenreComponent>;
  let component: GenreComponent;
  let musicServiceSpy: jasmine.SpyObj<MusicService>;
  let appPreferencesService: MockAppPreferencesService;
  let routeParamMap$: BehaviorSubject<ParamMap>;

  const recommendedSongs: RecommendedSong[] = [
    {
      songId: 'song-1',
      name: 'Midnight City',
      youtubeId: 'dX3k_QDnzHE',
      duration: '4:03',
      artists: ['M83'],
      genres: ['Synthpop', 'Indie Pop'],
    },
    {
      songId: 'song-2',
      name: 'Genesis',
      youtubeId: 'DOFZxV3KFbY',
      duration: '4:17',
      artists: ['Grimes'],
      genres: ['Electronic'],
    },
  ];

  beforeEach(async () => {
    routeParamMap$ = new BehaviorSubject(convertToParamMap({ genre: 'Rock' }));
    musicServiceSpy = jasmine.createSpyObj<MusicService>('MusicService', ['getRecommendations']);
    musicServiceSpy.getRecommendations.and.returnValue(of({ recommendedSongs }));
    appPreferencesService = new MockAppPreferencesService();

    await TestBed.configureTestingModule({
      imports: [GenreComponent],
      providers: [
        provideRouter([]),
        { provide: MusicService, useValue: musicServiceSpy },
        { provide: AppPreferencesService, useValue: appPreferencesService },
        {
          provide: ActivatedRoute,
          useValue: {
            paramMap: routeParamMap$.asObservable(),
          },
        },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(GenreComponent);
    component = fixture.componentInstance;
  });

  it('loads recommendations for the requested genre route', () => {
    fixture.detectChanges();

    expect(musicServiceSpy.getRecommendations).toHaveBeenCalledWith({
      genre: 'Rock',
      shouldRecommendNewArtists: true,
    });
    expect(component.genreDisplayName).toBe('Rock');
    expect(component.featuredSong).toEqual(recommendedSongs[0]);
    expect(component.songs).toEqual(recommendedSongs);

    const heading = fixture.nativeElement.querySelector('h1');
    expect(heading?.textContent).toContain('Rock');
    expect(fixture.nativeElement.textContent).toContain('Midnight City');
  });

  it('treats the any-genre route as a request without a genre filter', () => {
    routeParamMap$.next(convertToParamMap({ genre: 'any-genre' }));

    fixture.detectChanges();

    expect(musicServiceSpy.getRecommendations).toHaveBeenCalledWith({
      shouldRecommendNewArtists: true,
    });
    expect(component.genreDisplayName).toBe('Any genre');
    expect(component.genreDescription).toBe('Recommendations across all genres.');
    expect(fixture.nativeElement.textContent).toContain('Recommendations across all genres.');
  });
});
