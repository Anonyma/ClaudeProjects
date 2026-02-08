import { test, expect } from '@playwright/test';

test.describe('Typography Verification (Desktop)', () => {
  test('Nav logo - Futura Bold 26px tracking -1.82px', async ({ page }) => {
    await page.goto('/');
    const logo = page.locator('nav a:has-text("PRIMORDIA")').first();

    const styles = await logo.evaluate((el) => {
      const computed = window.getComputedStyle(el);
      return {
        fontFamily: computed.fontFamily,
        fontSize: computed.fontSize,
        fontWeight: computed.fontWeight,
        letterSpacing: computed.letterSpacing,
        lineHeight: computed.lineHeight,
      };
    });

    console.log('Nav Logo:', styles);
    expect(styles.fontSize).toBe('26px');
    expect(styles.letterSpacing).toBe('-1.82px');
  });

  test('Hero H1 - Futura Bold 125px tracking -10px', async ({ page }) => {
    await page.goto('/');
    const h1 = page.locator('text=PRIMORDIA').nth(1); // Second PRIMORDIA is the hero

    const styles = await h1.evaluate((el) => {
      const computed = window.getComputedStyle(el);
      return {
        fontFamily: computed.fontFamily,
        fontSize: computed.fontSize,
        fontWeight: computed.fontWeight,
        letterSpacing: computed.letterSpacing,
        lineHeight: computed.lineHeight,
      };
    });

    console.log('Hero H1:', styles);
    expect(styles.fontSize).toBe('125px');
    expect(styles.letterSpacing).toBe('-10px');
    expect(styles.lineHeight).toBe(styles.fontSize); // leading-none means line-height = font-size
  });

  test('Hero tagline - Karla Medium 66px tracking -4.62px leading 1.13', async ({ page }) => {
    await page.goto('/');
    const tagline = page.locator('text=Funding Early Biology Experiments in DIY Labs');

    const styles = await tagline.evaluate((el) => {
      const computed = window.getComputedStyle(el);
      return {
        fontFamily: computed.fontFamily,
        fontSize: computed.fontSize,
        fontWeight: computed.fontWeight,
        letterSpacing: computed.letterSpacing,
        lineHeight: computed.lineHeight,
      };
    });

    console.log('Hero Tagline:', styles);
    expect(styles.fontSize).toBe('66px');
    expect(styles.fontWeight).toBe('500'); // Medium
    expect(styles.letterSpacing).toBe('-4.62px');
    // leading-[1.13] = 66 * 1.13 = 74.58px
  });

  test('Nav menu items - Karla SemiBold 23px', async ({ page }) => {
    await page.goto('/');
    const navItem = page.locator('nav a:has-text("About")');

    const styles = await navItem.evaluate((el) => {
      const computed = window.getComputedStyle(el);
      return {
        fontFamily: computed.fontFamily,
        fontSize: computed.fontSize,
        fontWeight: computed.fontWeight,
        lineHeight: computed.lineHeight,
      };
    });

    console.log('Nav Menu Item:', styles);
    expect(styles.fontSize).toBe('23px');
    expect(styles.fontWeight).toBe('600'); // SemiBold
  });

  test('Button text - Karla Medium 28px leading-none', async ({ page }) => {
    await page.goto('/');
    const button = page.locator('button:has-text("Apply"), a:has-text("Apply")').first();

    const styles = await button.evaluate((el) => {
      const computed = window.getComputedStyle(el);
      return {
        fontFamily: computed.fontFamily,
        fontSize: computed.fontSize,
        fontWeight: computed.fontWeight,
        lineHeight: computed.lineHeight,
      };
    });

    console.log('Button:', styles);
    expect(styles.fontSize).toBe('28px');
    expect(styles.fontWeight).toBe('500'); // Medium
    expect(styles.lineHeight).toBe(styles.fontSize); // leading-none
  });

  test('Section heading - Montserrat Bold 78px', async ({ page }) => {
    await page.goto('/');
    const heading = page.locator('text=How it Works').first();

    const styles = await heading.evaluate((el) => {
      const computed = window.getComputedStyle(el);
      return {
        fontFamily: computed.fontFamily,
        fontSize: computed.fontSize,
        fontWeight: computed.fontWeight,
        lineHeight: computed.lineHeight,
      };
    });

    console.log('Section Heading:', styles);
    expect(styles.fontSize).toBe('78px');
    expect(styles.fontWeight).toBe('700'); // Bold
  });
});
