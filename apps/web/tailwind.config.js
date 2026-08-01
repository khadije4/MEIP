/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        mauritania: { 50: '#eef9f4', 100: '#d7f1e5', 500: '#07804e', 600: '#056b41', 700: '#075d3b', 900: '#063d2a' },
        gold: { 50: '#fffaf0', 100: '#f9edcc', 200: '#efd99b', 300: '#e4c46b', 400: '#d9ac47', 500: '#c8962e', 600: '#a77420' },
        navy: { 900: '#183149', 950: '#102538' },
      },
      boxShadow: { card: '0 18px 50px -30px rgba(6, 61, 42, 0.38)' },
      fontFamily: { sans: ['Inter', 'Noto Sans Arabic', 'Segoe UI', 'Arial', 'sans-serif'] },
    },
  },
  plugins: [],
}
