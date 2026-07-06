'use client'

import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import {
  Shield, LayoutDashboard, AlertTriangle, Map, Building2,
  Zap, FileText, Settings, LogOut, ChevronLeft,
} from 'lucide-react'
import { useState } from 'react'
import clsx from 'clsx'

const NAV_ITEMS = [
  { href: '/dashboard',           label: 'Overview',      icon: LayoutDashboard },
  { href: '/dashboard/incidents', label: 'Incidents',     icon: AlertTriangle },
  { href: '/dashboard/map',       label: 'Live Map',      icon: Map },
  { href: '/dashboard/resources', label: 'Resources',     icon: Building2 },
  { href: '/dashboard/missions',  label: 'Missions',      icon: Zap },
  { href: '/dashboard/reports',   label: 'Reports',       icon: FileText },
  { href: '/dashboard/settings',  label: 'Settings',      icon: Settings },
]

export default function Sidebar() {
  const pathname = usePathname()
  const router = useRouter()
  const [collapsed, setCollapsed] = useState(false)

  const handleLogout = () => {
    localStorage.removeItem('aegis_token')
    localStorage.removeItem('aegis_user')
    router.push('/login')
  }

  return (
    <aside className={clsx(
      'relative flex-shrink-0 h-screen flex flex-col border-r transition-all duration-300',
      'border-white/[0.06]',
      collapsed ? 'w-16' : 'w-56',
    )} style={{ background: 'rgba(10,15,30,0.95)' }}>
      {/* Logo */}
      <div className={clsx('flex items-center gap-3 px-4 h-16 border-b border-white/[0.06]', collapsed && 'justify-center px-2')}>
        <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center primary-glow">
          <Shield className="w-4 h-4 text-white" />
        </div>
        {!collapsed && (
          <div>
            <span className="font-bold text-white text-sm tracking-wide">AegisAI</span>
            <p className="text-[10px] text-slate-500 leading-tight">Command Center</p>
          </div>
        )}
      </div>

      {/* Nav Items */}
      <nav className="flex-1 overflow-y-auto py-4 px-2 space-y-1">
        {NAV_ITEMS.map(({ href, label, icon: Icon }) => {
          const active = pathname === href || (href !== '/dashboard' && pathname.startsWith(href))
          return (
            <Link
              key={href}
              href={href}
              title={collapsed ? label : undefined}
              className={clsx(
                'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-150 group',
                collapsed && 'justify-center',
                active
                  ? 'bg-indigo-600/20 text-indigo-400 border border-indigo-500/20'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'
              )}
            >
              <Icon className={clsx('flex-shrink-0', collapsed ? 'w-5 h-5' : 'w-4 h-4')} />
              {!collapsed && label}
              {active && !collapsed && (
                <div className="ml-auto w-1.5 h-1.5 rounded-full bg-indigo-400" />
              )}
            </Link>
          )
        })}
      </nav>

      {/* Logout */}
      <div className="p-2 border-t border-white/[0.06]">
        <button
          onClick={handleLogout}
          title={collapsed ? 'Logout' : undefined}
          className={clsx(
            'w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-slate-500 hover:text-rose-400 hover:bg-rose-500/10 transition-all duration-150',
            collapsed && 'justify-center'
          )}
        >
          <LogOut className="w-4 h-4 flex-shrink-0" />
          {!collapsed && 'Sign Out'}
        </button>
      </div>

      {/* Collapse Toggle */}
      <button
        onClick={() => setCollapsed(!collapsed)}
        className="absolute -right-3 top-[72px] w-6 h-6 rounded-full bg-slate-800 border border-white/10 flex items-center justify-center text-slate-400 hover:text-white hover:border-white/20 transition-all z-10"
      >
        <ChevronLeft className={clsx('w-3 h-3 transition-transform duration-300', collapsed && 'rotate-180')} />
      </button>
    </aside>
  )
}
