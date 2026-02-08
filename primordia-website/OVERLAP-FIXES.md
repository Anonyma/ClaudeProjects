# Overlap & Z-Index Fixes

## Issues Fixed

### 1. ✅ "View Funded Experiments" Button Overlap
**Problem**: Button was extending outside "How it Works" section, overlapping "Definition" section below

**Root Cause**:
- Section height: 906px
- Inner container height: 951px with top: -14px
- Button at top: 789px extends beyond section bounds

**Fix**: Added `overflow-hidden` to section
```tsx
<section className="relative w-full h-[906px] overflow-hidden">
```

### 2. ✅ "Stories & Lab Notes" Title Overlap
**Problem**: Title "Stories & Lab Notes" was collapsing onto subtitle "Learn about DIY community bio initiatives"

**Root Cause**: `leading-none` on 66px font caused text to have no line-height spacing

**Fix**: Changed to `leading-[1.2]` for proper spacing
```tsx
<h2 className="... text-[66px] leading-[1.2] ...">
  Stories & Lab Notes
</h2>
```

**Subtitle**: Changed to `leading-[1.5]` for better readability
```tsx
<p className="... text-[32px] leading-[1.5] ...">
  Learn about DIY community bio initiatives
</p>
```

### 3. ✅ Hero Button Helper Text Spacing
**Problem**: Helper text appeared very small in screenshots vs Figma

**Root Cause**: Text had no line-height specified, causing cramped rendering

**Fix**: Added `leading-[1.67]` for proper line spacing
```tsx
<p className="... text-[18px] leading-[1.67] ...">
  Up-to $3000 for your project
</p>
```

## Font Rendering Note

**Futura vs Impact**: Current implementation uses Impact as Futura fallback
- Impact is ~10% wider than Futura Bold
- This causes slight visual differences but maintains geometric proportions
- To use actual Futura: Add `futura-bold.woff2` to `/public/fonts/`

## Files Modified

1. **app/page.tsx**
   - Line 135: Added `overflow-hidden` to How it Works section
   - Line 211-217: Updated Stories section heading line-heights
   - Line 80, 89: Updated hero button helper text line-heights

## Testing

Run visual tests to verify fixes:
```bash
npm run dev
npm run test:ui:update  # Update baselines
npm run test:ui         # Verify no overlaps
```

## Verification Checklist

- [ ] "View Funded Experiments" button contained within section
- [ ] "Stories & Lab Notes" title doesn't overlap subtitle
- [ ] Hero button helper text properly spaced below buttons
- [ ] No z-index issues between sections
- [ ] All text readable and matches Figma spacing

## Next Steps

If overlaps persist:
1. Check browser DevTools for computed `overflow` values
2. Verify z-index stacking contexts (all sections are `position: relative`)
3. Measure actual rendered heights vs design values
4. Compare screenshots side-by-side with Figma exports
