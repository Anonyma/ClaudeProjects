# Phase 2 Ready Checklist - Mobile & Tablet Implementation

## ✅ Phase 1 Complete: Desktop (1440px)

All components and pages are built with responsive architecture. Phase 2 will **NOT require refactoring** — only adding breakpoint rules.

---

## 📱 Phase 2 Breakpoints Strategy

### Breakpoint Definitions
```typescript
screens: {
  'sm': '375px',   // iPhone (Portrait)
  'md': '768px',   // iPad (Portrait)
  'lg': '1024px',  // iPad (Landscape) / Small Desktop
  'xl': '1440px',  // Desktop (current)
}
```

---

## 🎯 Components Requiring Responsive Updates

### 1. MenuBar Component (`components/MenuBar.tsx`)

**Desktop (Current):**
- Full horizontal menu with visible links
- Logo on left, menu in center, buttons on right

**Mobile (Add):**
- Logo on left
- Hamburger icon on right
- Full-screen overlay menu when open
- Stack menu items vertically

**Changes Required:**
```tsx
// Add mobile state
const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

// Hide desktop menu on mobile
<div className="hidden lg:flex items-center gap-[54px]">

// Add hamburger button (mobile only)
<button className="lg:hidden" onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
  {/* Hamburger icon */}
</button>

// Add mobile menu overlay
{mobileMenuOpen && (
  <div className="lg:hidden fixed inset-0 bg-white z-50">
    {/* Mobile menu content */}
  </div>
)}
```

**Breakpoint Rules:**
- `sm:` Hide full menu, show hamburger
- `lg:` Show full menu, hide hamburger

---

### 2. Button Component (`components/Button.tsx`)

**Desktop (Current):**
- 3 sizes: sm (40px), md (56px), lg (56px)
- Text: 20px, 28px, 29px

**Mobile/Tablet (Add):**
- Scale down text sizes proportionally
- Reduce padding for smaller screens

**Changes Required:**
```tsx
const sizeStyles = {
  sm: 'h-[32px] md:h-[36px] lg:h-[40px] text-[16px] md:text-[18px] lg:text-[20px]',
  md: 'h-[44px] md:h-[50px] lg:h-[56px] text-[20px] md:text-[24px] lg:text-[28px]',
  lg: 'h-[44px] md:text-[50px] lg:h-[56px] text-[21px] md:text-[25px] lg:text-[29px]',
};
```

**Breakpoint Rules:**
- `sm:` 0.7x scale
- `md:` 0.85x scale
- `lg:` 1.0x scale (current)

---

### 3. Hero Sections (Both Pages)

**Desktop (Current):**
- Wide layout with side-by-side title + description
- Large hero image background
- CTA buttons inline

**Mobile (Add):**
- Stack title and description vertically
- Reduce hero height
- Stack CTA buttons vertically
- Scale down typography

**Changes Required:**
```tsx
// Hero container
<section className="h-[500px] md:h-[650px] lg:h-[828px]">

// Title
<h1 className="text-[48px] md:text-[80px] lg:text-[125px] tracking-[-4px] md:tracking-[-7px] lg:tracking-[-10px]">

// Description
<p className="text-[28px] md:text-[42px] lg:text-[66px] tracking-[-2px] md:tracking-[-3px] lg:tracking-[-4.62px]">

// Button container
<div className="flex flex-col sm:flex-col md:flex-row gap-[12px] md:gap-[20px] lg:gap-[26px]">
```

**Breakpoint Rules:**
- `sm:` Height 500px, text 48px/28px, vertical buttons
- `md:` Height 650px, text 80px/42px, horizontal buttons
- `lg:` Height 828px, text 125px/66px (current)

---

### 4. "How it Works" Step Cards

**Desktop (Current):**
- 5 cards in a row (horizontal)
- Each card 237px wide
- 60px gap between cards

**Mobile (Add):**
- Stack vertically (1 column)
- Full width cards

**Tablet (Add):**
- 2 columns with wrapping

**Changes Required:**
```tsx
<div className="flex flex-col sm:flex-col md:grid md:grid-cols-2 lg:flex lg:flex-row gap-[30px] md:gap-[40px] lg:gap-[60px]">
  {/* Step cards */}
</div>
```

**Breakpoint Rules:**
- `sm:` 1 column, full width
- `md:` 2 columns, grid
- `lg:` 5 columns, flex row (current)

---

### 5. Project Cards (Stories Section)

**Desktop (Current):**
- 2 columns, 2 rows (4 cards total)
- Each card 499px × 499px
- 55px gap

**Mobile (Add):**
- 1 column, stacked vertically
- Full width cards (max 375px)

**Tablet (Add):**
- 2 columns (same as desktop)

**Changes Required:**
```tsx
<div className="grid grid-cols-1 md:grid-cols-2 gap-[30px] md:gap-[40px] lg:gap-[55px]">
  <ProjectCard ... />
  <ProjectCard ... />
</div>
```

**Breakpoint Rules:**
- `sm:` 1 column
- `md:` 2 columns (current)
- `lg:` 2 columns (current)

---

### 6. FAQ Accordion

**Desktop (Current):**
- Width: 922px
- Padding: 40px horizontal
- Text: 23px

**Mobile (Add):**
- Full width (with margins)
- Reduced padding: 20px horizontal
- Text: 18px

**Changes Required:**
```tsx
<div className="w-full max-w-[922px] mx-auto px-[20px] md:px-0">
  <button className="px-[20px] md:px-[40px] py-[16px] md:py-[20.5px]">
    <span className="text-[18px] md:text-[20px] lg:text-[23px]">
      {item.question}
    </span>
  </button>
</div>
```

**Breakpoint Rules:**
- `sm:` Full width, padding 20px, text 18px
- `md:` Max 922px, padding 40px, text 20px
- `lg:` Max 922px, padding 40px, text 23px (current)

---

### 7. Footer

**Desktop (Current):**
- Two columns (links left, attribution right)
- Horizontal padding: 120px
- Font size: 26px (links), 22px (attribution)

**Mobile (Add):**
- Stack vertically (center-aligned)
- Reduced padding: 20px
- Font size: 20px / 18px

**Changes Required:**
```tsx
<div className="flex flex-col md:flex-row justify-between items-center md:items-start px-[20px] md:px-[60px] lg:px-[120px]">
  <div className="text-center md:text-left text-[20px] md:text-[24px] lg:text-[26px]">
    {/* Links */}
  </div>
  <div className="text-center md:text-right text-[18px] md:text-[20px] lg:text-[22px] mt-[30px] md:mt-0">
    {/* Attribution */}
  </div>
</div>
```

**Breakpoint Rules:**
- `sm:` Vertical stack, center-aligned, padding 20px
- `md:` Horizontal row, left/right aligned, padding 60px
- `lg:` Horizontal row (current), padding 120px

---

## 📐 Typography Scaling Rules

### Mobile (sm: 375px)
- Scale: 0.6x - 0.7x of desktop
- Line height: Slightly increased for readability
- Tracking: Reduced proportionally

### Tablet (md: 768px)
- Scale: 0.8x - 0.85x of desktop
- Line height: Same as desktop
- Tracking: Same as desktop

### Desktop (lg: 1440px)
- Scale: 1.0x (current implementation)
- No changes needed

---

## 🎨 Spacing Scaling Rules

### Mobile (sm: 375px)
| Element | Desktop | Mobile |
|---------|---------|--------|
| Section padding (horizontal) | 120px | 20px |
| Section padding (vertical) | 80px | 40px |
| Card gap | 55px | 20px |
| Button gap | 26px | 12px |
| Step gap | 60px | 30px |

### Tablet (md: 768px)
| Element | Desktop | Tablet |
|---------|---------|--------|
| Section padding (horizontal) | 120px | 60px |
| Section padding (vertical) | 80px | 60px |
| Card gap | 55px | 40px |
| Button gap | 26px | 20px |
| Step gap | 60px | 40px |

---

## 🚀 Implementation Order for Phase 2

### Step 1: Update Tailwind Config
```typescript
// tailwind.config.ts
screens: {
  'sm': '375px',
  'md': '768px',
  'lg': '1024px',
  'xl': '1440px',
}
```

### Step 2: Update MenuBar (Mobile Menu)
- Add hamburger icon
- Add mobile menu overlay
- Add close button
- Add animations

### Step 3: Update Button Component (Responsive Sizes)
- Add `sm:`, `md:`, `lg:` classes to size variants
- Test all button sizes on all breakpoints

### Step 4: Update Home Page Sections
- Hero: Add responsive typography + layout
- What is Primordia: Add responsive text + image sizing
- How it Works: Change flex to grid for mobile/tablet
- Stories: Change card grid to responsive columns
- FAQs: Add responsive width + padding

### Step 5: Update Fund Page Sections
- Hero: Same as home hero
- For Donors: Add responsive card grid
- Donations graphic: Stack vertically on mobile
- FAQs: Same as home FAQs

### Step 6: Update Footer
- Add flex-col to flex-row breakpoint
- Add responsive padding
- Add responsive text sizes

### Step 7: Testing
- Test all pages on 375px (iPhone)
- Test all pages on 768px (iPad)
- Test all pages on 1440px (Desktop)
- Test transitions between breakpoints
- Test on real devices

---

## 🔧 Files to Modify for Phase 2

```
✏️ tailwind.config.ts          (Add breakpoints)
✏️ components/MenuBar.tsx       (Mobile menu + hamburger)
✏️ components/Button.tsx        (Responsive sizes)
✏️ components/Footer.tsx        (Responsive layout)
✏️ components/FAQAccordion.tsx  (Responsive padding/text)
✏️ components/ProjectCard.tsx   (Responsive sizing)
✏️ components/StepCard.tsx      (Responsive sizing)
✏️ app/page.tsx                 (Add sm:/md:/lg: prefixes)
✏️ app/fund/page.tsx            (Add sm:/md:/lg: prefixes)
✏️ app/globals.css              (Add responsive utilities if needed)
```

**Total files to modify:** 10
**New components needed:** 0
**Refactoring needed:** None

---

## ✅ Phase 2 Success Criteria

### Mobile (375px)
- [ ] All content fits without horizontal scroll
- [ ] Typography is legible (minimum 16px)
- [ ] Touch targets are 44x44px minimum
- [ ] Navigation menu works (hamburger)
- [ ] Images scale proportionally
- [ ] Buttons stack vertically where needed

### Tablet (768px)
- [ ] 2-column layouts work correctly
- [ ] Typography scales appropriately
- [ ] Spacing feels balanced
- [ ] Navigation shows full menu
- [ ] Cards display in grid (2 columns)

### Desktop (1440px)
- [ ] No changes from Phase 1
- [ ] Layout remains pixel-perfect
- [ ] All existing functionality works

---

## 🎬 Ready for Phase 2

**Current Status:** Phase 1 Complete ✅

**To Start Phase 2:**
1. User selects iPhone + iPad frames in Figma for both pages
2. User provides updated Figma context
3. Apply responsive breakpoint rules (no refactoring)
4. Test on all three viewport sizes
5. Deploy updated version

**Estimated Time:** 2-3 hours
**Estimated Complexity:** Low (additive changes only)

