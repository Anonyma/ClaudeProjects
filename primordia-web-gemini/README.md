# Primordia Web (Gemini)

This is the Next.js implementation of the Primordia design (Desktop Phase).

## Tech Stack
- **Framework:** Next.js 15 (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **Fonts:** 
  - Google Fonts: Karla, Montserrat (loaded via `next/font/google`)
  - Custom: Futura (configured as `font-futura` looking for local font or system fallback)

## Setup

1.  **Install Dependencies:**
    ```bash
    npm install
    ```

2.  **Run Development Server:**
    ```bash
    npm run dev
    ```

3.  **Build for Production:**
    ```bash
    npm run build
    npm start
    ```

## Design Notes (Phase 1)
- **Typography:** Pixel-perfect sizes extracted from Figma (`text-125`, `text-78`, etc.).
- **Components:** Reusable Button, Navbar, Footer, Section, FAQAccordion.
- **Pages:**
  - Home: `/`
  - Fund Experiments: `/fund-experiments`

## Fonts
The design uses **Futura** (Bold) for the logo. As this is a paid font often not on Google Fonts, the project is configured to use a system fallback stack. To use the exact font, place `Futura-Bold.woff2` in `public/fonts` and update `src/app/layout.tsx` to load it using `next/font/local`.

## Next Steps (Phase 2)
- Mobile Responsiveness (iPhone/iPad frames).