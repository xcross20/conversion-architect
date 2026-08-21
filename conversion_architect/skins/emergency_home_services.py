"""
Emergency Home Services Skin v1

Vertical skin for home services that handle urgent/emergency situations.
Examples: HVAC, plumbing, electrical, locksmith, roofing.
"""
from conversion_architect.schemas import VerticalSkin, Vertical


def create_emergency_home_services_skin() -> VerticalSkin:
    """Create Emergency Home Services vertical skin."""
    return VerticalSkin(
        skin_id="emergency_home_services_v1",
        name="Emergency Home Services",
        vertical=Vertical.HOME_SERVICES,
        family_id="portfolio_v1",
        status="active",
        
        # Visual tokens
        colors={
            "primary": "#E53935",  # Urgent red
            "secondary": "#1565C0",  # Trust blue
            "accent": "#FFC107",  # Warning/attention amber
            "background_light": "#FAFAFA",
            "background_dark": "#1A1A2E",
            "text_primary": "#212121",
            "text_secondary": "#757575",
            "cta_color": "#FFA000",  # High-contrast orange
            "cta_text_color": "#FFFFFF",
            "success": "#4CAF50",
            "warning": "#FF9800"
        },
        
        # Typography
        typography={
            "font_family_primary": "Inter, -apple-system, sans-serif",
            "font_family_headings": "Inter, -apple-system, sans-serif",
            "base_size": 16,
            "scale_ratio": 1.25,
            "heading_weights": {"h1": 700, "h2": 600, "h3": 600}
        },
        
        # Imagery style
        imagery_style={
            "photo_types": ["real_job", "technician", "before_after"],
            "illustration_style": "flat_technical",
            "icon_set": "heroicons_outline",
            "avoid": ["stock_generic", "cartoon", "clipart"]
        },
        
        # Spacing overrides
        spacing_overrides={
            "section_padding_top": 48,
            "section_padding_bottom": 48
        },
        
        # Trust signals for home services
        trust_signals=[
            "license_badge",
            "insurance_badge",
            "review_stars",
            "guarantee_badge",
            "years_in_business",
            "local_address",
            "bbb_accredited"
        ],
        
        # Urgency tokens
        urgency_tokens=[
            "24_hour",
            "same_day",
            "available_now",
            "response_time",
            "emergency_live_answer"
        ],
        
        # Authority markers
        authority_markers=[
            "state_license",
            "manufacturer_certified",
            "industry_association",
            "award_badge"
        ],
        
        # Compliance
        required_disclosures=[
            "license_number",
            "service_area",
            "guarantee_terms",
            "price_disclaimer"
        ],
        restricted_claims=[
            "only_provider",
            "lowest_price",
            "guaranteed_outcome"
        ],
        
        tags=["home_services", "emergency", "urgent", "hvac", "plumbing", "electrical"]
    )
