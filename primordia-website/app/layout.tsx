import type { Metadata } from 'next';
import { Karla, Montserrat } from 'next/font/google';
import localFont from 'next/font/local';
import './globals.css';

const karla = Karla({
  subsets: ['latin'],
  weight: ['400', '500', '600'],
  variable: '--font-karla',
  display: 'swap',
});

const montserrat = Montserrat({
  subsets: ['latin'],
  weight: ['600', '700'],
  variable: '--font-montserrat',
  display: 'swap',
});

// Futura placeholder - uses system fallbacks (Impact, Arial Black)
// To use actual Futura: add futura-bold.woff2 to public/fonts/
const futuraVariable = '--font-futura';

export const metadata: Metadata = {
  title: 'Primordia - Funding Early Biology Experiments in DIY Labs',
  description:
    'Primordia is a microgrants program for early stage biology experiments run in community labs. We provide small, fast grants and a structure for sharing lab notes, results, and stories.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${karla.variable} ${montserrat.variable}`} style={{ [futuraVariable]: 'Impact, "Arial Black", sans-serif' } as React.CSSProperties}>
      <body className={karla.className}>{children}</body>
    </html>
  );
}
