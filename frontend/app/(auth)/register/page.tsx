'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Shield, Mail, Lock, User, Phone, AlertTriangle, Loader2 } from 'lucide-react'

export default function RegisterPage() {
  const router = useRouter()
  const [formData, setFormData] = useState({ name: '', email: '', password: '', phone: '', role: 'citizen' })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const res = await fetch(`${API_URL}/api/v1/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      })
      if (!res.ok) {
        const data = await res.json()
        throw new Error(data.detail || 'Registration failed')
      }
      router.push('/login?registered=true')
    } catch (err: any) {
      setError(err.message || 'Registration failed.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen gradient-bg flex items-center justify-center p-4">
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 right-1/4 w-96 h-96 bg-indigo-600/10 rounded-full blur-3xl" />
      </div>
      <div className="relative w-full max-w-md">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-indigo-600 mb-4 primary-glow">
            <Shield className="w-9 h-9 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-white">Join AegisAI</h1>
          <p className="text-slate-400 mt-1 text-sm">Register as a responder or citizen</p>
        </div>

        <div className="glass-card p-8">
          <h2 className="text-xl font-semibold text-slate-100 mb-6">Create an Account</h2>

          {error && (
            <div className="mb-5 flex items-start gap-3 p-3.5 rounded-lg bg-rose-500/10 border border-rose-500/30">
              <AlertTriangle className="w-5 h-5 text-rose-400 flex-shrink-0 mt-0.5" />
              <p className="text-rose-300 text-sm">{error}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Full Name</label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                <input type="text" placeholder="Your full name" required className="input-field pl-10"
                  value={formData.name} onChange={e => setFormData({ ...formData, name: e.target.value })} />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Email</label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                <input type="email" placeholder="you@example.com" required className="input-field pl-10"
                  value={formData.email} onChange={e => setFormData({ ...formData, email: e.target.value })} />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Phone (Optional)</label>
              <div className="relative">
                <Phone className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                <input type="tel" placeholder="+91 98765 00000" className="input-field pl-10"
                  value={formData.phone} onChange={e => setFormData({ ...formData, phone: e.target.value })} />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Password</label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                <input type="password" placeholder="At least 8 characters" required className="input-field pl-10"
                  value={formData.password} onChange={e => setFormData({ ...formData, password: e.target.value })} />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Role</label>
              <select className="input-field"
                value={formData.role} onChange={e => setFormData({ ...formData, role: e.target.value })}>
                <option value="citizen">Citizen</option>
                <option value="volunteer">Volunteer Responder</option>
                <option value="ngo">NGO Worker</option>
              </select>
            </div>

            <button type="submit" disabled={loading} className="btn-primary w-full py-3 mt-2">
              {loading ? <><Loader2 className="w-4 h-4 animate-spin" />Creating account...</> : 'Create Account'}
            </button>
          </form>

          <p className="text-center text-sm text-slate-500 mt-5">
            Already registered?{' '}
            <Link href="/login" className="text-indigo-400 hover:text-indigo-300 transition-colors">Sign in</Link>
          </p>
        </div>
      </div>
    </div>
  )
}
