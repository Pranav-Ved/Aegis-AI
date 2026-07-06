'use client'

import { Building2, Stethoscope, Package } from 'lucide-react'

export default function ResourceStatus({ stats, loading }: { stats: any; loading?: boolean }) {
  const shelterPct = stats?.shelter_occupancy_pct ?? 0
  const hospitalPct = stats?.total_hospital_beds
    ? Math.round(((stats.total_hospital_beds - stats.available_hospital_beds) / stats.total_hospital_beds) * 100)
    : 0

  return (
    <div className="glass-card p-5">
      <div className="flex items-center gap-2 mb-4">
        <Package className="w-4 h-4 text-indigo-400" />
        <h2 className="text-base font-semibold text-slate-100">Resource Status</h2>
      </div>

      {loading ? (
        <div className="space-y-4">
          {[...Array(2)].map((_, i) => <div key={i} className="skeleton h-12 rounded-lg" />)}
        </div>
      ) : (
        <div className="space-y-4">
          {/* Shelters */}
          <ResourceRow
            icon={Building2}
            label="Emergency Shelters"
            current={stats?.available_shelters ?? 0}
            total={stats?.total_shelter_capacity ?? 0}
            pct={shelterPct}
            unit="open"
          />
          {/* Hospitals */}
          <ResourceRow
            icon={Stethoscope}
            label="Hospital Beds"
            current={stats?.available_hospital_beds ?? 0}
            total={stats?.total_hospital_beds ?? 0}
            pct={hospitalPct}
            unit="avail."
            invertColor
          />
        </div>
      )}
    </div>
  )
}

function ResourceRow({ icon: Icon, label, current, total, pct, unit, invertColor }: {
  icon: any; label: string; current: number; total: number;
  pct: number; unit: string; invertColor?: boolean;
}) {
  const colorClass = pct > 80 ? 'bg-rose-500' : pct > 50 ? 'bg-amber-500' : 'bg-emerald-500'

  return (
    <div>
      <div className="flex items-center gap-2 mb-2">
        <Icon className="w-4 h-4 text-slate-400" />
        <span className="text-sm text-slate-300 flex-1">{label}</span>
        <span className="text-sm font-semibold text-white">{current}
          <span className="text-xs text-slate-500 font-normal"> {unit}</span>
        </span>
      </div>
      <div className="h-1.5 rounded-full bg-white/5 overflow-hidden">
        <div className={`h-full rounded-full ${colorClass} transition-all duration-700`}
          style={{ width: `${Math.min(pct, 100)}%` }} />
      </div>
      <div className="flex justify-between mt-1 text-xs text-slate-600">
        <span>{pct}% utilized</span>
        <span>{total} capacity</span>
      </div>
    </div>
  )
}
