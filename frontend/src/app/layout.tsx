import type { Metadata } from 'next'
import { Inter, Outfit } from 'next/font/google'
import './globals.css'
import { Providers } from '@/components/providers'
import { Toaster } from 'react-hot-toast'

const inter = Inter({
    subsets: ['latin'],
    variable: '--font-inter',
})

const outfit = Outfit({
    subsets: ['latin'],
    variable: '--font-outfit',
})

export const metadata: Metadata = {
    title: 'FinBuddy - AI Financial Assistant',
    description: 'Your intelligent financial coach powered by AI',
    keywords: ['finance', 'ai', 'assistant', 'budgeting', 'investments'],
}

export default function RootLayout({
    children,
}: {
    children: React.ReactNode
}) {
    return (
        <html lang="en" className={`${inter.variable} ${outfit.variable}`}>
            <body className="min-h-screen bg-mono-50">
                <Providers>
                    {children}
                    <Toaster
                        position="top-right"
                        toastOptions={{
                            duration: 4000,
                            style: {
                                background: 'rgba(255, 255, 255, 0.9)',
                                backdropFilter: 'blur(15px)',
                                color: '#111111',
                                border: '1px solid rgba(0, 0, 0, 0.06)',
                                borderRadius: '12px',
                                boxShadow: '0 8px 32px 0 rgba(0, 0, 0, 0.08)',
                            },
                            success: {
                                iconTheme: {
                                    primary: '#111111',
                                    secondary: '#FFFFFF',
                                },
                            },
                            error: {
                                iconTheme: {
                                    primary: '#404040',
                                    secondary: '#FFFFFF',
                                },
                            },
                        }}
                    />
                </Providers>
            </body>
        </html>
    )
}
