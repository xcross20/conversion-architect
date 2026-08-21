"""
Professional Services Skin v1

Vertical skin for B2B professional services.
Examples: consulting, legal, accounting, marketing agencies, staffing.
"""
from conversion_architect.schemas import VerticalSkin, Vertical


def create_professional_services_skin() -> VerticalSkin:
    """Create Professional Services vertical skin."""
    return VerticalSkin(
        skin_id="professional_services_v1",
        name="Professional Services",
        vertical=Vertical.B2B_SERVICES,
        family_id="portfolio_v1",
        status="active",
        
        # Visual tokens - premium, trust
        colors={
            "primary": "#1E3A5F",  # Navy - professional
            "secondary": "#2E5A8F",  # Lighter navy
            "accent": "#2196F3",  # Action blue
            "background_light": "#FFFFFF",
            "background_dark": "#0D1B2A",
            "text_primary": "#1A1A2E",
            "text_secondary": "#5A6A7A",
            "cta_color": "#2196F3",
            "cta_text_color": "#FFFFFF",
            "success": "#2E7D32",
            "warning": "#ED6C02"
        },
        
        # Typography - clean, readable
        typography={
            "font_family_primary": "Inter, -apple-system, sans-serif",
            "font_family_headings": "Inter, -apple-system, sans-serif",
            "base_size": 16,
            "scale_ratio": 1.2,  # Slightly larger for readability
            "heading_weights": {"h1": 600, "h2": 600, "h3": 500}
        },
        
        # Imagery style - professional, not casual
        imagery_style={
            "photo_types": ["team_photo", "office", "consultation", "data_charts"],
            "illustration_style": "minimal_corporate",
            "icon_set": "phosphor_regular",
            "avoid": ["casual", "stock_smiling", "cartoon"]
        },
        
        # Spacing overrides - more breathing room
        spacing_overrides={
            "section_padding_top": 80,
            "section_padding_bottom": 80
        },
        
        # Trust signals for B2B
        trust_signals=[
            "case_study",
            "enterprise_logo",
            "roi_stat",
            "security_badge",
            "certification_badge",
            "testimonial_b2b"
        ],
        
        # No urgency - B2B is deliberate
        urgency_tokens=[
            "limited_consultation",
            "cohort_starting"
        ],
        
        # Authority markers
        authority_markers=[
            "certification",
            "award",
            "publication_mention",
            "case_study",
            "roi_proof"
        ],
        
        # Compliance
        required_disclosures=[
            "terms_of_service",
            "privacy_policy",
            "professional_license"
        ],
        restricted_claims=[
            "instant_results",
            "no_risk",
            "guaranteed_roi"
        ],
        
        tags=["b2b", "professional", "consulting", "saas", "agency", "legal", "accounting"]
    )
