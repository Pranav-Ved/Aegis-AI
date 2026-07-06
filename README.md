# 🛡️ AegisAI
### Shielding Lives with Intelligent Response

> An AI-powered Multi-Agent Disaster Management Platform built using **Google ADK**, **MCP Servers**, **FastAPI**, and **Next.js** to coordinate emergency response, optimize resource allocation, and assist disaster management authorities through intelligent agent collaboration.

![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.11+-blue)
![Next.js](https://img.shields.io/badge/Next.js-15-black)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688)
![Google ADK](https://img.shields.io/badge/Google-ADK-green)
![MCP](https://img.shields.io/badge/MCP-Integrated-purple)

---

# 📖 Table of Contents

- Problem Statement
- Solution
- Key Features
- System Architecture
- Multi-Agent Workflow
- MCP Architecture
- Tech Stack
- Folder Structure
- Demo Credentials
- Installation
- Running the Project
- Demo Mode vs AI Mode
- Security Features
- Sample Workflow
- Screenshots
- Future Improvements
- License

---

# 🚨 Problem Statement

Natural disasters demand rapid coordination between emergency responders, hospitals, shelters, volunteers, and government agencies.

Current systems often suffer from:

- Manual coordination
- Delayed resource allocation
- Fragmented communication
- Lack of real-time situational awareness
- Slow decision-making

During critical emergencies, every minute matters.

---

# 💡 Solution

**AegisAI** is an intelligent disaster response platform powered by a **Google ADK Multi-Agent System**.

Instead of relying on a single AI model, AegisAI coordinates multiple specialized agents that collaborate to:

- Detect disasters
- Analyze emergency reports
- Locate incidents
- Allocate nearby resources
- Generate rescue plans
- Notify responders
- Produce situation reports

The platform also integrates **Model Context Protocol (MCP) Servers** for maps, weather, notifications, reports, logging, and database operations.


<img width="1917" height="917" alt="Image" src="https://github.com/user-attachments/assets/f80fb818-3da0-480e-a750-93b44e5707fe" />



---

# ✨ Key Features

## 🤖 Google ADK Multi-Agent System

- Emergency Intake Agent
- Disaster Detection Agent
- Location Intelligence Agent
- Resource Coordination Agent
- Rescue Planning Agent
- Notification Agent
- Report Generation Agent
- Central Orchestrator Agent

---

## 🛰 Real-Time Incident Management

- Emergency reporting
- Incident dashboard
- Disaster categorization
- Severity prediction
- Live updates
- WebSocket synchronization

<img width="1917" height="921" alt="Image" src="https://github.com/user-attachments/assets/f7c34761-04c8-42f1-8be3-5469e340dfec" />

---

## 🗺 Interactive Disaster Map

- Leaflet Maps
- Incident markers
- Shelter locations
- Hospital locations
- Resource tracking
- Live mission visualization

<img width="1912" height="922" alt="Image" src="https://github.com/user-attachments/assets/bc5b0eb2-807d-4030-9a40-96805aca3f8f" />

---

## 🚑 Rescue Coordination

- Shelter allocation
- Hospital assignment
- Volunteer deployment
- Vehicle assignment
- Resource optimization

<img width="1917" height="917" alt="Image" src="https://github.com/user-attachments/assets/ef1dc134-98c5-4620-b9fc-e497a2c26e59" />

---

## 📄 Automated Reports

- Situation reports
- Mission reports
- Incident summaries
- PDF generation

---

## 🔔 Notification System

- Incident notifications
- Mission updates
- Resource alerts
- WebSocket live notifications
- Mock SMS/Email support

---

## 🔒 Security

- JWT Authentication
- Role-Based Access Control (RBAC)
- Prompt Injection Protection
- Safe Tool Execution
- Input Validation
- Structured Logging
- Rate Limiting

---

# 🧠 Multi-Agent Architecture

```
Citizen Report
        │
        ▼
Emergency Intake Agent
        │
        ▼
Disaster Detection Agent
        │
        ▼
Location Intelligence Agent
        │
        ▼
Resource Coordination Agent
        │
        ▼
Rescue Planning Agent
        │
        ▼
Notification Agent
        │
        ▼
Report Generation Agent
        │
        ▼
Dashboard & Authorities
```

---

# 🔌 MCP Architecture

```
                 Google ADK
                      │
        ┌─────────────┼─────────────┐
        │             │             │
   Maps MCP      Weather MCP    Database MCP
        │             │             │
        ├─────────────┼─────────────┤
        │             │             │
Notification MCP   PDF MCP     Logging MCP
```

Each agent communicates with external tools through dedicated MCP servers, enabling modular, secure, and extensible integrations.

---

# 🛠 Tech Stack

## Frontend

- Next.js 15
- React
- TypeScript
- Tailwind CSS
- Leaflet
- React Hook Form

---

## Backend

- FastAPI
- Python
- Pydantic
- WebSockets
- JWT Authentication

---

## AI

- Google ADK
- Multi-Agent Architecture
- Gemini (Optional AI Mode)

---

## MCP Servers

- Maps MCP
- Weather MCP
- Firestore / MockDB MCP
- Notification MCP
- PDF MCP
- Logging MCP

---

## Database

Default:

- MockDB (Offline Demo)

Optional:

- Google Firestore

---

# 📂 Folder Structure

```
AegisAI/

backend/
    app/
        agents/
        api/
        core/
        mcp_servers/
        models/
        services/
        websocket/

frontend/
    app/
    components/
    hooks/

docs/

docker/

README.md

.env.example

docker-compose.yml

requirements.txt
```

---

# 👥 Demo Credentials

| Role | Email | Password |
|------|--------|----------|
| Admin | admin@aegisai.com | admin123 |
| Government Officer | officer@aegisai.com | officer123 |
| Operator | operator@aegisai.com | operator123 |
| Volunteer | volunteer@aegisai.com | volunteer123 |
| Citizen | citizen@aegisai.com | citizen123 |

> These are **demo credentials** for the local MockDB environment only.

---

# ⚙ Installation

## Backend

```bash
cd backend

python -m venv venv

pip install -r requirements.txt

uvicorn app.main:app --reload
```

---

## Frontend

```bash
cd frontend

npm install

npm run dev
```

Frontend:

```
http://localhost:3000
```

Backend:

```
http://localhost:8000
```

---

# 🚀 Running the Project

Clone:

```bash
git clone https://github.com/yourusername/AegisAI.git

cd AegisAI
```

Backend:

```bash
uvicorn app.main:app --reload
```

Frontend:

```bash
npm run dev
```

---

# 🧪 Demo Mode vs AI Mode

## Demo Mode (Default)

No setup required.

Uses:

- Mock AI agents
- Mock database
- Mock notifications
- Local simulation
- Sample disaster data

The application works immediately after cloning.

---

## AI Mode (Optional)

To enable real AI-powered reasoning:

Create a `.env` file:

```env
GEMINI_API_KEY=YOUR_API_KEY
```

The application automatically switches to Google ADK + Gemini when configured.

---

# 🔒 Security Features

- JWT Authentication
- Role-Based Access Control
- Prompt Injection Protection
- Environment Variable Isolation
- Safe MCP Execution
- Secure Input Validation
- Audit Logging
- Password Hashing (bcrypt)

---

# 🌊 Sample Workflow

```
Citizen reports flood

↓

Emergency Intake Agent validates report

↓

Disaster Detection Agent classifies disaster

↓

Location Agent identifies coordinates

↓

Resource Agent allocates nearest shelters

↓

Rescue Planner creates deployment plan

↓

Notification Agent alerts responders

↓

Report Agent generates PDF

↓

Dashboard updates in real time
```

---

# 📊 Mock Dataset

The project ships with a realistic offline dataset including:

- 20 Disaster Incidents
- 10 Rescue Missions
- 25 Shelters
- 15 Hospitals
- 50 Volunteers
- 20 Rescue Vehicles
- 15 Warehouses
- 100 Notifications
- 30 Reports
- 15 Emergency Resource Requests

---

# 📸 Screenshots

Add screenshots here:

- Login Screen

```
docs/screenshots/login.png
```

- Dashboard

```
docs/screenshots/dashboard.png
```

- Incident Map

```
docs/screenshots/map.png
```

- Resource Management

```
docs/screenshots/resources.png
```

- Mission Dashboard

```
docs/screenshots/missions.png
```

---

# 🚀 Future Improvements

- Satellite imagery integration
- Drone coordination
- Voice-based emergency reporting
- Predictive disaster analytics
- Mobile application
- Offline-first disaster response
- Multi-language support
- IoT sensor integration

---

# 🏆 Hackathon Requirements Covered

✅ Google ADK Multi-Agent System

✅ MCP Server Integration

✅ Security Features

✅ Deployable Architecture

✅ Agent Skills

✅ Antigravity Development Workflow

✅ GitHub Documentation

---

# 🤝 Contributing

Contributions, suggestions, and improvements are welcome.

Feel free to fork the project and submit pull requests.

---

# 📜 License

This project is licensed under the MIT License.

---

# ❤️ Acknowledgements

- Google AI
- Google ADK
- Model Context Protocol (MCP)
- FastAPI
- Next.js
- Leaflet
- Open Source Community

---

## ⭐ If you like this project, please consider giving it a star!
