/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      spacing: {
        'mobile-sm': '0.25rem',
        'mobile-md': '0.5rem',
        'mobile-lg': '0.75rem',
      },
      fontSize: {
        'mobile-xs': '0.625rem',
        'mobile-sm': '0.75rem',
        'mobile-base': '0.875rem',
      },
    },
  },
  plugins: [],
};
