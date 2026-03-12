import { Component } from '@angular/core';

@Component({
  selector: 'app-random-dummy',
  standalone: true,
  template: `
    <div class="min-h-screen bg-white dark:bg-slate-950">
      <div class="mx-auto max-w-[880px] px-6 py-16">
        <h1 class="text-[34px] font-extrabold tracking-[-0.02em] text-slate-900 dark:text-slate-100">
          Random page
        </h1>
        <p class="mt-3 text-[15px] leading-6 text-slate-500 dark:text-slate-400">
          Placeholder route for checking the shared header.
        </p>
      </div>
    </div>
  `
})
export class RandomDummyComponent {}
