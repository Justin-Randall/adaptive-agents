// @ts-check
const { test, expect } = require('@playwright/test');
const fs = require('fs/promises');
const path = require('path');

test.describe('Markdown Browser', () => {
  test('loads Project Layer INDEX.md on start', async ({ page }) => {
    // Capture console messages for debugging
    const logs = [];
    page.on('console', msg => logs.push(msg.type() + ': ' + msg.text()));
    page.on('pageerror', err => logs.push('PAGE ERROR: ' + err.message));

    await page.goto('/');
    const content = page.locator('#content');
    await expect(content).toBeVisible({ timeout: 10000 });

    // Log any captured errors
    if (logs.length > 0) {
      console.log('Console messages:', logs.join('\n'));
    }

    // Check if the ready function eventually populated it
    await expect(async () => {
      const text = await content.textContent();
      expect(text.length).toBeGreaterThan(0);
    }).toPass({ timeout: 10000 });
  });

  test('navigating via ?path= query param loads the file', async ({ page }) => {
    await page.goto('/view?path=README.md');
    const content = page.locator('#content');
    await expect(content).toBeVisible({ timeout: 5000 });
    await expect(content).toContainText(/Adaptive Agents/);
  });

  test('browser back button restores previous file', async ({ page }) => {
    await page.goto('/view?path=README.md');
    await expect(page.locator('#content')).toBeVisible({ timeout: 5000 });
    await page.goto('/view?path=AGENTS.md');
    await expect(page.locator('#content')).toBeVisible({ timeout: 5000 });
    await page.goBack();
    await expect(page).toHaveURL(/\/view\?path=README\.md/);
  });

  test('markdown link navigation works', async ({ page }) => {
    await page.goto('/view?path=AGENTS.md');
    const content = page.locator('#content');
    await expect(content).toBeVisible({ timeout: 5000 });
    // Find a relative .md link and click it
    const mdLink = content.locator('a[href$=".md"]').first();
    if (await mdLink.count() > 0) {
      await mdLink.click();
      await expect(page).toHaveURL(/\/view\?path=/);
    }
  });

  test('external link opens in new tab', async ({ page, context }) => {
    await page.goto('/view?path=AGENTS.md');
    const extLink = page.locator('a[href^="http"]').first();
    if (await extLink.count() > 0) {
      const [newPage] = await Promise.all([
        context.waitForEvent('page'),
        extLink.click(),
      ]);
      expect(newPage).toBeTruthy();
      await newPage.close();
    }
  });

  test('/api/tree returns valid JSON', async ({ page }) => {
    const response = await page.goto('/api/tree');
    expect(response.ok()).toBeTruthy();
    const body = await response.json();
    expect(body).toHaveProperty('type', 'directory');
    expect(body).toHaveProperty('children');
    expect(Array.isArray(body.children)).toBeTruthy();
  });

  test('/api/file returns markdown content', async ({ page }) => {
    const response = await page.goto('/api/file?path=README.md');
    expect(response.ok()).toBeTruthy();
    const text = await response.text();
    expect(text.length).toBeGreaterThan(100);
    expect(text).toContain('#');
  });

  test('/events returns SSE stream', async () => {
    const http = require('http');
    const headers = await new Promise((resolve, reject) => {
      const req = http.get('http://127.0.0.1:8099/events', (res) => {
        resolve(res.headers);
        req.destroy();
      });
      req.on('error', reject);
      req.setTimeout(5000, () => { req.destroy(); reject(new Error('timeout')); });
    });
    expect(headers['content-type']).toContain('text/event-stream');
  });

  test('updates every client displaying markdown after the file changes', async ({ page, context }, testInfo) => {
    const repoRoot = path.resolve(__dirname, '../..');
    const fixturePath = testInfo.outputPath('live-update.md');
    const fixtureUrlPath = path.relative(repoRoot, fixturePath).replaceAll('\\', '/');
    const secondPage = await context.newPage();
    await fs.mkdir(path.dirname(fixturePath), { recursive: true });
    await fs.writeFile(fixturePath, '# Before update\n', 'utf8');

    await page.goto('/view?path=' + encodeURIComponent(fixtureUrlPath));
    await secondPage.goto('/view?path=' + encodeURIComponent(fixtureUrlPath));
    await expect(page.locator('#content')).toContainText('Before update');
    await expect(secondPage.locator('#content')).toContainText('Before update');

    await fs.writeFile(fixturePath, '# After update\n', 'utf8');

    await expect(page.locator('#content')).toContainText('After update', { timeout: 5000 });
    await expect(secondPage.locator('#content')).toContainText('After update', { timeout: 5000 });
  });
});
