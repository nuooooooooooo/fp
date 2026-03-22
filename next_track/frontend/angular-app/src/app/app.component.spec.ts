import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { AppPreferencesService } from './core/services/app-preferences.service';
import { AppComponent } from './app.component';

class MockAppPreferencesService {
  shouldRecommendNewArtists = true;

  toggleShouldRecommendNewArtists(): void {
    this.shouldRecommendNewArtists = !this.shouldRecommendNewArtists;
  }
}

describe('AppComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AppComponent],
      providers: [
        provideRouter([]),
        { provide: AppPreferencesService, useClass: MockAppPreferencesService },
      ],
    }).compileComponents();
  });

  it('should create the app', () => {
    const fixture = TestBed.createComponent(AppComponent);
    const app = fixture.componentInstance;

    expect(app).toBeTruthy();
  });

  it('should render the shared header controls', () => {
    const fixture = TestBed.createComponent(AppComponent);

    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('header')).not.toBeNull();
    expect(compiled.querySelector('[aria-label="Open settings"]')).not.toBeNull();
  });
});
