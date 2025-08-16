import type { Config } from "tailwindcss";

const config: Config = {
    darkMode: ["class"],
    content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
  	extend: {
  		fontFamily: {
  			sans: [
  				'DM Sans',
  				'sans-serif'
  			]
  		},
  		colors: {
  			background: 'hsl(var(--background))',
  			foreground: 'hsl(var(--foreground))',
  			card: {
  				DEFAULT: 'hsl(var(--card))',
  				foreground: 'hsl(var(--card-foreground))'
  			},
  			popover: {
  				DEFAULT: 'hsl(var(--popover))',
  				foreground: 'hsl(var(--popover-foreground))'
  			},
  			primary: {
  				DEFAULT: 'hsl(var(--primary))',
  				foreground: 'hsl(var(--primary-foreground))'
  			},
  			secondary: {
  				DEFAULT: 'hsl(var(--secondary))',
  				foreground: 'hsl(var(--secondary-foreground))'
  			},
  			muted: {
  				DEFAULT: 'hsl(var(--muted))',
  				foreground: 'hsl(var(--muted-foreground))'
  			},
  			accent: {
  				DEFAULT: 'hsl(var(--accent))',
  				foreground: 'hsl(var(--accent-foreground))'
  			},
  			destructive: {
  				DEFAULT: 'hsl(var(--destructive))',
  				foreground: 'hsl(var(--destructive-foreground))'
  			},
  			border: 'hsl(var(--border))',
  			input: 'hsl(var(--input))',
  			ring: 'hsl(var(--ring))',
  			chart: {
  				'1': 'hsl(var(--chart-1))',
  				'2': 'hsl(var(--chart-2))',
  				'3': 'hsl(var(--chart-3))',
  				'4': 'hsl(var(--chart-4))',
  				'5': 'hsl(var(--chart-5))'
  			},
  			// FitAgent custom theme colors
  			fitagent: {
  				green: {
  					50: '#f0fdf4',
  					100: '#dcfce7',
  					200: '#bbf7d0',
  					300: '#86efac',
  					400: '#4ade80',
  					500: '#22c55e', // Primary green for healthy/growth
  					600: '#16a34a',
  					700: '#15803d',
  					800: '#166534',
  					900: '#14532d'
  				},
  				orange: {
  					50: '#fff7ed',
  					100: '#ffedd5',
  					200: '#fed7aa',
  					300: '#fdba74',
  					400: '#fb923c',
  					500: '#f97316', // Energy/motivation orange
  					600: '#ea580c',
  					700: '#c2410c',
  					800: '#9a3412',
  					900: '#7c2d12'
  				},
  				purple: {
  					50: '#faf5ff',
  					100: '#f3e8ff',
  					200: '#e9d5ff',
  					300: '#d8b4fe',
  					400: '#c084fc',
  					500: '#a855f7', // VP rewards purple
  					600: '#9333ea',
  					700: '#7c3aed',
  					800: '#6b21a8',
  					900: '#581c87'
  				}
  			}
  		},
  		borderRadius: {
  			lg: 'var(--radius)',
  			md: 'calc(var(--radius) - 2px)',
  			sm: 'calc(var(--radius) - 4px)'
  		}
  	}
  },
  plugins: [require("tailwindcss-animate")],
};
export default config;
