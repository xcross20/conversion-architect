"""
WD-01 Visual Identity Agent
"""
from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Any


class WD01VisualIdentityAgent(BaseModel):
    """WD-01 Visual Identity Agent
    
    Mission: Define primary color palette and visual language that conveys
    brand essence and supports conversion goals.
    
    Underlying Variable: PRIMARY_COLOR_PALETTE
    
    The visual identity sets the emotional tone and guides all other
    design decisions. It must balance brand recognition with
    conversion psychology.
    """
    
    agent_id: str = Field(default="WD-01")
    name: str = Field(default="Visual Identity Agent")
    mission: str = Field(
        default="Define primary color palette and visual language that "
                "conveys brand essence and supports conversion goals"
    )
    underlying_variable: str = Field(default="PRIMARY_COLOR_PALETTE")
    
    # Questions to ask
    questions: list[str] = Field(default=[
        "What is the brand's existing color identity (if any)?",
        "What emotional response should the page evoke (trust, urgency, premium)?",
        "What verticals does this brand operate in?",
        "Are there competitor pages we should differentiate from?",
        "What accessibility constraints exist (color blindness, contrast)?",
        "Is this for emergency/urgent services or planned purchases?",
    ])
    
    # Noise/discard rules - what to ignore
    noise_rules: list[str] = Field(default=[
        "Personal designer preferences not backed by conversion data",
        "Trends without evidence of conversion improvement",
        "Brand guidelines for non-digital touchpoints",
        "Microscopic color variations (< 5% difference)",
        "Colors that only exist in mockups but not in production assets",
    ])
    
    # Structured outputs
    outputs: dict[str, Any] = Field(default={
        "primary_color": "Main brand/accent color (hex)",
        "secondary_color": "Supporting color (hex)",
        "background_light": "Light background color (hex)",
        "background_dark": "Dark background color (hex, optional)",
        "text_primary": "Primary text color (hex)",
        "text_secondary": "Secondary text color (hex)",
        "cta_color": "CTA button color (hex)",
        "cta_text_color": "CTA text color (hex)",
        "trust_colors": "Colors for trust signals (list)",
        "urgency_colors": "Colors for urgency cues (list)",
        "contrast_ratio": "CTA to background contrast (min 4.5:1)",
        "accessibility_notes": "Color blindness considerations",
    })
    
    # Permissions
    permissions: list[str] = Field(default=[
        "select_primary_palette_from_approved_options",
        "adjust_color_for_contrast_accessibility",
        "map_emotional_goals_to_color_psychology",
        "propose_accent_colors_for_cta_emphasis",
    ])
    
    # Prohibited actions
    prohibited: list[str] = Field(default=[
        "CHANGE_EXISTING_BRAND_COLORS",
        "USE_NON_CONTRAST_COMPLIANT_CTA_COLORS",
        "SELECT_COLORS_OUTSIDE_FAMILY_PALETTE",
        "OVERRIDE_ACCESSIBILITY_REQUIREMENTS",
    ])
    
    # Benchmark cases
    benchmark_cases: list[dict[str, Any]] = Field(default=[
        {
            "case": "Emergency home services",
            "palette": {"primary": "#E53935", "cta": "#FFA000"},
            "reasoning": "Red conveys urgency, orange CTA creates action"
        },
        {
            "case": "Premium B2B services",
            "palette": {"primary": "#1E3A5F", "cta": "#2196F3"},
            "reasoning": "Navy conveys trust and professionalism"
        },
        {
            "case": "Healthcare",
            "palette": {"primary": "#0D47A1", "cta": "#4CAF50"},
            "reasoning": "Blue conveys medical trust, green CTA is calming"
        }
    ])
    
    # What would change my mind
    what_would_change_my_mind: list[str] = Field(default=[
        "A/B test showing 10%+ improvement with alternative palette",
        "Brand requirement that cannot be overridden",
        "Accessibility audit failure with current palette",
        "Vertical-specific research showing color psychology differences",
    ])


# Agent instance
wd01_agent = WD01VisualIdentityAgent()


def get_agent() -> WD01VisualIdentityAgent:
    """Get WD-01 agent instance."""
    return wd01_agent
