'use client'

import { useState, useEffect } from 'react'
import { Zap, Clock, ShieldAlert, CheckCircle2, User, Users, MapPin, Loader2, Navigation } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const STATUS_BADGES: Record<string, string> = {
  planned: 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/30',
  active: 'bg-amber-500/10 text-amber-400 border border-amber-500/30 animate-pulse',
  completed: 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30',
  failed: 'bg-rose-500/10 text-rose-400 border border-rose-500/30',
}

export default function MissionsPage() {
  const [missions, setMissions] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [updating, setUpdating] = useState<string | null>(null)

  const fetchMissions = async () => {
    const token = localStorage.getItem('aegis_token')
    try {
      const res = await fetch(`${API_URL}/api/v1/missions?limit=50`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      if (res.ok) setMissions(await res.json())
      else setMissions(MOCK_MISSIONS)
    } catch {
      setMissions(MOCK_MISSIONS)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchMissions()
  }, [])

  const advanceMission = async (missionId: string, currentStatus: string) => {
    const token = localStorage.getItem('aegis_token')
    let nextStatus = 'active'
    if (currentStatus === 'active') nextStatus = 'completed'
    else if (currentStatus === 'completed') return // already done

    setUpdating(missionId)
    try {
      const res = await fetch(`${API_URL}/api/v1/missions/${missionId}`, {
        method: 'PATCH',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status: nextStatus }),
      })
      if (res.ok) {
        const updated = await res.json()
        setMissions(prev => prev.map(m => m.id === missionId ? updated : m))
      }
    } catch {} finally {
      setUpdating(null)
    }
  }

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-bold text-white">Rescue Deployments</h1>
        <p className="text-sm text-slate-500 mt-0.5">Tactical operations coordination, rescue teams, and field mission directives.</p>
      </div>

      <div className="grid gap-4">
        {loading ? (
          [...Array(2)].map((_, i) => <div key={i} className="glass-card p-5 skeleton h-48 rounded-xl" />)
        ) : missions.length === 0 ? (
          <div className="glass-card p-12 text-center text-slate-500">
            <Zap className="w-10 h-10 mx-auto mb-3 opacity-30 animate-bounce" />
            <p>No rescue missions currently registered</p>
          </div>
        ) : (
          missions.map((m) => (
            <div key={m.id} className="glass-card p-5 hover:border-white/12 transition-all">
              <div className="flex flex-col lg:flex-row gap-4 justify-between lg:items-start border-b border-white/5 pb-4 mb-4">
                <div>
                  <div className="flex items-center gap-2 flex-wrap mb-1.5">
                    <span className={`severity-badge ${STATUS_BADGES[m.status] || ''}`}>
                      {m.status.toUpperCase()}
                    </span>
                    <span className="text-xs text-slate-500 font-mono">ID: {m.id?.slice(-8)}</span>
                    {m.incident_id && (
                      <span className="text-xs text-slate-600 bg-white/5 px-2 py-0.5 rounded">
                        Incident: {m.incident_id?.slice(-8)}
                      </span>
                    )}
                  </div>
                  <h3 className="font-semibold text-slate-100 text-base">{m.description || 'Disaster Response Operation'}</h3>
                  <div className="flex items-center gap-3 mt-2 text-xs text-slate-500">
                    <span className="flex items-center gap-1">
                      <Clock className="w-3.5 h-3.5" />
                      Started {formatDistanceToNow(new Date(m.created_at), { addSuffix: true })}
                    </span>
                  </div>
                </div>

                {m.status !== 'completed' && (
                  <button
                    onClick={() => advanceMission(m.id, m.status)}
                    disabled={updating === m.id}
                    className={`btn-primary self-start lg:self-auto px-4 py-2 text-xs font-semibold ${
                      m.status === 'active' ? 'bg-emerald-600 hover:bg-emerald-500' : 'bg-indigo-600 hover:bg-indigo-500'
                    }`}
                  >
                    {updating === m.id ? (
                      <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    ) : m.status === 'active' ? (
                      <>
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        Complete Mission
                      </>
                    ) : (
                      <>
                        <Navigation className="w-3.5 h-3.5" />
                        Activate Mission
                      </>
                    )}
                  </button>
                )}
              </div>

              {/* Responders & Tactical Details */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div>
                  <h4 className="text-xs font-semibold text-indigo-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                    <Users className="w-3.5 h-3.5" /> Assigned Responders ({m.responders?.length || 0})
                  </h4>
                  {m.responders && m.responders.length > 0 ? (
                    <div className="flex flex-wrap gap-2">
                      {m.responders.map((r: string, idx: number) => (
                        <div key={idx} className="flex items-center gap-1 bg-white/3 border border-white/5 rounded px-2.5 py-1 text-xs text-slate-300">
                          <User className="w-3 h-3 text-slate-500" />
                          {r}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-xs text-slate-600">No responders assigned yet</p>
                  )}
                </div>

                <div>
                  <h4 className="text-xs font-semibold text-indigo-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                    <Zap className="w-3.5 h-3.5" /> Tactical Steps
                  </h4>
                  {m.rescue_steps && m.rescue_steps.length > 0 ? (
                    <div className="space-y-1.5 max-h-32 overflow-y-auto pr-1">
                      {m.rescue_steps.map((step: any, idx: number) => (
                        <div key={idx} className="flex items-start gap-2 text-xs text-slate-400">
                          <span className={`w-4 h-4 rounded-full flex items-center justify-center font-bold text-[9px] flex-shrink-0 mt-0.5 ${
                            step.status === 'completed' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-slate-700/50 text-slate-500 border border-white/5'
                          }`}>
                            {idx + 1}
                          </span>
                          <span className={step.status === 'completed' ? 'line-through text-slate-600' : 'text-slate-300'}>
                            {step.description}
                          </span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-xs text-slate-600 font-medium">No tactical instructions outlined</p>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

const MOCK_MISSIONS = [
  {
    id: 'mis_mock_001',
    incident_id: 'inc_mock_001',
    description: 'Dharavi Sports Complex Evacuation & Boat Rescue Ops',
    status: 'active',
    responders: ['Mumbai NDRF Team A', 'Local NGO Volunteers', 'BMC Disaster Management Unit'],
    rescue_steps: [
      { order: 1, description: 'Establish temporary command post near Dharavi Sports Complex', status: 'completed' },
      { order: 2, description: 'Deploy inflatable rescue boats to flood sectors', status: 'completed' },
      { order: 3, description: 'Evacuate stranded citizens to Sion relief camp', status: 'pending' },
    ],
    created_at: new Date(Date.now() - 30 * 60000).toISOString(),
  },
  {
    id: 'mis_mock_002',
    incident_id: 'inc_mock_002',
    description: 'Andheri East Debris Search and Rescue Ops',
    status: 'planned',
    responders: ['NDRF Heavy Rescue', 'Mumbai Fire Brigade Squad C'],
    rescue_steps: [
      { order: 1, description: 'Clear building access paths for search gear', status: 'pending' },
      { order: 2, description: 'Deploy canine search unit for trapped signs', status: 'pending' },
    ],
    created_at: new Date(Date.now() - 90 * 60000).toISOString(),
  },
]
