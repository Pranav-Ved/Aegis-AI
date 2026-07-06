'use client'

import { useState, useEffect, useRef } from 'react'
import { Bell, Search, Sun, Moon, AlertTriangle, Check, MailOpen } from 'lucide-react'
import { format } from 'date-fns'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function Header() {
  const [dark, setDark] = useState(true)
  const [time, setTime] = useState(new Date())
  const [notifCount, setNotifCount] = useState(0)
  const [notifications, setNotifications] = useState<any[]>([])
  const [showDropdown, setShowDropdown] = useState(false)
  const [user, setUser] = useState<{ name?: string; role?: string } | null>(null)
  const dropdownRef = useRef<HTMLDivElement>(null)

  const fetchNotifications = async () => {
    const token = localStorage.getItem('aegis_token')
    if (!token) return
    try {
      const res = await fetch(`${API_URL}/api/v1/dashboard/notifications`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      if (res.ok) {
        const data = await res.json()
        setNotifications(data.notifications || [])
        setNotifCount(data.unread_count ?? 0)
      } else {
        setNotifications(MOCK_NOTIFICATIONS)
        setNotifCount(MOCK_NOTIFICATIONS.filter(n => n.status === 'unread').length)
      }
    } catch {
      setNotifications(MOCK_NOTIFICATIONS)
      setNotifCount(MOCK_NOTIFICATIONS.filter(n => n.status === 'unread').length)
    }
  }

  const markAsRead = async (id: string) => {
    const token = localStorage.getItem('aegis_token')
    if (!token) return
    try {
      const res = await fetch(`${API_URL}/api/v1/dashboard/notifications/${id}/read`, {
        method: 'PATCH',
        headers: { Authorization: `Bearer ${token}` }
      })
      if (res.ok) {
        setNotifications(prev => prev.map(n => n.id === id ? { ...n, status: 'read' } : n))
        setNotifCount(prev => Math.max(0, prev - 1))
      }
    } catch {
      // Fallback local update
      setNotifications(prev => prev.map(n => n.id === id ? { ...n, status: 'read' } : n))
      setNotifCount(prev => Math.max(0, prev - 1))
    }
  }

  const markAllAsRead = async () => {
    const token = localStorage.getItem('aegis_token')
    if (!token) return
    try {
      // Mark all in state
      const unreadIds = notifications.filter(n => n.status === 'unread').map(n => n.id)
      await Promise.all(unreadIds.map(id => 
        fetch(`${API_URL}/api/v1/dashboard/notifications/${id}/read`, {
          method: 'PATCH',
          headers: { Authorization: `Bearer ${token}` }
        })
      ))
      setNotifications(prev => prev.map(n => ({ ...n, status: 'read' })))
      setNotifCount(0)
    } catch {
      setNotifications(prev => prev.map(n => ({ ...n, status: 'read' })))
      setNotifCount(0)
    }
  }

  useEffect(() => {
    const raw = localStorage.getItem('aegis_user')
    if (raw) setUser(JSON.parse(raw))
    const tick = setInterval(() => setTime(new Date()), 1000)
    
    fetchNotifications()
    const interval = setInterval(fetchNotifications, 10000)

    // Handle clicks outside of dropdown to close it
    const handleOutsideClick = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setShowDropdown(false)
      }
    }
    document.addEventListener('mousedown', handleOutsideClick)

    return () => {
      clearInterval(tick)
      clearInterval(interval)
      document.removeEventListener('mousedown', handleOutsideClick)
    }
  }, [])

  const toggleTheme = () => {
    setDark(!dark)
    document.documentElement.classList.toggle('light', dark)
  }

  return (
    <header className="relative flex items-center justify-between h-16 px-5 border-b border-white/[0.06] flex-shrink-0 z-50"
      style={{ background: 'rgba(10,15,30,0.9)', backdropFilter: 'blur(12px)' }}>

      {/* Left: Clock */}
      <div className="flex items-center gap-3">
        <div className="text-sm">
          <span className="font-semibold text-slate-100">{format(time, 'HH:mm:ss')}</span>
          <span className="text-slate-500 ml-2 text-xs">{format(time, 'dd MMM yyyy')}</span>
        </div>
        <div className="hidden md:flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20">
          <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
          <span className="text-xs text-emerald-400 font-medium">LIVE</span>
        </div>
      </div>

      {/* Center: Search */}
      <div className="hidden md:flex items-center gap-2 bg-white/5 border border-white/10 rounded-lg px-3 py-2 w-64 focus-within:border-indigo-500 transition-colors">
        <Search className="w-4 h-4 text-slate-500 flex-shrink-0" />
        <input
          type="text"
          placeholder="Search incidents, resources..."
          className="bg-transparent text-sm text-slate-300 placeholder-slate-600 focus:outline-none flex-1 min-w-0"
        />
      </div>

      {/* Right: Actions + User */}
      <div className="flex items-center gap-2 relative">
        {/* Notifications Button */}
        <div ref={dropdownRef} className="relative">
          <button 
            onClick={() => setShowDropdown(!showDropdown)}
            className={`relative w-9 h-9 rounded-lg flex items-center justify-center transition-colors ${
              showDropdown ? 'bg-white/10 text-white' : 'text-slate-400 hover:bg-white/5 hover:text-slate-200'
            }`}
          >
            <Bell className="w-4 h-4" />
            {notifCount > 0 && (
              <span className="absolute top-1.5 right-1.5 w-4 h-4 rounded-full bg-rose-500 text-white text-[10px] font-bold flex items-center justify-center">
                {notifCount}
              </span>
            )}
          </button>

          {/* Notifications Dropdown Panel */}
          {showDropdown && (
            <div className="absolute right-0 mt-2 w-80 rounded-xl border border-white/10 shadow-2xl overflow-hidden z-50 bg-slate-900/95 backdrop-blur-xl animate-fade-in">
              <div className="p-3 border-b border-white/5 flex items-center justify-between">
                <span className="font-semibold text-xs text-slate-200">Alert Center</span>
                {notifCount > 0 && (
                  <button 
                    onClick={markAllAsRead}
                    className="text-[10px] text-indigo-400 hover:text-indigo-300 flex items-center gap-1 font-medium"
                  >
                    <Check className="w-3 h-3" /> Mark all read
                  </button>
                )}
              </div>
              <div className="max-h-64 overflow-y-auto divide-y divide-white/5">
                {notifications.length === 0 ? (
                  <div className="p-8 text-center text-xs text-slate-500">
                    <MailOpen className="w-6 h-6 mx-auto mb-2 opacity-30" />
                    No notifications
                  </div>
                ) : (
                  notifications.map((n) => (
                    <div 
                      key={n.id} 
                      onClick={() => markAsRead(n.id)}
                      className={`p-3 text-left transition-colors cursor-pointer hover:bg-white/5 ${
                        n.status === 'unread' ? 'bg-indigo-500/5' : ''
                      }`}
                    >
                      <div className="flex items-start gap-2.5">
                        <div className={`w-1.5 h-1.5 rounded-full mt-1.5 flex-shrink-0 ${
                          n.status === 'unread' ? 'bg-indigo-400' : 'bg-transparent'
                        }`} />
                        <div className="flex-1 min-w-0">
                          <p className="text-xs text-slate-200 leading-normal break-words">{n.message}</p>
                          <span className="text-[10px] text-slate-500 block mt-1">
                            {format(new Date(n.created_at || Date.now()), 'HH:mm • dd MMM')}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>

        {/* Theme Toggle */}
        <button onClick={toggleTheme}
          className="w-9 h-9 rounded-lg hover:bg-white/5 flex items-center justify-center text-slate-400 hover:text-slate-200 transition-colors">
          {dark ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
        </button>

        {/* User Avatar */}
        <div className="flex items-center gap-2 pl-2 border-l border-white/10 ml-1">
          <div className="w-8 h-8 rounded-full bg-indigo-600/50 border border-indigo-500/30 flex items-center justify-center text-sm font-semibold text-indigo-300">
            {user?.name?.[0]?.toUpperCase() ?? 'A'}
          </div>
          <div className="hidden sm:block">
            <p className="text-sm font-medium text-slate-200 leading-tight">{user?.name ?? 'Admin'}</p>
            <p className="text-xs text-slate-500 capitalize leading-tight">{user?.role ?? 'admin'}</p>
          </div>
        </div>
      </div>
    </header>
  )
}

const MOCK_NOTIFICATIONS = [
  { id: 'n1', message: '[System Alert] Heavy rainfall warning issued for coastal districts.', status: 'unread', created_at: new Date(Date.now() - 300000).toISOString() },
  { id: 'n2', message: '[System Alert] BKC Emergency Camp is now at capacity.', status: 'unread', created_at: new Date(Date.now() - 1200000).toISOString() },
  { id: 'n3', message: '[System Alert] Rescue mission status updated to completed.', status: 'read', created_at: new Date(Date.now() - 3600000).toISOString() },
]
