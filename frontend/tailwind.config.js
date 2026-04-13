/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        title: ["Sora", "sans-serif"],
        body: ["Outfit", "sans-serif"],
      },
      colors: {
        eco: {
          50: "#eefbf2",
          100: "#dcf6e2",
          200: "#bdecc9",
          300: "#8ddb9f",
          400: "#57c673",
          500: "#2fa856",
          600: "#258747",
          700: "#206b3d",
          800: "#1d5634",
          900: "#19472d"
        }
      },
      boxShadow: {
        panel: "0 20px 55px -30px rgba(9, 42, 22, 0.55)",
      },
      animation: {
        rise: "rise 700ms ease-out forwards",
      },
      keyframes: {
        rise: {
          "0%": { opacity: 0, transform: "translateY(18px)" },
          "100%": { opacity: 1, transform: "translateY(0)" },
        },
      },
    },
  },
  plugins: [],
};
