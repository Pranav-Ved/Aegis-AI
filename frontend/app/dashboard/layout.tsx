'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Sidebar from '@/components/Sidebar'
import Header from '@/components/Header'

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter()

  useEffect(() => {
    const token = localStorage.getItem('aegis_token')
    if (!token) router.push('/login')
  }, [router])

  return (
    <div className="flex h-screen overflow-hidden" style={{ background: 'var(--background)' }}>
      <Sidebar />
      <div className="flex flex-col flex-1 overflow-hidden min-w-0">
        <Header />
        <main className="flex-1 overflow-auto p-4 lg:p-6">
          <div className="animate-fade-in max-w-screen-2xl mx-auto">
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}
