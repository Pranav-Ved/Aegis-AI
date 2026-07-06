'use client'

import { LucideIcon, TrendingUp, TrendingDown } from 'lucide-react'
import clsx from 'clsx'

interface StatsCardProps {
  title: string
  value: string | number
  unit?: string
  icon: LucideIcon
  iconColor?: string
  loading?: boolean
  trend?: number
  trendType?: 'up' | 'down'
}

export default function StatsCard({
  title, value, unit, icon: Icon, iconColor = 'text-indigo-400',
  loading, trend, trendType,
}: StatsCardProps) {
  return (
    <div className="glass-card p-5 hover:primary-glow transition-all duration-200">
      <div className="flex items-start justify-between mb-3">
        <div className={clsx('p-2.5 rounded-xl bg-white/5', iconColor)}>
          <Icon className="w-5 h-5" />
        </div>
        {trend !== undefined && (
          <div className={clsx('flex items-center gap-1 text-xs font-medium px-2 py-0.5 rounded-full',
            trendType === 'up' ? 'bg-rose-500/15 text-rose-400' : 'bg-emerald-500/15 text-emerald-400')}>
            {trendType === 'up' ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
            {trend}
          </div>
        )}
      </div>
      {loading ? (
        <div className="space-y-2">
          <div className="skeleton h-7 w-16 rounded" />
          <div className="skeleton h-3 w-24 rounded" />
        </div>
      ) : (
        <>
          <div className="flex items-baseline gap-1.5">
            <span className="text-3xl font-bold text-white tabular-nums">{value}</span>
            {unit && <span className="text-xs text-slate-500">{unit}</span>}
          </div>
          <p className="text-xs text-slate-500 mt-1">{title}</p>
        </>
      )}
    </div>
  )
}
