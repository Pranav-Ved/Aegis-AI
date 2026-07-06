import uuid
import structlog
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from app.core.config import settings

logger = structlog.get_logger(__name__)

class MockDB:
    """
    In-memory Mock Database with realistic seed data.
    Used for local development when Firestore credentials are not provided.
    """
    def __init__(self):
        self._store: Dict[str, Dict[str, Dict[str, Any]]] = {
            "users": {},
            "incidents": {},
            "missions": {},
            "shelters": {},
            "hospitals": {},
            "resources": {},
            "audit_logs": {},
            "notifications": {},
            "reports": {},
            "volunteers": {},
            "vehicles": {},
            "warehouses": {},
            "resource_requests": {}
        }
        self._seed_data()
        
    def _seed_data(self):
        # 1. Seed Users (passwords are 'Admin@123', 'Govt@123', etc.)
        admin_pw = "$2b$12$8bks.LD9RZsLMnizlNnWmOco3s5F4VI6TKr/0It5nKaDTTTWvvwg."
        gov_pw = "$2b$12$JFiKS4TtW3zKJURIp7H6aOIIRvI5/ZTIp04c7cWYvOZ5pauK5xamK"
        
        roles = [
            ("admin", "admin@aegisai.com", "AegisAI Admin", admin_pw),
            ("government", "govt@aegisai.com", "Govt Officer", gov_pw),
            ("operator", "operator@aegisai.com", "Emergency Operator", admin_pw),
            ("volunteer", "volunteer@aegisai.com", "Lead Volunteer", admin_pw),
            ("citizen", "citizen@aegisai.com", "Rahul Sharma", admin_pw)
        ]
        for role, email, name, pw in roles:
            uid = f"user_{role}_001"
            self._store["users"][uid] = {
                "id": uid,
                "email": email,
                "name": name,
                "role": role,
                "phone": "+91-98765-00000",
                "hashed_password": pw,
                "is_active": True,
                "created_at": datetime.utcnow().isoformat()
            }

        # 2. Seed 25 Shelters across India
        shelter_data = [
            ("shelter_001", "Dharavi Relief Center", "Dharavi, Mumbai", 19.0380, 72.8526, 500, 287, ["water", "food", "medical", "blankets", "charging"]),
            ("shelter_002", "BKC Emergency Camp", "Bandra Kurla Complex, Mumbai", 19.0642, 72.8669, 300, 298, ["water", "food", "blankets"]),
            ("shelter_003", "Andheri Sports Ground Camp", "Andheri East, Mumbai", 19.1136, 72.8697, 800, 145, ["water", "food", "medical", "blankets", "wifi"]),
            ("shelter_004", "Dwarka Community Hall", "Sector 10, Dwarka, Delhi", 28.5823, 77.0500, 400, 120, ["water", "food", "medical"]),
            ("shelter_005", "Rohini Sports Complex", "Sector 9, Rohini, Delhi", 28.7158, 77.1210, 600, 50, ["water", "blankets"]),
            ("shelter_006", "Salt Lake Stadium Block A", "Salt Lake, Kolkata", 22.5694, 88.4093, 1000, 410, ["water", "food", "medical", "blankets", "charging"]),
            ("shelter_007", "Howrah Girls School", "Howrah, Kolkata", 22.5851, 88.3180, 250, 240, ["water", "food"]),
            ("shelter_008", "Chennai Central Relief Camp", "Periamet, Chennai", 13.0824, 80.2750, 700, 620, ["water", "food", "medical", "blankets", "wifi"]),
            ("shelter_009", "Velachery Flood Shelter", "Velachery, Chennai", 12.9815, 80.2224, 500, 480, ["water", "food", "medical"]),
            ("shelter_010", "Secunderabad Club Grounds", "Secunderabad, Hyderabad", 17.4436, 78.4900, 350, 90, ["water", "food", "charging"]),
            ("shelter_011", "Gachibowli Stadium Shelter", "Gachibowli, Hyderabad", 17.4401, 78.3489, 1200, 150, ["water", "food", "medical", "wifi"]),
            ("shelter_012", "Koramangala Indoor Stadium", "Koramangala, Bangalore", 12.9352, 77.6244, 900, 230, ["water", "food", "medical", "blankets"]),
            ("shelter_013", "Whitefield Community Center", "Whitefield, Bangalore", 12.9698, 77.7499, 450, 40, ["water", "blankets"]),
            ("shelter_014", "Sabarmati Ashram Camp", "Sabarmati, Ahmedabad", 23.0605, 72.5808, 400, 350, ["water", "food", "medical"]),
            ("shelter_015", "Pune Cantonment Hall", "Camp, Pune", 18.5132, 73.8830, 500, 280, ["water", "food", "blankets", "charging"]),
            ("shelter_016", "Bhubaneswar Exhibition Ground", "Unit 3, Bhubaneswar", 20.2798, 85.8398, 800, 750, ["water", "food", "medical", "blankets"]),
            ("shelter_017", "Puri Temple Road Dharamshala", "Puri, Odisha", 19.8049, 85.8178, 600, 580, ["water", "food", "blankets"]),
            ("shelter_018", "Guwahati Commerce College Hall", "RG Baruah Rd, Guwahati", 26.1732, 91.7756, 300, 290, ["water", "food"]),
            ("shelter_019", "Kadavanthra Indoor Stadium", "Ernakulam, Kochi", 9.9675, 76.2954, 700, 110, ["water", "food", "medical", "wifi"]),
            ("shelter_020", "Vizag Port Trust Golden Jubilee Hall", "Port Area, Vishakhapatnam", 17.6974, 83.2987, 850, 800, ["water", "food", "medical", "blankets", "charging"]),
            ("shelter_021", "Shimla Municipal Hall", "Mall Road, Shimla", 31.1044, 77.1743, 200, 180, ["water", "blankets", "heating"]),
            ("shelter_022", "Dehradun Parade Ground Camp", "Dehradun", 30.3256, 78.0435, 500, 150, ["water", "food", "medical"]),
            ("shelter_023", "Srinagar Tourist Reception Centre", "Srinagar", 34.0722, 74.8210, 600, 550, ["water", "food", "heating", "medical"]),
            ("shelter_024", "Patna Gandhi Maidan Shelter", "Patna", 25.6174, 85.1438, 1500, 1300, ["water", "food", "medical", "blankets"]),
            ("shelter_025", "Nagpur Town Hall", "Mahal, Nagpur", 21.1441, 79.1032, 400, 80, ["water", "food", "charging"])
        ]
        for sid, name, address, lat, lng, cap, occ, amen in shelter_data:
            status_val = "full" if occ >= cap else "open"
            self._store["shelters"][sid] = {
                "id": sid,
                "name": name,
                "address": address,
                "location": {"lat": lat, "lng": lng},
                "total_capacity": cap,
                "current_occupancy": occ,
                "amenities": amen,
                "contact": f"+91-{lat:.4f}".replace(".", "-")[:14],
                "status": status_val,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }

        # 3. Seed 15 Hospitals across India
        hospital_data = [
            ("hospital_001", "KEM Hospital", "Parel, Mumbai", 18.9967, 72.8414, 200, 47, ["trauma", "burns", "pediatrics", "ICU"]),
            ("hospital_002", "Lokmanya Tilak Municipal Hospital", "Sion, Mumbai", 19.0390, 72.8619, 150, 12, ["trauma", "general", "ICU"]),
            ("hospital_003", "AIIMS Delhi Trauma Centre", "Safdarjung Enclave, Delhi", 28.5672, 77.2100, 300, 110, ["trauma", "burns", "ICU", "neuro"]),
            ("hospital_004", "Ram Manohar Lohia Hospital", "Baba Kharak Singh Marg, Delhi", 28.6247, 77.2025, 250, 15, ["trauma", "ICU"]),
            ("hospital_005", "SSKM Hospital", "A.J.C. Bose Road, Kolkata", 22.5398, 88.3444, 400, 85, ["trauma", "cardiology", "ICU"]),
            ("hospital_006", "Rajiv Gandhi Government General Hospital", "Park Town, Chennai", 13.0805, 80.2743, 500, 140, ["trauma", "burns", "pediatrics", "ICU"]),
            ("hospital_007", "NIMS Hyderabad", "Punjagutta, Hyderabad", 17.4239, 78.4554, 300, 68, ["trauma", "neuro", "ICU"]),
            ("hospital_008", "Victoria Hospital", "Kalasipalyam, Bangalore", 12.9632, 77.5739, 350, 95, ["trauma", "burns", "ICU"]),
            ("hospital_009", "Ahmedabad Civil Hospital", "Asarwa, Ahmedabad", 23.0511, 72.6033, 600, 240, ["trauma", "burns", "ICU", "pediatrics"]),
            ("hospital_010", "Sassoon General Hospital", "Near Pune Station, Pune", 18.5283, 73.8741, 400, 108, ["trauma", "ICU", "general"]),
            ("hospital_011", "AIIMS Bhubaneswar", "Sijua, Bhubaneswar", 20.2445, 85.7761, 300, 140, ["trauma", "ICU", "neuro"]),
            ("hospital_012", "Guwahati Medical College Hospital", "Bhangagarh, Guwahati", 26.1559, 91.7687, 450, 18, ["trauma", "pediatrics", "ICU"]),
            ("hospital_013", "Ernakulam General Hospital", "Cochin, Kochi", 9.9723, 76.2818, 250, 45, ["trauma", "ICU"]),
            ("hospital_014", "King George Hospital", "Maharanipeta, Vishakhapatnam", 17.7082, 83.3039, 350, 30, ["trauma", "burns", "ICU"]),
            ("hospital_015", "Patna Medical College Hospital", "Patna", 25.6206, 85.1554, 500, 190, ["trauma", "ICU", "general"])
        ]
        for hid, name, address, lat, lng, cap, beds, spec in hospital_data:
            hstatus = "operational" if beds > 0 else "overwhelmed"
            self._store["hospitals"][hid] = {
                "id": hid,
                "name": name,
                "address": address,
                "location": {"lat": lat, "lng": lng},
                "emergency_capacity": cap,
                "available_beds": beds,
                "specialties": spec,
                "contact": f"+91-{lng:.4f}".replace(".", "-")[:14],
                "status": hstatus,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }

        # 4. Seed Resources in Stock
        self._store["resources"]["res_001"] = {
            "id": "res_001",
            "type": "food",
            "quantity": 150000,
            "unit": "meals",
            "warehouse_name": "NDRF Central Warehouse A",
            "location": {"lat": 19.0760, "lng": 72.8777},
            "allocated_to": None,
            "last_updated": datetime.utcnow().isoformat()
        }
        self._store["resources"]["res_002"] = {
            "id": "res_002",
            "type": "water",
            "quantity": 500000,
            "unit": "liters",
            "warehouse_name": "NDRF Central Warehouse A",
            "location": {"lat": 19.0760, "lng": 72.8777},
            "allocated_to": None,
            "last_updated": datetime.utcnow().isoformat()
        }
        self._store["resources"]["res_003"] = {
            "id": "res_003",
            "type": "medicine",
            "quantity": 85000,
            "unit": "kits",
            "warehouse_name": "Medical Store B",
            "location": {"lat": 19.0540, "lng": 72.8325},
            "allocated_to": None,
            "last_updated": datetime.utcnow().isoformat()
        }
        self._store["resources"]["res_004"] = {
            "id": "res_004",
            "type": "blankets",
            "quantity": 40000,
            "unit": "pieces",
            "warehouse_name": "NDRF Central Warehouse A",
            "location": {"lat": 19.0760, "lng": 72.8777},
            "allocated_to": None,
            "last_updated": datetime.utcnow().isoformat()
        }

        # 5. Seed 20 Disaster Incidents across India
        cities_dict = {
            "mumbai": (19.0760, 72.8777, "Mumbai, Maharashtra"),
            "delhi": (28.6139, 77.2090, "Delhi National Capital Region"),
            "kolkata": (22.5726, 88.3639, "Kolkata, West Bengal"),
            "chennai": (13.0827, 80.2707, "Chennai, Tamil Nadu"),
            "hyderabad": (17.3850, 78.4867, "Hyderabad, Telangana"),
            "bangalore": (12.9716, 77.5946, "Bangalore, Karnataka"),
            "ahmedabad": (23.0225, 72.5714, "Ahmedabad, Gujarat"),
            "pune": (18.5204, 73.8567, "Pune, Maharashtra"),
            "bhubaneswar": (20.2961, 85.8245, "Bhubaneswar, Odisha"),
            "guwahati": (26.1445, 91.7362, "Guwahati, Assam"),
            "kochi": (9.9312, 76.2673, "Kochi, Kerala"),
            "vizag": (17.6868, 83.2185, "Vishakhapatnam, Andhra Pradesh"),
            "shimla": (31.1048, 77.1734, "Shimla, Himachal Pradesh"),
            "dehradun": (30.3165, 78.0322, "Dehradun, Uttarakhand"),
            "srinagar": (34.0837, 74.7973, "Srinagar, Jammu & Kashmir"),
            "nagpur": (21.1458, 79.0882, "Nagpur, Maharashtra"),
            "patna": (25.5941, 85.1376, "Patna, Bihar"),
            "jaipur": (26.9124, 75.7873, "Jaipur, Rajasthan"),
            "lucknow": (26.8467, 80.9462, "Lucknow, Uttar Pradesh"),
            "bhopal": (23.2599, 77.4126, "Bhopal, Madhya Pradesh")
        }

        incident_raw = [
            ("inc_001", "Dharavi Sectors 3 & 5 Flooding", "flood", "critical", "active", "mumbai", "Severe flooding in Dharavi slum area. Ground floor houses completely submerged under 6 feet of water. 15 families stranded on roofs. Water levels rising."),
            ("inc_002", "Rohini Industrial Area Chemical Leak", "chemical_leak", "critical", "active", "delhi", "Toxic chlorine gas leaking from industrial storage tank in Rohini Sector 16. Local residents reporting breathing difficulties and skin irritation. Evacuation needed."),
            ("inc_003", "Kolkata Cyclone Amphan Destruction", "cyclone", "critical", "resolved", "kolkata", "Severe cyclonic winds in Kolkata central. Downed power lines, uprooted trees blocking main arterial roads, and partial collapse of old structures in Central Avenue."),
            ("inc_004", "Velachery Urban Waterlogging", "flood", "high", "active", "chennai", "Heavily flooded roads in Velachery area after 25cm rainfall. Water entered residential apartments. Elderly residents need urgent evacuation and food supply."),
            ("inc_005", "Secunderabad Commercial Building Collapse", "building_collapse", "critical", "active", "hyderabad", "A 4-story commercial complex collapsed in Secunderabad near Metro Station. An estimated 25 people are feared trapped inside the debris. NDRF search underway."),
            ("inc_006", "Bangalore Forest Fire near Bannerghatta", "wildfire", "medium", "active", "bangalore", "Forest fire spreading through the buffer zone of Bannerghatta National Park. Wind pushing smoke toward adjacent residential layouts. Forest department fighting."),
            ("inc_007", "Shimla National Highway Landslide", "landslide", "high", "active", "shimla", "Massive landslide near NH-5 blocking road connectivity to Shimla. Three tourist vehicles trapped under debris. Heavy earthmovers deployed for clearance."),
            ("inc_008", "Dehradun Earthquake Tremors Damage", "earthquake", "medium", "reported", "dehradun", "Earthquake tremors of magnitude 5.2 felt across Dehradun. Structural cracks reported in several multi-story apartments. No casualties confirmed yet."),
            ("inc_009", "Wayanad Landslide Disaster", "landslide", "critical", "active", "kochi", "Major landslide in Wayanad hills following heavy monsoon downpour. Two villages completely cut off, roads washed away. Rescue operations underway."),
            ("inc_010", "Jhelum River Crossing Floods", "flood", "high", "active", "srinagar", "Jhelum River flowing above danger mark. Low-lying areas of Srinagar flooded. Local administration issuing red alerts and shifting families to tourist centre shelter."),
            ("inc_011", "Vizag Port Trust Oil Spill & Fire", "chemical_leak", "critical", "resolved", "vizag", "Chemical oil spill followed by minor fire at Vizag port terminal. Port fire fighters successfully contained the spill and extinguished the fire. Clean-up in progress."),
            ("inc_012", "Yamuna Expressway Multi-Vehicle Collision", "road_accident", "medium", "resolved", "delhi", "10-car pile-up on Yamuna Expressway due to dense morning fog. 15 injured citizens transported to nearby trauma centers. Road cleared for traffic."),
            ("inc_013", "Cyclone Fani Coastline Destruction", "cyclone", "high", "resolved", "bhubaneswar", "Cyclone Fani made landfall in Odisha coast. High velocity winds destroyed semi-permanent shelters, disrupted electricity, and washed away coastal roads in Puri."),
            ("inc_014", "Patna Ganga River Overflow Flooding", "flood", "critical", "active", "patna", "Ganga river overflowed near Patna ghats, inundating several low-lying blocks. Thousands displaced, emergency boats distributing food packets."),
            ("inc_015", "Guwahati Brahmaputra River Flood Rescue", "flood", "high", "active", "guwahati", "Brahmaputra river water entered urban areas of Guwahati. Flooding reported in commercial complexes. Rescue teams deploying inflatable dinghies."),
            ("inc_016", "Ahmedabad Chemical Unit Explosion", "fire", "high", "active", "ahmedabad", "Boiler blast at chemical processing unit in Vatva GIDC industrial estate. Large fire engulfing the factory premises. 8 worker casualties reported."),
            ("inc_017", "Old Lucknow Haveli Structural Collapse", "building_collapse", "medium", "active", "lucknow", "A 100-year-old vacant haveli partially collapsed in Chowk area, Lucknow. Adjacent houses damaged. Municipal authorities evacuating neighbors."),
            ("inc_018", "Bhopal Satpura Forest Wildfire", "wildfire", "medium", "reported", "bhopal", "Wildfire reported in forest reserve adjacent to Bhopal outskirts. Smoke affecting visibility on state highway. Forest patrol teams investigating."),
            ("inc_019", "Nagpur Medical Outbreak Emergency", "medical_emergency", "medium", "resolved", "nagpur", "Sudden surge in waterborne diseases in outer Nagpur blocks after water contamination. Mobile medical units deployed to treat affected citizens."),
            ("inc_020", "Jaipur Jaipur-Delhi Highway Bus Crash", "road_accident", "high", "active", "jaipur", "A passenger tourist bus overturned on the Jaipur-Delhi highway. 35 passengers injured, 4 trapped inside the vehicle. Fire department cutting the cabin.")
        ]

        for iid, name, itype, sev, status, city_key, desc in incident_raw:
            lat, lng, address = cities_dict[city_key]
            self._store["incidents"][iid] = {
                "id": iid,
                "description": desc,
                "incident_type": itype,
                "severity": sev,
                "status": status,
                "location": {"lat": lat, "lng": lng, "address": f"{name}, {address}"},
                "media_urls": [],
                "reporter_name": "Emergency System Reporter",
                "reporter_phone": "+91-99999-88888",
                "agent_status": {
                    "emergency_intake": "completed",
                    "disaster_detection": "completed",
                    "location_intelligence": "completed",
                    "resource_coordination": "completed",
                    "rescue_planning": "completed"
                },
                "detection_result": {
                    "incident_type": itype,
                    "confidence": 0.95,
                    "severity": sev,
                    "description": f"AI classified {itype} threat of {sev} severity.",
                    "ai_available": True
                },
                "location_context": {
                    "address": f"{name}, {address}",
                    "nearby_shelters": [],
                    "nearby_hospitals": [],
                    "weather_summary": "Monsoon / Humid, Temp: 29C, Wind: 15km/h",
                    "risk_level": sev
                },
                "resource_plan": {
                    "recommended_shelter": None,
                    "recommended_hospital": None,
                    "resources_allocated": [{"type": "food", "quantity": 500, "unit": "meals"}],
                    "estimated_arrival_minutes": 25
                },
                "rescue_plan": {
                    "priority_level": 1 if sev=="critical" else 2,
                    "rescue_steps": ["Secure perimeter", "Evacuate survivors", "Administer first aid", "Transport to shelter"],
                    "team_assignment": {"name": "NDRF Quick Response Team", "members_count": 12},
                    "estimated_completion_hours": 6.5
                },
                "created_at": (datetime.utcnow() - timedelta(hours=int(iid.split("_")[1]))).isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }

        # 6. Seed 10 Rescue Missions
        missions_raw = [
            ("mis_001", "inc_001", "Dharavi Flood Rescue Mission", "Evacuate 15 stranded citizens from rooftops in Dharavi Sectors 3 and 5.", "shelter_001", "hospital_001"),
            ("mis_002", "inc_002", "Rohini Chemical Containment Operation", "Contain the leaking chlorine gas valve and evacuate residents in 1km radius.", "shelter_004", "hospital_003"),
            ("mis_004", "inc_004", "Velachery Flood Evacuation", "Transport stranded elderly citizens via rescue rafts to Velachery Relief Shelter.", "shelter_009", "hospital_006"),
            ("mis_005", "inc_005", "Secunderabad Building Collapse Search & Rescue", "Exhume trapped victims from debris using acoustic sensors and search dogs.", "shelter_010", "hospital_007"),
            ("mis_007", "inc_007", "Shimla Landslide Road Clearance", "Clear NH-5 debris using earthmovers and rescue trapped tourists inside cars.", "shelter_021", "hospital_003"),
            ("mis_009", "inc_009", "Wayanad Landslide Rescue Operation", "Deploy military and NDRF units to transport stranded villagers in Wayanad.", "shelter_019", "hospital_013"),
            ("mis_010", "inc_010", "Srinagar Low-Lying Area Evacuation", "Ferry flooded sector families to Srinagar Tourist Reception Centre Shelter.", "shelter_023", "hospital_012"),
            ("mis_014", "inc_014", "Patna Flood Supply Distribution", "Distribute water purification tablets and food packets to flooded sectors.", "shelter_024", "hospital_015"),
            ("mis_015", "inc_015", "Guwahati Brahmaputra Flood Rescue", "Evacuate stranded merchants from commercial markets using motorboats.", "shelter_018", "hospital_012"),
            ("mis_020", "inc_020", "Jaipur highway Bus Extraction Mission", "Use cutters to open overturned tourist bus cabin and rescue passengers.", "shelter_004", "hospital_004")
        ]

        for mid, iid, title, desc, sid, hid in missions_raw:
            self._store["missions"][mid] = {
                "id": mid,
                "incident_id": iid,
                "status": "active" if mid != "mis_007" else "completed",
                "priority": 1 if mid in ["mis_001", "mis_002", "mis_005", "mis_009"] else 2,
                "title": title,
                "description": desc,
                "rescue_steps": [
                    {"order": 1, "description": "Deploy response units to the coordinates", "status": "completed", "completed_at": datetime.utcnow().isoformat()},
                    {"order": 2, "description": "Execute search & rescue / hazard containment", "status": "active" if mid != "mis_007" else "completed", "completed_at": datetime.utcnow().isoformat() if mid == "mis_007" else None},
                    {"order": 3, "description": "Transport victims to designated shelters/hospitals", "status": "pending" if mid != "mis_007" else "completed", "completed_at": datetime.utcnow().isoformat() if mid == "mis_007" else None}
                ],
                "assigned_teams": [
                    {"id": "team_01", "name": "NDRF Quick Response Team", "role": "Search and Rescue Operations", "contact": "+91-90000-11111"}
                ],
                "shelter_id": sid,
                "hospital_id": hid,
                "resources_allocated": [
                    {"type": "food", "quantity": 100, "unit": "meals"},
                    {"type": "water", "quantity": 200, "unit": "liters"}
                ],
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            # Link mission to incident
            if iid in self._store["incidents"]:
                self._store["incidents"][iid]["mission_id"] = mid

        # 7. Seed 50 Volunteers
        volunteer_first = ["Amit", "Sunita", "Rajesh", "Pooja", "Vikram", "Neha", "Sanjay", "Anjali", "Ramesh", "Deepa"]
        volunteer_last = ["Sharma", "Verma", "Patel", "Singh", "Joshi", "Das", "Reddy", "Nair", "Gupta", "Rao"]
        volunteer_roles = ["Medical First Aid", "Food Distribution", "Debris Clearance", "Logistics Driver", "Shelter Management"]
        
        for idx in range(1, 51):
            vid = f"vol_{idx:03d}"
            name = f"{volunteer_first[idx % 10]} {volunteer_last[(idx * 3) % 10]}"
            role = volunteer_roles[idx % 5]
            self._store["volunteers"][vid] = {
                "id": vid,
                "name": name,
                "role": role,
                "phone": f"+91-98200-{idx:05d}",
                "status": "available" if idx % 3 != 0 else "deployed",
                "assigned_mission_id": "mis_001" if idx % 3 == 0 else None,
                "created_at": datetime.utcnow().isoformat()
            }

        # 8. Seed 20 Vehicles
        vehicle_types = ["Ambulance", "Rescue Boat", "Fire Tender", "Logistics Truck", "Heavy Excavator"]
        for idx in range(1, 21):
            veid = f"veh_{idx:03d}"
            vtype = vehicle_types[idx % 5]
            self._store["vehicles"][veid] = {
                "id": veid,
                "name": f"Aegis-{vtype}-{idx}",
                "type": vtype.lower().replace(" ", "_"),
                "registration_no": f"MH-12-EQ-{idx:04d}",
                "status": "available" if idx % 4 != 0 else "deployed",
                "assigned_mission_id": "mis_001" if idx % 4 == 0 else None,
                "created_at": datetime.utcnow().isoformat()
            }

        # 9. Seed 15 Warehouses
        warehouse_names = [
            "Central Depot Mumbai", "Delhi Logistics Hub", "Kolkata Port Warehouse",
            "Chennai Relief Storage", "Hyderabad Emergency Depot", "Bangalore Supply Base",
            "Ahmedabad Materials Yard", "Pune Support Depot", "Bhubaneswar Reserve",
            "Guwahati Brahmaputra Depot", "Kochi Shipping Storage", "Vizag Port Depot",
            "Shimla Alpine Reserve", "Dehradun Valley Storage", "Srinagar Base Camp Depot"
        ]
        for idx, wname in enumerate(warehouse_names, 1):
            whid = f"wh_{idx:03d}"
            self._store["warehouses"][whid] = {
                "id": whid,
                "name": wname,
                "address": f"Industrial Sector {idx}, {wname.split(' ')[-2]}",
                "inventory": {
                    "food": 1000 * idx,
                    "water": 2000 * idx,
                    "medicine": 500 * idx,
                    "blankets": 800 * idx
                },
                "created_at": datetime.utcnow().isoformat()
            }

        # 10. Seed 100 Notifications (alerts generated by System / Agents)
        descriptions = [
            "Heavy rainfall warning issued for coastal districts.",
            "Emergency shelter fully occupied. Redirecting survivors.",
            "Rescue mission status updated to completed.",
            "Boats deployed for water extraction operations.",
            "Medical kits dispatch confirmed from Warehouse B.",
            "Volunteer squad deployed to shelter.",
            "Weather alert: cyclone winds expected to increase.",
            "Critical incident reported. Operator review required."
        ]
        for idx in range(1, 101):
            nid = f"notif_{idx:03d}"
            self._store["notifications"][nid] = {
                "id": nid,
                "type": "alert" if idx % 3 == 0 else "info",
                "message": f"[System Alert] {descriptions[idx % len(descriptions)]} (Ref: #{idx:03d})",
                "status": "unread" if idx <= 20 else "read",
                "created_at": (datetime.utcnow() - timedelta(minutes=15 * idx)).isoformat()
            }

        # 11. Seed 30 Reports (PDF situation reports mock metadata)
        for idx in range(1, 31):
            repid = f"rep_{idx:03d}"
            ref_inc = f"inc_{1 + (idx % 20):03d}"
            self._store["reports"][repid] = {
                "id": repid,
                "incident_id": ref_inc,
                "title": f"Situation Brief Report - {ref_inc.upper()}",
                "file_path": f"/tmp/aegisai_reports/brief_{repid}.pdf",
                "generated_by": "Report Generation Agent",
                "created_at": (datetime.utcnow() - timedelta(hours=idx * 2)).isoformat()
            }

        # 12. Seed 15 Resource Requests
        req_types = ["food", "water", "medicine", "blankets"]
        for idx in range(1, 16):
            req_id = f"req_{idx:03d}"
            self._store["resource_requests"][req_id] = {
                "id": req_id,
                "incident_id": f"inc_{1 + (idx % 20):03d}",
                "item_type": req_types[idx % 4],
                "quantity": 100 * idx,
                "unit": "meals" if idx%4==0 else "liters" if idx%4==1 else "kits" if idx%4==2 else "pieces",
                "status": "pending" if idx <= 5 else "approved" if idx <= 12 else "fulfilled",
                "requester_role": "volunteer",
                "created_at": (datetime.utcnow() - timedelta(hours=idx)).isoformat()
            }


    async def create_document(self, collection: str, data: dict, doc_id: Optional[str] = None) -> str:
        if collection not in self._store:
            self._store[collection] = {}
        new_id = doc_id or str(uuid.uuid4())
        self._store[collection][new_id] = {**data, "id": new_id}
        return new_id
        
    async def get_document(self, collection: str, doc_id: str) -> Optional[dict]:
        if collection not in self._store or doc_id not in self._store[collection]:
            return None
        return {**self._store[collection][doc_id]}
        
    async def update_document(self, collection: str, doc_id: str, data: dict) -> bool:
        if collection not in self._store or doc_id not in self._store[collection]:
            return False
            
        current = self._store[collection][doc_id]
        
        # Support dot-notation nested updates
        for key, value in data.items():
            if "." in key:
                parts = key.split(".")
                nested = current
                for part in parts[:-1]:
                    if part not in nested or not isinstance(nested[part], dict):
                        nested[part] = {}
                    nested = nested[part]
                nested[parts[-1]] = value
            else:
                current[key] = value
                
        self._store[collection][doc_id] = current
        return True
        
    async def delete_document(self, collection: str, doc_id: str) -> bool:
        if collection not in self._store or doc_id not in self._store[collection]:
            return False
        del self._store[collection][doc_id]
        return True
        
    async def query_collection(
        self, 
        collection: str, 
        filters: List[dict] = None, 
        limit: int = 100, 
        order_by: str = None
    ) -> List[dict]:
        if collection not in self._store:
            return []
            
        results = list(self._store[collection].values())
        
        if filters:
            for f in filters:
                field = f.get("field")
                op = f.get("op", "==")
                value = f.get("value")
                
                filtered = []
                for doc in results:
                    doc_val = doc
                    if "." in field:
                        for part in field.split("."):
                            if isinstance(doc_val, dict):
                                doc_val = doc_val.get(part)
                            else:
                                doc_val = None
                    else:
                        doc_val = doc.get(field)
                        
                    if op == "==" and doc_val == value:
                        filtered.append(doc)
                    elif op == "!=" and doc_val != value:
                        filtered.append(doc)
                    elif op == ">" and doc_val > value:
                        filtered.append(doc)
                    elif op == "<" and doc_val < value:
                        filtered.append(doc)
                    elif op == ">=" and doc_val >= value:
                        filtered.append(doc)
                    elif op == "<=" and doc_val <= value:
                        filtered.append(doc)
                    elif op == "in" and isinstance(value, list) and doc_val in value:
                        filtered.append(doc)
                results = filtered
                
        if order_by:
            descending = order_by.startswith("-")
            field = order_by.lstrip("-")
            results.sort(key=lambda x: str(x.get(field, "")), reverse=descending)
            
        return [ {**doc} for doc in results[:limit] ]
        
    async def batch_write(self, operations: List[dict]) -> bool:
        for op in operations:
            op_type = op.get("type")
            collection = op.get("collection")
            doc_id = op.get("doc_id")
            data = op.get("data", {})
            
            if op_type == "create" or op_type == "set":
                await self.create_document(collection, data, doc_id)
            elif op_type == "update":
                await self.update_document(collection, doc_id, data)
            elif op_type == "delete":
                await self.delete_document(collection, doc_id)
        return True


class FirestoreDB:
    """
    Production-ready wrapper around Google Cloud Firestore.
    """
    def __init__(self):
        import firebase_admin
        from firebase_admin import credentials, firestore
        
        cred = credentials.Certificate(settings.firestore_credentials_path)
        try:
            firebase_admin.get_app()
        except ValueError:
            firebase_admin.initialize_app(cred, {"projectId": settings.firestore_project_id})
            
        self.db = firestore.client()
        
    async def create_document(self, collection: str, data: dict, doc_id: Optional[str] = None) -> str:
        ref = self.db.collection(collection)
        if doc_id:
            ref.document(doc_id).set(data)
            return doc_id
        else:
            _, doc_ref = ref.add(data)
            return doc_ref.id
            
    async def get_document(self, collection: str, doc_id: str) -> Optional[dict]:
        doc = self.db.collection(collection).document(doc_id).get()
        if not doc.exists:
            return None
        return doc.to_dict()
        
    async def update_document(self, collection: str, doc_id: str, data: dict) -> bool:
        doc_ref = self.db.collection(collection).document(doc_id)
        doc_ref.update(data)
        return True
        
    async def delete_document(self, collection: str, doc_id: str) -> bool:
        self.db.collection(collection).document(doc_id).delete()
        return True
        
    async def query_collection(
        self, 
        collection: str, 
        filters: List[dict] = None, 
        limit: int = 100, 
        order_by: str = None
    ) -> List[dict]:
        ref = self.db.collection(collection)
        
        if filters:
            for f in filters:
                field = f.get("field")
                op = f.get("op", "==")
                value = f.get("value")
                ref = ref.where(field, op, value)
                
        if order_by:
            descending = order_by.startswith("-")
            field = order_by.lstrip("-")
            direction = "DESCENDING" if descending else "ASCENDING"
            ref = ref.order_by(field, direction=direction)
            
        ref = ref.limit(limit)
        docs = ref.stream()
        return [doc.to_dict() for doc in docs]
        
    async def batch_write(self, operations: List[dict]) -> bool:
        batch = self.db.batch()
        for op in operations:
            op_type = op.get("type")
            collection = op.get("collection")
            doc_id = op.get("doc_id")
            data = op.get("data", {})
            
            ref = self.db.collection(collection).document(doc_id)
            if op_type == "create" or op_type == "set":
                batch.set(ref, data)
            elif op_type == "update":
                batch.update(ref, data)
            elif op_type == "delete":
                batch.delete(ref)
        batch.commit()
        return True

_db_instance = None

def get_db() -> MockDB | FirestoreDB:
    global _db_instance
    if _db_instance is None:
        if settings.db_mode == "firestore":
            logger.info("Initializing Firestore database connection", project=settings.firestore_project_id)
            _db_instance = FirestoreDB()
        else:
            logger.info("Initializing In-Memory Mock Database")
            _db_instance = MockDB()
    return _db_instance

async def get_db_dep():
    yield get_db()
