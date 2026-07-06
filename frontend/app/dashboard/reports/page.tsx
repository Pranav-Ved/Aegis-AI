'use client'

import { useEffect, useState } from 'react'
import { FileText, Download, Loader2, RefreshCw, Plus } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function ReportsPage() {
  const [reports, setReports] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)

  const fetchReports = async () => {
    const token = localStorage.getItem('aegis_token')
    setLoading(true)
    try {
      const res = await fetch(`${API_URL}/api/v1/reports/`, { headers: { Authorization: `Bearer ${token}` } })
      if (res.ok) {
        const data = await res.json()
        setReports(Array.isArray(data) ? data : [])
        if (!Array.isArray(data) || data.length === 0) setReports(MOCK_REPORTS)
      } else {
        setReports(MOCK_REPORTS)
      }
    } catch { setReports(MOCK_REPORTS) }
    finally { setLoading(false) }
  }

  const generateReport = async () => {
    const token = localStorage.getItem('aegis_token')
    setGenerating(true)
    try {
      const res = await fetch(`${API_URL}/api/v1/reports/generate`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ report_type: 'situation', format: 'pdf' }),
      })
      if (res.ok) {
        await fetchReports()
      } else {
        const err = await res.json().catch(() => ({}))
        alert(err.detail || 'Report generation failed. Please try again.')
      }
    } catch (err) {
      console.error('Generate error:', err)
    } finally { setGenerating(false) }
  }

  const downloadReport = async (reportId: string) => {
    const token = localStorage.getItem('aegis_token')
    try {
      const res = await fetch(`${API_URL}/api/v1/reports/${reportId}/download`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok) throw new Error('Download failed')
      const blob = await res.blob()
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `aegisai_report_${reportId}.pdf`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    } catch (err) {
      console.error('Download error:', err)
      alert('Download failed. Please try again.')
    }
  }

  useEffect(() => { fetchReports() }, [])

  return (
    <div className="space-y-5">
      <div className="flex items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Reports</h1>
          <p className="text-sm text-slate-500 mt-0.5">AI-generated disaster situation reports</p>
        </div>
        <div className="flex gap-3 ml-auto">
          <button onClick={fetchReports} className="btn-ghost">
            <RefreshCw className="w-4 h-4" /> Refresh
          </button>
          <button onClick={generateReport} disabled={generating} className="btn-primary">
            {generating ? <Loader2 className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
            Generate Report
          </button>
        </div>
      </div>

      <div className="grid gap-4">
        {loading ? (
          [...Array(3)].map((_, i) => <div key={i} className="glass-card p-5 skeleton h-24 rounded-xl" />)
        ) : reports.length === 0 ? (
          <div className="glass-card p-12 text-center text-slate-500">
            <FileText className="w-10 h-10 mx-auto mb-3 opacity-30" />
            <p>No reports generated yet. Click "Generate Report" to create one.</p>
          </div>
        ) : (
          reports.map(r => (
            <div key={r.id} className="glass-card p-5 flex items-start gap-4 hover:border-white/15 transition-colors">
              <div className="w-10 h-10 rounded-xl bg-indigo-600/20 flex items-center justify-center flex-shrink-0">
                <FileText className="w-5 h-5 text-indigo-400" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap mb-1">
                  <h3 className="font-semibold text-slate-100 capitalize">
                    {r.report_type?.replace('_', ' ')} Report
                  </h3>
                  <span className={`text-xs px-2 py-0.5 rounded-full ${
                    r.status === 'completed' ? 'bg-emerald-500/20 text-emerald-400' :
                    r.status === 'generating' ? 'bg-amber-500/20 text-amber-400' :
                    'bg-slate-600/20 text-slate-400'
                  }`}>{r.status}</span>
                  <span className="text-xs text-slate-600 uppercase font-mono ml-auto">{r.format}</span>
                </div>
                {r.summary && <p className="text-sm text-slate-400 line-clamp-2">{r.summary}</p>}
                <p className="text-xs text-slate-600 mt-1.5">
                  {formatDistanceToNow(new Date(r.created_at), { addSuffix: true })}
                </p>
              </div>
              {r.status === 'completed' && (
                <button
                  onClick={() => downloadReport(r.id)}
                  className="flex-shrink-0 flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs text-indigo-400 border border-indigo-500/30 hover:bg-indigo-500/10 transition-colors"
                >
                  <Download className="w-3.5 h-3.5" /> Download
                </button>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  )
}

const MOCK_REPORTS = [
  {
    id: 'rpt_001', report_type: 'situation', format: 'PDF', status: 'completed',
    summary: 'Comprehensive situation report for the Mumbai flood event. 3 active incidents, 2 shelters operational, rescue teams deployed.',
    created_at: new Date(Date.now() - 2 * 3600000).toISOString(),
  },
]
