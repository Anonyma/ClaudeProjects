import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
        black: "#000000",
        white: "#FFFFFF",
      },
      fontFamily: {
        karla: ["var(--font-karla)", "sans-serif"],
        montserrat: ["var(--font-montserrat)", "sans-serif"],
        futura: ["Futura", "Futura-Bold", "sans-serif"], // Fallback stack
      },
      fontSize: {
        // Extracted exact sizes
        "125": ["125px", { lineHeight: "1", letterSpacing: "-10px" }], // H1
        "78": ["78px", { lineHeight: "1" }], // Section Heading
        "66": ["66px", { lineHeight: "1.13", letterSpacing: "-4.62px" }], // Hero
        "31": ["31px", { lineHeight: "1.48" }], // Body
        "28": ["28px", { lineHeight: "1" }], // Button (Large)
        "26": ["26px", { lineHeight: "1", letterSpacing: "-1.82px" }], // Logo
        "23": ["23px", { lineHeight: "1" }], // Nav & FAQ
        "20": ["20px", { lineHeight: "1" }], // Nav Button
      },
      borderRadius: {
        "39": "39px", // Button radius
      },
      spacing: {
        // Common spacings observed (approximated for now, usually multiples of 4 or 8)
        "100": "100px", // Menubar height
      },
    },
  },
  plugins: [],
};
export default config;
