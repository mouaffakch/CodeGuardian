/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        guardian: {
          900: '#0a0f1d',
          800: '#111827',
          700: '#1e293b',
          600: '#334155',
          accent: '#06b6d4', // cyan-500
          success: '#10b981', // emerald-500
          warning: '#f59e0b', // amber-500
          danger: '#ef4444', // red-500
        }
      }
    },
  },
  plugins: [],
}
