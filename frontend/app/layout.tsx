import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  weight: ['300', '400', '500', '600', '700'],
})

export const metadata: Metadata = {
  title: 'AegisAI — Disaster Management Platform',
  description: 'AI-powered multi-agent disaster management and emergency response coordination platform powered by Google ADK and Gemini AI.',
  keywords: ['disaster management', 'emergency response', 'AI agents', 'Google ADK', 'Gemini AI'],
  authors: [{ name: 'AegisAI Team' }],
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <head>
        <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🛡️</text></svg>" />
      </head>
      <body className={`${inter.variable} font-sans antialiased`}>
        {children}
      </body>
    </html>
  )
}
