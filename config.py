from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    # App
    APP_NAME: str = "PromptForge Academy"
    TAGLINE: str = "Forge Your AI Future"
    DEBUG: bool = True
    SECRET_KEY: str = "promptforge-secret-key-change-in-production"

    # Database
    DATABASE_URL: str = "sqlite:///./promptforge.db"

    # JWT
    JWT_SECRET: str = "jwt-secret-key-change-in-production"
    JWT_EXPIRE_HOURS: int = 24

    # bdApps (Demo Mode)
    DEMO_MODE: bool = True
    DEMO_OTP: str = "123456"
    BDAPPS_APP_ID: str = "APP_DEMO123"
    BDAPPS_PASSWORD: str = "demo_password"
    BDAPPS_BASE_URL: str = "https://developer.bdapps.com"

    # Charge
    CHARGE_AMOUNT: str = "2.78"
    CURRENCY: str = "BDT"

    # Supported Operators
    ROBI_PREFIX: str = "8801"
    VALID_PREFIXES: list = ["88018", "88016"]

    # Claude AI
    GEMINI_API_KEY: str = ""
    class Config:
        env_file = ".env"

settings = Settings()