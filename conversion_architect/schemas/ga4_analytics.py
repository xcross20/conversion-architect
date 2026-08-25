"""
GA4 Analytics Schema

Google Analytics 4 data structures for Conversion Architect.
Provides conversion metrics, keyword performance, and audience insights.
"""
from __future__ import annotations

from datetime import datetime, date
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class TrafficSource(str, Enum):
    ORGANIC_SEARCH = "organic_search"
    PAID_SEARCH = "paid_search"
    DIRECT = "direct"
    REFERRAL = "referral"
    SOCIAL = "social"
    EMAIL = "email"
    DISPLAY = "display"


class ConversionStatus(str, Enum):
    HIGH_PERFORMING = "high_performing"
    AVERAGE = "average"
    UNDERPERFORMING = "underperforming"
    NO_DATA = "no_data"


class KeywordPerformance(BaseModel):
    """Performance metrics for a keyword."""
    keyword: str = Field(..., description="Search keyword")
    sessions: int = Field(default=0, description="Number of sessions")
    conversions: int = Field(default=0, description="Conversion count")
    conversion_rate: float = Field(default=0.0, description="CVR as decimal")
    conversion_value: float = Field(default=0.0, description="Total conversion value")
    bounce_rate: float = Field(default=0.0, description="Bounce rate as decimal")
    avg_session_duration: float = Field(default=0.0, description="Average session in seconds")
    page_views: int = Field(default=0, description="Total page views")
    source: TrafficSource = Field(default=TrafficSource.PAID_SEARCH)
    status: ConversionStatus = Field(default=ConversionStatus.NO_DATA)

    class Config:
        json_schema_extra = {
            "example": {
                "keyword": "emergency hvac repair",
                "sessions": 1234,
                "conversions": 42,
                "conversion_rate": 0.034,
                "conversion_value": 1890.00,
                "bounce_rate": 0.45,
                "avg_session_duration": 125.5,
                "page_views": 3456,
                "source": "paid_search",
                "status": "high_performing"
            }
        }


class GeographicPerformance(BaseModel):
    """Performance metrics by geography."""
    state: str = Field(..., description="State code (e.g., 'CA')")
    city: str | None = Field(None, description="City name")
    zip_code: str | None = Field(None, description="ZIP code")
    sessions: int = Field(default=0)
    conversions: int = Field(default=0)
    conversion_rate: float = Field(default=0.0)
    conversion_value: float = Field(default=0.0)
    avg_order_value: float = Field(default=0.0)
    status: ConversionStatus = Field(default=ConversionStatus.NO_DATA)

    class Config:
        json_schema_extra = {
            "example": {
                "state": "TX",
                "city": "Houston",
                "sessions": 567,
                "conversions": 28,
                "conversion_rate": 0.049,
                "conversion_value": 1400.00,
                "avg_order_value": 50.00,
                "status": "high_performing"
            }
        }


class PagePerformance(BaseModel):
    """Performance metrics for a landing page."""
    page_path: str = Field(..., description="Page URL path")
    page_title: str | None = Field(None)
    sessions: int = Field(default=0)
    engaged_sessions: int = Field(default=0)
    conversions: int = Field(default=0)
    conversion_rate: float = Field(default=0.0)
    bounce_rate: float = Field(default=0.0)
    avg_engagement_time: float = Field(default=0.0)
    exits: int = Field(default=0)
    exit_rate: float = Field(default=0.0)
    status: ConversionStatus = Field(default=ConversionStatus.NO_DATA)

    class Config:
        json_schema_extra = {
            "example": {
                "page_path": "/hvac-emergency",
                "page_title": "24/7 Emergency HVAC Repair",
                "sessions": 890,
                "engaged_sessions": 612,
                "conversions": 38,
                "conversion_rate": 0.043,
                "bounce_rate": 0.31,
                "avg_engagement_time": 95.5,
                "exits": 156,
                "exit_rate": 0.18,
                "status": "high_performing"
            }
        }


class DevicePerformance(BaseModel):
    """Performance breakdown by device category."""
    device_category: str = Field(..., description="mobile, desktop, tablet")
    sessions: int = Field(default=0)
    conversions: int = Field(default=0)
    conversion_rate: float = Field(default=0.0)
    bounce_rate: float = Field(default=0.0)
    avg_page_load_time: float = Field(default=0.0)
    mobile_friendly: bool = Field(default=True)

    class Config:
        json_schema_extra = {
            "example": {
                "device_category": "mobile",
                "sessions": 2345,
                "conversions": 67,
                "conversion_rate": 0.029,
                "bounce_rate": 0.52,
                "avg_page_load_time": 3.2,
                "mobile_friendly": True
            }
        }


class AudienceInsight(BaseModel):
    """Audience demographic and behavioral insights."""
    age_brackets: dict[str, float] = Field(
        default_factory=dict,
        description="Sessions by age bracket"
    )
    gender_split: dict[str, float] = Field(
        default_factory=dict,
        description="Gender distribution"
    )
    interests: list[str] = Field(
        default_factory=list,
        description="Top interests/categories"
    )
    new_vs_returning: dict[str, float] = Field(
        default_factory=dict,
        description="new vs returning session ratio"
    )
    avg_pages_per_session: float = Field(default=0.0)
    avg_session_duration: float = Field(default=0.0)

    class Config:
        json_schema_extra = {
            "example": {
                "age_brackets": {"25-34": 0.35, "35-44": 0.28, "45-54": 0.22},
                "gender_split": {"male": 0.62, "female": 0.38},
                "interests": ["Home Services", "Contractors", "Home Improvement"],
                "new_vs_returning": {"new": 0.68, "returning": 0.32},
                "avg_pages_per_session": 3.2,
                "avg_session_duration": 185.5
            }
        }


class FunnelAnalysis(BaseModel):
    """Conversion funnel stages and drop-off."""
    stages: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Funnel stages with metrics"
    )
    overall_conversion_rate: float = Field(default=0.0)
    cart_abandonment_rate: float | None = Field(None)
    form_abandonment_rate: float | None = Field(None)
    primary_drop_off_stage: str | None = Field(None)

    class Config:
        json_schema_extra = {
            "example": {
                "stages": [
                    {"name": "landing_page_view", "sessions": 1000, "rate": 1.0},
                    {"name": "cta_click", "sessions": 450, "rate": 0.45},
                    {"name": "phone_call", "sessions": 38, "rate": 0.038}
                ],
                "overall_conversion_rate": 0.038,
                "cart_abandonment_rate": None,
                "form_abandonment_rate": 0.72,
                "primary_drop_off_stage": "cta_click"
            }
        }


class GA4ReportQuery(BaseModel):
    """Query parameters for GA4 report."""
    property_id: str = Field(..., description="GA4 property ID")
    start_date: date = Field(..., description="Report start date")
    end_date: date = Field(..., description="Report end date")
    dimensions: list[str] = Field(
        default=["date", "source", "medium", "campaign"],
        description="GA4 dimensions"
    )
    metrics: list[str] = Field(
        default=["sessions", "conversions", "conversionRate", "totalRevenue"],
        description="GA4 metrics"
    )
    dimension_filter: dict[str, Any] | None = Field(None)
    limit: int = Field(default=10000, description="Row limit")


class GA4AnalyticsData(BaseModel):
    """Complete GA4 analytics data for Conversion Architect."""
    report_id: str = Field(..., description="Unique report identifier")
    property_id: str = Field(..., description="GA4 property ID")
    report_date: date = Field(default_factory=date.today)
    date_range: tuple[date, date] = Field(..., description="Data date range")

    # Summary metrics
    total_sessions: int = Field(default=0)
    total_conversions: int = Field(default=0)
    overall_conversion_rate: float = Field(default=0.0)
    total_conversion_value: float = Field(default=0.0)
    avg_conversion_value: float = Field(default=0.0)

    # Performance by keyword
    keyword_performance: list[KeywordPerformance] = Field(default_factory=list)
    top_converting_keywords: list[str] = Field(default_factory=list)
    keywords_need_optimization: list[str] = Field(default_factory=list)

    # Geographic performance
    geographic_performance: list[GeographicPerformance] = Field(default_factory=list)
    best_performing_state: str | None = Field(None)
    worst_performing_state: str | None = Field(None)

    # Page performance
    page_performance: list[PagePerformance] = Field(default_factory=list)
    best_performing_page: str | None = Field(None)

    # Device breakdown
    device_performance: list[DevicePerformance] = Field(default_factory=list)
    mobile_friendly_score: float = Field(default=1.0)

    # Audience insights
    audience_insights: AudienceInsight | None = Field(None)

    # Funnel analysis
    funnel_analysis: FunnelAnalysis | None = Field(None)

    # Trend indicators
    conversion_trend: str = Field(default="stable")  # improving, declining, stable
    conversion_trend_pct: float = Field(default=0.0)

    # Data quality
    data_confidence: str = Field(default="medium")  # high, medium, low
    sample_rate: float | None = Field(None)
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "report_id": "ga4_rpt_2024_01_15",
                "property_id": "properties/123456789",
                "report_date": "2024-01-15",
                "date_range": ("2024-01-01", "2024-01-15"),
                "total_sessions": 15000,
                "total_conversions": 525,
                "overall_conversion_rate": 0.035,
                "total_conversion_value": 26250.00,
                "avg_conversion_value": 50.00,
                "top_converting_keywords": [
                    "emergency plumber",
                    "24 hour locksmith",
                    "hvac repair near me"
                ],
                "best_performing_state": "TX",
                "best_performing_page": "/emergency-services",
                "mobile_friendly_score": 0.85,
                "conversion_trend": "improving",
                "conversion_trend_pct": 12.5,
                "data_confidence": "high"
            }
        }


class GA4InsightRecommendation(BaseModel):
    """Actionable insight from GA4 data."""
    insight_type: str = Field(..., description="Type: keyword, geo, device, content")
    priority: str = Field(default="medium")  # high, medium, low
    title: str = Field(..., description="Insight title")
    description: str = Field(..., description="Detailed description")
    data_supporting: dict[str, Any] = Field(default_factory=dict)
    recommended_action: str = Field(..., description="What to do")
    expected_impact: str = Field(..., description="Expected outcome")
    confidence: str = Field(default="medium")  # high, medium, low

    class Config:
        json_schema_extra = {
            "example": {
                "insight_type": "keyword",
                "priority": "high",
                "title": "High-converting keywords not in campaign",
                "description": "'emergency hvac service' has 4.2% CVR but isn't targeted",
                "data_supporting": {
                    "keyword": "emergency hvac service",
                    "cvr": 0.042,
                    "sessions": 234
                },
                "recommended_action": "Add 'emergency hvac service' to keyword list",
                "expected_impact": "+15% conversions",
                "confidence": "high"
            }
        }


class GA4ConversionInsights(BaseModel):
    """Generated insights from GA4 data for Conversion Architect."""
    insights_id: str = Field(..., description="Unique insights identifier")
    ga4_report_id: str = Field(..., description="Source report ID")
    generated_at: datetime = Field(default_factory=datetime.utcnow)

    # Key insights
    recommendations: list[GA4InsightRecommendation] = Field(default_factory=list)

    # Design implications
    design_implications: list[str] = Field(default_factory=list)
    ux_improvements: list[str] = Field(default_factory=list)
    content_opportunities: list[str] = Field(default_factory=list)

    # Priority actions
    immediate_actions: list[str] = Field(default_factory=list)
    short_term_actions: list[str] = Field(default_factory=list)
    long_term_actions: list[str] = Field(default_factory=list)

    # Success metrics for landing page
    target_cvr: float = Field(default=0.04)
    target_bounce_rate: float = Field(default=0.35)
    target_cta_click_rate: float = Field(default=0.05)

    class Config:
        json_schema_extra = {
            "example": {
                "insights_id": "insights_2024_01_15",
                "ga4_report_id": "ga4_rpt_2024_01_15",
                "recommendations": [
                    {
                        "insight_type": "geo",
                        "priority": "high",
                        "title": "TX outperforms other states by 40%",
                        "description": "Texas has significantly higher CVR",
                        "recommended_action": "Prioritize TX in landing page targeting",
                        "expected_impact": "+25% overall conversions",
                        "confidence": "high"
                    }
                ],
                "design_implications": [
                    "Mobile optimization critical (62% mobile traffic)",
                    "Emergency urgency messaging improves CVR"
                ],
                "target_cvr": 0.05,
                "target_bounce_rate": 0.30,
                "target_cta_click_rate": 0.06
            }
        }
