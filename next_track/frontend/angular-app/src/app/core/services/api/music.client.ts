import { inject, Injectable } from "@angular/core";
import { environment } from "../../../../environments/environment.production";
import { HttpClient, HttpHeaders } from "@angular/common/http";
import { Observable } from "rxjs";

@Injectable({ providedIn: 'root' })
export class MusicClient {
    #apiUrl = `${environment.apiUrl}`;
    #http = inject(HttpClient);
    #httpOptions = {
        headers: new HttpHeaders({ 'Content-Type': 'application/json' })
    }

       getHelloWorld(): Observable<{ message: string }[]> {
        return this.#http.get<{ message: string }[]>(`${this.#apiUrl}/hello`);
    }

}