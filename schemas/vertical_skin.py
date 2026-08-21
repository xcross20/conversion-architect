"""
VerticalSkin Schema
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class Vertical(str, Enum):
    HOME_SERVICES = "home_services"
    LEGAL = "legal"
    MEDICAL = "medical"
    DENTAL = "dental"
    AUTOMOTIVE = "automotive"
    REAL_ESTATE = "real_estate"
    FINANCIAL = "financial"
    INSURANCE = "insurance"
    EDUCATION = "education"
    B2B_SERVICES = "b2b_services"
    ECOMMERCE = "ecommerce"
    OTHER = "other"


class SkinStatus(str, Enum):
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    EXPERIMENTAL = "experimental"


class VerticalSkin(BaseModel):
    """VerticalSkin defines visual tokens specific to a vertical.
    
    Skin tokens include colors, typography, imagery style, and
    perceptual cues that vary by vertical.
    """
    
    # Identity
    skin_id: str = Field(..., description="Unique skin identifier")
    name: str = Field(..., description="Human-readable skin name")
    vertical: Vertical = Field(..., description="Primary vertical")
    family_id: str = Field(..., description="Parent family ID")
    status: SkinStatus = Field(default=SkinStatus.ACTIVE)
    
    # Visual tokens
    colors: dict[str, Any] = Field(
        default_factory=dict,
        description="Color tokens: primary, secondary, accent, backgrounds, text"
    )
    typography: dict[str, Any] = Field(
        default_factory=dict,
        description="Typography tokens: font families, sizes, weights, line heights"
    )
    imagery_style: dict[str, Any] = Field(
        default_factory=dict,
        description="Image style tokens: photo types, illustration style, icons"
    )
    spacing_overrides: dict[str, int] = Field(
        default_factory=dict,
        description="Vertical-specific spacing overrides from family"
    )
    
    # Perception cues
    trust_signals: list[str] = Field(
        default_factory=list,
        description="Trust signal types (certifications, reviews, guarantees)"
    )
    urgency_tokens: list[str] = Field(
        default_factory=list,
        description="Urgency cue types (limited time, scarcity, proximity)"
    )
    authority_markers: list[str] = Field(
        default_factory=list,
        description="Authority signal types (credentials, awards, media)"
    )
    
    # Compliance
    required_disclosures: list[str] = Field(
        default_factory=list,
        description="Legal disclosures required for this vertical"
    )
    restricted_claims: list[str] = Field(
        default_factory=list,
        description="Claims not permitted in this vertical"
    )
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    meta_data: dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "skin_id": "emergency_home_services_v1",
                "name": "Emergency Home Services",
                "vertical": "home_services",
                "family_id": "portfolio_v1",
                "status": "active",
                "colors": {
                    "primary": "#E53935",
                    "secondary": "#1565C0",
                    "accent": "#FFC107",
                    "background_light": "#FAFAFA",
                    "text_primary": "#212121",
                    "text_secondary": "#757575"
                },
                "typography": {
                    "font_family_primary": "Inter, sans-serif",
                    "font_family_headings": "Inter, sans-serif",
                    "base_size": 16,
                    "scale_ratio": 1.25
                },
                "trust_signals": ["license_badge", "insurance_badge", "review_stars", "guarantee_badge"],
                "urgency_tokens": ["24_hour", "same_day", "available_now"],
                "required_disclosures": ["license_number", "service_area"],
                "restricted_claims": ["only_provider", "lowest_price"]
            }
        }
