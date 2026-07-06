'use client'

import { useEffect, useState } from 'react'
import { Activity, AlertTriangle, Building2, Target, Cpu, CheckCircle2, Clock, XCircle } from 'lucide-react'
import StatsCard from '@/components/dashboard/StatsCard'
import AlertFeed from '@/components/dashboard/AlertFeed'
import AIStatusBanner from '@/components/dashboard/AIStatusBanner'
import WeatherPanel from '@/components/dashboard/WeatherPanel'
import ResourceStatus from '@/components/dashboard/ResourceStatus'
import MissionTimeline from '@/components/dashboard/MissionTimeline'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const AGENTS = [
  { key: 'emergency_intake', label: 'Emergency Intake' },
  { key: 'disaster_detection', label: 'Disaster Detection' },
  { key: 'location_intelligence', label: 'Location Intelligence' },
  { key: 'resource_coordination', label: 'Resource Coordination' },
  { key: 'rescue_planning', label: 'Rescue Planning' },
  { key: 'notification', label: 'Notification Agent' },
  { key: 'report_generation', label: 'Report Generation' },
]

export default function DashboardPage() {
  const [stats, setStats] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [agentStatuses, setAgentStatuses] = useState<Record<string, string>>({})

  const fetchStats = async () => {
    try {
      const token = localStorage.getItem('aegis_token')
      const res = await fetch(`${API_URL}/api/v1/dashboard/stats`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (res.ok) {
        const data = await res.json()
        setStats(data)
      } else {
        // Use mock stats if backend returns error (demo mode)
        if (!stats) setStats(MOCK_STATS)
      }
    } catch {
      // Backend not running - show mock data
      if (!stats) setStats(MOCK_STATS)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchStats()
    const interval = setInterval(fetchStats, 30000)

    // Setup WebSocket for live agent updates
    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'
    let ws: WebSocket
    try {
      ws = new WebSocket(`${wsUrl}/ws/dashboard`)
      ws.onmessage = (event) => {
        const msg = JSON.parse(event.data)
        if (msg.event === 'agent_progress') {
          setAgentStatuses(prev => ({ ...prev, [msg.agent]: msg.status }))
        }
        if (msg.event === 'workflow_completed') {
          fetchStats()
          setAgentStatuses({})
        }
      }
    } catch {}

    return () => {
      clearInterval(interval)
      ws?.close()
    }
  }, [])

  const getAgentStatusIcon = (status: string) => {
    switch (status) {
      case 'running': return <Clock className="w-3.5 h-3.5 text-amber-400 animate-spin" />
      case 'completed': return <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
      case 'failed': return <XCircle className="w-3.5 h-3.5 text-rose-400" />
      default: return <div className="w-3.5 h-3.5 rounded-full border border-slate-600" />
    }
  }

  return (
    <div className="space-y-5">
      {/* AI Unavailable Banner */}
      {stats && !stats.ai_available && (
        <AIStatusBanner
          aiAvailable={stats.ai_available}
          dbMode={stats.db_mode}
          notificationsMode={stats.notifications_mode}
        />
      )}

      {/* Row 1: KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatsCard
          title="Active Incidents"
          value={stats?.active_incidents ?? '—'}
          icon={AlertTriangle}
          iconColor="text-rose-400"
          loading={loading}
          trend={stats?.active_incidents > 2 ? stats.active_incidents : undefined}
          trendType="up"
        />
        <StatsCard
          title="Active Missions"
          value={stats?.active_missions ?? '—'}
          icon={Target}
          iconColor="text-indigo-400"
          loading={loading}
        />
        <StatsCard
          title="Open Shelters"
          value={stats?.available_shelters ?? '—'}
          unit={`/ ${stats?.total_shelter_capacity ?? '—'} cap.`}
          icon={Building2}
          iconColor="text-emerald-400"
          loading={loading}
        />
        <StatsCard
          title="Critical Alerts"
          value={stats?.critical_incidents ?? '—'}
          icon={Activity}
          iconColor="text-amber-400"
          loading={loading}
        />
      </div>

      {/* Row 2: Alert Feed + Agent Pipeline */}
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-5">
        {/* Alert Feed */}
        <div className="lg:col-span-3 glass-card p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-base font-semibold text-slate-100">Live Incident Feed</h2>
            <span className="text-xs text-slate-500">{stats?.total_incidents ?? 0} total</span>
          </div>
          <AlertFeed incidents={stats?.recent_incidents ?? []} loading={loading} />
        </div>

        {/* Agent Pipeline Status */}
        <div className="lg:col-span-2 glass-card p-5">
          <div className="flex items-center gap-2 mb-4">
            <Cpu className="w-4 h-4 text-indigo-400" />
            <h2 className="text-base font-semibold text-slate-100">Agent Pipeline</h2>
          </div>
          <div className="space-y-2.5">
            {AGENTS.map(agent => (
              <div key={agent.key} className="flex items-center gap-3 py-1.5 px-3 rounded-lg hover:bg-white/5 transition-colors">
                {getAgentStatusIcon(agentStatuses[agent.key] || 'idle')}
                <span className="text-sm text-slate-300 flex-1">{agent.label}</span>
                <span className={`text-xs capitalize px-2 py-0.5 rounded-full ${
                  agentStatuses[agent.key] === 'running' ? 'bg-amber-500/20 text-amber-400' :
                  agentStatuses[agent.key] === 'completed' ? 'bg-emerald-500/20 text-emerald-400' :
                  agentStatuses[agent.key] === 'failed' ? 'bg-rose-500/20 text-rose-400' :
                  'bg-slate-700/50 text-slate-500'
                }`}>
                  {agentStatuses[agent.key] || 'idle'}
                </span>
              </div>
            ))}
          </div>
          {!stats?.ai_available && (
            <p className="mt-4 text-xs text-indigo-400/70 text-center border-t border-white/5 pt-3">
              🛡 Active in Demo Mode
            </p>
          )}
        </div>
      </div>

      {/* Row 3: Weather + Resources + Timeline */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        <WeatherPanel />
        <ResourceStatus stats={stats} loading={loading} />
        <MissionTimeline />
      </div>

      {/* System Status Bar */}
      <div className="glass-card px-5 py-3 flex flex-wrap items-center gap-4 text-xs text-slate-500">
        <StatusDot label="Gemini AI" active={stats?.ai_available} />
        <StatusDot label="Database" active={true} mode={stats?.db_mode} />
        <StatusDot label="Maps" active={stats?.maps_mode === 'google'} mode={stats?.maps_mode} />
        <StatusDot label="Weather" active={stats?.weather_mode === 'live'} mode={stats?.weather_mode} />
        <StatusDot label="SMS" active={stats?.notifications_mode === 'live'} mode={stats?.notifications_mode} />
      </div>
    </div>
  )
}

function StatusDot({ label, active, mode }: { label: string; active?: boolean; mode?: string }) {
  return (
    <div className="flex items-center gap-1.5">
      <div className={`w-2 h-2 rounded-full ${active ? 'bg-emerald-400' : 'bg-amber-400'}`} />
      <span className="text-slate-400">{label}:</span>
      <span className={active ? 'text-emerald-400' : 'text-amber-400'}>{mode || (active ? 'live' : 'mock')}</span>
    </div>
  )
}

const MOCK_STATS = {
  total_incidents: 20,
  active_incidents: 14,
  resolved_incidents: 3,
  critical_incidents: 8,
  total_missions: 10,
  active_missions: 6,
  available_shelters: 18,
  total_shelter_capacity: 9500,
  shelter_occupancy_pct: 52.3,
  total_hospital_beds: 2800,
  available_hospital_beds: 630,
  recent_incidents: [
    {
      id: 'inc_001',
      description: 'Severe flooding in Dharavi area. Multiple families stranded on rooftops.',
      incident_type: 'flood',
      severity: 'critical',
      status: 'active',
      location: { lat: 19.0380, lng: 72.8526, address: 'Dharavi, Mumbai' },
      created_at: new Date(Date.now() - 3600000).toISOString(),
    },
    {
      id: 'inc_002',
      description: 'Chemical gas leak in Rohini Industrial Area. Residents evacuating.',
      incident_type: 'chemical_leak',
      severity: 'critical',
      status: 'active',
      location: { lat: 28.6139, lng: 77.2090, address: 'Rohini, Delhi' },
      created_at: new Date(Date.now() - 7200000).toISOString(),
    },
    {
      id: 'inc_003',
      description: 'Building collapse at Secunderabad commercial complex. Rescue teams on site.',
      incident_type: 'building_collapse',
      severity: 'critical',
      status: 'active',
      location: { lat: 17.3850, lng: 78.4867, address: 'Secunderabad, Hyderabad' },
      created_at: new Date(Date.now() - 10800000).toISOString(),
    },
    {
      id: 'inc_004',
      description: 'Cyclone damage reported in Kolkata central. Power lines down.',
      incident_type: 'cyclone',
      severity: 'high',
      status: 'resolved',
      location: { lat: 22.5726, lng: 88.3639, address: 'Kolkata, West Bengal' },
      created_at: new Date(Date.now() - 86400000).toISOString(),
    },
    {
      id: 'inc_005',
      description: 'Velachery waterlogging. Elderly residents need urgent evacuation.',
      incident_type: 'flood',
      severity: 'high',
      status: 'active',
      location: { lat: 13.0827, lng: 80.2707, address: 'Velachery, Chennai' },
      created_at: new Date(Date.now() - 14400000).toISOString(),
    },
  ],
  ai_available: false,
  db_mode: 'mock',
  notifications_mode: 'mock',
  maps_mode: 'mock',
  weather_mode: 'mock',
}
