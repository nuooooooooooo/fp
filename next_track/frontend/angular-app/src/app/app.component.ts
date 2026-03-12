import { Component, OnDestroy, OnInit } from '@angular/core';
import { NgIf } from '@angular/common';
import { Router, RouterLink, RouterOutlet } from '@angular/router';
import { IStaticMethods } from 'preline/preline';

declare global {
  interface Window {
    HSStaticMethods: IStaticMethods;
  }
}

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [NgIf, RouterOutlet, RouterLink],
  templateUrl: './app.component.html',
  providers: []
})
export class AppComponent implements OnInit, OnDestroy {
  private readonly storageKey = 'next-track-theme';
  private mediaQuery: MediaQueryList | null = null;
  private readonly handleSystemThemeChange = (event: MediaQueryListEvent): void => {
    if (localStorage.getItem(this.storageKey)) {
      return;
    }

    this.applyTheme(event.matches);
  };
  isDarkMode = false;

  constructor(private router: Router) {
  }

  ngOnInit(): void {
    if (typeof window === 'undefined') {
      return;
    }

    this.mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');

    const storedTheme = localStorage.getItem(this.storageKey);
    const useDarkMode = storedTheme ? storedTheme === 'dark' : this.mediaQuery.matches;

    this.applyTheme(useDarkMode);
    this.mediaQuery.addEventListener('change', this.handleSystemThemeChange);
  }

  ngOnDestroy(): void {
    this.mediaQuery?.removeEventListener('change', this.handleSystemThemeChange);
  }

  shouldShowHeader(): boolean {
    return this.router.url !== '/home';
  }

  toggleDarkMode(): void {
    const useDarkMode = !this.isDarkMode;

    this.applyTheme(useDarkMode);
    localStorage.setItem(this.storageKey, useDarkMode ? 'dark' : 'light');
  }

  private applyTheme(useDarkMode: boolean): void {
    this.isDarkMode = useDarkMode;
    document.documentElement.classList.toggle('dark', useDarkMode);
    document.documentElement.style.colorScheme = useDarkMode ? 'dark' : 'light';
  }
}
