# Primordia Website - Phase 1: Desktop Implementation

Pixel-perfect Next.js implementation of the Primordia website, currently optimized for desktop (1440px).

## 🚀 Quick Start

### Installation

```bash
npm install
```

### Development

```bash
npm run dev
```

Visit [http://localhost:3000](http://localhost:3000)

### Production Build

```bash
npm run build
npm start
```

## 📐 Phase 1 Implementation (DESKTOP ONLY)

### Pages Implemented
- **Home** (`/`) - Full homepage with all sections
- **Fund Experiments** (`/fund`) - Donor-focused page

### Design Specifications (Desktop)
- **Viewport:** 1440px width
- **Typography:**
  - Futura Bold (Logo)
  - Montserrat Bold/SemiBold (Headings)
  - Karla Regular/Medium/SemiBold (Body)
- **Colors:**
  - Primary: #000000 (Black)
  - Background: #FFFFFF (White)
  - Card BG: #F4F4F4
  - Border: #C3D1E9
- **Border Radius:** 39px (buttons), 48px (cards), 20px (FAQ items)
- **Border Width:** 2.5px (consistent across all borders)

### Key Features
- ✅ Pixel-accurate desktop layout (1440px)
- ✅ Accessible FAQ accordion (keyboard navigable, aria-labeled)
- ✅ Hover states on all interactive elements
- ✅ Semantic HTML structure
- ✅ Component-based architecture
- ✅ Design tokens layer (Tailwind config)

### Components
- `Button` - 4 variants (primary, secondary, nav, status), 3 sizes
- `MenuBar` - Global navigation with logo and CTA buttons
- `Footer` - Site footer with links and attribution
- `FAQAccordion` - Accessible accordion with keyboard support
- `ProjectCard` - Story/lab notes cards with status badges
- `StepCard` - Process step cards with icons

## 🎯 Phase 2 Ready - Responsive Implementation Checklist

### Current Architecture Supports Easy Responsive Updates

#### ✅ Already Responsive-Ready
1. **Design Tokens** - All spacing, colors, typography centralized in `tailwind.config.ts`
2. **Component System** - Reusable components accept props for layout variations
3. **Semantic Structure** - Clean HTML ready for media query adjustments

#### 📱 For Phase 2 (Mobile/Tablet):
When iPhone and iPad frames are selected, add responsive breakpoints:

**Breakpoints to Add:**
- `sm:` - 375px (iPhone)
- `md:` - 768px (iPad)
- `lg:` - 1024px+ (Desktop)

**Components Needing Updates:**
- `MenuBar` → Add hamburger menu for mobile
- `Button` → Adjust sizes (sm: text-[18px], md: text-[24px], lg: text-[28px])
- `StepCard` → Stack vertically on mobile, 2-column on tablet
- `ProjectCard` → Full width on mobile, 2-column on tablet
- `FAQAccordion` → Adjust padding for smaller screens

**Layout Updates:**
- Hero section: Stack title/CTA vertically on mobile
- Section padding: Reduce from 120px to 20px (mobile), 40px (tablet)
- Typography scale down: 0.6x for mobile, 0.8x for tablet
- Max-width containers: 375px (mobile), 768px (tablet), 1440px (desktop)

**No Refactoring Required:**
- Component structure stays the same
- Just add Tailwind responsive prefixes (sm:, md:, lg:)
- Update design tokens for responsive font sizes
- Add conditional rendering for mobile menu

### Files to Update for Phase 2:
```
tailwind.config.ts → Add responsive fontSize scale
components/MenuBar.tsx → Add mobile hamburger
components/Button.tsx → Add responsive size variants
app/globals.css → Add responsive utility classes
All page sections → Add sm:/md:/lg: prefixes to spacing
```

## 🛠️ Tech Stack

- **Framework:** Next.js 14 (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **Fonts:** Google Fonts (Karla, Montserrat) + Futura (system)
- **Images:** Served from Figma MCP localhost server

## 📁 Project Structure

```
primordia-website/
├── app/
│   ├── layout.tsx          # Root layout with fonts
│   ├── page.tsx            # Home page
│   ├── fund/
│   │   └── page.tsx        # Fund Experiments page
│   └── globals.css         # Global styles + design tokens
├── components/
│   ├── Button.tsx          # Reusable button component
│   ├── MenuBar.tsx         # Global navigation
│   ├── Footer.tsx          # Site footer
│   ├── FAQAccordion.tsx    # Accessible accordion
│   ├── ProjectCard.tsx     # Story cards
│   └── StepCard.tsx        # Process step cards
├── tailwind.config.ts      # Design tokens + theme
├── tsconfig.json
├── package.json
└── README.md
```

## 🔑 Key Design Decisions

### Why This Architecture?
1. **Token-Based:** All design values in Tailwind config = easy global updates
2. **Component Props:** Components accept variant/size props = no duplication
3. **Semantic HTML:** Proper heading hierarchy, landmarks, ARIA = accessibility
4. **Absolute Positioning:** Matches Figma's exact pixel positions for Phase 1
5. **Responsive Hooks:** Structure ready for breakpoint rules without refactoring

### Accessibility Features
- Keyboard navigation for FAQ accordion
- Focus-visible styles on all interactive elements
- Semantic HTML (nav, main, section, footer)
- ARIA labels and expanded states
- Skip links ready to add

## 📊 Performance Considerations

- Images loaded from localhost MCP server (Phase 1)
- For production: Move images to `/public` or CDN
- Next.js Image component used where appropriate
- Lazy loading ready for below-fold content

## 🐛 Known Limitations (Phase 1)

- Desktop-only layout (1440px)
- No mobile/tablet breakpoints yet
- Images served from localhost:3845 (Figma MCP)
- No form validation (contact/apply pages not implemented)
- FAQ answers are placeholder text

## 🎨 Design Fidelity

This implementation follows the Figma designs with:
- ✅ Exact typography (families, weights, sizes, line-heights, tracking)
- ✅ Exact colors and backgrounds
- ✅ Exact spacing and positioning
- ✅ Exact border radius and widths
- ✅ Exact shadow specifications
- ✅ Hover/focus states as designed

## 📞 Next Steps

1. **Phase 2:** Select iPhone + iPad frames in Figma
2. **Add Breakpoints:** Update components with responsive Tailwind classes
3. **Test:** Verify pixel accuracy on all three screen sizes
4. **Deploy:** Move to production hosting (Vercel/Netlify)

---

**Built with Claude Code** | Phase 1 Complete ✅
