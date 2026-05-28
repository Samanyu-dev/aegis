import os
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional

class Settings(BaseSettings):
    BRIGHT_DATA_SERP_API_KEY: Optional[str] = Field(None, env="BRIGHT_DATA_SERP_API_KEY")
    BRIGHT_DATA_WEB_UNLOCKER_URL: Optional[str] = Field(None, env="BRIGHT_DATA_WEB_UNLOCKER_URL")
    BRIGHT_DATA_SCRAPING_BROWSER_URL: Optional[str] = Field(None, env="BRIGHT_DATA_SCRAPING_BROWSER_URL")
    
    AIML_API_KEY: Optional[str] = Field(None, env="AIML_API_KEY")
    AIML_API_BASE_URL: str = Field("https://api.aimlapi.com/v1", env="AIML_API_BASE_URL")
    
    COGNEE_API_KEY: Optional[str] = Field(None, env="COGNEE_API_KEY")
    TRIGGERWARE_WEBHOOK_URL: Optional[str] = Field(None, env="TRIGGERWARE_WEBHOOK_URL")
    
    # Use SQLite as fallback if PostgreSQL database url is not provided
    DATABASE_URL: Optional[str] = Field(None, env="DATABASE_URL")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

# Fetch environment, fallback to process environment variables directly if needed
settings = Settings()
