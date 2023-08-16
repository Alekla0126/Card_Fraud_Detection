import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  private baseURL = 'http://localhost:5000';  // Your Flask API URL

  constructor(private http: HttpClient) { }

  register(userData: any): Observable<any> {
    return this.http.post(`${this.baseURL}/signup`, userData);
  }

  login(userData: any): Observable<any> {
    return this.http.post(`${this.baseURL}/login`, userData);
  }
}
