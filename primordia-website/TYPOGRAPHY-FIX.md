# Typography Fix Summary

## Problems Found

### 1. **Font Loading Issues**
- ❌ Google Fonts imported via CSS `@import` (blocks rendering)
- ❌ Futura loaded via `@font-face` with system fallback (not reliable)
- ❌ Font variables not properly connected to Tailwind classes

### 2. **Typography Tokens Wrong**
From Figma MCP, exact values are:
- **Nav items**: Karla SemiBold, 23px, leading-none
- **Nav logo**: Futura Bold, 26px, tracking-[-1.82px]
- **Hero H1**: Futura Bold, 125px, tracking-[-10px], leading-none
- **Hero tagline**: Karla Medium, 66px, leading-[1.13], tracking-[-4.62px]
- **Section headings**: Montserrat Bold, 78px, leading-none
- **Body text**: Karla Regular, 18-32px, leading varies (1.22-1.63)
- **Button text**: Karla Medium, 18-29px, leading-none

### 3. **Missing Typography**
- No `leading-none` on buttons
- Wrong tracking values (using Tailwind presets vs exact px)

## Fixes Applied

### 1. Font Loading (app/layout.tsx)
```typescript
// ✅ Using next/font/google for optimal loading
const karla = Karla({
  weight: ['400', '500', '600'], // Regular, Medium, SemiBold
  variable: '--font-karla',
  display: 'swap',
});

const montserrat = Montserrat({
  weight: ['600', '700'], // SemiBold, Bold
  variable: '--font-montserrat',
  display: 'swap',
});

// ✅ Futura with system fallback (Impact, Arial Black)
// User must add futura-bold.woff2 to public/fonts/ for actual Futura
const futuraVariable = '--font-futura';
// Fallback: Impact, Arial Black, sans-serif
```

### 2. Tailwind Config (tailwind.config.ts)
```typescript
fontFamily: {
  futura: ["var(--font-futura)", "Impact", "Arial Black", "sans-serif"],
  montserrat: ["var(--font-montserrat)", "sans-serif"],
  karla: ["var(--font-karla)", "sans-serif"],
},
```

### 3. Global Styles (app/globals.css)
- ✅ Removed `@import` for fonts (handled by next/font)
- ✅ Removed `@font-face` for Futura (handled by next/font/local)
- ✅ Body inherits Karla from layout className

### 4. Component Updates
- ✅ Button: Added `leading-none` to baseStyles
- ✅ All components: Using exact px values from MCP

## Files Changed

1. **app/layout.tsx** - Font loading with next/font
2. **app/globals.css** - Removed CSS font imports
3. **tailwind.config.ts** - Font family variables
4. **components/Button.tsx** - Added leading-none
5. **package.json** - Added Playwright for visual tests
6. **playwright.config.ts** - Visual regression config (NEW)
7. **tests/visual.spec.ts** - Screenshot tests (NEW)
8. **public/fonts/README.md** - Futura instructions (NEW)

## Visual Regression Testing

### Setup
```bash
npm install
npx playwright install
```

### Run Tests
```bash
# Generate baseline screenshots
npm run test:ui:update

# Run visual regression tests
npm run test:ui
```

### Update Baselines
```bash
# After fixing issues, update snapshots
npm run test:ui:update
```

### Test Matrix
- **Desktop**: 1440x900 (home, fund)
- **iPhone**: 390x844 (home, fund) - Phase 2
- **iPad**: 1024x1366 (home, fund) - Phase 2

## Exact Typography Values (from MCP)

### Navigation
```
Logo: font-['Futura:Bold'] text-[26px] tracking-[-1.82px] leading-none
Menu items: font-['Karla:SemiBold'] text-[23px] leading-none
Nav buttons: font-['Karla:SemiBold'] text-[20px] h-[40px]
```

### Hero Section
```
H1 "PRIMORDIA": font-['Futura:Bold'] text-[125px] tracking-[-10px] leading-none
Tagline: font-['Karla:Medium'] text-[66px] leading-[1.13] tracking-[-4.62px]
Button text: font-['Karla:Medium'] text-[28px] leading-none
Button help text: font-['Karla:Medium'] text-[18px] leading-none
```

### Section Headings
```
H2: font-['Montserrat:Bold'] text-[78px] leading-none
H3: font-['Montserrat:Bold'] text-[22-31px] leading-[1.24] or leading-none
```

### Body Text
```
Large body: font-['Karla:Regular'] text-[31-32px] leading-[1.48] or leading-none
Medium body: font-['Karla:Regular'] text-[23px] leading-[1.54] (FAQ)
Small body: font-['Karla:Regular'] text-[18px] leading-[1.22] (step cards)
```

### Buttons
```
Primary/Secondary: font-['Karla:Medium'] text-[28-29px] leading-none h-[56px]
Small: font-['Karla:Medium'] text-[20px] leading-none h-[40px]
Status badge: font-['Karla:Medium'] text-[23px] leading-none h-[42px]
```

## Next Steps

### Immediate
1. Run `npm install` to get Playwright
2. Run `npm run dev` to start server
3. Run `npm run test:ui:update` to generate baselines
4. Review screenshots in `tests/visual.spec.ts-snapshots/`

### If Typography Still Wrong
1. Check font loading in DevTools Network tab
2. Verify CSS variables in browser inspector
3. Compare computed styles vs MCP values
4. Run visual tests to see exact differences

### Phase 2 (Mobile/Tablet)
- Tests already configured for iPhone/iPad viewports
- Will fail until responsive breakpoints added
- Use baselines to verify responsive updates

## Futura Font Setup (Optional)

To use actual Futura Bold:

1. Purchase Futura Bold from a font foundry
2. Convert to WOFF2: https://cloudconvert.com/ttf-to-woff2
3. Save as `public/fonts/futura-bold.woff2`
4. Uncomment localFont config in `app/layout.tsx`

**Current**: Uses Impact/Arial Black fallback with similar geometric proportions
