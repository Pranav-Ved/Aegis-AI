# 🛡️ AegisAI — Intelligent Disaster Management Platform

> *Shielding Lives with Intelligent Response*

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-green.svg)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org)
[![Google ADK](https://img.shields.io/badge/Google_ADK-1.0+-yellow.svg)](https://google.github.io/adk-docs/)

AegisAI is a production-grade, AI-powered **Multi-Agent Emergency and Disaster Management Platform** designed to help governments, emergency responders, NGOs, and citizens coordinate disaster response across India and beyond. It leverages the **Google Agent Development Kit (ADK)**, **Gemini 2.0 Flash**, modular **MCP Servers**, and a modern real-time web dashboard.

---

## 🚀 Key Features

### 🤖 AI-Powered Multi-Agent Pipeline
| Agent | Role |
|---|---|
| **Emergency Intake Agent** | Validates and sanitizes citizen reports with prompt injection protection |
| **Disaster Detection Agent** | Classifies threats using Gemini Vision and assigns severity levels |
| **Location Intelligence Agent** | Geocodes addresses, fetches live weather, identifies nearby resources |
| **Resource Coordination Agent** | Allocates shelters, hospital beds, and logistics supply chains |
| **Rescue Planning Agent** | Plans tactical rescue operations and team assignments |
| **Notification Agent** | Dispatches SMS/email alerts to emergency response squads |
| **Report Generation Agent** | Generates formal situation PDF briefs for government officials |

### 🔌 Modular MCP Servers
- **Maps MCP** – Google Maps / Mock geocoding & distance calculations
- **Weather MCP** – OpenWeatherMap / Mock weather conditions
- **Firestore MCP** – Google Cloud Firestore / In-Memory MockDB  
- **Notifications MCP** – Twilio SMS + SendGrid / Console logging fallback
- **PDF MCP** – ReportLab PDF generation for situation briefs
- **Logging MCP** – Structured audit trail and event logging

### 📊 Real-Time Dashboard
- **Live Incident Feed** with status tracking and agent progress
- **Interactive Leaflet Map** with disaster markers, shelters, and hospitals
- **Resource Management** – shelter occupancy, hospital beds, supply inventory
- **Mission Coordination** – rescue team deployments with step-by-step progress
- **Report Downloads** – PDF situation briefs per incident
- **WebSocket Real-Time Updates** – instant dashboard refresh on new events

---

## 🏗️ Architecture

```
AegisAI/
├── backend/                        # FastAPI Python Backend
│   ├── app/
│   │   ├── main.py                 # App entrypoint, WebSocket handlers
│   │   ├── core/
│   │   │   ├── config.py           # Pydantic Settings from environment
│   │   │   ├── database.py         # MockDB / Firestore wrapper + seed data
│   │   │   ├── security.py         # JWT auth, bcrypt hashing, RBAC
│   │   │   ├── middleware.py       # Request logging middleware
│   │   │   ├── exceptions.py       # Custom HTTP exceptions
│   │   │   └── prompt_guard.py     # Prompt injection protection
│   │   ├── models/
│   │   │   ├── emergency.py        # Incident schemas and enums
│   │   │   ├── user.py             # User and auth schemas
│   │   │   ├── resource.py         # Shelter, Hospital, Resource schemas
│   │   │   └── mission.py          # Mission and team schemas
│   │   ├── services/
│   │   │   ├── incident_service.py # Incident CRUD logic
│   │   │   └── resource_service.py # Shelter/Hospital/Resource logic
│   │   ├── agents/
│   │   │   ├── orchestrator.py     # Master ADK Orchestrator
│   │   │   ├── emergency_intake.py # Intake & sanitization agent
│   │   │   ├── disaster_detection.py  # Gemini threat classification
│   │   │   ├── location_intelligence.py  # Geocoding & weather
│   │   │   ├── resource_coordination.py  # Supply allocation
│   │   │   ├── rescue_planning.py  # Tactical rescue planning
│   │   │   ├── notification_agent.py  # SMS/email dispatch
│   │   │   └── report_generation.py   # PDF situation briefs
│   │   ├── mcp_servers/
│   │   │   ├── base.py             # MCPToolResult wrapper base class
│   │   │   ├── maps_mcp.py         # Maps & geocoding
│   │   │   ├── weather_mcp.py      # Weather data
│   │   │   ├── firestore_mcp.py    # Database operations
│   │   │   ├── notifications_mcp.py # SMS/email alerts
│   │   │   ├── pdf_mcp.py          # PDF generation
│   │   │   └── logging_mcp.py      # Audit logging
│   │   ├── api/v1/
│   │   │   ├── router.py           # URL prefix registration
│   │   │   ├── auth.py             # Login, register, demo-login
│   │   │   ├── emergency.py        # Incident CRUD + agent trigger
│   │   │   ├── dashboard.py        # Stats and system status
│   │   │   ├── missions.py         # Mission CRUD
│   │   │   ├── resources.py        # Shelter/Hospital/Inventory
│   │   │   └── reports.py          # PDF download
│   │   └── websocket/
│   │       └── manager.py          # Room-based WebSocket manager
│   ├── tests/
│   │   ├── test_main.py
│   │   └── test_api.py
│   ├── requirements.txt
│   └── Dockerfile
└── frontend/                       # Next.js 14 Dashboard
    ├── app/
    │   ├── layout.tsx              # Root layout
    │   ├── page.tsx                # Root redirect to /login
    │   ├── globals.css             # Global styles, Leaflet CSS
    │   ├── (auth)/
    │   │   ├── login/page.tsx      # Login with Demo Login button
    │   │   └── register/page.tsx   # User registration
    │   └── dashboard/
    │       ├── layout.tsx          # Dashboard shell with sidebar/header
    │       ├── page.tsx            # Overview: stats, alerts, weather
    │       ├── incidents/page.tsx  # Incident list and submission form
    │       ├── map/page.tsx        # Live Leaflet disaster map
    │       ├── resources/page.tsx  # Shelter & hospital management
    │       ├── missions/page.tsx   # Rescue mission tracker
    │       ├── reports/page.tsx    # PDF report downloader
    │       └── settings/page.tsx   # User & system settings
    ├── components/
    │   ├── Header.tsx              # Top nav with clock and notifications
    │   ├── Sidebar.tsx             # Left navigation drawer
    │   ├── dashboard/              # StatsCards, AlertFeed, etc.
    │   └── map/DisasterMap.tsx     # Client-side Leaflet map
    ├── next.config.js
    ├── tailwind.config.ts
    └── Dockerfile
```

---

## 🔄 Multi-Agent Orchestration Flow

```mermaid
sequenceDiagram
    autonumber
    actor Citizen as Citizen/Responder
    participant API as FastAPI
    participant ORCH as Orchestrator
    participant INTAKE as Intake Agent
    participant DETECT as Detection Agent
    participant LOC as Location Agent
    participant RES as Resource Agent
    participant RESCUE as Rescue Agent
    participant NOTIF as Notification Agent
    participant REPORT as Report Agent
    database DB as MockDB/Firestore

    Citizen->>API: POST /api/v1/incidents
    API->>DB: Store incident (status: reported)
    API->>ORCH: Trigger background pipeline
    
    ORCH->>INTAKE: 1. Validate & sanitize
    INTAKE-->>ORCH: Cleaned incident data
    
    par Parallel Phase
        ORCH->>DETECT: 2a. Classify threat (Gemini)
        DETECT-->>ORCH: severity + type
    and
        ORCH->>LOC: 2b. Geocode + weather
        LOC-->>ORCH: address + nearby resources
    end
    
    ORCH->>RES: 3. Allocate shelter + hospital
    RES->>DB: Reserve inventory
    
    ORCH->>RESCUE: 4. Plan tactical operation
    RESCUE->>DB: Create Mission record
    
    ORCH->>NOTIF: 5. Send SMS/email alerts
    ORCH->>REPORT: 6. Generate PDF brief
    ORCH->>DB: Mark workflow complete
    ORCH-->>API: WebSocket: workflow_completed
```

---

## 🎭 Demo Mode vs AI Mode

AegisAI supports **two execution modes** with zero code changes required:

### 🟢 Demo Mode (Default — No API Keys Required)
Clone the repo and start both servers. Everything works immediately using:
- In-memory Mock Database with **20+ realistic Indian disaster incidents**
- Simulated multi-agent pipelines with realistic mock responses
- Mock weather data, geocoding, and SMS/email (logged to console)
- All 7 ADK agents execute through a heuristic fallback pipeline

### 🔵 AI Mode (Optional — Add API Keys)
Add your `GEMINI_API_KEY` to `.env` to unlock:
- Real **Gemini 2.0 Flash** disaster classification
- Live weather via OpenWeatherMap (add `OPENWEATHER_API_KEY`)
- Real geocoding via Google Maps (add `GOOGLE_MAPS_API_KEY`)
- Live SMS via Twilio (add `TWILIO_*` keys)
- Live email via SendGrid (add `SENDGRID_API_KEY`)
- Cloud persistence via Firestore (add `FIRESTORE_*` keys)

---

## 👤 Demo Accounts

> ⚠️ These are **demonstration credentials for local development only**. Change all passwords before any production deployment.

| Role | Email | Password | Access Level |
|---|---|---|---|
| **Admin** | admin@aegisai.com | `Admin@123` | Full system access |
| **Operator** | operator@aegisai.com | `Operator@123` | Incident + Mission management |
| **District Officer** | govt@aegisai.com | `Govt@123` | Government-level access |
| **Volunteer** | volunteer@aegisai.com | `Volunteer@123` | Field operations |
| **Citizen** | citizen@aegisai.com | `Citizen@123` | Report submission only |

**Quick Access:** Click the **"Demo Login (Admin)"** button on the login page for immediate dashboard access.

---

## 🛠️ Setup & Local Installation

### Prerequisites
- Python 3.10+ (Python 3.11 recommended)
- Node.js 18+
- Git

### Step 1: Clone Repository
```bash
git clone https://github.com/your-username/AegisAI.git
cd AegisAI
```

### Step 2: Configure Environment
```bash
# Copy environment template
cp .env.example .env
```
For **Demo Mode**: no further changes needed — just start the servers.  
For **AI Mode**: edit `.env` and add your `GEMINI_API_KEY`.

### Step 3: Start Backend (FastAPI)
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate
# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start development server
python -m uvicorn app.main:app --reload --port 8000
```

> 📌 Backend runs at: **`http://localhost:8000`**  
> 📖 API docs at: **`http://localhost:8000/api/docs`**

### Step 4: Start Frontend (Next.js)
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

> 📌 Dashboard runs at: **`http://localhost:3000`**

> 💡 **Windows PowerShell note:** If you get a script execution error, run:  
> `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`

---

## 🐳 Docker Deployment

```bash
# Build and start both services
docker compose up --build

# Stop services
docker compose down
```

- **Frontend:** `http://localhost:3000`
- **Backend:** `http://localhost:8000`

---

## 🔒 Security Architecture

| Feature | Implementation |
|---|---|
| **Authentication** | JWT (HS256) with access + refresh tokens |
| **Password Hashing** | bcrypt (native module, Python 3.13 compatible) |
| **Role-Based Access** | 5 roles: admin, government, ngo, volunteer, citizen |
| **Prompt Injection** | Regex-based detection with 30+ attack patterns |
| **Rate Limiting** | SlowAPI: 5/min for reports, 20/min public, 100/min auth |
| **CORS** | Restricted to configured frontend origins |
| **Input Validation** | Pydantic v2 with strict field validators |
| **No Hardcoded Secrets** | All credentials via environment variables |

---

## 📡 API Reference

### Authentication
```
GET  /api/v1/auth/demo-login      # Quick demo access token
POST /api/v1/auth/register        # Register new user
POST /api/v1/auth/login           # Login with credentials
GET  /api/v1/auth/me              # Current user profile
```

### Incidents
```
POST /api/v1/incidents/           # Report new emergency
GET  /api/v1/incidents            # List all incidents
GET  /api/v1/incidents/{id}       # Get incident details
PUT  /api/v1/incidents/{id}/resolve   # Resolve an incident
PATCH /api/v1/incidents/{id}/status   # Update status (admin)
```

### Resources
```
GET   /api/v1/resources/shelters  # List shelters
PATCH /api/v1/resources/shelters/{id}/occupancy   # Update capacity
GET   /api/v1/resources/hospitals # List hospitals
PATCH /api/v1/resources/hospitals/{id}/beds       # Update beds
GET   /api/v1/resources/inventory # Warehouse inventory
```

### Missions
```
GET   /api/v1/missions            # List rescue missions
GET   /api/v1/missions/{id}       # Mission details
PATCH /api/v1/missions/{id}       # Update mission status
```

### Dashboard
```
GET /api/v1/dashboard/stats       # Aggregated stats (counts, recent incidents)
GET /api/v1/dashboard/system-status # API health check
```

### Reports
```
GET /api/v1/reports               # List generated briefs
GET /api/v1/reports/{id}/download # Download PDF brief
```

---

## 🌐 WebSocket Events

Connect to: `ws://localhost:8000/ws/dashboard`

| Event | Description |
|---|---|
| `incident_created` | New incident registered |
| `agent_progress` | Agent pipeline state update |
| `workflow_completed` | Full agent pipeline finished |
| `incident_updated` | Incident status changed |
| `mission_updated` | Mission status changed |
| `shelter_updated` | Shelter occupancy changed |
| `hospital_updated` | Hospital beds changed |

---

## 🚢 Production Deployment Checklist

Before deploying to production:

- [ ] Change `SECRET_KEY` to a strong random key (min. 32 chars)
- [ ] Set `ENVIRONMENT=production` and `DEBUG=false`
- [ ] Add real `GEMINI_API_KEY` for AI features
- [ ] Configure Firestore for persistent data
- [ ] Add Twilio/SendGrid for real notifications
- [ ] Set up SSL/TLS (HTTPS)
- [ ] Configure proper CORS origins
- [ ] Use a reverse proxy (Nginx/Caddy)
- [ ] Set up container orchestration (Kubernetes/Cloud Run)

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **AI Agents** | Google Agent Development Kit (ADK) + Gemini 2.0 Flash |
| **Backend** | FastAPI 0.111 + Python 3.11 |
| **Database** | In-Memory MockDB / Google Cloud Firestore |
| **Auth** | JWT (python-jose) + bcrypt |
| **MCP** | Model Context Protocol (6 servers) |
| **Frontend** | Next.js 14 (App Router) + TypeScript |
| **Styling** | Tailwind CSS v3 + Custom CSS |
| **Maps** | Leaflet.js + CartoDB Dark Tiles |
| **WebSockets** | FastAPI native WebSocket support |
| **PDF** | ReportLab |
| **SMS** | Twilio |
| **Email** | SendGrid |
| **Notifications** | OpenWeatherMap |
| **Rate Limiting** | SlowAPI |
| **Logging** | structlog |
| **Container** | Docker + Docker Compose |
