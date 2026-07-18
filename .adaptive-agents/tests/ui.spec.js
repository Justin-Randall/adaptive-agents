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
    expect(body.name).toBe('adaptive-agents');
    expect(body).toHaveProperty('children');
    expect(Array.isArray(body.children)).toBeTruthy();
    expect(body.children.map(child => child.name)).toContain('README.md');
  });

  test('/api/context exposes target and system roots', async ({ page }) => {
    const response = await page.goto('/api/context');
    expect(response.ok()).toBeTruthy();
    const body = await response.json();
    expect(body.targetName).toBe('Adaptive Agents');
    expect(body.targetRoot).toContain('adaptive-agents');
    expect(body.projectLayerRoot).toContain('.adaptive-agents');
    expect(body.projectLayerExists).toBeTruthy();
    expect(body.systemName).toBe('Adaptive Agents');
    expect(body.systemHome).toContain('adaptive-agents');
  });

  test('/api/index-tree returns Project Layer index navigation', async ({ page }) => {
    const response = await page.goto('/api/index-tree');
    expect(response.ok()).toBeTruthy();
    const body = await response.json();
    expect(body).toMatchObject({
      name: '.adaptive-agents',
      path: '.adaptive-agents/INDEX.md',
    });
    expect(body.children.map(child => child.name)).toEqual(expect.arrayContaining([
      'instructions',
      'memory',
      'planning',
      'playbooks',
      'retrospectives',
      'skills',
    ]));
    const planning = body.children.find(child => child.name === 'planning');
    expect(planning.children.map(child => child.name)).toEqual(expect.arrayContaining(['backlog', 'closed']));
    // links array is populated and does not overlap with children
    expect(Array.isArray(body.links)).toBeTruthy();
    expect(body.links.length).toBeGreaterThan(0);
    const linkPaths = new Set(body.links.map(l => l.path));
    const childPaths = new Set(body.children.map(c => c.path));
    for (const p of linkPaths) {
      expect(childPaths.has(p)).toBeFalsy();
    }
    // acyclic: a link should not appear more than once
    expect(linkPaths.size).toEqual(body.links.length);
  });

  test('/api/system-index-tree returns system-wide Adaptive Agents navigation', async ({ page }) => {
    const response = await page.goto('/api/system-index-tree');
    expect(response.ok()).toBeTruthy();
    const body = await response.json();
    expect(body).toMatchObject({
      name: 'Adaptive Agents',
      type: 'index',
      path: 'system:INDEX.md',
    });
    expect(Array.isArray(body.children)).toBeTruthy();
    expect(Array.isArray(body.links)).toBeTruthy();
    expect(body.links).toEqual([]);
    expect(body.children.map(child => child.name)).toEqual(expect.arrayContaining([
      'instructions',
      'skills',
      'prompts',
      'playbooks',
      'retrospectives',
      'templates',
      'scripts',
    ]));
    expect(body.children.map(child => child.name)).not.toContain('.adaptive-agents');
    for (const child of body.children) {
      if (child.path) {
        expect(child.path.startsWith('system:')).toBeTruthy();
      }
    }

    const instructions = body.children.find(child => child.name === 'instructions');
    expect(instructions.path).toBe('system:instructions/INDEX.md');
    expect(instructions.children.map(child => child.name)).toEqual(expect.arrayContaining(['global', 'coding', 'tdd']));
    expect(instructions.children.find(child => child.name === 'global').path).toBe('system:instructions/global.instructions.md');

    const skills = body.children.find(child => child.name === 'skills');
    expect(skills.path).toBe('system:skills/INDEX.md');
    expect(skills.children.map(child => child.name)).toEqual(expect.arrayContaining(['bootstrap-project-layer', 'update-adaptive-agents', 'upgrade-project-layer']));

    const prompts = body.children.find(child => child.name === 'prompts');
    expect(prompts.path).toBe('system:prompts/INDEX.md');
    expect(prompts.children.map(child => child.name)).toContain('capture-retrospective');

    const agents = body.children.find(child => child.name === 'agents');
    expect(agents.path).toBe('system:agents/INDEX.md');

    const memory = body.children.find(child => child.name === 'memory');
    expect(memory.path).toBe('system:memory/INDEX.md');
  });

  test('/api/file serves system-wide Adaptive Agents files by namespace', async ({ page }) => {
    const response = await page.goto('/api/file?path=system%3AINDEX.md');
    expect(response.ok()).toBeTruthy();
    const text = await response.text();
    expect(text).toContain('Adaptive Agents');
  });

  test('sidebar shows Project Repo, Project Layer, and System sections', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('#target-root')).toContainText('Adaptive Agents');
    await expect(page.locator('#system-root')).toContainText('Adaptive Agents');
    await expect(page.locator('#sidebar h2').first()).toHaveText('Project Repo');
    await expect(page.locator('#sidebar h2').nth(1)).toHaveText('Project Layer');
    await expect(page.locator('#sidebar h2').nth(2)).toHaveText('System');
    await expect(page.locator('#root-tree')).toContainText('adaptive-agents');
    await expect(page.locator('#root-tree a[data-path="README.md"]')).toHaveText('README.md');
    await expect(page.locator('#system-tree')).toBeVisible();
    await expect(page.locator('#system-tree a[data-path="system:INDEX.md"]')).toHaveText('Adaptive Agents');
    await expect(page.locator('#system-tree', { hasText: 'instructions' })).toBeVisible();
    await expect(page.locator('#system-tree', { hasText: 'prompts' })).toBeVisible();
    await expect(page.locator('#system-tree', { hasText: 'skills' })).toBeVisible();
    await expect(page.locator('#system-tree a[data-path="system:agents/INDEX.md"]')).toHaveText('agents');
    await expect(page.locator('#system-tree a[data-path="system:memory/INDEX.md"]')).toHaveText('memory');
    await expect(page.locator('#system-tree a', { hasText: 'Executable Scripts as Dynamic Instruction Sources' })).toHaveCount(0);
  });

  test('/api/file returns markdown content', async ({ page }) => {
    const response = await page.goto('/api/file?path=README.md');
    expect(response.ok()).toBeTruthy();
    const text = await response.text();
    expect(text.length).toBeGreaterThan(100);
    expect(text).toContain('#');
  });

  test('sidebar navigates Project Layer index pages', async ({ page }) => {
    await page.goto('/');
    const sidebar = page.locator('#sidebar');
    const planningLink = sidebar.locator('a[data-path=".adaptive-agents/planning/INDEX.md"]');
    await expect(planningLink).toBeVisible();
    await planningLink.click();
    await expect(page).toHaveURL(/path=\.adaptive-agents%2Fplanning%2FINDEX\.md/);
    await expect(page.locator('#content')).toContainText('Planning');
    await expect(planningLink).toHaveClass(/active/);
  });

  test('sidebar link entries navigate to referenced files', async ({ page }) => {
    await page.goto('/');
    const sidebar = page.locator('#sidebar');
    // The root .adaptive-agents INDEX.md links to scripts/README.md
    const linkEntry = sidebar.locator('a[data-path$="scripts/README.md"]');
    await expect(linkEntry.first()).toBeVisible({ timeout: 5000 });
    await linkEntry.first().click();
    await expect(page).toHaveURL(/path=.adaptive-agents%2Fscripts%2FREADME\.md/);
    await expect(page.locator('#content')).toContainText('Project Layer');
  });

  test('sidebar defaults to only top-level nodes expanded', async ({ page }) => {
    await page.goto('/');
    const sidebar = page.locator('#sidebar');
    const rootToggle = sidebar.locator('button[data-path=".adaptive-agents/INDEX.md"]');
    const planningToggle = sidebar.locator('button[data-path=".adaptive-agents/planning/INDEX.md"]');
    const backlogLink = sidebar.locator('a[data-path=".adaptive-agents/planning/backlog/INDEX.md"]');

    // Root node (depth 0) is expanded
    await expect(rootToggle).toHaveAttribute('aria-expanded', 'true');
    // Non-root nodes start collapsed
    await expect(planningToggle).toHaveAttribute('aria-expanded', 'false');
    await expect(backlogLink).toBeHidden();
  });

  test('sidebar tree branches collapse and expand', async ({ page }) => {
    await page.goto('/');
    const sidebar = page.locator('#sidebar');
    const planningToggle = sidebar.locator('button[data-path=".adaptive-agents/planning/INDEX.md"]');
    const backlogLink = sidebar.locator('a[data-path=".adaptive-agents/planning/backlog/INDEX.md"]');
    const closedLink = sidebar.locator('a[data-path=".adaptive-agents/planning/closed/INDEX.md"]');

    // Planning starts collapsed (non-root). Expand it.
    await expect(planningToggle).toHaveAttribute('aria-expanded', 'false');
    await planningToggle.click();
    await expect(planningToggle).toHaveAttribute('aria-expanded', 'true');
    await expect(backlogLink).toBeVisible();
    await expect(closedLink).toBeVisible();

    // Collapse it
    await planningToggle.click();
    await expect(planningToggle).toHaveAttribute('aria-expanded', 'false');
    await expect(backlogLink).toBeHidden();
    await expect(closedLink).toBeHidden();

    // Expand again
    await planningToggle.click();
    await expect(planningToggle).toHaveAttribute('aria-expanded', 'true');
    await expect(backlogLink).toBeVisible();
    await expect(closedLink).toBeVisible();
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
