/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        forge: {
          bg: '#0D0F14',
          sidebar: '#11131A',
          surface: '#181B24',
          elevated: '#202431',
          border: '#292D39',
          primary: '#8B5CF6',
          secondary: '#22D3EE',
          success: '#34D399',
          warning: '#FBBF24',
          error: '#FB7185',
          text: '#F4F4F5',
          muted: '#A1A1AA',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Menlo', 'Monaco', 'Courier New', 'monospace'],
      },
      borderRadius: {
        'forge': '12px',
      },
    },
  },
  plugins: [],
}

