"""
Configuration for Halloween Quest Telegram Bot
"""

import os
from dataclasses import dataclass

@dataclass
class BotConfig:
    # Telegram Bot Settings
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "7909656312:AAEtxP0EFV4PqmttfhHMTdCZz_pRIH9_H2I")
    BOT_USERNAME: str = os.getenv("BOT_USERNAME", "imashaquestbot")
    
    # API Settings
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("PORT", os.getenv("API_PORT", "8080")))
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///halloween_quest.db")
    
    # Web App URL
    WEB_APP_URL: str = os.getenv("WEB_APP_URL", "https://imasha.ru")
    
    # File Storage
    PHOTOS_DIR: str = os.getenv("PHOTOS_DIR", "./uploads/photos")
    MAX_PHOTO_SIZE: int = 10 * 1024 * 1024  # 10MB

# Global config instance
config = BotConfig()
