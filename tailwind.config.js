/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './dashboard/templates/**/*.html',
    './static/js/**/*.js',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#fdf2f2',
          100: '#fce4e4',
          200: '#f9caca',
          300: '#f4a5a5',
          400: '#ec7373',
          500: '#e04848',
          600: '#cc2f2f',
          700: '#993333', // Main burgundy
          800: '#7c2a2a',
          900: '#5c1f1f',
        },
        secondary: {
          50: '#fefce8',
          100: '#fef9c3',
          200: '#fef08a',
          300: '#fde047',
          400: '#facc15',
          500: '#D4AF37', // Main gold
          600: '#ca8a04',
          700: '#a16207',
          800: '#854d0e',
          900: '#713f12',
        },
      },
      fontFamily: {
        'arabic': ['Tajawal', 'sans-serif'],
        'english': ['Inter', 'sans-serif'],
      },
      borderRadius: {
        'card': '0.75rem',
      },
      boxShadow: {
        'card': '0 8px 24px rgba(0,0,0,0.06), 0 2px 8px rgba(0,0,0,0.04)',
        'card-hover': '0 10px 28px rgba(0,0,0,.08), 0 3px 10px rgba(0,0,0,.05)',
        'ring': '0 0 0 3px rgba(153, 51, 51, 0.25)',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}
