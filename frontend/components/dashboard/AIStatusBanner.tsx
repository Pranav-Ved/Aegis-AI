'use client'

import { Info, X } from 'lucide-react'
import { useState } from 'react'

export default function AIStatusBanner({
  aiAvailable, dbMode, notificationsMode
}: { aiAvailable: boolean; dbMode: string; notificationsMode: string }) {
  const [dismissed, setDismissed] = useState(false)
  if (dismissed) return null

  return (
    <div className="relative flex items-start gap-3 px-4 py-3 rounded-xl bg-indigo-500/10 border border-indigo-500/25 animate-slide-in-bottom">
      <Info className="w-4 h-4 text-indigo-400 flex-shrink-0 mt-0.5" />
      <div className="flex-1 min-w-0 text-sm text-indigo-300">
        <span className="font-semibold">Running in Demo Mode.</span>{' '}
        You can enable live AI capabilities using the <code className="bg-indigo-500/20 px-1 py-0.5 rounded text-xs">GEMINI_API_KEY</code> environment variable in your <code className="bg-indigo-500/20 px-1 py-0.5 rounded text-xs">.env</code> file.
        All multi-agent pipelines and simulations are fully operational locally.
      </div>
      <button onClick={() => setDismissed(true)}
        className="flex-shrink-0 w-5 h-5 rounded-md hover:bg-white/10 flex items-center justify-center text-indigo-400 transition-colors">
        <X className="w-3.5 h-3.5" />
      </button>
    </div>
  )
}
