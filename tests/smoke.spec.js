import { expect, test } from '@playwright/test';

const routes = [
  '',
  'projects/context-video-translator/',
  'projects/remotekey/',
  'resume/',
  'privacy/',
  '404.html',
];

async function loadAllImages(page) {
  const count = await page.locator('img').count();
  for (let index = 0; index < count; index += 1) {
    const image = page.locator('img').nth(index);
    await image.scrollIntoViewIfNeeded();
  }
  await page.waitForTimeout(150);
}

for (const route of routes) {
  test(`${route || 'home'} renders without broken resources`, async ({ page }) => {
    const consoleErrors = [];
    const pageErrors = [];
    page.on('console', (message) => {
      if (message.type() === 'error') consoleErrors.push(message.text());
    });
    page.on('pageerror', (error) => pageErrors.push(error.message));

    const response = await page.goto(route, { waitUntil: 'networkidle' });
    expect(response?.status(), `HTTP status for ${route}`).toBeLessThan(400);
    await expect(page.locator('h1')).toHaveCount(1);
    await expect(page.locator('main')).toHaveCount(1);
    await loadAllImages(page);

    const brokenImages = await page.locator('img').evaluateAll((images) => images
      .filter((image) => !image.complete || image.naturalWidth === 0)
      .map((image) => image.getAttribute('src')));
    expect(brokenImages).toEqual([]);
    expect(pageErrors).toEqual([]);
    expect(consoleErrors).toEqual([]);
  });
}

test('theme toggle persists and has an accessible name', async ({ page }) => {
  await page.goto('');
  const toggle = page.locator('[data-theme-toggle]');
  await expect(toggle).toBeVisible();
  const before = await page.locator('html').getAttribute('data-theme');
  await toggle.click();
  const after = await page.locator('html').getAttribute('data-theme');
  expect(after).not.toBe(before);
  await expect(toggle).toHaveAttribute('aria-label', /theme/i);
});

test('mobile navigation opens, closes with Escape, and does not overflow', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto('');
  const menu = page.locator('[data-menu-toggle]');
  await expect(menu).toBeVisible();
  await menu.click();
  await expect(menu).toHaveAttribute('aria-expanded', 'true');
  await expect(page.locator('[data-nav-links]')).toHaveClass(/open/);
  await page.keyboard.press('Escape');
  await expect(menu).toHaveAttribute('aria-expanded', 'false');
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
  expect(overflow).toBeLessThanOrEqual(1);
});

test('core content is readable without JavaScript', async ({ browser }) => {
  const context = await browser.newContext({ javaScriptEnabled: false });
  const page = await context.newPage();
  for (const route of ['', 'projects/context-video-translator/', 'projects/remotekey/', 'resume/']) {
    await page.goto(new URL(route, 'http://127.0.0.1:4173/portfolio-dtp/').toString());
    await expect(page.locator('h1')).toBeVisible();
    await expect(page.locator('main')).toBeVisible();
  }
  await context.close();
});

test('skip link moves focus to main content', async ({ page }) => {
  await page.goto('');
  await page.keyboard.press('Tab');
  const skip = page.locator('.skip-link');
  await expect(skip).toBeFocused();
  await page.keyboard.press('Enter');
  await expect(page.locator('main')).toBeFocused();
});
