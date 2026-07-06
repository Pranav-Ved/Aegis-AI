'use client'

import { AlertTriangle, MapPin, Clock } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'

interface Incident {
  id: string
  description: string
  incident_type: string
  severity: string
  status: string
  location: { address?: string; lat: number; lng: number }
  created_at: string
}

const SEVERITY_STYLES: Record<string, string> = {
  critical: 'severity-critical',
  high: 'severity-high',
  medium: 'severity-medium',
  low: 'severity-low',
}

const TYPE_EMOJI: Record<string, string> = {
  flood: '🌊', earthquake: '⚠️', fire: '🔥', cyclone: '🌀',
  tsunami: '🌊', landslide: '⛰️', drought: '☀️', medical: '🏥', unknown: '⚡',
}

export default function AlertFeed({ incidents, loading }: { incidents: Incident[]; loading?: boolean }) {
  if (loading) {
    return (
      <div className="space-y-3">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="space-y-2 p-3 rounded-lg bg-white/3">
            <div className="skeleton h-4 w-3/4 rounded" />
            <div className="skeleton h-3 w-1/2 rounded" />
          </div>
        ))}
      </div>
    )
  }

  if (!incidents.length) {
    return (
      <div className="flex flex-col items-center justify-center py-10 text-slate-500">
        <AlertTriangle className="w-8 h-8 mb-2 opacity-30" />
        <p className="text-sm">No active incidents</p>
      </div>
    )
  }

  return (
    <div className="space-y-3 max-h-80 overflow-y-auto pr-1">
      {incidents.map((inc) => (
        <div key={inc.id}
          className={`relative p-4 rounded-xl border bg-white/3 hover:bg-white/5 transition-colors cursor-pointer ${
            inc.severity === 'critical' ? 'border-rose-500/30 emergency-glow' : 'border-white/8'
          }`}>
          <div className="flex items-start gap-3">
            <span className="text-xl flex-shrink-0 mt-0.5">
              {TYPE_EMOJI[inc.incident_type] ?? '⚡'}
            </span>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 flex-wrap mb-1">
                <span className={`severity-badge ${SEVERITY_STYLES[inc.severity] ?? 'severity-medium'}`}>
                  {inc.severity.toUpperCase()}
                </span>
                <span className="text-xs text-slate-500 capitalize">{inc.incident_type}</span>
                {inc.status === 'active' && (
                  <span className="ml-auto flex items-center gap-1 text-xs text-emerald-400">
                    <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                    Active
                  </span>
                )}
              </div>
              <p className="text-sm text-slate-300 leading-relaxed line-clamp-2">{inc.description}</p>
              <div className="flex items-center gap-3 mt-2 text-xs text-slate-500">
                {inc.location?.address && (
                  <span className="flex items-center gap-1">
                    <MapPin className="w-3 h-3" />{inc.location.address}
                  </span>
                )}
                <span className="flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  {formatDistanceToNow(new Date(inc.created_at), { addSuffix: true })}
                </span>
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
