import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { of } from 'rxjs';
import { Genre } from '../../core/domain/genre';
import { MusicService } from '../../core/services/music.service';
import { HomeComponent } from './home.component';

describe('HomeComponent', () => {
  let component: HomeComponent;
  let fixture: ComponentFixture<HomeComponent>;
  let musicServiceSpy: jasmine.SpyObj<MusicService>;

  const genres: Genre[] = [
    { id: '1', name: 'Rock' },
    { id: '2', name: 'Other' },
    { id: '3', name: 'Jazz' },
  ];

  beforeEach(async () => {
    musicServiceSpy = jasmine.createSpyObj<MusicService>('MusicService', ['getGenres']);
    musicServiceSpy.getGenres.and.returnValue(of(genres));

    await TestBed.configureTestingModule({
      imports: [HomeComponent],
      providers: [
        provideRouter([]),
        { provide: MusicService, useValue: musicServiceSpy },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(HomeComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('loads, filters, and sorts the available genres for the home route', () => {
    expect(component).toBeTruthy();
    expect(musicServiceSpy.getGenres).toHaveBeenCalledTimes(1);
    expect(component.genres).toEqual([
      { id: 'any-genre', name: 'Any genre', routeSegment: 'any-genre' },
      { id: '3', name: 'Jazz', routeSegment: 'Jazz' },
      { id: '1', name: 'Rock', routeSegment: 'Rock' },
    ]);

    const renderedLabels = Array.from(
      fixture.nativeElement.querySelectorAll('.genre-card-label'),
      (element: Element) => element.textContent?.trim()
    );

    expect(renderedLabels).toEqual(['Any genre', 'Jazz', 'Rock']);
    expect(renderedLabels).not.toContain('Other');
  });

  it('builds navigation links for each genre tile', () => {
    const links = Array.from(
      fixture.nativeElement.querySelectorAll('a.genre-card'),
      (element: Element) => element.getAttribute('href')
    );

    expect(links).toEqual(['/any-genre', '/Jazz', '/Rock']);
  });
});
