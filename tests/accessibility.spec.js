import AxeBuilder from '@axe-core/playwright';
import { expect, test } from '@playwright/test';

const routes = [
  '',
  'projects/context-video-translator/',
  'projects/remotekey/',
  'resume/',
  'privacy/',
  '404.html',
];

for (const theme of ['dark', 'light']) {
  for (const route of routes) {
    test(`${route || 'home'} has no serious accessibility violations in ${theme} mode`, async ({ page }) => {
      await page.addInitScript((selectedTheme) => {
        localStorage.setItem('portfolio-theme', selectedTheme);
      }, theme);
      await page.goto(route, { waitUntil: 'networkidle' });
      const results = await new AxeBuilder({ page })
        .withTags(['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa'])
        .analyze();
      const blocking = results.violations.filter((item) => ['critical', 'serious'].includes(item.impact));
      expect(blocking, JSON.stringify(blocking, null, 2)).toEqual([]);
    });
  }
}

test('mobile menu exposes expanded state and returns focus on Escape', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto('');
  const menu = page.locator('[data-menu-toggle]');
  await menu.focus();
  await page.keyboard.press('Enter');
  await expect(menu).toHaveAttribute('aria-expanded', 'true');
  await page.keyboard.press('Escape');
  await expect(menu).toHaveAttribute('aria-expanded', 'false');
  await expect(menu).toBeFocused();
});

test('pages reflow without horizontal scrolling at narrow width', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  for (const route of routes) {
    await page.goto(route);
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
    expect(overflow, `Horizontal overflow on ${route}`).toBeLessThanOrEqual(1);
  }
});
