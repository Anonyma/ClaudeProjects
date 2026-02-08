import { test, expect } from '@playwright/test';

test.describe('Home Page Visual Regression', () => {
  test('desktop viewport', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await expect(page).toHaveScreenshot('home-desktop.png', { fullPage: true });
  });

  test('iphone viewport', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await expect(page).toHaveScreenshot('home-iphone.png', { fullPage: true });
  });

  test('ipad viewport', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await expect(page).toHaveScreenshot('home-ipad.png', { fullPage: true });
  });
});

test.describe('Fund Page Visual Regression', () => {
  test('desktop viewport', async ({ page }) => {
    await page.goto('/fund');
    await page.waitForLoadState('networkidle');
    await expect(page).toHaveScreenshot('fund-desktop.png', { fullPage: true });
  });

  test('iphone viewport', async ({ page }) => {
    await page.goto('/fund');
    await page.waitForLoadState('networkidle');
    await expect(page).toHaveScreenshot('fund-iphone.png', { fullPage: true });
  });

  test('ipad viewport', async ({ page }) => {
    await page.goto('/fund');
    await page.waitForLoadState('networkidle');
    await expect(page).toHaveScreenshot('fund-ipad.png', { fullPage: true });
  });
});
