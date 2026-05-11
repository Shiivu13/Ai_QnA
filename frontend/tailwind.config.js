/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // ── Backgrounds ──────────────────────────
        bg: {
          base:    '#FAF8F5',   // warm off-white / cream
          surface: '#FFFFFF',   // pure white cards
          subtle:  '#F3F0EB',   // slightly tinted panels
          purple:  '#F5F0FF',   // light lavender wash
        },
        // ── Primary Accent — Purple / Lavender ───
        primary: {
          DEFAULT: '#9F7AEA',   // lavender purple (buttons)
          hover:   '#8B5CF6',   // deeper on hover
          light:   '#EDE9FE',   // pale lavender (badges, tags)
          border:  '#C4B5FD',   // border lavender
          glow:    'rgba(167,139,250,0.25)',
        },
        // ── Text ─────────────────────────────────
        ink: {
          DEFAULT: '#1E1B2E',   // deep purple-black headline
          body:    '#4B4563',   // warm dark slate body
          muted:   '#6B7280',   // muted label
          light:   '#9CA3AF',   // placeholder / dimmed
        },
        // ── Borders ──────────────────────────────
        border: {
          DEFAULT: '#E5E0F5',   // very light purple-tinted border
          strong:  '#C4B5FD',   // lavender border
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      boxShadow: {
        card:         '0 2px 16px rgba(0,0,0,0.07)',
        'card-hover': '0 8px 32px rgba(159,122,234,0.18)',
        purple:       '0 4px 24px rgba(159,122,234,0.35)',
        sm:           '0 1px 8px rgba(0,0,0,0.06)',
      },
      backgroundImage: {
        'hero-gradient':   'linear-gradient(135deg, #9F7AEA 0%, #C084FC 100%)',
        'text-gradient':   'linear-gradient(135deg, #7C3AED 0%, #A78BFA 60%, #C084FC 100%)',
        'badge-gradient':  'linear-gradient(135deg, #F5F0FF 0%, #EDE9FE 100%)',
      },
    },
  },
  plugins: [],
}
