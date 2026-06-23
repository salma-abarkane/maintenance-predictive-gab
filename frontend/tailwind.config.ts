import type { Config } from 'tailwindcss'

export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        bporange: {
          50: '#FFF1E8',
          100: '#FFE2CC',
          200: '#FFC499',
          300: '#FFA766',
          400: '#FF7A1A',
          500: '#F05A00',
          600: '#D94A00',
          700: '#B83F00',
          800: '#8F3100',
          900: '#662300'
        }
      },
      boxShadow: {
        soft: '0 20px 45px rgba(15, 23, 42, 0.08)'
      }
    }
  },
  plugins: []
} satisfies Config
