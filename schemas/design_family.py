"""
DesignFamily Schema
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class DesignFamilyStatus(str, Enum):
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    EXPERIMENTAL = "experimental"


class DesignFamily(BaseModel):
    """DesignFamily is a collection of family signatures defining design grammar.
    
    This is the canonical container for design rules. Framer objects are NOT
    canonical — they are output targets only.
    """
    
    # Identity
    family_id: str = Field(..., description="Unique family identifier")
    name: str = Field(..., description="Human-readable family name")
    version: str = Field(default="1.0.0", description="Semantic version")
    status: DesignFamilyStatus = Field(default=DesignFamilyStatus.ACTIVE)
    
    # Description
    description: str | None = Field(None, description="Family description")
    vertical: str | None = Field(None, description="Primary vertical (or None for universal)")
    
    # Signatures (grammar rules)
    headline_grammar: dict[str, Any] = Field(
        default_factory=dict,
        description="Headline structure rules: H1 format, length limits, tone markers"
    )
    cta_grammar: dict[str, Any] = Field(
        default_factory=dict,
        description="CTA rules: size ranges, shape, color contrast specs"
    )
    spacing_grammar: dict[str, Any] = Field(
        default_factory=dict,
        description="Grid/spacing rules: base unit, rhythm, responsive breakpoints"
    )
    proof_grammar: dict[str, Any] = Field(
        default_factory=dict,
        description="Social proof rules: testimonial format, star placement, attribution"
    )
    mobile_grammar: dict[str, Any] = Field(
        default_factory=dict,
        description="Mobile rules: sticky action bar behavior, touch targets, viewport"
    )
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    tags: list[str] = Field(default_factory=list)
    meta_data: dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "family_id": "portfolio_v1",
                "name": "Portfolio Master Family",
                "version": "1.0.0",
                "status": "active",
                "vertical": None,
                "headline_grammar": {
                    "h1_structure": "benefit_statement | hook",
                    "max_length": 70,
                    "tone_markers": ["urgent", "clarifying", "social"]
                },
                "cta_grammar": {
                    "primary_size": {"min_width": 200, "height": 56},
                    "shape": "rounded",
                    "contrast_ratio": 4.5
                },
                "spacing_grammar": {
                    "base_unit": 8,
                    "rhythm": [8, 16, 24, 32, 48, 64]
                },
                "proof_grammar": {
                    "testimonial_format": "problem_agitation_solution",
                    "star_placement": "left_aligned"
                },
                "mobile_grammar": {
                    "sticky_bar": True,
                    "touch_target_min": 44
                }
            }
        }
