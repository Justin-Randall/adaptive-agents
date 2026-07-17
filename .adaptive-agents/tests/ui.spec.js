// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('Markdown Browser', () => {
  test('loads the app shell', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('#sidebar')).toBeVisible();
    await expect(page.locator('#preview')).toBeVisible();
    await expect(page.locator('h1')).toHaveText('Adaptive Agents');
  });

  test('file tree loads with entries', async ({ page }) => {
    await page.goto('/');
    // Wait for tree to populate from /api/tree
    const treeItems = page.locator('#tree li');
    await expect(treeItems.first()).toBeVisible({ timeout: 5000 });
    // Should see at least instructions, scripts, retrospectives, etc.
    const count = await treeItems.count();
    expect(count).toBeGreaterThan(5);
  });

  test('clicking a file in the sidebar renders markdown', async ({ page }) => {
    await page.goto('/');
    // Use data-path attribute for exact match to avoid ambiguity
    const readme = page.locator('#tree li.file[data-path="README.md"]');
    await readme.click();
    // Content area should now have rendered markdown
    const content = page.locator('#content');
    await expect(content).toBeVisible({ timeout: 5000 });
    // URL should update
    await expect(page).toHaveURL(/\/view\?path=README\.md/);
  });

  test('navigating via ?path= query param loads the file', async ({ page }) => {
    await page.goto('/view?path=README.md');
    const content = page.locator('#content');
    await expect(content).toBeVisible({ timeout: 5000 });
    // Sidebar should highlight the active file
    const active = page.locator('#tree li.active');
    await expect(active).toHaveText(/README/);
  });

  test('browser back button restores previous file', async ({ page }) => {
    await page.goto('/');
    // Navigate to README
    const readme = page.locator('#tree li.file[data-path="README.md"]');
    await readme.click();
    await expect(page.locator('#content')).toBeVisible({ timeout: 5000 });
    // Navigate to another file
    const agent = page.locator('#tree li.file[data-path="AGENTS.md"]');
    await agent.click();
    await expect(page.locator('#content')).toBeVisible({ timeout: 5000 });
    // Press back
    await page.goBack();
    // Should see README content again
    await expect(page.locator('#content')).toBeVisible();
    await expect(page).toHaveURL(/\/view\?path=README\.md/);
  });

  test('markdown link navigation works', async ({ page }) => {
    await page.goto('/view?path=AGENTS.md');
    const content = page.locator('#content');
    await expect(content).toBeVisible({ timeout: 5000 });
    // AGENTS.md likely links to INDEX.md — find a relative .md link and click it
    const mdLink = content.locator('a[href$=".md"]').first();
    if (await mdLink.count() > 0) {
      const href = await mdLink.getAttribute('href');
      await mdLink.click();
      // Should navigate within the app
      await expect(page).toHaveURL(/\/view\?path=/);
    }
  });

  test('external link opens in new tab', async ({ page, context }) => {
    await page.goto('/view?path=AGENTS.md');
    // Find an http/https link
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
    // Should be markdown, not HTML
    expect(text).toContain('#');
  });

  test('/events returns SSE stream', async () => {
    // Use Node's http module to check headers without reading the stream body
    const http = require('http');
    const headers = await new Promise((resolve, reject) => {
      const req = http.get('http://127.0.0.1:8099/events', (res) => {
        resolve(res.headers);
        req.destroy(); // Don't read the body — SSE never ends
      });
      req.on('error', reject);
      req.setTimeout(5000, () => { req.destroy(); reject(new Error('timeout')); });
    });
    expect(headers['content-type']).toContain('text/event-stream');
  });
});
