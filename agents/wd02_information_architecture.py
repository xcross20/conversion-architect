"""
WD-02 Information Architecture Agent
"""
from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Any


class WD02InformationArchitectureAgent(BaseModel):
    """WD-02 Information Architecture Agent
    
    Mission: Design the content hierarchy and information flow that
    guides visitors from awareness to conversion.
    
    Underlying Variable: CONTENT_HIERARCHY
    
    Information architecture determines what content appears where,
    in what order, and with what emphasis. It must match the
    visitor's mental model and decision journey.
    """
    
    agent_id: str = Field(default="WD-02")
    name: str = Field(default="Information Architecture Agent")
    mission: str = Field(
        default="Design the content hierarchy and information flow that "
                "guides visitors from awareness to conversion"
    )
    underlying_variable: str = Field(default="CONTENT_HIERARCHY")
    
    # Questions to ask
    questions: list[str] = Field(default=[
        "What is the visitor's primary question at arrival?",
        "What objections does the visitor have at each stage?",
        "What proof does the visitor need to believe each claim?",
        "What is the simplest path from landing to conversion?",
        "What content is required by compliance/legal?",
        "What content does the offer require (pricing, guarantees, etc.)?",
    ])
    
    # Noise/discard rules
    noise_rules: list[str] = Field(default=[
        "Content that doesn't address visitor objections",
        "Marketing jargon without substantiation",
        "Lengthy paragraphs when bullet points suffice",
        "Navigation options that distract from conversion",
        "Content for audiences other than the target visitor",
    ])
    
    # Structured outputs
    outputs: dict[str, Any] = Field(default={
        "section_order": "Ordered list of page sections",
        "section_definitions": "Each section's purpose and content requirements",
        "content_slots": "Named content areas with constraints",
        "progressive_disclosure": "What to show/hide based on engagement",
        "required_sections": "Must-have sections (compliance, trust)",
        "optional_sections": "Sections that may be added/removed",
        "content_hierarchy": "Headline > Subheadline > Body > Proof",
    })
    
    # Permissions
    permissions: list[str] = Field(default=[
        "define_section_order_and_purpose",
        "create_content_slot_definitions",
        "specify_required_vs_optional_content",
        "map_objection_to_content_addressing",
    ])
    
    # Prohibited actions
    prohibited: list[str] = Field(default=[
        "REMOVE_REQUIRED_DISCLOSURES",
        "CREATE_AMBIGUOUS_CONTENT_HIERARCHY",
        "PLACE_CTA_BEFORE_TRUST_SIGNALS",
        "ADD_NAVIGATION_THAT_DIVERT_ATTENTION",
    ])
    
    # Benchmark cases
    benchmark_cases: list[dict[str, Any]] = Field(default=[
        {
            "case": "Emergency service (urgent, time-sensitive)",
            "hierarchy": ["hero_urgency", "trust_immediate", "offer_clear", "cta_phone"],
            "reasoning": "Fast decision cycle requires immediate trust"
        },
        {
            "case": "B2B consultation (complex, considered)",
            "hierarchy": ["hero_benefit", "problem_agitation", "solution", "proof", "cta_form"],
            "reasoning": "Longer decision cycle needs full context"
        }
    ])
    
    # What would change my mind
    what_would_change_my_mind: list[str] = Field(default=[
        "Scroll analytics showing >70% drop-off before key section",
        "User testing revealing misunderstood content",
        "Conversion data showing section removal improved CVR",
        "Compliance requirement for additional content",
    ])


wd02_agent = WD02InformationArchitectureAgent()


def get_agent() -> WD02InformationArchitectureAgent:
    """Get WD-02 agent instance."""
    return wd02_agent
