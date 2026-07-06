'use client'

import { useState, useEffect } from 'react'
import { Settings, Shield, Cpu, Key, Database, Bell, RefreshCw, CheckCircle2, AlertCircle } from 'lucide-react'

export default function SettingsPage() {
  const [dbMode, setDbMode] = useState('mock')
  const [weatherMode, setWeatherMode] = useState('mock')
  const [mapsMode, setMapsMode] = useState('mock')
  const [geminiStatus, setGeminiStatus] = useState(false)
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)

  useEffect(() => {
    // Load config or mock status
    const timer = setTimeout(() => {
      setDbMode('mock')
      setWeatherMode('mock')
      setMapsMode('mock')
      setGeminiStatus(false)
    }, 300)
    return () => clearTimeout(timer)
  }, [])

  const handleSave = () => {
    setLoading(true)
    setSuccess(false)
    setTimeout(() => {
      setLoading(false)
      setSuccess(true)
      setTimeout(() => setSuccess(false), 2000)
    }, 800)
  }

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h1 className="text-2xl font-bold text-white">System Settings</h1>
        <p className="text-sm text-slate-500 mt-0.5">Configure MCP Server endpoints, API credentials, and default emergency notification thresholds.</p>
      </div>

      {success && (
        <div className="flex items-center gap-2 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 p-3.5 rounded-xl animate-slide-in-bottom">
          <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
          <span className="text-sm">Settings updated successfully!</span>
        </div>
      )}

      {/* Integration Panel */}
      <div className="glass-card p-6 space-y-6">
        <h3 className="text-base font-semibold text-slate-100 flex items-center gap-2">
          <Cpu className="w-5 h-5 text-indigo-400" />
          MCP Servers & API Integrations
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 border-b border-white/5 pb-6">
          <div>
            <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Firestore DB Provider</label>
            <select
              value={dbMode}
              onChange={(e) => setDbMode(e.target.value)}
              className="input-field"
            >
              <option value="mock">In-Memory MockDB (Local Dev)</option>
              <option value="live">Google Cloud Firestore (Live Production)</option>
            </select>
            <p className="text-[11px] text-slate-500 mt-1.5">
              Switching to Live requires setting <code className="bg-white/5 px-1 py-0.5 rounded text-indigo-300">FIRESTORE_PROJECT_ID</code> in env config.
            </p>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Maps & Geocoding</label>
            <select
              value={mapsMode}
              onChange={(e) => setMapsMode(e.target.value)}
              className="input-field"
            >
              <option value="mock">OSM Leaflet + Mock Address Solver</option>
              <option value="google">Google Maps Geocoding API</option>
            </select>
            <p className="text-[11px] text-slate-500 mt-1.5">
              Requires Google Maps Platform key for full directions.
            </p>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Weather Forecast Service</label>
            <select
              value={weatherMode}
              onChange={(e) => setWeatherMode(e.target.value)}
              className="input-field"
            >
              <option value="mock">Static Monsoon Heuristics (Mock)</option>
              <option value="live">OpenWeatherMap API</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">ADK Gemini Engine</label>
            <div className="flex items-center gap-3 h-[42px] border border-white/10 rounded-lg px-4 bg-white/5">
              <Key className="w-4 h-4 text-slate-500" />
              <span className="text-sm text-slate-300 flex-1">Google Gemini API Connection</span>
              <span className={`w-2.5 h-2.5 rounded-full ${geminiStatus ? 'bg-emerald-400' : 'bg-rose-400'}`} />
              <span className={`text-xs font-medium ${geminiStatus ? 'text-emerald-400' : 'text-rose-400'}`}>
                {geminiStatus ? 'Connected' : 'Offline / Mock'}
              </span>
            </div>
          </div>
        </div>

        {/* Notifications & Warning thresholds */}
        <div>
          <h3 className="text-base font-semibold text-slate-100 flex items-center gap-2 mb-4">
            <Bell className="w-5 h-5 text-indigo-400" />
            Alert Dispatch Defaults
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">SMS Notification Threshold</label>
              <select className="input-field">
                <option value="critical">Critical Severity Only (Red Alerts)</option>
                <option value="high">High & Critical (Orange & Red)</option>
                <option value="all">All Incidents</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Government Agency Alerts</label>
              <select className="input-field">
                <option value="auto">Automatic (Orchestrator Dispatched)</option>
                <option value="manual">Manual Approval Needed</option>
              </select>
            </div>
          </div>
        </div>

        {/* Action Button */}
        <div className="flex gap-4 justify-end border-t border-white/5 pt-5">
          <button onClick={handleSave} disabled={loading} className="btn-primary px-6">
            {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : 'Save Configurations'}
          </button>
        </div>
      </div>
    </div>
  )
}
