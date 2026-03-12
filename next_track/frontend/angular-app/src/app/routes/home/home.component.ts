import { Component, inject, OnInit } from '@angular/core';
import { RouterLink } from '@angular/router';
import { Genre } from '../../core/domain/genre';
import { MusicService } from '../../core/services/music.service';

@Component({
  selector: 'app-home',
  imports: [RouterLink],
  templateUrl: './home.component.html',
  styleUrl: './home.component.scss',
})
export class HomeComponent implements OnInit {
  private readonly musicService: MusicService = inject(MusicService);
  readonly genres: Genre[] = [];
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
      this.genres.splice(0, this.genres.length, ...genres);
    });
  }

  getGenreCardClass(index: number): string {
    return this.genreCardClasses[(index * 3 + 1) % this.genreCardClasses.length];
  }

  getGenreDisplayName(name: string): string {
    return name.toLowerCase() === 'other' ? 'Any genre' : name;
  }
}
