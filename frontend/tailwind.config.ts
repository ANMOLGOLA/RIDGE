import type { Config } from 'tailwindcss'

export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        ridge: {
          navy: '#002060',
          orange: '#FF5C1F',
          deep: '#0B1B3F',
          card: '#F3F6FC',
          border: '#D3DDF2',
          text: '#1F2A44',
          surface: '#FFFFFF',
          darkbg: '#070F22',
          darkcard: '#0D1E42',
          darkborder: '#1E3566',
        },
        risk: {
          open: '#10B981',       // Green
          risky: '#F59E0B',      // Amber
          high: '#EF4444',       // Red
          blocked: '#111827',    // Black / Dark Slate
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      }
    },
  },
  plugins: [],
} satisfies Config
