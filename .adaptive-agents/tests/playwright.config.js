// @ts-check
const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  testDir: '.',
  timeout: 15000,
  retries: 0,
  use: {
    baseURL: 'http://localhost:8099',
    headless: true,
  },
  // Only chromium for MVP — no need for cross-browser
  projects: [
    { name: 'chromium', use: { browserName: 'chromium' } },
  ],
});
