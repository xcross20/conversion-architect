"""
Fixture Provider

Fallback design pattern provider for CI and offline environments.
Provides pre-defined patterns that pass schema validation.
"""
from __future__ import annotations

from typing import Any
import logging

from conversion_architect.providers.design_pattern_provider import (
    DesignPatternProvider,
    PatternQuery,
)
from conversion_architect.schemas import DesignPattern

logger = logging.getLogger(__name__)


class FixtureProvider(DesignPatternProvider):
    """Fixture/fallback provider for design patterns.
    
    Used when MotionSites MCP is unavailable or in CI environments.
    Provides pre-defined patterns that pass schema validation.
    """
    
    def __init__(self):
        """Initialize fixture provider with built-in patterns."""
        self._patterns: dict[str, DesignPattern] = self._load_fixtures()
    
    def is_available(self) -> bool:
        """Fixture provider is always available."""
        return True
    
    async def health_check(self) -> dict[str, Any]:
        """Fixture provider is always healthy."""
        return {
            "available": True,
            "provider": "fixture",
            "status": "always_available",
            "pattern_count": len(self._patterns)
        }
    
    async def query(self, query: PatternQuery) -> list[DesignPattern]:
        """Query fixture patterns.
        
        For CI/offline, returns all patterns (no actual filtering).
        """
        patterns = list(self._patterns.values())
        
        # Basic filtering
        if query.page_type:
            patterns = [p for p in patterns if p.page_type == query.page_type]
        if query.section_type:
            patterns = [p for p in patterns if p.section_type == query.section_type]
        if query.desired_perceptions:
            patterns = [
                p for p in patterns
                if any(perc in p.perceptions for perc in query.desired_perceptions)
            ]
        
        return patterns[:query.limit]
    
    async def get(self, pattern_id: str) -> DesignPattern | None:
        """Get a specific pattern by ID."""
        return self._patterns.get(pattern_id)
    
    async def list_sections(self, page_type: str) -> list[str]:
        """List available section types."""
        sections = set()
        for pattern in self._patterns.values():
            if pattern.page_type == page_type:
                sections.add(pattern.section_type.value if hasattr(pattern.section_type, 'value') else pattern.section_type)
        return sorted(list(sections))
    
    def _load_fixtures(self) -> dict[str, DesignPattern]:
        """Load fixture patterns."""
        fixtures = [
            # Hero patterns
            {
                "pattern_id": "hero_urgency_v1",
                "name": "Hero - Urgency (Home Services)",
                "page_type": "landing",
                "section_type": "hero",
                "perceptions": ["urgency", "trust"],
                "structure": {
                    "layout": "split",
                    "columns": {"desktop": 2, "mobile": 1}
                },
                "elements": [
                    {"type": "headline", "slot": "main_headline", "required": True},
                    {"type": "subheadline", "slot": "sub_headline", "required": True},
                    {"type": "cta_button", "slot": "primary_cta", "required": True},
                ],
                "content_slots": {
                    "main_headline": {"type": "text", "max_length": 60},
                    "primary_cta": {"type": "cta"}
                },
                "source": "fixture",
                "confidence": 0.85
            },
            # Trust badges pattern
            {
                "pattern_id": "trust_badges_v1",
                "name": "Trust Badges Section",
                "page_type": "landing",
                "section_type": "trust_badges",
                "perceptions": ["trust"],
                "structure": {
                    "layout": "row",
                    "items_per_row": {"desktop": 5, "mobile": 3}
                },
                "elements": [
                    {"type": "badge", "slot": "badges", "required": True, "multi": True}
                ],
                "content_slots": {
                    "badges": {"type": "badge", "multi": True}
                },
                "source": "fixture",
                "confidence": 0.90
            },
            # CTA pattern
            {
                "pattern_id": "cta_inline_v1",
                "name": "Inline CTA Section",
                "page_type": "landing",
                "section_type": "cta",
                "perceptions": ["urgency"],
                "structure": {
                    "layout": "centered",
                    "max_width": 600
                },
                "elements": [
                    {"type": "headline", "slot": "cta_headline", "required": True},
                    {"type": "cta_button", "slot": "primary_cta", "required": True}
                ],
                "content_slots": {
                    "primary_cta": {"type": "cta"}
                },
                "source": "fixture",
                "confidence": 0.88
            },
            # Sticky bar pattern
            {
                "pattern_id": "sticky_bar_v1",
                "name": "Mobile Sticky Action Bar",
                "page_type": "landing",
                "section_type": "sticky_bar",
                "perceptions": ["convenience", "urgency"],
                "structure": {
                    "position": "bottom",
                    "height": 64,
                    "full_width": True
                },
                "elements": [
                    {"type": "cta_button", "slot": "primary_cta", "required": True}
                ],
                "content_slots": {
                    "primary_cta": {"type": "cta", "cta_type": "phone"}
                },
                "source": "fixture",
                "confidence": 0.92
            },
            # Features pattern
            {
                "pattern_id": "features_grid_v1",
                "name": "Features Grid",
                "page_type": "landing",
                "section_type": "features",
                "perceptions": ["trust", "value"],
                "structure": {
                    "layout": "grid",
                    "columns": {"desktop": 3, "mobile": 1}
                },
                "elements": [
                    {"type": "icon", "slot": "icon", "required": True},
                    {"type": "headline", "slot": "feature_title", "required": True},
                    {"type": "text", "slot": "feature_description", "required": True}
                ],
                "content_slots": {
                    "feature_title": {"type": "text", "max_length": 50},
                    "feature_description": {"type": "text", "max_length": 150}
                },
                "source": "fixture",
                "confidence": 0.85
            },
            # Testimonials pattern
            {
                "pattern_id": "testimonials_v1",
                "name": "Testimonials Section",
                "page_type": "landing",
                "section_type": "testimonials",
                "perceptions": ["trust"],
                "structure": {
                    "layout": "carousel",
                    "items_visible": {"desktop": 3, "mobile": 1}
                },
                "elements": [
                    {"type": "quote", "slot": "testimonial", "required": True},
                    {"type": "author", "slot": "author", "required": True},
                    {"type": "rating", "slot": "rating", "required": True}
                ],
                "content_slots": {
                    "testimonial": {"type": "text", "max_length": 200},
                    "author": {"type": "text"}
                },
                "source": "fixture",
                "confidence": 0.88
            }
        ]
        
        patterns = {}
        for fixture in fixtures:
            try:
                pattern = DesignPattern(**fixture)
                patterns[pattern.pattern_id] = pattern
            except Exception as e:
                logger.warning(f"Failed to load fixture pattern: {e}")
        
        return patterns


def create_fixture_provider() -> FixtureProvider:
    """Create fixture provider instance."""
    return FixtureProvider()
