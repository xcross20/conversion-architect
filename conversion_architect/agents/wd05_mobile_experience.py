"""
WD-05 Mobile Experience Agent
"""
from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Any


class WD05MobileExperienceAgent(BaseModel):
    """WD-05 Mobile Experience Agent
    
    Mission: Ensure the landing page delivers an optimal experience
    on mobile devices with appropriate responsive behavior.
    
    Underlying Variable: RESPONSIVE_BEHAVIOR
    
    Mobile-first isn't just about smaller screens. It affects
    touch targets, thumb reach, loading speed, and the entire
    interaction paradigm.
    """
    
    agent_id: str = Field(default="WD-05")
    name: str = Field(default="Mobile Experience Agent")
    mission: str = Field(
        default="Ensure the landing page delivers an optimal experience "
                "on mobile devices with appropriate responsive behavior"
    )
    underlying_variable: str = Field(default="RESPONSIVE_BEHAVIOR")
    
    questions: list[str] = Field(default=[
        "What percentage of traffic is mobile?",
        "Is the primary action click-to-call (mobile-optimized)?",
        "What is the thumb reach zone on mobile?",
        "Are there mobile-specific elements needed (tap-to-call)?",
        "What is the mobile loading budget?",
        "Should sticky bar be mobile-only?",
    ])
    
    noise_rules: list[str] = Field(default=[
        "Desktop-first design considerations",
        "Animations that don't serve mobile UX",
        "Hover states that don't translate to touch",
        "Responsive breakpoints that don't match analytics",
    ])
    
    outputs: dict[str, Any] = Field(default={
        "touch_targets": {"min_size": 44, "recommended": 48},
        "sticky_bar_mobile": "Sticky bar configuration for mobile",
        "thumb_zones": "Primary action placement in thumb zone",
        "loading_strategy": "Mobile-specific optimization",
        "breakpoints": {"mobile": 640, "tablet": 1024},
        "progressive_disclosure_mobile": "What collapses on mobile",
    })
    
    permissions: list[str] = Field(default=[
        "define_touch_target_sizes",
        "configure_sticky_bar_mobile",
        "specify_mobile_breakpoints",
        "optimize_for_thumb_zones",
    ])
    
    prohibited: list[str] = Field(default=[
        "USE_TOUCH_TARGETS_BELOW_44PX",
        "PLACE_PRIMARY_CTA_OUTSIDE_THUMB_ZONE",
        "IGNORE_MOBILE_LOADING_PERFORMANCE",
        "CARRY_DESKTOP_CLUTTER_TO_MOBILE",
    ])
    
    benchmark_cases: list[dict[str, Any]] = Field(default=[
        {
            "case": "Click-to-call mobile (emergency)",
            "config": {"sticky": "always", "position": "bottom", "full_width": True},
            "reasoning": "Emergency callers expect instant phone access"
        }
    ])
    
    what_would_change_my_mind: list[str] = Field(default=[
        "Mobile analytics showing >20% tap miss rate",
        "Core Web Vitals failing on mobile",
        "Mobile conversion rate < 50% of desktop",
    ])


wd05_agent = WD05MobileExperienceAgent()


def get_agent() -> WD05MobileExperienceAgent:
    return wd05_agent
