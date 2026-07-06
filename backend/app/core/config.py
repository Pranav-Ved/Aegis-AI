from typing import Optional, List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Application Config
    app_name: str = "AegisAI"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = True
    
    # JWT Security
    secret_key: str = "CHANGE-ME-IN-PRODUCTION-USE-STRONG-RANDOM-KEY-AT-LEAST-32-CHARS"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # AI / Gemini Config
    gemini_api_key: Optional[str] = None
    
    # Maps Config
    google_maps_api_key: Optional[str] = None
    
    # Database Config
    firestore_project_id: Optional[str] = None
    firestore_credentials_path: Optional[str] = None
    
    # Notifications Config
    twilio_account_sid: Optional[str] = None
    twilio_auth_token: Optional[str] = None
    twilio_from_number: Optional[str] = None
    sendgrid_api_key: Optional[str] = None
    sendgrid_from_email: str = "noreply@aegisai.example.com"
    
    # Weather Config
    openweather_api_key: Optional[str] = None
    
    # URLs and CORS Config
    frontend_url: str = "http://localhost:3000"
    backend_url: str = "http://localhost:8000"
    cors_origins: List[str] = [
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://localhost:3002",
        "http://127.0.0.1:3002",
        "http://localhost:3003",
        "http://127.0.0.1:3003"
    ]
    
    # Rate Limiting Config
    rate_limit_public: str = "20/minute"
    rate_limit_authenticated: str = "100/minute"
    rate_limit_emergency: str = "5/minute"

    @property
    def gemini_available(self) -> bool:
        return bool(self.gemini_api_key and self.gemini_api_key.strip())
    
    @property
    def db_mode(self) -> str:
        return "firestore" if (self.firestore_project_id and self.firestore_credentials_path) else "mock"
    
    @property
    def notifications_mode(self) -> str:
        if self.twilio_account_sid or self.sendgrid_api_key:
            return "live"
        return "mock"
    
    @property
    def maps_mode(self) -> str:
        return "google" if self.google_maps_api_key else "mock"
    
    @property
    def weather_mode(self) -> str:
        return "live" if self.openweather_api_key else "mock"

settings = Settings()
