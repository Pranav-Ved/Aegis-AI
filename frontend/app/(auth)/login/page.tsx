'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Shield, Mail, Lock, Eye, EyeOff, AlertTriangle, Loader2, Zap } from 'lucide-react'

export default function LoginPage() {
  const router = useRouter()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [demoLoading, setDemoLoading] = useState(false)
  const [error, setError] = useState('')

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const res = await fetch(`${API_URL}/api/v1/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      })
      if (!res.ok) {
        const data = await res.json()
        throw new Error(data.detail || 'Invalid credentials')
      }
      const data = await res.json()
      localStorage.setItem('aegis_token', data.access_token)
      localStorage.setItem('aegis_user', JSON.stringify(data.user))
      router.push('/dashboard')
    } catch (err: any) {
      setError(err.message || 'Login failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleDemoLogin = async () => {
    setError('')
    setDemoLoading(true)
    try {
      const res = await fetch(`${API_URL}/api/v1/auth/demo-login`)
      if (!res.ok) throw new Error('Demo login unavailable')
      const data = await res.json()
      localStorage.setItem('aegis_token', data.access_token)
      localStorage.setItem('aegis_user', JSON.stringify(data.user))
      router.push('/dashboard')
    } catch (err: any) {
      setError(err.message || 'Demo login failed.')
    } finally {
      setDemoLoading(false)
    }
  }

  return (
    <div className="min-h-screen gradient-bg flex items-center justify-center p-4">
      {/* Background decorative elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-indigo-600/10 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-rose-600/10 rounded-full blur-3xl" />
      </div>

      <div className="relative w-full max-w-md">
        {/* Logo & Brand */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-indigo-600 mb-4 primary-glow">
            <Shield className="w-9 h-9 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-white tracking-tight">AegisAI</h1>
          <p className="text-slate-400 mt-1 text-sm">Shielding Lives with Intelligent Response</p>
        </div>

        {/* Login Card */}
        <div className="glass-card p-8">
          <h2 className="text-xl font-semibold text-slate-100 mb-6">Sign in to Command Center</h2>

          {error && (
            <div className="mb-5 flex items-start gap-3 p-3.5 rounded-lg bg-rose-500/10 border border-rose-500/30 animate-slide-in-bottom">
              <AlertTriangle className="w-5 h-5 text-rose-400 flex-shrink-0 mt-0.5" />
              <p className="text-rose-300 text-sm">{error}</p>
            </div>
          )}

          <form onSubmit={handleLogin} className="space-y-5">
            {/* Email Field */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Email Address</label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="admin@aegisai.com"
                  required
                  className="input-field pl-10"
                />
              </div>
            </div>

            {/* Password Field */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Password</label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                  className="input-field pl-10 pr-10"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 transition-colors"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            {/* Login Button */}
            <button type="submit" disabled={loading} className="btn-primary w-full py-3">
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Authenticating...
                </>
              ) : (
                'Sign In'
              )}
            </button>
          </form>

          {/* Divider */}
          <div className="flex items-center gap-3 my-5">
            <div className="flex-1 h-px bg-white/10" />
            <span className="text-xs text-slate-500">or</span>
            <div className="flex-1 h-px bg-white/10" />
          </div>

          {/* Demo Login Button */}
          <button
            onClick={handleDemoLogin}
            disabled={demoLoading}
            className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-lg border border-amber-500/30 bg-amber-500/10 text-amber-400 hover:bg-amber-500/20 transition-all duration-200 font-medium text-sm"
          >
            {demoLoading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Zap className="w-4 h-4" />
            )}
            Demo Login (Admin)
          </button>

          <p className="text-center text-sm text-slate-500 mt-5">
            Don&apos;t have an account?{' '}
            <Link href="/register" className="text-indigo-400 hover:text-indigo-300 transition-colors">
              Register here
            </Link>
          </p>
        </div>

        {/* Footer */}
        <p className="text-center text-xs text-slate-600 mt-6">
          Powered by Google ADK + Gemini AI · AegisAI v1.0
        </p>
      </div>
    </div>
  )
}
