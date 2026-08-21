"""
WD-03 Conversion Layout Agent
"""
from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Any


class WD03ConversionLayoutAgent(BaseModel):
    """WD-03 Conversion Layout Agent
    
    Mission: Optimize CTA placement, geometry, and surrounding
    context to maximize conversion actions.
    
    Underlying Variable: CTA_PLACEMENT_GEOMETRY
    
    The CTA is the culmination of the page. Its placement, size,
    shape, and surrounding context determine whether visitors
    take the desired action.
    """
    
    agent_id: str = Field(default="WD-03")
    name: str = Field(default="Conversion Layout Agent")
    mission: str = Field(
        default="Optimize CTA placement, geometry, and surrounding "
                "context to maximize conversion actions"
    )
    underlying_variable: str = Field(default="CTA_PLACEMENT_GEOMETRY")
    
    questions: list[str] = Field(default=[
        "What is the primary conversion action (call, form, chat)?",
        "Where does the visitor's eye naturally travel?",
        "What is the optimal CTA size for the action type?",
        "Should there be one CTA or multiple CTAs?",
        "What urgency/scarcity elements support the CTA?",
        "Is click-to-call the primary action?",
    ])
    
    noise_rules: list[str] = Field(default=[
        "CTA designs that prioritize aesthetics over visibility",
        "Multiple competing CTAs without clear hierarchy",
        "CTA copy that is vague or doesn't match action",
        "CTAs placed before trust signals are established",
        "Geometry changes that don't affect conversion metrics",
    ])
    
    outputs: dict[str, Any] = Field(default={
        "primary_cta": {
            "text": "CTA button text",
            "action_type": "phone_call | form | chat | purchase",
            "placement": "hero_inline | sticky_bar | section_end | floating",
            "size": {"min_width": 200, "height": 56},
            "geometry": {"shape": "rounded", "border_radius": 8},
        },
        "secondary_ctas": "List of secondary CTA definitions",
        "sticky_bar": "Sticky action bar configuration",
        "cta_surroundings": "Trust elements adjacent to CTA",
        "urgency_elements": "Scarcity/urgency near CTA",
    })
    
    permissions: list[str] = Field(default=[
        "define_cta_placement_and_size",
        "specify_sticky_bar_configuration",
        "position_urgency_elements_near_cta",
        "create_cta_hierarchy",
    ])
    
    prohibited: list[str] = Field(default=[
        "REDUCE_CTA_SIZE_BELOW_TOUCH_TARGET_MIN",
        "PLACE_CTA_BELOW_FOLD_WITHOUT_STICKY",
        "CREATE_MULTIPLE_EQUAL_CTAs",
        "USE_VAGUE_CTA_COPY",
        "PLACE_CTA_BEFORE_OFFER_IS_CLEAR",
    ])
    
    benchmark_cases: list[dict[str, Any]] = Field(default=[
        {
            "case": "Click-to-call emergency service",
            "layout": {"cta": "sticky_bar_bottom", "size": "full_width"},
            "reasoning": "Mobile users expect phone at thumb reach"
        },
        {
            "case": "Lead capture with form",
            "layout": {"cta": "inline_after_hero", "size": "standard"},
            "reasoning": "Form complexity determines CTA placement"
        }
    ])
    
    what_would_change_my_mind: list[str] = Field(default=[
        "Heatmap showing CTA not being noticed",
        "A/B test with >10% CVR improvement from repositioning",
        "Mobile analytics showing thumb reach issues",
        "Accessibility audit flagging CTA visibility",
    ])


wd03_agent = WD03ConversionLayoutAgent()


def get_agent() -> WD03ConversionLayoutAgent:
    return wd03_agent
