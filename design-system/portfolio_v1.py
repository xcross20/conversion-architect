"""
Portfolio Master Family v1

The canonical design family for all landing pages.
Defines stable signatures for: headline, CTA, spacing, proof, mobile.
"""
from conversion_architect.schemas import DesignFamily


def create_portfolio_v1() -> DesignFamily:
    """Create Portfolio Master Family v1."""
    return DesignFamily(
        family_id="portfolio_v1",
        name="Portfolio Master Family",
        version="1.0.0",
        status="active",
        description="Master design family defining canonical grammar rules "
                    "for all landing pages. Stable signatures ensure consistency "
                    "while allowing vertical-specific customization via skins.",
        vertical=None,  # Universal
        
        # Editorial headline grammar
        headline_grammar={
            "h1_structure": "benefit_statement | hook | number_lead",
            "max_length": 70,
            "min_length": 20,
            "tone_markers": ["urgent", "clarifying", "social"],
            "allowed_formats": [
                "command_verb",
                "question_open",
                "number_lead",
                "superlative",
                "how_to"
            ],
            "prohibited_patterns": [
                "passive_voice",
                "question_mark_ending",
                "all_caps",
                "excessive_punctuation"
            ]
        },
        
        # Primary CTA grammar
        cta_grammar={
            "primary_size": {
                "min_width": 200,
                "height": 56,
                "max_height": 64
            },
            "shape": "rounded",
            "border_radius": 8,
            "contrast_ratio": 4.5,  # WCAG AA minimum
            "text_style": {
                "font_weight": 600,
                "text_transform": "none",
                "letter_spacing": 0.5
            },
            "spacing": {
                "padding_horizontal": 24,
                "padding_vertical": 16
            },
            "motion": {
                "hover_scale": 1.02,
                "transition_duration": 200
            }
        },
        
        # Spacing/grid rhythm
        spacing_grammar={
            "base_unit": 8,
            "rhythm": [8, 16, 24, 32, 48, 64, 96, 128],
            "max_content_width": 1200,
            "section_padding": {
                "desktop": {"top": 64, "bottom": 64},
                "tablet": {"top": 48, "bottom": 48},
                "mobile": {"top": 32, "bottom": 32}
            },
            "grid": {
                "columns": 12,
                "gutter": 24,
                "margin": {
                    "desktop": 48,
                    "tablet": 32,
                    "mobile": 16
                }
            }
        },
        
        # Proof-card grammar
        proof_grammar={
            "testimonial_format": "problem_agitation_solution",
            "testimonial_length": {
                "min": 50,
                "max": 200
            },
            "star_placement": "left_aligned",
            "author_format": "{name}, {location}",
            "attribution_required": True,
            "photo_preference": "real_photo",
            "verified_badge": True
        },
        
        # Mobile sticky-action grammar
        mobile_grammar={
            "sticky_bar": True,
            "sticky_height": 64,
            "touch_target_min": 44,
            "position": "bottom",
            "blur_background": True,
            "safe_area_aware": True,
            "hide_on_scroll_down": False,
            "show_on_scroll_up": True
        },
        
        tags=["master", "canonical", "v1"]
    )
