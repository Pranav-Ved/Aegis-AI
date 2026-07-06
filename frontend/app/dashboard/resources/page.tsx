'use client'

import { useState, useEffect } from 'react'
import { 
  Building2, Stethoscope, Package, Truck, Users, Plus, Minus, 
  ShieldAlert, Loader2, Edit2, X, Check, Save 
} from 'lucide-react'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function ResourcesPage() {
  const [activeTab, setActiveTab] = useState<'shelters' | 'hospitals' | 'inventory' | 'vehicles' | 'volunteers'>('shelters')
  const [shelters, setShelters] = useState<any[]>([])
  const [hospitals, setHospitals] = useState<any[]>([])
  const [inventory, setInventory] = useState<any[]>([])
  const [vehicles, setVehicles] = useState<any[]>([])
  const [volunteers, setVolunteers] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [updating, setUpdating] = useState<string | null>(null)
  
  // Edit modal/inline form state
  const [editingItem, setEditingItem] = useState<any | null>(null)

  const fetchData = async () => {
    const token = localStorage.getItem('aegis_token')
    const headers = { Authorization: `Bearer ${token}` }
    setLoading(true)
    try {
      if (activeTab === 'shelters') {
        const res = await fetch(`${API_URL}/api/v1/resources/shelters`, { headers })
        if (res.ok) setShelters(await res.json())
        else setShelters(MOCK_SHELTERS)
      } else if (activeTab === 'hospitals') {
        const res = await fetch(`${API_URL}/api/v1/resources/hospitals`, { headers })
        if (res.ok) setHospitals(await res.json())
        else setHospitals(MOCK_HOSPITALS)
      } else if (activeTab === 'inventory') {
        const res = await fetch(`${API_URL}/api/v1/resources/warehouses`, { headers })
        if (res.ok) {
          setInventory(await res.json())
        } else {
          setInventory(MOCK_WAREHOUSES)
        }
      } else if (activeTab === 'vehicles') {
        const res = await fetch(`${API_URL}/api/v1/resources/vehicles`, { headers })
        if (res.ok) setVehicles(await res.json())
        else setVehicles(MOCK_VEHICLES)
      } else if (activeTab === 'volunteers') {
        const res = await fetch(`${API_URL}/api/v1/resources/volunteers`, { headers })
        if (res.ok) setVolunteers(await res.json())
        else setVolunteers(MOCK_VOLUNTEERS)
      }
    } catch {
      if (activeTab === 'shelters') setShelters(MOCK_SHELTERS)
      else if (activeTab === 'hospitals') setHospitals(MOCK_HOSPITALS)
      else if (activeTab === 'inventory') setInventory(MOCK_WAREHOUSES)
      else if (activeTab === 'vehicles') setVehicles(MOCK_VEHICLES)
      else if (activeTab === 'volunteers') setVolunteers(MOCK_VOLUNTEERS)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [activeTab])

  const handleEditSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!editingItem) return
    const token = localStorage.getItem('aegis_token')
    const headers = { 
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json' 
    }
    
    setUpdating(editingItem.id)
    const id = editingItem.id
    
    try {
      let url = ''
      let payload = {}
      
      if (activeTab === 'shelters') {
        url = `${API_URL}/api/v1/resources/shelters/${id}`
        payload = {
          name: editingItem.name,
          total_capacity: Number(editingItem.total_capacity),
          current_occupancy: Number(editingItem.current_occupancy),
          status: editingItem.status,
          address: editingItem.address
        }
      } else if (activeTab === 'hospitals') {
        url = `${API_URL}/api/v1/resources/hospitals/${id}`
        payload = {
          name: editingItem.name,
          emergency_capacity: Number(editingItem.emergency_capacity),
          available_beds: Number(editingItem.available_beds),
          status: editingItem.status
        }
      } else if (activeTab === 'inventory') {
        url = `${API_URL}/api/v1/resources/warehouses/${id}`
        payload = {
          name: editingItem.name,
          address: editingItem.address,
          inventory: {
            food: Number(editingItem.inventory.food),
            water: Number(editingItem.inventory.water),
            medicine: Number(editingItem.inventory.medicine),
            blankets: Number(editingItem.inventory.blankets),
            fuel: Number(editingItem.inventory.fuel || 0),
            medical_kits: Number(editingItem.inventory.medical_kits || 0)
          }
        }
      } else if (activeTab === 'vehicles') {
        url = `${API_URL}/api/v1/resources/vehicles/${id}`
        payload = {
          status: editingItem.status,
          driver: editingItem.driver,
          assigned_mission_id: editingItem.assigned_mission_id || null
        }
      } else if (activeTab === 'volunteers') {
        url = `${API_URL}/api/v1/resources/volunteers/${id}`
        payload = {
          status: editingItem.status,
          assigned_mission_id: editingItem.assigned_mission_id || null,
          phone: editingItem.phone
        }
      }
      
      const res = await fetch(url, {
        method: 'PATCH',
        headers,
        body: JSON.stringify(payload)
      })
      
      if (res.ok) {
        const updated = await res.json()
        if (activeTab === 'shelters') {
          setShelters(prev => prev.map(item => item.id === id ? updated : item))
        } else if (activeTab === 'hospitals') {
          setHospitals(prev => prev.map(item => item.id === id ? updated : item))
        } else if (activeTab === 'inventory') {
          setInventory(prev => prev.map(item => item.id === id ? updated : item))
        } else if (activeTab === 'vehicles') {
          setVehicles(prev => prev.map(item => item.id === id ? updated : item))
        } else if (activeTab === 'volunteers') {
          setVolunteers(prev => prev.map(item => item.id === id ? updated : item))
        }
        setEditingItem(null)
      } else {
        alert('Failed to update resource. Please verify your permissions.')
      }
    } catch (err) {
      console.error(err)
      alert('Network error. Failed to save.')
    } finally {
      setUpdating(null)
    }
  }

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-bold text-white">Emergency Resources</h1>
        <p className="text-sm text-slate-500 mt-0.5">Real-time tracking and live CRUD management for shelters, hospitals, warehouses, vehicles, and volunteers.</p>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-white/5 space-x-6 overflow-x-auto pb-1">
        <button
          onClick={() => setActiveTab('shelters')}
          className={`pb-3 text-sm font-semibold border-b-2 flex items-center gap-2 transition-all whitespace-nowrap ${
            activeTab === 'shelters' ? 'border-indigo-500 text-indigo-400' : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <Building2 className="w-4 h-4" />
          Relief Shelters
        </button>
        <button
          onClick={() => setActiveTab('hospitals')}
          className={`pb-3 text-sm font-semibold border-b-2 flex items-center gap-2 transition-all whitespace-nowrap ${
            activeTab === 'hospitals' ? 'border-indigo-500 text-indigo-400' : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <Stethoscope className="w-4 h-4" />
          Hospitals & Beds
        </button>
        <button
          onClick={() => setActiveTab('inventory')}
          className={`pb-3 text-sm font-semibold border-b-2 flex items-center gap-2 transition-all whitespace-nowrap ${
            activeTab === 'inventory' ? 'border-indigo-500 text-indigo-400' : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <Package className="w-4 h-4" />
          Warehouses
        </button>
        <button
          onClick={() => setActiveTab('vehicles')}
          className={`pb-3 text-sm font-semibold border-b-2 flex items-center gap-2 transition-all whitespace-nowrap ${
            activeTab === 'vehicles' ? 'border-indigo-500 text-indigo-400' : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <Truck className="w-4 h-4" />
          Vehicles
        </button>
        <button
          onClick={() => setActiveTab('volunteers')}
          className={`pb-3 text-sm font-semibold border-b-2 flex items-center gap-2 transition-all whitespace-nowrap ${
            activeTab === 'volunteers' ? 'border-indigo-500 text-indigo-400' : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <Users className="w-4 h-4" />
          Volunteers
        </button>
      </div>

      {/* Content Area */}
      <div className="grid gap-4">
        {loading ? (
          [...Array(3)].map((_, i) => <div key={i} className="glass-card p-5 skeleton h-28 rounded-xl" />)
        ) : activeTab === 'shelters' ? (
          shelters.map((s) => {
            const capacity = s.total_capacity || s.capacity || 1
            const pct = Math.round((s.current_occupancy / capacity) * 100)
            return (
              <div key={s.id} className="glass-card p-5 flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="font-semibold text-slate-100">{s.name}</h3>
                    <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${
                      s.status === 'open' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' :
                      s.status === 'full' ? 'bg-rose-500/10 text-rose-400 border-rose-500/20' :
                      'bg-slate-500/10 text-slate-400 border-slate-500/20'
                    }`}>
                      {s.status?.toUpperCase()}
                    </span>
                  </div>
                  <p className="text-xs text-slate-500">📍 {s.address || 'Central Camp'}</p>
                  <div className="flex items-center gap-4 mt-3">
                    <div className="flex-1 max-w-xs h-2 rounded-full bg-white/5 overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all ${
                          pct >= 90 ? 'bg-rose-500' : pct >= 65 ? 'bg-amber-500' : 'bg-emerald-500'
                        }`}
                        style={{ width: `${Math.min(pct, 100)}%` }}
                      />
                    </div>
                    <span className="text-xs text-slate-400 font-medium">{pct}% utilized ({s.current_occupancy}/{capacity})</span>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <button 
                    onClick={() => setEditingItem(s)}
                    className="p-2 rounded-lg bg-white/5 border border-white/10 hover:border-indigo-500 text-slate-300 hover:text-indigo-400 transition-colors"
                  >
                    <Edit2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            )
          })
        ) : activeTab === 'hospitals' ? (
          hospitals.map((h) => {
            const totalBeds = h.emergency_capacity || h.total_beds || 1
            const utilization = Math.round(((totalBeds - h.available_beds) / totalBeds) * 100)
            return (
              <div key={h.id} className="glass-card p-5 flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="font-semibold text-slate-100">{h.name}</h3>
                    <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${
                      h.status === 'operational' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' :
                      h.status === 'limited' ? 'bg-amber-500/10 text-amber-400 border-amber-500/20' :
                      'bg-rose-500/10 text-rose-400 border-rose-500/20'
                    }`}>
                      {h.status?.toUpperCase()}
                    </span>
                  </div>
                  <p className="text-xs text-slate-500">📍 {h.address || 'Emergency Ward'}</p>
                  <div className="flex items-center gap-4 mt-3">
                    <div className="flex-1 max-w-xs h-2 rounded-full bg-white/5 overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all ${
                          utilization >= 90 ? 'bg-rose-500' : utilization >= 70 ? 'bg-amber-500' : 'bg-emerald-500'
                        }`}
                        style={{ width: `${Math.min(utilization, 100)}%` }}
                      />
                    </div>
                    <span className="text-xs text-slate-400 font-medium">Bed occupancy {utilization}% ({totalBeds - h.available_beds}/{totalBeds})</span>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <button 
                    onClick={() => setEditingItem(h)}
                    className="p-2 rounded-lg bg-white/5 border border-white/10 hover:border-indigo-500 text-slate-300 hover:text-indigo-400 transition-colors"
                  >
                    <Edit2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            )
          })
        ) : activeTab === 'inventory' ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {inventory.map((w) => (
              <div key={w.id} className="glass-card p-5 hover:border-white/15 transition-all relative">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="font-semibold text-slate-100">{w.name}</h3>
                    <p className="text-[10px] text-slate-500 mt-0.5">📍 {w.address}</p>
                  </div>
                  <button 
                    onClick={() => setEditingItem(w)}
                    className="p-1.5 rounded-lg bg-white/5 border border-white/10 hover:border-indigo-500 text-slate-300 hover:text-indigo-400 transition-colors"
                  >
                    <Edit2 className="w-3.5 h-3.5" />
                  </button>
                </div>
                <div className="grid grid-cols-2 gap-3 text-xs">
                  <div className="bg-white/5 p-2 rounded-lg">
                    <span className="text-slate-500 block">Food</span>
                    <span className="font-semibold text-white text-sm">{w.inventory?.food ?? w.inventory?.meals ?? 0}</span>
                  </div>
                  <div className="bg-white/5 p-2 rounded-lg">
                    <span className="text-slate-500 block">Water</span>
                    <span className="font-semibold text-white text-sm">{w.inventory?.water ?? w.inventory?.liters ?? 0} L</span>
                  </div>
                  <div className="bg-white/5 p-2 rounded-lg">
                    <span className="text-slate-500 block">Medicine</span>
                    <span className="font-semibold text-white text-sm">{w.inventory?.medicine ?? w.inventory?.kits ?? 0}</span>
                  </div>
                  <div className="bg-white/5 p-2 rounded-lg">
                    <span className="text-slate-500 block">Blankets</span>
                    <span className="font-semibold text-white text-sm">{w.inventory?.blankets ?? w.inventory?.pieces ?? 0}</span>
                  </div>
                  <div className="bg-white/5 p-2 rounded-lg">
                    <span className="text-slate-500 block">Fuel</span>
                    <span className="font-semibold text-white text-sm">{w.inventory?.fuel ?? 0} L</span>
                  </div>
                  <div className="bg-white/5 p-2 rounded-lg">
                    <span className="text-slate-500 block">Medical Kits</span>
                    <span className="font-semibold text-white text-sm">{w.inventory?.medical_kits ?? 0}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : activeTab === 'vehicles' ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {vehicles.map((v) => (
              <div key={v.id} className="glass-card p-5 flex flex-col justify-between">
                <div>
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="font-semibold text-slate-100">{v.name}</h3>
                      <p className="text-[10px] text-slate-500">{v.registration_no} • {v.type?.replace('_', ' ')}</p>
                    </div>
                    <span className={`text-[10px] px-2 py-0.5 rounded-full border ${
                      v.status === 'available' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' :
                      'bg-amber-500/10 text-amber-400 border-amber-500/20'
                    }`}>
                      {v.status}
                    </span>
                  </div>
                  <div className="mt-4 space-y-2 text-xs">
                    <div className="flex justify-between">
                      <span className="text-slate-500">Driver:</span>
                      <span className="text-slate-300 font-medium">{v.driver || 'Unassigned'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-500">Mission:</span>
                      <span className="text-slate-300 font-medium truncate max-w-[150px]">{v.assigned_mission_id || 'None'}</span>
                    </div>
                  </div>
                </div>
                <div className="mt-4 border-t border-white/5 pt-3 flex justify-end">
                  <button 
                    onClick={() => setEditingItem(v)}
                    className="p-1.5 rounded-lg bg-white/5 border border-white/10 hover:border-indigo-500 text-slate-300 hover:text-indigo-400 transition-colors flex items-center gap-1.5 text-xs px-2.5"
                  >
                    <Edit2 className="w-3.5 h-3.5" /> Edit
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {volunteers.map((v) => (
              <div key={v.id} className="glass-card p-5 flex flex-col justify-between">
                <div>
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="font-semibold text-slate-100">{v.name}</h3>
                      <p className="text-[10px] text-slate-500">{v.role}</p>
                    </div>
                    <span className={`text-[10px] px-2 py-0.5 rounded-full border ${
                      v.status === 'available' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' :
                      'bg-amber-500/10 text-amber-400 border-amber-500/20'
                    }`}>
                      {v.status}
                    </span>
                  </div>
                  <div className="mt-4 space-y-2 text-xs">
                    <div className="flex justify-between">
                      <span className="text-slate-500">Contact:</span>
                      <span className="text-slate-300 font-medium">{v.phone}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-500">Mission:</span>
                      <span className="text-slate-300 font-medium">{v.assigned_mission_id || 'None'}</span>
                    </div>
                  </div>
                </div>
                <div className="mt-4 border-t border-white/5 pt-3 flex justify-end">
                  <button 
                    onClick={() => setEditingItem(v)}
                    className="p-1.5 rounded-lg bg-white/5 border border-white/10 hover:border-indigo-500 text-slate-300 hover:text-indigo-400 transition-colors flex items-center gap-1.5 text-xs px-2.5"
                  >
                    <Edit2 className="w-3.5 h-3.5" /> Edit
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Edit Modal Dialog */}
      {editingItem && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-white/10 rounded-2xl w-full max-w-lg shadow-2xl overflow-hidden animate-scale-in">
            <div className="p-5 border-b border-white/5 flex items-center justify-between">
              <h2 className="text-base font-semibold text-white">Edit Resource Details</h2>
              <button 
                onClick={() => setEditingItem(null)}
                className="text-slate-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <form onSubmit={handleEditSubmit} className="p-5 space-y-4">
              {activeTab === 'shelters' && (
                <>
                  <div>
                    <label className="block text-xs font-semibold text-slate-400 mb-1">Shelter Name</label>
                    <input 
                      type="text" 
                      value={editingItem.name || ''} 
                      onChange={e => setEditingItem({...editingItem, name: e.target.value})}
                      className="w-full bg-white/5 border border-white/10 rounded-lg p-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs font-semibold text-slate-400 mb-1">Total Capacity</label>
                      <input 
                        type="number" 
                        value={editingItem.total_capacity ?? editingItem.capacity ?? 0} 
                        onChange={e => setEditingItem({...editingItem, total_capacity: e.target.value})}
                        className="w-full bg-white/5 border border-white/10 rounded-lg p-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-semibold text-slate-400 mb-1">Current Occupancy</label>
                      <input 
                        type="number" 
                        value={editingItem.current_occupancy ?? 0} 
                        onChange={e => setEditingItem({...editingItem, current_occupancy: e.target.value})}
                        className="w-full bg-white/5 border border-white/10 rounded-lg p-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-400 mb-1">Status</label>
                    <select 
                      value={editingItem.status || 'open'} 
                      onChange={e => setEditingItem({...editingItem, status: e.target.value})}
                      className="w-full bg-slate-800 border border-white/10 rounded-lg p-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                    >
                      <option value="open">Open</option>
                      <option value="full">Full</option>
                      <option value="closed">Closed</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-400 mb-1">Address</label>
                    <input 
                      type="text" 
                      value={editingItem.address || ''} 
                      onChange={e => setEditingItem({...editingItem, address: e.target.value})}
                      className="w-full bg-white/5 border border-white/10 rounded-lg p-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                    />
                  </div>
                </>
              )}

              {activeTab === 'hospitals' && (
                <>
                  <div>
                    <label className="block text-xs font-semibold text-slate-400 mb-1">Hospital Name</label>
                    <input 
                      type="text" 
                      value={editingItem.name || ''} 
                      onChange={e => setEditingItem({...editingItem, name: e.target.value})}
                      className="w-full bg-white/5 border border-white/10 rounded-lg p-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs font-semibold text-slate-400 mb-1">Emergency Capacity</label>
                      <input 
                        type="number" 
                        value={editingItem.emergency_capacity ?? editingItem.total_beds ?? 0} 
                        onChange={e => setEditingItem({...editingItem, emergency_capacity: e.target.value})}
                        className="w-full bg-white/5 border border-white/10 rounded-lg p-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-semibold text-slate-400 mb-1">Available Beds</label>
                      <input 
                        type="number" 
                        value={editingItem.available_beds ?? 0} 
                        onChange={e => setEditingItem({...editingItem, available_beds: e.target.value})}
                        className="w-full bg-white/5 border border-white/10 rounded-lg p-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-400 mb-1">Status</label>
                    <select 
                      value={editingItem.status || 'operational'} 
                      onChange={e => setEditingItem({...editingItem, status: e.target.value})}
                      className="w-full bg-slate-800 border border-white/10 rounded-lg p-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                    >
                      <option value="operational">Operational</option>
                      <option value="limited">Limited</option>
                      <option value="overwhelmed">Overwhelmed</option>
                      <option value="closed">Closed</option>
                    </select>
                  </div>
                </>
              )}

              {activeTab === 'inventory' && (
                <>
                  <div>
                    <label className="block text-xs font-semibold text-slate-400 mb-1">Warehouse Name</label>
                    <input 
                      type="text" 
                      value={editingItem.name || ''} 
                      onChange={e => setEditingItem({...editingItem, name: e.target.value})}
                      className="w-full bg-white/5 border border-white/10 rounded-lg p-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-400 mb-1">Address</label>
                    <input 
                      type="text" 
                      value={editingItem.address || ''} 
                      onChange={e => setEditingItem({...editingItem, address: e.target.value})}
                      className="w-full bg-white/5 border border-white/10 rounded-lg p-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                    />
                  </div>
                  <div className="grid grid-cols-3 gap-3">
                    <div>
                      <label className="block text-[10px] font-semibold text-slate-400 mb-1">Food (meals)</label>
                      <input 
                        type="number" 
                        value={editingItem.inventory?.food ?? 0} 
                        onChange={e => setEditingItem({
                          ...editingItem, 
                          inventory: { ...editingItem.inventory, food: e.target.value }
                        })}
                        className="w-full bg-white/5 border border-white/10 rounded-lg p-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                      />
                    </div>
                    <div>
                      <label className="block text-[10px] font-semibold text-slate-400 mb-1">Water (liters)</label>
                      <input 
                        type="number" 
                        value={editingItem.inventory?.water ?? 0} 
                        onChange={e => setEditingItem({
                          ...editingItem, 
                          inventory: { ...editingItem.inventory, water: e.target.value }
                        })}
                        className="w-full bg-white/5 border border-white/10 rounded-lg p-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                      />
                    </div>
                    <div>
                      <label className="block text-[10px] font-semibold text-slate-400 mb-1">Medicine (kits)</label>
                      <input 
                        type="number" 
                        value={editingItem.inventory?.medicine ?? 0} 
                        onChange={e => setEditingItem({
                          ...editingItem, 
                          inventory: { ...editingItem.inventory, medicine: e.target.value }
                        })}
                        className="w-full bg-white/5 border border-white/10 rounded-lg p-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                      />
                    </div>
                    <div>
                      <label className="block text-[10px] font-semibold text-slate-400 mb-1">Blankets (pieces)</label>
                      <input 
                        type="number" 
                        value={editingItem.inventory?.blankets ?? 0} 
                        onChange={e => setEditingItem({
                          ...editingItem, 
                          inventory: { ...editingItem.inventory, blankets: e.target.value }
                        })}
                        className="w-full bg-white/5 border border-white/10 rounded-lg p-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                      />
                    </div>
                    <div>
                      <label className="block text-[10px] font-semibold text-slate-400 mb-1">Fuel (liters)</label>
                      <input 
                        type="number" 
                        value={editingItem.inventory?.fuel ?? 0} 
                        onChange={e => setEditingItem({
                          ...editingItem, 
                          inventory: { ...editingItem.inventory, fuel: e.target.value }
                        })}
                        className="w-full bg-white/5 border border-white/10 rounded-lg p-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                      />
                    </div>
                    <div>
                      <label className="block text-[10px] font-semibold text-slate-400 mb-1">Medical Kits</label>
                      <input 
                        type="number" 
                        value={editingItem.inventory?.medical_kits ?? 0} 
                        onChange={e => setEditingItem({
                          ...editingItem, 
                          inventory: { ...editingItem.inventory, medical_kits: e.target.value }
                        })}
                        className="w-full bg-white/5 border border-white/10 rounded-lg p-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                      />
                    </div>
                  </div>
                </>
              )}

              {activeTab === 'vehicles' && (
                <>
                  <div>
                    <label className="block text-xs font-semibold text-slate-400 mb-1">Status</label>
                    <select 
                      value={editingItem.status || 'available'} 
                      onChange={e => setEditingItem({...editingItem, status: e.target.value})}
                      className="w-full bg-slate-800 border border-white/10 rounded-lg p-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                    >
                      <option value="available">Available</option>
                      <option value="deployed">Deployed</option>
                      <option value="maintenance">Maintenance</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-400 mb-1">Driver Name</label>
                    <input 
                      type="text" 
                      value={editingItem.driver || ''} 
                      onChange={e => setEditingItem({...editingItem, driver: e.target.value})}
                      className="w-full bg-white/5 border border-white/10 rounded-lg p-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-400 mb-1">Assigned Mission ID</label>
                    <input 
                      type="text" 
                      placeholder="e.g. mis_001 or leave blank"
                      value={editingItem.assigned_mission_id || ''} 
                      onChange={e => setEditingItem({...editingItem, assigned_mission_id: e.target.value})}
                      className="w-full bg-white/5 border border-white/10 rounded-lg p-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                    />
                  </div>
                </>
              )}

              {activeTab === 'volunteers' && (
                <>
                  <div>
                    <label className="block text-xs font-semibold text-slate-400 mb-1">Availability Status</label>
                    <select 
                      value={editingItem.status || 'available'} 
                      onChange={e => setEditingItem({...editingItem, status: e.target.value})}
                      className="w-full bg-slate-800 border border-white/10 rounded-lg p-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                    >
                      <option value="available">Available</option>
                      <option value="deployed">Deployed</option>
                      <option value="unavailable">Unavailable</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-400 mb-1">Contact Phone</label>
                    <input 
                      type="text" 
                      value={editingItem.phone || ''} 
                      onChange={e => setEditingItem({...editingItem, phone: e.target.value})}
                      className="w-full bg-white/5 border border-white/10 rounded-lg p-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-400 mb-1">Assigned Mission ID</label>
                    <input 
                      type="text" 
                      placeholder="e.g. mis_001 or leave blank"
                      value={editingItem.assigned_mission_id || ''} 
                      onChange={e => setEditingItem({...editingItem, assigned_mission_id: e.target.value})}
                      className="w-full bg-white/5 border border-white/10 rounded-lg p-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                    />
                  </div>
                </>
              )}

              <div className="pt-3 border-t border-white/5 flex justify-end gap-3">
                <button 
                  type="button" 
                  onClick={() => setEditingItem(null)}
                  className="btn-ghost px-4 py-2 text-xs"
                >
                  Cancel
                </button>
                <button 
                  type="submit" 
                  disabled={updating === editingItem.id}
                  className="btn-primary px-4 py-2 text-xs flex items-center gap-1.5"
                >
                  {updating === editingItem.id ? (
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  ) : (
                    <Save className="w-3.5 h-3.5" />
                  )}
                  Save Changes
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

const MOCK_SHELTERS = [
  { id: 'shelter_001', name: 'Dharavi Sports Complex Relief Camp', current_occupancy: 287, total_capacity: 500, status: 'open', address: 'Dharavi, Mumbai' },
  { id: 'shelter_002', name: 'BKC Emergency Camp', current_occupancy: 298, total_capacity: 300, status: 'full', address: 'BKC, Mumbai' },
  { id: 'shelter_003', name: 'Andheri Sports Ground Camp', current_occupancy: 145, total_capacity: 800, status: 'open', address: 'Andheri, Mumbai' },
]

const MOCK_HOSPITALS = [
  { id: 'hospital_001', name: 'KEM Hospital Emergency Unit', available_beds: 47, emergency_capacity: 200, status: 'operational', address: 'Parel, Mumbai' },
  { id: 'hospital_002', name: 'Lokmanya Tilak Hospital', available_beds: 12, emergency_capacity: 150, status: 'operational', address: 'Sion, Mumbai' },
]

const MOCK_WAREHOUSES = [
  { 
    id: 'wh_001', 
    name: 'NDRF Central Depot Mumbai', 
    address: 'Sector 1, Mumbai', 
    inventory: { food: 15000, water: 50000, medicine: 5000, blankets: 8000, fuel: 1200, medical_kits: 450 } 
  },
  { 
    id: 'wh_002', 
    name: 'Delhi Logistics Hub', 
    address: 'Sector 2, Delhi', 
    inventory: { food: 25000, water: 80000, medicine: 12000, blankets: 15000, fuel: 3000, medical_kits: 900 } 
  },
]

const MOCK_VEHICLES = [
  { id: 'veh_001', name: 'Aegis-Ambulance-1', type: 'ambulance', registration_no: 'MH-12-EQ-0001', status: 'available', driver: 'Suresh Kumar', assigned_mission_id: null },
  { id: 'veh_002', name: 'Aegis-RescueBoat-1', type: 'rescue_boat', registration_no: 'MH-12-EQ-0002', status: 'deployed', driver: 'Ramesh Patel', assigned_mission_id: 'mis_001' },
]

const MOCK_VOLUNTEERS = [
  { id: 'vol_001', name: 'Amit Sharma', role: 'Medical First Aid', phone: '+91-98200-00001', status: 'available', assigned_mission_id: null },
  { id: 'vol_002', name: 'Pooja Singh', role: 'Food Distribution', phone: '+91-98200-00004', status: 'deployed', assigned_mission_id: 'mis_001' },
]
