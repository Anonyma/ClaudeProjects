import type { Metadata } from "next";
import { Karla, Montserrat } from "next/font/google";
import "./globals.css";

// Configure Google Fonts
const karla = Karla({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  variable: "--font-karla",
  display: "swap",
});

const montserrat = Montserrat({
  subsets: ["latin"],
  weight: ["700"],
  variable: "--font-montserrat",
  display: "swap",
});

// We'll use a class-based approach for Futura since we don't have the local file yet.
// For now, we define a variable that falls back to system fonts, 
// ensuring the customized Tailwind config picks it up.

export const metadata: Metadata = {
  title: "Primordia",
  description: "Funding Early Biology Experiments in DIY Labs",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${karla.variable} ${montserrat.variable} font-sans antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
