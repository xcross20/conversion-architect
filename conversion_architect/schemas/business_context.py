"""
BusinessConversionContext Schema
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ConversionGoal(str, Enum):
    PHONE_CALL = "phone_call"
    LEAD_CAPTURE = "lead_capture"
    APPOINTMENT = "appointment"
    PURCHASE = "purchase"
    SIGNUP = "signup"
    QUOTE_REQUEST = "quote_request"


class UrgencyLevel(str, Enum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class BusinessConversionContext(BaseModel):
    """BusinessConversionContext captures the economic and conversion inputs
    for genome generation.
    
    This is the input adapter from CallQuant — it normalizes
    CampaignCell, IntentCluster, OfferVariant, and ClaimManifest
    into a form the Conversion Architect can use.
    """
    
    # Identity
    context_id: str = Field(..., description="Unique context identifier")
    campaign_cell_id: str = Field(..., description="Source campaign cell")
    
    # Vertical/vertical
    vertical: str = Field(..., description="Business vertical")
    sub_vertical: str | None = Field(None, description="Sub-vertical")
    
    # Offer
    offer: dict[str, Any] = Field(..., description="Offer variant data")
    offer_headline: str = Field(..., description="Primary offer headline")
    offer_value_prop: str = Field(..., description="Value proposition")
    offer_urgency: UrgencyLevel = Field(default=UrgencyLevel.MEDIUM)
    
    # Claims
    claim_manifest_id: str | None = Field(None, description="Source claim manifest")
    supported_claims: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Validated claims"
    )
    unsupported_claims: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Excluded claims"
    )
    compliance_constraints: list[str] = Field(
        default_factory=list,
        description="Compliance requirements"
    )
    
    # Intent
    intent_cluster_id: str | None = Field(None)
    intent_keywords: list[str] = Field(default_factory=list)
    intent_perceptions: list[str] = Field(
        default_factory=list,
        description="Desired perceptions (urgency, trust, etc.)"
    )
    
    # Conversion
    conversion_goal: ConversionGoal = Field(..., description="Primary conversion action")
    click_to_call_number: str | None = Field(None, description="Tracking phone number")
    form_fields: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Form field definitions"
    )
    
    # Economics (primary metric supplied by business)
    primary_metric: str = Field(
        default="cost_per_qualified_call",
        description="Primary economic metric"
    )
    target_metric_value: float | None = Field(
        None,
        description="Target value for primary metric"
    )
    current_metric_value: float | None = Field(
        None,
        description="Baseline/current value"
    )
    budget_limit: float | None = Field(None, description="Budget ceiling")
    
    # Audience
    target_states: list[str] = Field(default_factory=list)
    target_zip_codes: list[str] = Field(default_factory=list)
    service_area: str | None = Field(None, description="Service area description")
    
    # Trust signals available
    available_trust_signals: list[str] = Field(
        default_factory=list,
        description="Trust signals to include"
    )
    
    # Provider mapping
    experiment_id: str | None = Field(None, description="Design experiment ID")
    genome_ids: dict[str, str] = Field(
        default_factory=dict,
        description="Genome IDs by variant"
    )
    
    # GA4 Analytics enrichment
    ga4_property_id: str | None = Field(
        None,
        description="GA4 property ID for analytics"
    )
    ga4_report_id: str | None = Field(
        None,
        description="Latest GA4 report ID"
    )
    top_converting_keywords: list[str] = Field(
        default_factory=list,
        description="Highest CVR keywords from GA4"
    )
    best_performing_state: str | None = Field(
        None,
        description="State with highest CVR from GA4"
    )
    best_performing_page: str | None = Field(
        None,
        description="Page path with highest CVR"
    )
    mobile_friendly_score: float = Field(
        default=1.0,
        description="Mobile usability score from GA4"
    )
    conversion_trend: str = Field(
        default="stable",
        description="Conversion trend: improving, declining, stable"
    )
    conversion_trend_pct: float = Field(
        default=0.0,
        description="Period-over-period change percentage"
    )
    
    # GA4-derived design targets
    target_cvr: float | None = Field(
        None,
        description="Target CVR from GA4 insights"
    )
    target_bounce_rate: float | None = Field(
        None,
        description="Target bounce rate from GA4 insights"
    )
    target_cta_click_rate: float | None = Field(
        None,
        description="Target CTA click rate"
    )
    
    # Audience insights
    dominant_age_bracket: str | None = Field(
        None,
        description="Primary audience age bracket from GA4"
    )
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    meta_data: dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "context_id": "ctx_hvac_emergency",
                "campaign_cell_id": "cell_hvac_emergency",
                "vertical": "home_services",
                "sub_vertical": "hvac",
                "offer": {
                    "type": "emergency_service",
                    "price": "$89",
                    "guarantee": "45-minute arrival"
                },
                "offer_headline": "24/7 Emergency HVAC Service",
                "offer_value_prop": "Fast, reliable HVAC repair when you need it most",
                "offer_urgency": "high",
                "claim_manifest_id": "manifest_hvac_001",
                "supported_claims": [
                    {"claim": "24_hour_service", "status": "supported"},
                    {"claim": "licensed", "status": "supported"},
                    {"claim": "insured", "status": "supported"}
                ],
                "intent_perceptions": ["urgency", "trust", "speed"],
                "conversion_goal": "phone_call",
                "click_to_call_number": "+1-800-422-9181",
                "primary_metric": "cost_per_qualified_call",
                "target_metric_value": 75.0,
                "available_trust_signals": [
                    "license_badge",
                    "insurance_badge",
                    "review_stars",
                    "guarantee_badge",
                    "years_in_business"
                ],
                "ga4_property_id": "properties/123456789",
                "ga4_report_id": "ga4_rpt_2024_01_15",
                "top_converting_keywords": [
                    "emergency hvac repair",
                    "24 hour plumber"
                ],
                "best_performing_state": "TX",
                "best_performing_page": "/emergency-services",
                "mobile_friendly_score": 0.85,
                "conversion_trend": "improving",
                "conversion_trend_pct": 12.5,
                "target_cvr": 0.045,
                "target_bounce_rate": 0.35,
                "dominant_age_bracket": "35-44"
            }
        }
