import {  Component } from '@angular/core';
import { Router, RouterOutlet } from '@angular/router';
import { IStaticMethods } from 'preline/preline';
import { BehaviorSubject, filter } from 'rxjs';
declare global {
  interface Window {
    HSStaticMethods: IStaticMethods;
  }
}

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet],
  templateUrl: './app.component.html',
  providers: []
})
export class AppComponent {

  title = 'NextTrack';

  showNavigation$: BehaviorSubject<boolean> = new BehaviorSubject<boolean>(true);

  constructor(private router: Router) {
  }

  ngOnInit() {
   
  }




}
