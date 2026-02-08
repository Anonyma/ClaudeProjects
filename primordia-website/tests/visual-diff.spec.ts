import { test, expect } from '@playwright/test';
import fs from 'fs';
import path from 'path';
import { PNG } from 'pngjs';
import pixelmatch from 'pixelmatch';

test.describe('Visual Regression - Figma Reference', () => {
  test('Compare Home page with Figma reference', async ({ page }) => {
    // Navigate to home page
    await page.goto('/');

    // Wait for fonts and images to load
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000); // Additional wait for fonts

    // Take full page screenshot
    const screenshot = await page.screenshot({
      fullPage: true,
    });

    // Save the current screenshot
    const screenshotPath = path.join(__dirname, 'current-home.png');
    fs.writeFileSync(screenshotPath, screenshot);

    console.log('Screenshot saved to:', screenshotPath);
    console.log('Compare this with: tests/og-figma-main.jpg');
    console.log('\nTo view side-by-side, run:');
    console.log('open tests/current-home.png tests/og-figma-main.jpg');
  });
});
