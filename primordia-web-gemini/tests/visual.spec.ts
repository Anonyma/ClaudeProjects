import { test, expect } from '@playwright/test';

// Defined based on Phase 1 (Desktop)
const viewports = [
  { 
    name: 'home-desktop', 
    path: '/', 
    width: 1500, 
    height: 5374 // Use height from Figma for initial viewport, though fullPage screenshot handles scroll
  },
  { 
    name: 'fund-desktop', 
    path: '/fund-experiments', 
    width: 1500, 
    height: 2842 
  },
];

test.describe('Figma Visual Regression', () => {
  test.use({ deviceScaleFactor: 4 });

  for (const vp of viewports) {
    test(`match ${vp.name}`, async ({ page }) => {
      // 1. Set viewport to match Figma baseline width
      await page.setViewportSize({ width: vp.width, height: 800 }); // Height doesn't strictly matter for fullPage, but width does.

      // 2. Load the route
      await page.goto(vp.path);

      // 3. Wait for fonts/images (networkidle is usually sufficient for static content)
      await page.waitForLoadState('networkidle');
      
      // Additional wait to ensure custom fonts are definitely rendered if there's any FOUT
      await page.evaluate(() => document.fonts.ready);

      // 4. Compare screenshot
      console.log(`Comparing screenshot: ${vp.name}.png`);
      await expect(page).toHaveScreenshot(`${vp.name}.png`, {
        fullPage: true,
        scale: 'device',
        timeout: 30000,
        // Optional: Adjust threshold if rendering differs slightly across environments
        maxDiffPixelRatio: 0.02, 
      });
    });
  }
});
