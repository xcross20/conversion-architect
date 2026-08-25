"""
Conversion Architect API Configuration
"""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class GA4Settings(BaseSettings):
    """Google Analytics MCP configuration."""
    
    enabled: bool = Field(default=True)
    property_id: str = Field(default="")
    credentials_path: str = Field(default="")
    project_id: str = Field(default="")
    mcp_command: str = Field(default="")
    cache_ttl_seconds: int = Field(default=3600)
    
    model_config = SettingsConfigDict(env_prefix="GA4_")


class APISettings(BaseSettings):
    """API configuration."""
    
    api_key: str = Field(default="")
    cors_origins: list[str] = Field(
        default_factory=lambda: [
            "*",  # Framer plugin can be hosted anywhere
        ]
    )
    
    model_config = SettingsConfigDict(env_prefix="")


class Settings(BaseSettings):
    """Application settings."""
    
    app_name: str = Field(default="conversion-architect-api")
    app_env: str = Field(default="development")
    app_debug: bool = Field(default=True)
    app_host: str = Field(default="0.0.0.0")
    app_port: int = Field(default=8000)
    
    ga4: GA4Settings = Field(default_factory=GA4Settings)
    api: APISettings = Field(default_factory=APISettings)
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()