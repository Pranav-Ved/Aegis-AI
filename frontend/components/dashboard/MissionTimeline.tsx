'use client'

import { CheckCircle2, Clock, AlertTriangle } from 'lucide-react'

const MOCK_TIMELINE = [
  { time: '18:42', event: 'Flood alert received – Dharavi', type: 'alert' },
  { time: '18:43', event: 'Emergency Intake Agent activated', type: 'agent' },
  { time: '18:44', event: 'Disaster Detection analysis complete', type: 'agent' },
  { time: '18:45', event: 'Location Intelligence mapping started', type: 'agent' },
  { time: '18:46', event: 'Resource Coordination – 3 shelters identified', type: 'success' },
  { time: '18:47', event: 'Rescue teams dispatched', type: 'success' },
]

const TYPE_ICON: Record<string, JSX.Element> = {
  alert: <AlertTriangle className="w-3.5 h-3.5 text-amber-400 flex-shrink-0" />,
  agent: <Clock className="w-3.5 h-3.5 text-indigo-400 flex-shrink-0" />,
  success: <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />,
}

export default function MissionTimeline() {
  return (
    <div className="glass-card p-5">
      <h2 className="text-base font-semibold text-slate-100 mb-4">Mission Timeline</h2>
      <div className="relative pl-5 space-y-3">
        <div className="absolute left-[7px] top-2 bottom-2 w-px bg-white/8" />
        {MOCK_TIMELINE.map((item, i) => (
          <div key={i} className="flex items-start gap-2.5 relative">
            <div className="absolute -left-5 top-0.5 w-3.5 h-3.5 flex items-center justify-center">
              {TYPE_ICON[item.type]}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm text-slate-300 leading-relaxed">{item.event}</p>
              <p className="text-xs text-slate-600 mt-0.5">{item.time}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
