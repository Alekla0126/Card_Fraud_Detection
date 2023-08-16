import { Component } from '@angular/core';
import { AuthService } from '../auth.service';

@Component({
  selector: 'app-register',
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.css']
})
export class RegisterComponent {
  
  userData = {username: '', password: ''};
  
  constructor(private authService: AuthService) { }

  register() {
    this.authService.register(this.userData).subscribe(
      res => {
        console.log('Registration successful');
      },
      err => {
        console.error('Registration failed', err);
      }
    );
  }
}
