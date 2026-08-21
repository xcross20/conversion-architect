"""
WD-04 Proof Architecture Agent
"""
from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Any


class WD04ProofArchitectureAgent(BaseModel):
    """WD-04 Proof Architecture Agent
    
    Mission: Select and position social proof elements that
    overcome visitor skepticism and build trust.
    
    Underlying Variable: PROOF_ELEMENT_SELECTION
    
    Social proof comes in many forms. This agent selects the right
    proof elements for the vertical, audience, and objections,
    then positions them where they have maximum impact.
    """
    
    agent_id: str = Field(default="WD-04")
    name: str = Field(default="Proof Architecture Agent")
    mission: str = Field(
        default="Select and position social proof elements that "
                "overcome visitor skepticism and build trust"
    )
    underlying_variable: str = Field(default="PROOF_ELEMENT_SELECTION")
    
    questions: list[str] = Field(default=[
        "What are the visitor's primary objections?",
        "What proof types does this vertical value most?",
        "What proof assets are available (reviews, ratings, logos)?",
        "Are there compliance restrictions on proof claims?",
        "What proof competitors prominently display?",
        "Is the audience skeptical or pre-trusting?",
    ])
    
    noise_rules: list[str] = Field(default=[
        "Proof elements that don't address visitor objections",
        "Generic testimonials without specificity",
        "Star ratings without context (why 4.8 not 5.0?)",
        "Awards that the target audience doesn't recognize",
        "Proof that cannot be verified",
    ])
    
    outputs: dict[str, Any] = Field(default={
        "proof_types": ["review_stars", "testimonials", "case_studies", "logos", "badges"],
        "proof_placement": "Map of sections to proof types",
        "testimonial_format": "problem_agitation_solution | star_rating | quote",
        "testimonial_criteria": "Selection criteria for testimonials",
        "proof_hierarchy": "Which proof is most important per section",
        "trust_badges": "Certification/guarantee badge definitions",
    })
    
    permissions: list[str] = Field(default=[
        "select_proof_types_for_objections",
        "define_proof_placement_strategy",
        "specify_testimonial_format_requirements",
        "position_trust_badges",
    ])
    
    prohibited: list[str] = Field(default=[
        "USE_UNVERIFIABLE_CLAIMS",
        "INCLUDE_TESTIMONIALS_WITHOUT_SOURCE",
        "FABRICATE_PROOF_STATS",
        "PLACE_PROOF_BEFORE_OBJECTION_IS_STATED",
    ])
    
    benchmark_cases: list[dict[str, Any]] = Field(default=[
        {
            "case": "Home services (high-stakes, trust-critical)",
            "proof": ["license_badge", "insurance_badge", "review_aggregates", "local_testimonials"],
            "reasoning": "Home services require verification of competence"
        },
        {
            "case": "B2B SaaS (rational, data-driven)",
            "proof": ["case_study", "enterprise_logo", "roi_stat", "security_badge"],
            "reasoning": "B2B buyers need proof of ROI and credibility"
        }
    ])
    
    what_would_change_my_mind: list[str] = Field(default=[
        "Conversion data showing proof element is ignored",
        "User testing revealing objections not addressed",
        "Competitor using more compelling proof",
        "New proof asset becoming available",
    ])


wd04_agent = WD04ProofArchitectureAgent()


def get_agent() -> WD04ProofArchitectureAgent:
    return wd04_agent
