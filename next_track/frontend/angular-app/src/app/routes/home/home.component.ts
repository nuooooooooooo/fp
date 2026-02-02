import { Component, inject, OnInit } from '@angular/core';
import { RouterLink } from '@angular/router';
import { FormControl, FormGroup, FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MusicService } from '../../core/services/music.service';


@Component({
  selector: 'app-home',
  imports: [
  ],
  templateUrl: './home.component.html',
  styleUrl: './home.component.scss'
})
export class HomeComponent implements OnInit {
  private readonly musicService: MusicService = inject(MusicService);

  ngOnInit() {
  this.musicService.getHelloWorld().subscribe(data => {
    console.log(data);
  });
}

}
