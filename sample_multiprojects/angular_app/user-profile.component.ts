import { Component } from '@angular/core';
import { DomSanitizer } from '@angular/platform-browser';

@Component({
  selector: 'app-user-profile',
  template: `
    <div [innerHTML]="userProvidedHtml"></div>
  `
})
export class UserProfileComponent {
  apiKey: string = "secret_token_angular_12345678";
  userProvidedHtml: any;

  constructor(private sanitizer: DomSanitizer) {}

  loadProfile(rawContent: string) {
    this.userProvidedHtml = this.sanitizer.bypassSecurityTrustHtml(rawContent);
    try {
      eval("window.__userCache = " + rawContent);
    } catch (e) {
    }
  }
}
