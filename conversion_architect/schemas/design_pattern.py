"""
DesignPattern Schema
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class PageType(str, Enum):
    LANDING = "landing"
    SQUEEZE = "squeeze"
    SALES = "sales"
    QUIZ = "quiz"
    LEAD_CAPTURE = "lead_capture"
    CONTACT = "contact"
    ABOUT = "about"


class SectionType(str, Enum):
    HERO = "hero"
    FEATURES = "features"
    BENEFITS = "benefits"
    PRICING = "pricing"
    TESTIMONIALS = "testimonials"
    FAQ = "faq"
    CTA = "cta"
    GUARANTEE = "guarantee"
    TRUST_BADGES = "trust_badges"
    FORM = "form"
    FOOTER = "footer"
    NAVIGATION = "navigation"
    STICKY_BAR = "sticky_bar"


class DesiredPerception(str, Enum):
    URGENCY = "urgency"
    TRUST = "trust"
    PREMIUM = "premium"
    VALUE = "value"
    CONVENIENCE = "convenience"
    EXPERTISE = "expertise"
    SAFETY = "safety"
    SPEED = "speed"
    AFFORDABILITY = "affordability"
    SIMPLICITY = "simplicity"


class DesignPattern(BaseModel):
    """DesignPattern represents a reusable section or element pattern.
    
    Patterns are sourced from MotionSites (or fixture providers) and
    provide proven layouts for specific purposes.
    """
    
    # Identity
    pattern_id: str = Field(..., description="Unique pattern identifier")
    name: str = Field(..., description="Human-readable pattern name")
    
    # Classification
    page_type: PageType = Field(..., description="Primary page type")
    section_type: SectionType = Field(..., description="Section type")
    perceptions: list[DesiredPerception] = Field(
        default_factory=list,
        description="Desired perceptions this pattern supports"
    )
    
    # Content structure
    structure: dict[str, Any] = Field(
        default_factory=dict,
        description="Structural definition (elements, layout, flow)"
    )
    elements: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Element definitions with types and constraints"
    )
    content_slots: dict[str, Any] = Field(
        default_factory=dict,
        description="Named content slots to fill with offer/claim data"
    )
    
    # Variants
    variants: list[str] = Field(
        default_factory=list,
        description="Variant names (a, b, c, dark, light, etc.)"
    )
    responsive_strategies: dict[str, dict[str, Any]] = Field(
        default_factory=dict,
        description="Responsive handling per breakpoint"
    )
    
    # Constraints
    min_content: dict[str, Any] = Field(
        default_factory=dict,
        description="Minimum content requirements"
    )
    max_content: dict[str, Any] = Field(
        default_factory=dict,
        description="Maximum content limits"
    )
    
    # Provenance
    source: str = Field(default="motionsites", description="Pattern source")
    source_id: str | None = Field(None, description="External pattern ID")
    source_url: str | None = Field(None, description="Preview URL")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    usage_count: int = Field(default=0, description="Times used in genomes")
    conversion_benchmark: float | None = Field(None, description="Known CVR benchmark")
    
    # Constraints from parent
    cannot_override: list[str] = Field(
        default_factory=lambda: ["offer", "claims", "economics", "accessibility", 
                                 "family_signature", "cta_hierarchy"],
        description="Aspects this pattern cannot change"
    )
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    meta_data: dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "pattern_id": "hero_urgency_home_services_v1",
                "name": "Hero - Urgency (Home Services)",
                "page_type": "landing",
                "section_type": "hero",
                "perceptions": ["urgency", "trust", "speed"],
                "structure": {
                    "layout": "split",
                    "columns": {"desktop": 2, "mobile": 1},
                    "background": "gradient"
                },
                "elements": [
                    {"type": "headline", "slot": "main_headline", "required": True},
                    {"type": "subheadline", "slot": "sub_headline", "required": True},
                    {"type": "cta_button", "slot": "primary_cta", "required": True},
                    {"type": "trust_badge", "slot": "trust_indicators", "required": True}
                ],
                "content_slots": {
                    "main_headline": {"type": "text", "max_length": 60},
                    "primary_cta": {"type": "cta", "cta_type": "phone"}
                },
                "source": "motionsites",
                "source_id": "ms_hero_urgency_001"
            }
        }
