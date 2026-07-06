'use client'

import { Cloud, Wind, Thermometer, Droplets, Eye } from 'lucide-react'
import { useEffect, useState } from 'react'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function WeatherPanel() {
  const [weather, setWeather] = useState<any>(null)

  useEffect(() => {
    const fetchWeather = async () => {
      try {
        const token = localStorage.getItem('aegis_token')
        const res = await fetch(`${API_URL}/api/v1/weather/current?lat=19.0760&lng=72.8777`, {
          headers: { Authorization: `Bearer ${token}` }
        })
        if (res.ok) setWeather(await res.json())
        else setWeather(MOCK_WEATHER)
      } catch { setWeather(MOCK_WEATHER) }
    }
    fetchWeather()
  }, [])

  return (
    <div className="glass-card p-5">
      <div className="flex items-center gap-2 mb-4">
        <Cloud className="w-4 h-4 text-sky-400" />
        <h2 className="text-base font-semibold text-slate-100">Weather Conditions</h2>
        <span className="ml-auto text-xs text-slate-500">{weather?.source === 'openweathermap' ? 'Live' : 'Mock'}</span>
      </div>
      {weather ? (
        <div className="space-y-3">
          <div className="flex items-center gap-3">
            <span className="text-4xl">{weather.icon}</span>
            <div>
              <p className="text-2xl font-bold text-white">{weather.temperature_c}°C</p>
              <p className="text-sm text-slate-400 capitalize">{weather.description}</p>
              <p className="text-xs text-slate-500">{weather.location}</p>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-2 pt-2 border-t border-white/5">
            <WeatherStat icon={Droplets} label="Humidity" value={`${weather.humidity}%`} />
            <WeatherStat icon={Wind} label="Wind" value={`${weather.wind_speed} km/h`} />
            <WeatherStat icon={Eye} label="Visibility" value={`${weather.visibility_km} km`} />
            <WeatherStat icon={Thermometer} label="Feels like" value={`${weather.feels_like_c ?? '—'}°C`} />
          </div>
          {weather.disaster_risk && weather.disaster_risk !== 'none' && (
            <div className={`px-3 py-2 rounded-lg text-xs font-medium ${
              weather.disaster_risk === 'high' ? 'bg-rose-500/15 text-rose-400' :
              weather.disaster_risk === 'medium' ? 'bg-amber-500/15 text-amber-400' :
              'bg-emerald-500/15 text-emerald-400'
            }`}>
              ⚠ Disaster Risk: {weather.disaster_risk.toUpperCase()}
            </div>
          )}
        </div>
      ) : (
        <div className="space-y-3">
          {[...Array(4)].map((_, i) => <div key={i} className="skeleton h-4 rounded" />)}
        </div>
      )}
    </div>
  )
}

function WeatherStat({ icon: Icon, label, value }: { icon: any; label: string; value: string }) {
  return (
    <div className="flex items-center gap-2 text-xs">
      <Icon className="w-3.5 h-3.5 text-slate-500" />
      <span className="text-slate-500">{label}:</span>
      <span className="text-slate-300 font-medium">{value}</span>
    </div>
  )
}

const MOCK_WEATHER = {
  temperature_c: 28, feels_like_c: 32, description: 'Heavy Rain', icon: '🌧️',
  humidity: 89, wind_speed: 24, visibility_km: 4, location: 'Mumbai',
  disaster_risk: 'medium', source: 'mock',
}
