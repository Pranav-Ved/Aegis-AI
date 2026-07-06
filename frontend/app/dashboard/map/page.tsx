'use client'

import dynamic from 'next/dynamic'
import { useState, useEffect } from 'react'
import { Map as MapIcon, Layers, AlertTriangle, Building2, Ambulance, RefreshCw } from 'lucide-react'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// Leaflet must be loaded client-side only
const MapContainer = dynamic(() => import('@/components/map/DisasterMap'), {
  ssr: false,
  loading: () => (
    <div className="flex items-center justify-center h-full text-slate-500">
      <div className="text-center">
        <MapIcon className="w-10 h-10 mx-auto mb-3 animate-pulse" />
        <p className="text-sm">Loading map...</p>
      </div>
    </div>
  ),
})

const LAYERS = [
  { id: 'incidents', label: 'Incidents', icon: AlertTriangle, activeClass: 'bg-rose-500/20 text-rose-400 border-rose-500/30' },
  { id: 'shelters', label: 'Shelters', icon: Building2, activeClass: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30' },
  { id: 'hospitals', label: 'Hospitals', icon: Ambulance, activeClass: 'bg-sky-500/20 text-sky-400 border-sky-500/30' },
]

export default function MapPage() {
  const [activeLayers, setActiveLayers] = useState(['incidents', 'shelters', 'hospitals'])
  const [incidents, setIncidents] = useState<any[]>([])
  const [shelters, setShelters] = useState<any[]>([])
  const [hospitals, setHospitals] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [lastRefresh, setLastRefresh] = useState(new Date())

  const fetchData = async () => {
    const token = localStorage.getItem('aegis_token')
    const headers = { Authorization: `Bearer ${token}` }
    setLoading(true)
    try {
      const [incRes, shelRes, hosRes] = await Promise.allSettled([
        fetch(`${API_URL}/api/v1/incidents?limit=50`, { headers }),
        fetch(`${API_URL}/api/v1/resources/shelters`, { headers }),
        fetch(`${API_URL}/api/v1/resources/hospitals`, { headers }),
      ])
      if (incRes.status === 'fulfilled' && incRes.value.ok) setIncidents(await incRes.value.json())
      if (shelRes.status === 'fulfilled' && shelRes.value.ok) setShelters(await shelRes.value.json())
      if (hosRes.status === 'fulfilled' && hosRes.value.ok) setHospitals(await hosRes.value.json())
      setLastRefresh(new Date())
    } catch {}
    finally { setLoading(false) }
  }

  useEffect(() => { fetchData() }, [])

  const toggleLayer = (id: string) => {
    setActiveLayers(prev => prev.includes(id) ? prev.filter(l => l !== id) : [...prev, id])
  }

  return (
    <div className="flex flex-col h-[calc(100vh-7rem)] gap-4">
      {/* Top controls */}
      <div className="flex flex-wrap items-center gap-3">
        <div className="flex items-center gap-2">
          <MapIcon className="w-5 h-5 text-indigo-400" />
          <h1 className="text-xl font-bold text-white">Live Disaster Map</h1>
        </div>

        <div className="flex items-center gap-2 ml-auto flex-wrap">
          {LAYERS.map(layer => (
            <button key={layer.id} onClick={() => toggleLayer(layer.id)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border transition-all ${
                activeLayers.includes(layer.id)
                  ? layer.activeClass
                  : 'bg-white/5 text-slate-500 border-white/10 hover:border-white/20'
              }`}>
              <layer.icon className="w-3.5 h-3.5" />
              {layer.label}
            </button>
          ))}

          <button onClick={fetchData} disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs text-slate-400 border border-white/10 hover:border-white/20 hover:text-slate-200 transition-all">
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>
      </div>

      {/* Map */}
      <div className="flex-1 glass-card overflow-hidden">
        <MapContainer
          incidents={activeLayers.includes('incidents') ? incidents : []}
          shelters={activeLayers.includes('shelters') ? shelters : []}
          hospitals={activeLayers.includes('hospitals') ? hospitals : []}
        />
      </div>

      {/* Legend */}
      <div className="flex flex-wrap gap-4 text-xs text-slate-500">
        <span className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded-full bg-rose-500" />Critical Incident
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded-full bg-amber-500" />High Severity
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded-full bg-emerald-500" />Shelter Open
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded-full bg-sky-500" />Hospital
        </span>
        <span className="ml-auto">Last updated: {lastRefresh.toLocaleTimeString()}</span>
      </div>
    </div>
  )
}
