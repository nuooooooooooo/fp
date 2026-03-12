import { Routes } from '@angular/router';
import { HomeComponent } from './routes/home/home.component';
import { GenreComponent } from './routes/genre/genre.component';
import { RandomDummyComponent } from './routes/random-dummy/random-dummy.component';

export const routes: Routes = [
    { path: '', redirectTo: 'home', pathMatch: 'full'},
    { path: 'home', component: HomeComponent },
    { path: 'random', component: RandomDummyComponent },
    { path: ':genre', component: GenreComponent },
];
