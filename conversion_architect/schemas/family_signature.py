"""
FamilySignature Schema
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class SignatureType(str, Enum):
    HEADLINE = "headline"
    CTA = "cta"
    SPACING = "spacing"
    PROOF = "proof"
    MOBILE = "mobile"
    OVERALL = "overall"


class ValidationLevel(str, Enum):
    REQUIRED = "required"
    RECOMMENDED = "recommended"
    OPTIONAL = "optional"


class FamilySignature(BaseModel):
    """FamilySignature defines grammar rules for a specific design element.
    
    Each signature constrains how a design element should behave while
    allowing variation within those constraints.
    """
    
    # Identity
    signature_id: str = Field(..., description="Unique signature identifier")
    family_id: str = Field(..., description="Parent family ID")
    signature_type: SignatureType = Field(..., description="Type of signature")
    
    # Constraints
    validation_level: ValidationLevel = Field(default=ValidationLevel.REQUIRED)
    constraints: dict[str, Any] = Field(
        default_factory=dict,
        description="Structural constraints (e.g., min/max length, required elements)"
    )
    patterns: list[str] = Field(
        default_factory=list,
        description="Allowed pattern names"
    )
    anti_patterns: list[str] = Field(
        default_factory=list,
        description="Explicitly forbidden patterns"
    )
    
    # Tone/perception
    tone_markers: list[str] = Field(
        default_factory=list,
        description="Tone indicators (urgent, trust, premium, etc.)"
    )
    perception_goals: list[str] = Field(
        default_factory=list,
        description="Desired perceptions (urgency, trust, clarity, etc.)"
    )
    
    # Responsiveness
    breakpoints: dict[str, int] = Field(
        default_factory=lambda: {"mobile": 640, "tablet": 1024, "desktop": 1280},
        description="Responsive breakpoints in pixels"
    )
    responsive_variants: dict[str, dict[str, Any]] = Field(
        default_factory=dict,
        description="Type-specific overrides per breakpoint"
    )
    
    # Provenance
    source: str = Field(default="manual", description="Pattern source (motionsites, manual, etc.)")
    source_id: str | None = Field(None, description="External pattern ID if applicable")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    meta_data: dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "signature_id": "headline_emergency_hvac_v1",
                "family_id": "emergency_home_services_v1",
                "signature_type": "headline",
                "validation_level": "required",
                "constraints": {
                    "max_length": 60,
                    "min_length": 20,
                    "structure": "urgency | benefit"
                },
                "patterns": ["question_open", "command_verb", "number_lead"],
                "anti_patterns": ["question_mark_ending", "passive_voice"],
                "tone_markers": ["urgent", "clarifying"],
                "perception_goals": ["trust", "urgency"],
                "source": "motionsites",
                "source_id": "ms_headline_urgency_001"
            }
        }
