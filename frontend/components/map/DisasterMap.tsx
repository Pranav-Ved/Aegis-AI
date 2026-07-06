'use client'

import { useEffect, useRef } from 'react'

interface Incident {
  id: string; description: string; incident_type: string; severity: string;
  location: { lat: number; lng: number; address?: string }
}

interface Shelter {
  id: string; name: string; capacity?: number; total_capacity?: number; current_occupancy: number;
  location: { lat: number; lng: number; address?: string }
}

interface Hospital {
  id: string; name: string; available_beds: number; total_beds?: number; emergency_capacity?: number;
  location: { lat: number; lng: number; address?: string }
}

interface DisasterMapProps {
  incidents: Incident[]
  shelters: Shelter[]
  hospitals: Hospital[]
}

const SEVERITY_COLORS: Record<string, string> = {
  critical: '#f43f5e', high: '#f97316', medium: '#f59e0b', low: '#22c55e',
}

export default function DisasterMap({ incidents, shelters, hospitals }: DisasterMapProps) {
  const mapRef = useRef<any>(null)
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (typeof window === 'undefined') return
    let isMounted = true
    let mapInstance: any = null

    const initMap = async () => {
      if (!containerRef.current) return
      if ((containerRef.current as any)._leaflet_id) return

      const L = await import('leaflet')
      if (!isMounted || !containerRef.current) return
      if ((containerRef.current as any)._leaflet_id) return

      const map = L.map(containerRef.current, {
        center: [19.0760, 72.8777],
        zoom: 11,
        zoomControl: false,
      })

      // Dark tile layer from CartoDB
      L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '©OpenStreetMap ©CartoDB',
        subdomains: 'abcd',
        maxZoom: 19,
      }).addTo(map)

      L.control.zoom({ position: 'bottomright' }).addTo(map)

      mapRef.current = map
      mapInstance = map
    }

    initMap()

    return () => {
      isMounted = false
      if (mapInstance) {
        mapInstance.remove()
      } else if (mapRef.current) {
        mapRef.current.remove()
        mapRef.current = null
      }
    }
  }, [])

  // Update markers when data changes
  useEffect(() => {
    if (!mapRef.current || typeof window === 'undefined') return

    const updateMarkers = async () => {
      const L = await import('leaflet')
      const map = mapRef.current
      // Clear existing layers (except tile)
      map.eachLayer((layer: any) => {
        if (layer instanceof L.Marker || layer instanceof L.CircleMarker || layer instanceof L.Circle) {
          map.removeLayer(layer)
        }
      })

      // Incidents
      incidents.forEach((inc) => {
        if (!inc.location?.lat) return
        const color = SEVERITY_COLORS[inc.severity] ?? '#f59e0b'
        const circle = L.circleMarker([inc.location.lat, inc.location.lng], {
          radius: inc.severity === 'critical' ? 14 : inc.severity === 'high' ? 10 : 8,
          fillColor: color, color: color, weight: 2,
          opacity: 0.9, fillOpacity: 0.4,
        })
        circle.bindPopup(`
          <div style="font-family: Inter, sans-serif; min-width: 200px">
            <div style="font-weight:600; color: ${color}; margin-bottom:6px">
              ${inc.incident_type.toUpperCase()} — ${inc.severity.toUpperCase()}
            </div>
            <div style="font-size:13px; color:#cbd5e1; line-height:1.5">${inc.description}</div>
            ${inc.location.address ? `<div style="font-size:11px; color:#64748b; margin-top:6px">📍 ${inc.location.address}</div>` : ''}
          </div>
        `)
        circle.addTo(map)

        // Pulsing effect for critical
        if (inc.severity === 'critical') {
          L.circle([inc.location.lat, inc.location.lng], {
            radius: 500, fillColor: color, color: color, weight: 1, opacity: 0.2, fillOpacity: 0.05,
          }).addTo(map)
        }
      })

      // Shelters
      shelters.forEach((s) => {
        if (!s.location?.lat) return
        const capacity = s.total_capacity || s.capacity || 1
        const pct = s.current_occupancy / capacity
        const color = pct > 0.9 ? '#f43f5e' : pct > 0.6 ? '#f97316' : '#22c55e'
        const icon = L.divIcon({
          html: `<div style="background:${color};width:22px;height:22px;border-radius:6px;display:flex;align-items:center;justify-content:center;font-size:12px;box-shadow:0 0 8px ${color}44">🏕️</div>`,
          className: '', iconSize: [22, 22], iconAnchor: [11, 11],
        })
        L.marker([s.location.lat, s.location.lng], { icon })
          .bindPopup(`
            <div style="font-family: Inter, sans-serif">
              <div style="font-weight:600; color:#22c55e; margin-bottom:4px">🏕️ ${s.name}</div>
              <div style="font-size:12px; color:#94a3b8">${s.current_occupancy}/${capacity} occupied (${Math.round(pct*100)}%)</div>
              ${s.location.address ? `<div style="font-size:11px; color:#64748b; margin-top:4px">📍 ${s.location.address}</div>` : ''}
            </div>
          `)
          .addTo(map)
      })

      // Hospitals
      hospitals.forEach((h) => {
        if (!h.location?.lat) return
        const totalBeds = h.emergency_capacity || h.total_beds || 1
        const icon = L.divIcon({
          html: `<div style="background:#0ea5e9;width:22px;height:22px;border-radius:6px;display:flex;align-items:center;justify-content:center;font-size:12px;box-shadow:0 0 8px #0ea5e944">🏥</div>`,
          className: '', iconSize: [22, 22], iconAnchor: [11, 11],
        })
        L.marker([h.location.lat, h.location.lng], { icon })
          .bindPopup(`
            <div style="font-family: Inter, sans-serif">
              <div style="font-weight:600; color:#0ea5e9; margin-bottom:4px">🏥 ${h.name}</div>
              <div style="font-size:12px; color:#94a3b8">Available beds: ${h.available_beds}/${totalBeds}</div>
              ${h.location?.address ? `<div style="font-size:11px; color:#64748b; margin-top:4px">📍 ${h.location.address}</div>` : ''}
            </div>
          `)
          .addTo(map)
      })
    }

    updateMarkers()
  }, [incidents, shelters, hospitals])

  return <div ref={containerRef} className="w-full h-full" style={{ minHeight: '400px' }} />
}
