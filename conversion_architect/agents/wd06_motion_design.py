"""
WD-06 Motion Design Agent
"""
from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Any


class WD06MotionDesignAgent(BaseModel):
    """WD-06 Motion Design Agent
    
    Mission: Define animation patterns that guide attention,
    provide feedback, and create appropriate emotional response
    without compromising performance or accessibility.
    
    Underlying Variable: ANIMATION_PATTERNS
    
    Motion should serve conversion, not decorate. Every animation
    needs a purpose tied to user attention or feedback.
    """
    
    agent_id: str = Field(default="WD-06")
    name: str = Field(default="Motion Design Agent")
    mission: str = Field(
        default="Define animation patterns that guide attention, "
                "provide feedback, and create appropriate emotional "
                "response without compromising performance"
    )
    underlying_variable: str = Field(default="ANIMATION_PATTERNS")
    
    questions: list[str] = Field(default=[
        "What is the desired perception (urgency, calm, premium)?",
        "What elements need motion to guide attention?",
        "What accessibility constraints exist (vestibular, reduced motion)?",
        "What is the animation performance budget?",
        "Should animations be triggered by scroll position?",
        "Are there brand motion guidelines?",
    ])
    
    noise_rules: list[str] = Field(default=[
        "Decorative animations without conversion purpose",
        "Motion that slows page load",
        "Animations that trigger for all users (accessibility)",
        "Excessive parallax or scroll-jacking",
        "Motion that conflicts with family signature",
    ])
    
    outputs: dict[str, Any] = Field(default={
        "attention_animations": "Elements and their entrance motion",
        "feedback_animations": "Button/interaction feedback",
        "urgency_motion": "Motion that conveys urgency (if applicable)",
        "loading_patterns": "Loading state animations",
        "reduced_motion": "Fallback for prefers-reduced-motion",
        "duration_limits": {"max_entrance": 500, "max_feedback": 200},
        "performance_budget": "Animation performance constraints",
    })
    
    permissions: list[str] = Field(default=[
        "define_entrance_animations",
        "specify_feedback_motion",
        "configure_urgency_animations",
        "implement_reduced_motion_fallbacks",
    ])
    
    prohibited: list[str] = Field(default=[
        "ADD_MOTION_WITHOUT_PURPOSE",
        "EXCEED_ANIMATION_PERFORMANCE_BUDGET",
        "IGNORE_REDUCED_MOTION_PREFERENCE",
        "USE_SCROLL_JACKING",
        "CREATE_VESTIBULAR_TRIGGERING_MOTION",
    ])
    
    benchmark_cases: list[dict[str, Any]] = Field(default=[
        {
            "case": "Emergency service (high urgency)",
            "motion": {"type": "fade_in", "duration": 300, "stagger": 100},
            "reasoning": "Fast, confident motion conveys efficiency"
        },
        {
            "case": "Premium B2B (deliberate, confident)",
            "motion": {"type": "slide_up", "duration": 500, "stagger": 150},
            "reasoning": "Slower motion conveys premium positioning"
        }
    ])
    
    what_would_change_my_mind: list[str] = Field(default=[
        "Performance audit showing animation impact on load time",
        "Accessibility violation flagged",
        "User testing showing motion distracts from CTA",
        "Reduced motion preference becoming common",
    ])


wd06_agent = WD06MotionDesignAgent()


def get_agent() -> WD06MotionDesignAgent:
    return wd06_agent


# Agents module init
def get_all_agents():
    """Get all WD agent instances."""
    from conversion_architect.agents.wd01_visual_identity import wd01_agent
    from conversion_architect.agents.wd02_information_architecture import wd02_agent
    from conversion_architect.agents.wd03_conversion_layout import wd03_agent
    from conversion_architect.agents.wd04_proof_architecture import wd04_agent
    from conversion_architect.agents.wd05_mobile_experience import wd05_agent
    
    return {
        "WD-01": wd01_agent,
        "WD-02": wd02_agent,
        "WD-03": wd03_agent,
        "WD-04": wd04_agent,
        "WD-05": wd05_agent,
        "WD-06": wd06_agent,
    }
