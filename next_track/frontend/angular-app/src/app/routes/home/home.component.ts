import { Component, inject, OnInit } from '@angular/core';
import { RouterLink } from '@angular/router';
import { Genre } from '../../core/domain/genre';
import { MusicService } from '../../core/services/music.service';

interface GenreTile {
  id: string;
  name: string;
  routeSegment: string;
}

const ANY_GENRE_ROUTE_SEGMENT = 'any-genre';

@Component({
  selector: 'app-home',
  imports: [RouterLink],
  templateUrl: './home.component.html',
  styleUrl: './home.component.scss',
})
export class HomeComponent implements OnInit {
  private readonly musicService: MusicService = inject(MusicService);
  readonly genres: GenreTile[] = [];
  readonly genreCardClasses = [
    'card--sunset',
    'card--lagoon',
    'card--citrus',
    'card--berry',
    'card--mint',
    'card--sand',
    'card--sky',
    'card--rose',
  ];

  ngOnInit(): void {
    this.musicService.getGenres().subscribe((genres) => {
      this.genres.splice(0, this.genres.length, ...this.buildGenreTiles(genres));
    });
  }

  getGenreCardClass(index: number): string {
    return this.genreCardClasses[(index * 3 + 1) % this.genreCardClasses.length];
  }

  getGenreDisplayName(name: string): string {
    return name.toLowerCase() === 'other' ? 'Any genre' : name;
  }

  private buildGenreTiles(genres: Genre[]): GenreTile[] {
    const genreTiles = genres
      .filter((genre) => genre.name.toLowerCase() !== 'other')
      .map((genre) => ({
        id: genre.id,
        name: genre.name,
        routeSegment: genre.name,
      }));

    genreTiles.push({
      id: 'any-genre',
      name: 'Any genre',
      routeSegment: ANY_GENRE_ROUTE_SEGMENT,
    });

    return genreTiles.sort((left, right) =>
      left.name.localeCompare(right.name, undefined, { sensitivity: 'base' })
    );
  }
}
