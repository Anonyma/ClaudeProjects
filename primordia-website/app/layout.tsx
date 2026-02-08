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

const futura = localFont({
  src: '../public/fonts/futura-bold-webfont.woff2',
  variable: '--font-futura',
  display: 'swap',
  weight: '700',
});

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
    <html lang="en" className={`${karla.variable} ${montserrat.variable} ${futura.variable}`}>
      <body className={karla.className}>{children}</body>
    </html>
  );
}
