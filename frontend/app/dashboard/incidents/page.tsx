'use client'

import { useState, useEffect } from 'react'
import { AlertTriangle, Plus, Filter, MapPin, Clock, Search, Loader2, CheckCircle2 } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const SEVERITY_OPTS = ['all', 'critical', 'high', 'medium', 'low']
const TYPE_OPTS = ['all', 'flood', 'earthquake', 'fire', 'cyclone', 'landslide', 'drought', 'medical', 'unknown']

const SEVERITY_STYLES: Record<string, string> = {
  critical: 'severity-critical', high: 'severity-high', medium: 'severity-medium', low: 'severity-low',
}
const TYPE_EMOJI: Record<string, string> = {
  flood: '🌊', earthquake: '⚠️', fire: '🔥', cyclone: '🌀', tsunami: '🌊', landslide: '⛰️', drought: '☀️', medical: '🏥', unknown: '⚡',
}

export default function IncidentsPage() {
  const [incidents, setIncidents] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [severity, setSeverity] = useState('all')
  const [type, setType] = useState('all')
  const [query, setQuery] = useState('')
  const [showForm, setShowForm] = useState(false)

  const fetchIncidents = async () => {
    const token = localStorage.getItem('aegis_token')
    try {
      const params = new URLSearchParams({ limit: '50', skip: '0' })
      if (severity !== 'all') params.set('severity', severity)
      if (type !== 'all') params.set('incident_type', type)
      const res = await fetch(`${API_URL}/api/v1/incidents/?${params}`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (res.ok) {
        setIncidents(await res.json())
      } else if (res.status === 401) {
        localStorage.removeItem('aegis_token')
        window.location.href = '/login'
      }
    } catch { setIncidents(MOCK_INCIDENTS) }
    finally { setLoading(false) }
  }

  useEffect(() => { fetchIncidents() }, [severity, type])

  const filtered = incidents.filter(inc =>
    !query || inc.description.toLowerCase().includes(query.toLowerCase()) ||
    inc.location?.address?.toLowerCase().includes(query.toLowerCase())
  )

  return (
    <div className="space-y-5">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Incidents</h1>
          <p className="text-sm text-slate-500 mt-0.5">{filtered.length} incidents loaded</p>
        </div>
        <button onClick={() => setShowForm(!showForm)} className="btn-primary sm:ml-auto">
          <Plus className="w-4 h-4" />
          Report Incident
        </button>
      </div>

      {/* Intake Form */}
      {showForm && <IncidentForm onClose={() => setShowForm(false)} onCreated={fetchIncidents} />}

      {/* Filters */}
      <div className="glass-card p-4 flex flex-wrap gap-3 items-center">
        <div className="relative flex-1 min-w-48">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
          <input type="text" placeholder="Search incidents..."
            className="input-field pl-9"
            value={query} onChange={e => setQuery(e.target.value)} />
        </div>
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-slate-500" />
          <select className="input-field w-auto" value={severity} onChange={e => setSeverity(e.target.value)}>
            {SEVERITY_OPTS.map(o => <option key={o} value={o}>{o === 'all' ? 'All Severity' : o.charAt(0).toUpperCase() + o.slice(1)}</option>)}
          </select>
          <select className="input-field w-auto" value={type} onChange={e => setType(e.target.value)}>
            {TYPE_OPTS.map(o => <option key={o} value={o}>{o === 'all' ? 'All Types' : o.charAt(0).toUpperCase() + o.slice(1)}</option>)}
          </select>
        </div>
      </div>

      {/* Incidents List */}
      <div className="grid gap-4">
        {loading ? (
          [...Array(3)].map((_, i) => (
            <div key={i} className="glass-card p-5 space-y-3">
              <div className="skeleton h-4 w-24 rounded" />
              <div className="skeleton h-4 w-full rounded" />
              <div className="skeleton h-4 w-2/3 rounded" />
            </div>
          ))
        ) : filtered.length === 0 ? (
          <div className="glass-card p-12 text-center text-slate-500">
            <AlertTriangle className="w-10 h-10 mx-auto mb-3 opacity-30" />
            <p>No incidents found</p>
          </div>
        ) : (
          filtered.map(inc => <IncidentCard key={inc.id} incident={inc} onRefresh={fetchIncidents} />)
        )}
      </div>
    </div>
  )
}

function IncidentCard({ incident: inc, onRefresh }: { incident: any; onRefresh: () => void }) {
  const [resolving, setResolving] = useState(false)
  const token = typeof window !== 'undefined' ? localStorage.getItem('aegis_token') : ''

  const handleResolve = async () => {
    setResolving(true)
    try {
      await fetch(`${API_URL}/api/v1/incidents/${inc.id}/resolve`, {
        method: 'PUT',
        headers: { Authorization: `Bearer ${token}` }
      })
      onRefresh()
    } catch {} finally { setResolving(false) }
  }

  const severityVal = (inc.severity || 'medium').toLowerCase()

  return (
    <div className={`glass-card p-5 hover:border-white/15 transition-all ${severityVal === 'critical' ? 'emergency-glow' : ''}`}>
      <div className="flex items-start gap-4">
        <span className="text-2xl mt-0.5 flex-shrink-0">{TYPE_EMOJI[inc.incident_type] ?? '⚡'}</span>
        <div className="flex-1 min-w-0">
          <div className="flex flex-wrap items-center gap-2 mb-2">
            <span className={`severity-badge ${SEVERITY_STYLES[severityVal] ?? 'severity-medium'}`}>{severityVal.toUpperCase()}</span>
            <span className="text-xs text-slate-500 capitalize">{inc.incident_type}</span>
            <span className={`ml-auto status-${inc.status === 'active' ? 'active' : 'resolved'} severity-badge`}>
              {inc.status}
            </span>
            <span className="text-xs text-slate-600 font-mono">{inc.id?.slice(-8)}</span>
          </div>
          <p className="text-slate-200 text-sm leading-relaxed">{inc.description}</p>
          <div className="flex flex-wrap items-center gap-4 mt-3 text-xs text-slate-500">
            {inc.location?.address && (
              <span className="flex items-center gap-1.5">
                <MapPin className="w-3.5 h-3.5" />{inc.location.address}
              </span>
            )}
            <span className="flex items-center gap-1.5">
              <Clock className="w-3.5 h-3.5" />
              {inc.created_at ? formatDistanceToNow(new Date(inc.created_at), { addSuffix: true }) : 'just now'}
            </span>
          </div>
        </div>
        {inc.status === 'active' && (
          <button onClick={handleResolve} disabled={resolving}
            className="flex-shrink-0 flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs text-emerald-400 border border-emerald-500/30 hover:bg-emerald-500/10 transition-colors">
            {resolving ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <CheckCircle2 className="w-3.5 h-3.5" />}
            Resolve
          </button>
        )}
      </div>
    </div>
  )
}

function IncidentForm({ onClose, onCreated }: { onClose: () => void; onCreated: () => void }) {
  const [form, setForm] = useState({ description: '', incident_type: 'flood', severity: 'medium', lat: '', lng: '', address: '' })
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)
  const token = typeof window !== 'undefined' ? localStorage.getItem('aegis_token') : ''

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      const res = await fetch(`${API_URL}/api/v1/incidents/`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({
          description: form.description,
          incident_type: form.incident_type,
          severity_hint: form.severity,
          location: {
            lat: parseFloat(form.lat) || 19.076,
            lng: parseFloat(form.lng) || 72.877,
            address: form.address || 'Mumbai, India'
          }
        }),
      })
      if (res.ok) { setSuccess(true); setTimeout(() => { onClose(); onCreated() }, 1200) }
    } catch {} finally { setLoading(false) }
  }

  return (
    <div className="glass-card p-5 border-indigo-500/20 animate-slide-in-bottom">
      <h3 className="font-semibold text-slate-100 mb-4">Report New Incident</h3>
      {success && (
        <div className="flex items-center gap-2 text-emerald-400 text-sm mb-4">
          <CheckCircle2 className="w-4 h-4" /> Incident reported successfully!
        </div>
      )}
      <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="md:col-span-2">
          <label className="block text-xs text-slate-400 mb-1.5">Description</label>
          <textarea rows={3} required className="input-field resize-none"
            placeholder="Describe the emergency..."
            value={form.description} onChange={e => setForm({ ...form, description: e.target.value })} />
        </div>
        <div>
          <label className="block text-xs text-slate-400 mb-1.5">Type</label>
          <select className="input-field" value={form.incident_type} onChange={e => setForm({ ...form, incident_type: e.target.value })}>
            {TYPE_OPTS.filter(t => t !== 'all').map(t => <option key={t} value={t}>{t.charAt(0).toUpperCase() + t.slice(1)}</option>)}
          </select>
        </div>
        <div>
          <label className="block text-xs text-slate-400 mb-1.5">Severity</label>
          <select className="input-field" value={form.severity} onChange={e => setForm({ ...form, severity: e.target.value })}>
            {SEVERITY_OPTS.filter(s => s !== 'all').map(s => <option key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</option>)}
          </select>
        </div>
        <div>
          <label className="block text-xs text-slate-400 mb-1.5">Location Address</label>
          <input className="input-field" placeholder="e.g. Dharavi, Mumbai"
            value={form.address} onChange={e => setForm({ ...form, address: e.target.value })} />
        </div>
        <div className="grid grid-cols-2 gap-2">
          <div>
            <label className="block text-xs text-slate-400 mb-1.5">Latitude</label>
            <input className="input-field" placeholder="19.076" value={form.lat} onChange={e => setForm({ ...form, lat: e.target.value })} />
          </div>
          <div>
            <label className="block text-xs text-slate-400 mb-1.5">Longitude</label>
            <input className="input-field" placeholder="72.877" value={form.lng} onChange={e => setForm({ ...form, lng: e.target.value })} />
          </div>
        </div>
        <div className="md:col-span-2 flex gap-3 justify-end">
          <button type="button" onClick={onClose} className="btn-ghost">Cancel</button>
          <button type="submit" disabled={loading} className="btn-primary">
            {loading ? <><Loader2 className="w-4 h-4 animate-spin" />Processing...</> : 'Submit Incident'}
          </button>
        </div>
      </form>
    </div>
  )
}

const MOCK_INCIDENTS = [
  {
    id: 'inc_mock_001', description: 'Severe flooding in Dharavi. Multiple families trapped on rooftops. Water level 4 feet and rising.',
    incident_type: 'flood', severity: 'critical', status: 'active',
    location: { lat: 19.0380, lng: 72.8526, address: 'Dharavi, Mumbai' },
    created_at: new Date(Date.now() - 45 * 60000).toISOString(),
  },
  {
    id: 'inc_mock_002', description: 'Building collapse in Andheri East. Estimated 12 people trapped.',
    incident_type: 'earthquake', severity: 'high', status: 'active',
    location: { lat: 19.1196, lng: 72.8680, address: 'Andheri East, Mumbai' },
    created_at: new Date(Date.now() - 2 * 3600000).toISOString(),
  },
]
