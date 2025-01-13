/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./static/**/*.js"
  ],
  theme: {
    extend: {
      animation: {
        'bounce-slow': 'bounce 1.5s infinite',
        'text-gradient': 'shine 3s linear infinite',
        'shine': 'shine 3s linear infinite'
      },
      keyframes: {
        shine: {
          '0%': { backgroundPosition: '0% 50%' },
          '50%': { backgroundPosition: '100% 50%' },
          '100%': { backgroundPosition: '0% 50%' }
        }
      }
    }
  },
  darkMode: 'class',
  plugins: []
}
