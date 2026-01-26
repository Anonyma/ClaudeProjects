# CLAUDE.md - Nirvex Project

This file provides context for Claude Code when working on Nirvex projects.

## About Nirvex

**Nirvex** is a B2B marketing agency based in Valencia, Spain. They specialize in SEO, Facebook Ads, and marketing strategy for businesses.

- **Website:** nirvex.es
- **Primary market:** Spain (77.6%), with presence in Mexico, Colombia
- **Audience:** B2B, desktop-first (80% ordenador)

---

## Brand Style Guide

### Color Palette

| Color | Hex | Usage |
|-------|-----|-------|
| Deep Navy | `#010012` | Primary background |
| Navy Blue | `#021644` | Secondary background, gradients |
| White | `#FFFFFF` | Primary text, headings |
| Gray Blue | `#A9AABA` | Body text, secondary text |
| Light Gray | `#C6C7D5` | Tertiary text |
| Link Blue | `#3FA2F6` | Links, highlights, CTAs |
| Success Green | `#25D366` | Positive metrics, success states |
| Warning Orange | `#f59e0b` | Warnings, opportunities |
| Purple | `#a855f7` | Accent, urgent items |
| Red | `#ef4444` | Errors, critical issues |

### Typography

- **Font Family:** Poppins (Google Fonts)
- **Weights:** 300 (light), 400 (regular), 500 (medium), 600 (semibold), 700 (bold)
- **Headings:** Light weight (300-400) for elegance
- **Body:** Regular weight (400)
- **Labels:** Semibold (600), uppercase, letter-spacing 1-1.5px

### Design Principles

1. **Dark theme** - Always use deep navy background
2. **Subtle borders** - `rgba(255, 255, 255, 0.16)` for separators
3. **Minimal decoration** - Clean, professional, no unnecessary elements
4. **Data-focused** - Let numbers and insights stand out
5. **Spanish language** - Always use proper tildes (á, é, í, ó, ú, ñ)

---

## SEO Monthly Report Structure

Reports follow this 9-slide structure (landscape A4 format):

### Slide 1: Portada (Cover)
- Nirvex logo centered
- "Informe SEO Mensual" title
- "Estado y próximas acciones" subtitle
- Client domain (nirvex.es)
- Period analyzed + emission date at bottom

### Slide 2: Estado SEO
- Traffic light status indicator (green/yellow/red)
- Executive reading (1-2 sentences)
- Main risk identification
- 4 key metrics: Impresiones, Clics, CTR, Posición media

### Slide 3: Evolución 30 días
- Side-by-side comparison: Current 30 days vs Previous 30 days
- Context explanation (seasonality, trends)
- Pie charts: Distribution by country and device

### Slide 4: Evolución 120 días
- Side-by-side comparison: Current 120 days vs Previous 120 days
- Quarterly trend analysis

### Slide 5: Keywords que importan
- Two columns: Keywords transaccionales + Keywords informacionales
- Table with: Keyword, Position, Impressions, Status
- Summary stats: Top 10 count, near Top 10, total tracked

### Slide 6: Rendimiento por página
- Table of top pages with: Clics, Impresiones, CTR, Posición, Estado
- Opportunity highlight (high impressions, low CTR)
- Model to replicate (what's working well)

### Slide 7: Trabajo SEO realizado este mes
- 3 metric cards (contenidos nuevos, optimizados, acciones)
- Two columns: "Contenido y optimización" + "SEO técnico y seguimiento"
- Checklist format with ✓ bullets

### Slide 8: Lo que funciona / Oportunidades
- Two-column layout with status boxes
- Green box: What's working (circle bullets)
- Yellow box: Opportunities / In progress (circle bullets)
- Impact on business summary

### Slide 9: Próximas acciones
- Numbered action cards (1-5)
- Each with title + description + objective
- Plan operativo intro

### Slide 10: Cierre (Closing)
- Centered layout with logo
- "Foco del próximo mes" summary
- 3 key metrics (contenidos, objetivo clics, meta keywords)
- Contact prompt

---

## Technical Specifications

### Report Format
- **Size:** A4 Landscape (297mm × 210mm)
- **CSS:** `@page { size: A4 landscape; margin: 0; }`
- **Padding:** 35px top/bottom, 45px left/right
- **Print:** `-webkit-print-color-adjust: exact;`

### Pie Charts (SVG)
Use high-contrast colors that are easily distinguishable:
```html
<!-- Country distribution -->
<circle stroke="#3FA2F6"/> <!-- España - Blue -->
<circle stroke="#f59e0b"/> <!-- México - Orange -->
<circle stroke="#a855f7"/> <!-- Colombia - Purple -->
<circle stroke="#4A4D5E"/> <!-- Otros - Gray -->

<!-- Device distribution -->
<circle stroke="#25D366"/> <!-- Ordenador - Green -->
<circle stroke="#3FA2F6"/> <!-- Móvil - Blue -->
<circle stroke="#a855f7"/> <!-- Tablet - Purple -->
```

### Bullet Points
Use CSS circles, not text characters:
```css
li::before {
    content: '';
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: var(--success-green);
}
```

### PDF Generation
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --headless --disable-gpu \
  --print-to-pdf="output.pdf" \
  --no-pdf-header-footer \
  input.html
```

---

## Project Files

| File | Purpose |
|------|---------|
| `nirvex-informe-final.html` | Current monthly report (landscape, dark theme) |
| `nirvex-informe-final.pdf` | Generated PDF for client delivery |
| `nirvex-informe-interactivo.html` | Interactive web version with animations |
| `nirvex-informe-light.html` | Light mode version (deprecated) |
| `NIRVEX-1.png` | Nirvex logo (white on transparent) |
| `FONDO-NIRVEX-_1_.webp` | Background texture asset |
| `og-docs/Template Informe Seo Mensual...pdf` | Reference template from client |

---

## Data Sources

Reports are generated from **Google Search Console** data:
- Impresiones (impressions)
- Clics (clicks)
- CTR (click-through rate)
- Posición media (average position)
- Distribution by country and device
- Top pages and keywords

### Key Metrics to Track
- **Transactional keywords:** "agencia seo valencia", "agencia marketing b2b", etc.
- **Informational keywords:** "organigrama departamento marketing", "pipeline de ventas", etc.
- **Brand keywords:** "nirvex" (should have high CTR ~17%)

---

## Spanish Language Notes

Always use proper Spanish orthography:
- distribución, posición, optimización, técnico
- atracción, indexación, emisión
- próximas, días, más, página
- tráfico, métricas, análisis
- navideño (not navideno)

---

## Common Tasks

### Generate new monthly report
1. Get latest Google Search Console data
2. Update metrics in `nirvex-informe-final.html`
3. Update dates (periodo analizado, fecha de emisión)
4. Update "Trabajo realizado" section with month's activities
5. Update "Próximas acciones" with planned work
6. Generate PDF with Chrome headless
7. Commit changes

### Update work done section
Located in Slide 7, update the `<li>` items under:
- "Contenido y optimización"
- "SEO técnico y seguimiento"

### Update next actions
Located in Slide 9, update the `.action-card` elements with:
- Numbered priorities (1-5)
- Title + description + objective for each

---

## Contact

For questions about Nirvex projects, the reports are delivered to the client's account manager.
