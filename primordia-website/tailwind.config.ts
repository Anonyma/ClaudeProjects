import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        futura: ["var(--font-futura)", "Impact", "Arial Black", "sans-serif"],
        montserrat: ["var(--font-montserrat)", "sans-serif"],
        karla: ["var(--font-karla)", "sans-serif"],
      },
      colors: {
        border: {
          light: "#C3D1E9",
        },
        card: {
          light: "#F4F4F4",
        },
        gray: {
          light: "#D9D9D9",
        },
      },
      borderRadius: {
        button: "39px",
        card: "48px",
        faq: "20px",
        section: "50px",
      },
      boxShadow: {
        card: "3px -4px 4.3px -3px rgba(0,0,0,0.25)",
        faq: "0px 1px 5px 0px rgba(0,0,0,0.25)",
        step: "5px -1px 5.1px 0px rgba(0,0,0,0.25)",
      },
      maxWidth: {
        desktop: "1440px",
      },
    },
  },
  plugins: [],
};

export default config;
