"""
GA4 API Routes

HTTP endpoints that proxy requests to the GA4 MCP server.
Provides a way for the Framer plugin (and other browser clients) to fetch
GA4 data without needing direct access to the MCP stdio server.
"""
from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from conversion_architect.api.services import GA4Service
from conversion_architect.schemas import (
    GA4AnalyticsData,
    GA4ConversionInsights,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/ga4", tags=["GA4"])


def get_ga4_service(request: Request) -> GA4Service:
    """Get GA4 service from app state."""
    service = getattr(request.app.state, "ga4_service", None)
    if service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GA4 service not initialized",
        )
    return service


@router.get("/health")
async def ga4_health(service: GA4Service = Depends(get_ga4_service)) -> dict[str, Any]:
    """Check GA4 service and MCP connection health."""
    return {
        "service": "healthy",
        "mcp_connected": service.mcp_connected,
        "cache_size": {
            "analytics": len(service._analytics_cache),
            "insights": len(service._insights_cache),
            "accounts": 1 if service._accounts_cache else 0,
        },
    }


@router.get("/accounts")
async def list_ga4_accounts(
    service: GA4Service = Depends(get_ga4_service),
    use_cache: bool = Query(default=True),
) -> dict[str, Any]:
    """List available GA4 accounts and properties.
    
    Returns:
        List of account summaries with properties
    """
    accounts = await service.get_accounts(use_cache=use_cache)
    
    return {
        "count": len(accounts),
        "accounts": accounts,
        "mcp_connected": service.mcp_connected,
    }


@router.get("/analytics", response_model=None)
async def get_ga4_analytics(
    service: GA4Service = Depends(get_ga4_service),
    property_id: str | None = Query(default=None, description="GA4 property ID"),
    days: int = Query(default=30, ge=1, le=365, description="Days to look back"),
    use_cache: bool = Query(default=True),
) -> dict[str, Any]:
    """Fetch GA4 analytics data.
    
    Returns:
        GA4AnalyticsData as JSON
    """
    try:
        data = await service.get_analytics(
            property_id=property_id,
            days=days,
            use_cache=use_cache,
        )
        return data.model_dump(mode="json")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Failed to fetch analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch analytics: {e}",
        )


@router.get("/insights", response_model=None)
async def get_ga4_insights(
    service: GA4Service = Depends(get_ga4_service),
    property_id: str | None = Query(default=None, description="GA4 property ID"),
    days: int = Query(default=30, ge=1, le=365),
    use_cache: bool = Query(default=True),
) -> dict[str, Any]:
    """Generate conversion insights from GA4 data.
    
    Returns:
        GA4ConversionInsights with recommendations
    """
    try:
        insights = await service.get_insights(
            property_id=property_id,
            days=days,
            use_cache=use_cache,
        )
        return insights.model_dump(mode="json")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Failed to generate insights: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate insights: {e}",
        )


@router.post("/cache/clear")
async def clear_ga4_cache(
    service: GA4Service = Depends(get_ga4_service),
) -> dict[str, Any]:
    """Clear all GA4 caches."""
    service.clear_cache()
    return {"status": "cache_cleared"}


@router.get("/property-summary")
async def get_property_summary(
    property_id: str = Query(..., description="GA4 property ID (e.g., properties/123456789)"),
    service: GA4Service = Depends(get_ga4_service),
    days: int = Query(default=30, ge=1, le=365),
) -> dict[str, Any]:
    """Get a one-shot summary combining analytics and insights.
    
    Useful for the Framer plugin to fetch everything in a single call.
    
    Returns:
        Dict with analytics + insights + property metadata
    """
    try:
        analytics = await service.get_analytics(property_id=property_id, days=days)
        insights = await service.get_insights(property_id=property_id, days=days)
        
        return {
            "property_id": property_id,
            "report_date": analytics.report_date.isoformat() if hasattr(analytics.report_date, 'isoformat') else str(analytics.report_date),
            "date_range": [str(d) for d in analytics.date_range],
            "analytics": analytics.model_dump(mode="json"),
            "insights": insights.model_dump(mode="json"),
            "mcp_connected": service.mcp_connected,
        }
    except Exception as e:
        logger.error(f"Failed to fetch property summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch property summary: {e}",
        )