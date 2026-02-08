import type { Metadata } from "next";
import { Karla, Montserrat, League_Spartan } from "next/font/google";
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

const leagueSpartan = League_Spartan({
  subsets: ["latin"],
  weight: ["700"],
  variable: "--font-league-spartan",
  display: "swap",
});

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
        className={`${karla.variable} ${montserrat.variable} ${leagueSpartan.variable} font-sans antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
