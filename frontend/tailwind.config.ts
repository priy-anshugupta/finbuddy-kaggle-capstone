import type { Config } from 'tailwindcss'

const config: Config = {
    content: [
        './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
        './src/components/**/*.{js,ts,jsx,tsx,mdx}',
        './src/app/**/*.{js,ts,jsx,tsx,mdx}',
    ],
    theme: {
        extend: {
            colors: {
                // Monochrome palette
                mono: {
                    50: '#F8F8F8',
                    100: '#E5E5E5',
                    200: '#D4D4D4',
                    300: '#A3A3A3',
                    400: '#737373',
                    500: '#6B6B6B',
                    600: '#525252',
                    700: '#404040',
                    800: '#262626',
                    900: '#111111',
                    950: '#0A0A0A',
                },
                // Legacy primary (mapped to monochrome)
                primary: {
                    50: '#F8F8F8',
                    100: '#E5E5E5',
                    200: '#D4D4D4',
                    300: '#A3A3A3',
                    400: '#737373',
                    500: '#525252',
                    600: '#404040',
                    700: '#262626',
                    800: '#171717',
                    900: '#111111',
                    950: '#0A0A0A',
                },
                secondary: {
                    50: '#F8F8F8',
                    100: '#F1F1F1',
                    200: '#E5E5E5',
                    300: '#D4D4D4',
                    400: '#A3A3A3',
                    500: '#6B6B6B',
                    600: '#525252',
                    700: '#404040',
                    800: '#262626',
                    900: '#171717',
                    950: '#0A0A0A',
                },
                accent: {
                    green: '#111111',
                    red: '#404040',
                    yellow: '#6B6B6B',
                    purple: '#262626',
                },
                // Glass backgrounds
                glass: {
                    white: 'rgba(255, 255, 255, 0.6)',
                    dark: 'rgba(0, 0, 0, 0.04)',
                },
                // Onyx (dark emphasis)
                onyx: '#0A0A0A',
            },
            fontFamily: {
                sans: ['Inter', 'system-ui', 'sans-serif'],
                display: ['Outfit', 'system-ui', 'sans-serif'],
            },
            letterSpacing: {
                'tight-heading': '-0.02em',
            },
            borderRadius: {
                'glass': '24px',
                'glass-sm': '12px',
            },
            spacing: {
                'grid': '24px',
                'grid-lg': '32px',
            },
            backgroundImage: {
                'gradient-radial': 'radial-gradient(ellipse at top, #F8F8F8 0%, #E5E5E5 100%)',
                'gradient-glass': 'linear-gradient(135deg, rgba(255,255,255,0.8) 0%, rgba(255,255,255,0.4) 100%)',
            },
            boxShadow: {
                'glass': '0 8px 32px 0 rgba(0, 0, 0, 0.04)',
                'glass-hover': '0 12px 40px 0 rgba(0, 0, 0, 0.08)',
                'onyx': '0 8px 32px 0 rgba(0, 0, 0, 0.12)',
                'subtle': '0 4px 14px 0 rgba(0, 0, 0, 0.06)',
            },
            animation: {
                'fade-in': 'fadeIn 0.5s ease-in-out',
                'slide-up': 'slideUp 0.5s ease-out',
                'slide-down': 'slideDown 0.3s ease-out',
                'pulse-slow': 'pulse 3s ease-in-out infinite',
                'shimmer': 'shimmer 2s linear infinite',
            },
            keyframes: {
                fadeIn: {
                    '0%': { opacity: '0' },
                    '100%': { opacity: '1' },
                },
                slideUp: {
                    '0%': { transform: 'translateY(20px)', opacity: '0' },
                    '100%': { transform: 'translateY(0)', opacity: '1' },
                },
                slideDown: {
                    '0%': { transform: 'translateY(-10px)', opacity: '0' },
                    '100%': { transform: 'translateY(0)', opacity: '1' },
                },
                shimmer: {
                    '0%': { backgroundPosition: '-200% 0' },
                    '100%': { backgroundPosition: '200% 0' },
                },
            },
            backdropBlur: {
                xs: '2px',
                glass: '15px',
            },
            transitionTimingFunction: {
                'glass': 'cubic-bezier(0.4, 0, 0.2, 1)',
            },
            transitionDuration: {
                'glass': '300ms',
            },
        },
    },
    plugins: [],
}

export default config
