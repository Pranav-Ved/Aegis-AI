import httpx
import structlog
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from app.mcp_servers.base import BaseMCPServer
from app.core.config import settings

logger = structlog.get_logger(__name__)

MOCK_WEATHER = {
    "temp_celsius": 29.5,
    "humidity_pct": 92,
    "wind_speed_kmh": 45.0,
    "wind_direction": "SW",
    "condition": "Heavy Rain",
    "description": "Severe monsoon precipitation with high winds and flood danger",
    "visibility_km": 3.0,
    "pressure_hpa": 997,
    "feels_like_celsius": 35.0,
    "timestamp": datetime.utcnow().isoformat()
}

MOCK_FORECAST = [
    {"date": (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%d"), "max_temp": 30.0, "min_temp": 25.0, "condition": "Heavy Rain", "precipitation_mm": 120.0, "wind_speed_kmh": 50.0},
    {"date": (datetime.utcnow() + timedelta(days=2)).strftime("%Y-%m-%d"), "max_temp": 29.0, "min_temp": 24.0, "condition": "Thunderstorm", "precipitation_mm": 180.0, "wind_speed_kmh": 65.0},
    {"date": (datetime.utcnow() + timedelta(days=3)).strftime("%Y-%m-%d"), "max_temp": 28.0, "min_temp": 24.0, "condition": "Continuous Rain", "precipitation_mm": 85.0, "wind_speed_kmh": 40.0},
    {"date": (datetime.utcnow() + timedelta(days=4)).strftime("%Y-%m-%d"), "max_temp": 31.0, "min_temp": 26.0, "condition": "Scattered Showers", "precipitation_mm": 20.0, "wind_speed_kmh": 25.0},
    {"date": (datetime.utcnow() + timedelta(days=5)).strftime("%Y-%m-%d"), "max_temp": 32.0, "min_temp": 27.0, "condition": "Partly Cloudy", "precipitation_mm": 5.0, "wind_speed_kmh": 15.0}
]

MOCK_STORM_ALERTS = [
    {
        "alert_type": "Cyclone Alert / Severe Rainfall Warning",
        "severity": "critical",
        "description": "Active deep depression over the Arabian Sea is moving towards coastal Maharashtra. Expected wind speeds up to 75 km/h. Extremely heavy rainfall (exceeding 200mm) expected in low-lying areas of Mumbai. Risk of coastal storm surge.",
        "start_time": datetime.utcnow().isoformat(),
        "end_time": (datetime.utcnow() + timedelta(days=2)).isoformat(),
        "source": "India Meteorological Department (IMD)"
    }
]

class WeatherMCPServer(BaseMCPServer):
    name = "weather-mcp"
    description = "Provides weather forecasts, current conditions, storm warnings, and risk indices"

    async def get_current_weather(self, lat: float, lng: float) -> dict:
        """Get current weather conditions at coordinates."""
        async def _run():
            if settings.openweather_api_key:
                url = "https://api.openweathermap.org/data/2.5/weather"
                params = {
                    "lat": lat,
                    "lon": lng,
                    "units": "metric",
                    "appid": settings.openweather_api_key
                }
                async with httpx.AsyncClient() as client:
                    resp = await client.get(url, params=params)
                    if resp.status_code == 200:
                        data = resp.json()
                        return {
                            "temp_celsius": data["main"]["temp"],
                            "humidity_pct": data["main"]["humidity"],
                            "wind_speed_kmh": round(data["wind"]["speed"] * 3.6, 2), # convert m/s to km/h
                            "wind_direction": str(data["wind"].get("deg", "N")),
                            "condition": data["weather"][0]["main"],
                            "description": data["weather"][0]["description"],
                            "visibility_km": round(data.get("visibility", 10000) / 1000.0, 1),
                            "pressure_hpa": data["main"]["pressure"],
                            "feels_like_celsius": data["main"]["feels_like"],
                            "timestamp": datetime.utcnow().isoformat()
                        }
            
            # Fallback
            return MOCK_WEATHER
            
        res = await self._execute_tool("get_current_weather", _run)
        return res.to_dict()

    async def get_forecast(self, lat: float, lng: float, days: int = 3) -> dict:
        """Get weather forecast for the next N days."""
        async def _run():
            if settings.openweather_api_key:
                url = "https://api.openweathermap.org/data/2.5/forecast"
                params = {
                    "lat": lat,
                    "lon": lng,
                    "units": "metric",
                    "appid": settings.openweather_api_key
                }
                async with httpx.AsyncClient() as client:
                    resp = await client.get(url, params=params)
                    if resp.status_code == 200:
                        data = resp.json()
                        daily_forecasts = []
                        # OpenWeather returns 3-hour chunks, let's group or select one per day (approx index intervals of 8)
                        for i in range(0, min(len(data.get("list", [])), days * 8), 8):
                            day_data = data["list"][i]
                            daily_forecasts.append({
                                "date": day_data["dt_txt"].split(" ")[0],
                                "max_temp": day_data["main"]["temp_max"],
                                "min_temp": day_data["main"]["temp_min"],
                                "condition": day_data["weather"][0]["main"],
                                "precipitation_mm": day_data.get("rain", {}).get("3h", 0.0) + day_data.get("snow", {}).get("3h", 0.0),
                                "wind_speed_kmh": round(day_data["wind"]["speed"] * 3.6, 2)
                            })
                        return daily_forecasts
                        
            # Fallback
            return MOCK_FORECAST[:days]
            
        res = await self._execute_tool("get_forecast", _run)
        return res.to_dict()

    async def get_storm_alerts(self, lat: float, lng: float) -> dict:
        """Fetch active meteorological and cyclone alert reports."""
        async def _run():
            # In production, call weather API alert endpoints. Fallback for now.
            return MOCK_STORM_ALERTS
            
        res = await self._execute_tool("get_storm_alerts", _run)
        return res.to_dict()

    async def assess_disaster_risk(self, lat: float, lng: float) -> dict:
        """Combine current weather conditions with storm warnings to gauge safety index."""
        async def _run():
            weather = MOCK_WEATHER
            if settings.openweather_api_key:
                w_result = await self.get_current_weather(lat, lng)
                if w_result["success"]:
                    weather = w_result["data"]
            
            # Simple heuristic formula for risk assessment
            wind = weather["wind_speed_kmh"]
            humidity = weather["humidity_pct"]
            cond = weather["condition"].lower()
            
            risk_factors = []
            risk_score = 0
            
            if wind > 60:
                risk_score += 40
                risk_factors.append("Gale force winds (>60 km/h)")
            elif wind > 40:
                risk_score += 20
                risk_factors.append("Strong winds (>40 km/h)")
                
            if "rain" in cond or "storm" in cond or "shower" in cond:
                risk_score += 30
                risk_factors.append("Heavy monsoon rainfall active")
                if humidity > 90:
                    risk_score += 15
                    risk_factors.append("Saturated atmospheric conditions")
            elif "cyclone" in cond or "hurricane" in cond:
                risk_score += 60
                risk_factors.append("Active tropical storm center")
                
            risk_level = "low"
            recommendation = "Normal conditions. Stay informed."
            
            if risk_score >= 80:
                risk_level = "critical"
                recommendation = "Immediate evacuation warning for low-lying and coastal regions. Shelter in place in secure concrete structures. Do not travel."
            elif risk_score >= 50:
                risk_level = "high"
                recommendation = "High risk of flash flooding and structural damage. Emergency responders on standby. Stay indoors and prepare emergency kits."
            elif risk_score >= 30:
                risk_level = "medium"
                recommendation = "Caution advised. Minor waterlogging in low areas. Monitor local weather channels."
                
            return {
                "risk_level": risk_level,
                "risk_score": risk_score,
                "risk_factors": risk_factors,
                "recommendation": recommendation
            }
            
        res = await self._execute_tool("assess_disaster_risk", _run)
        return res.to_dict()

weather_mcp = WeatherMCPServer()
