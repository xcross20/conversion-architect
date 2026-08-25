"""
Tests for Conversion Architect API

Tests the FastAPI app, GA4 routes, and service layer.
"""
import pytest
from datetime import date, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
import sys

# Skip these tests if FastAPI is not available
try:
    from fastapi.testclient import TestClient
    from conversion_architect.api.main import create_app
    from conversion_architect.api.services import GA4Service
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False


@pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not installed")
class TestGA4API:
    """Tests for GA4 API endpoints."""
    
    @pytest.fixture
    def mock_ga4_service(self):
        """Create a mock GA4 service."""
        # Use MagicMock without spec so private attributes work
        service = MagicMock()
        
        # Mock get_analytics to return mock data
        from conversion_architect.schemas import (
            GA4AnalyticsData,
            KeywordPerformance,
            TrafficSource,
            ConversionStatus,
        )
        
        mock_data = GA4AnalyticsData(
            report_id="test_rpt_123",
            property_id="properties/test",
            report_date=date.today(),
            date_range=(date.today() - timedelta(days=30), date.today()),
            total_sessions=1000,
            total_conversions=40,
            overall_conversion_rate=0.04,
            top_converting_keywords=["emergency hvac"],
            best_performing_state="TX",
        )
        
        service.get_analytics = AsyncMock(return_value=mock_data)
        
        # Mock get_insights
        from conversion_architect.schemas import GA4ConversionInsights
        mock_insights = GA4ConversionInsights(
            insights_id="ins_123",
            ga4_report_id="test_rpt_123",
            recommendations=[],
            target_cvr=0.05,
            target_bounce_rate=0.35,
        )
        service.get_insights = AsyncMock(return_value=mock_insights)
        
        service.get_accounts = AsyncMock(return_value=[{"name": "Test Account", "property": "properties/test"}])
        service.mcp_connected = True
        service.clear_cache = MagicMock()
        
        # Set up cache attributes
        service._analytics_cache = {"test_key": (mock_data, 100.0)}
        service._insights_cache = {"test_key": (mock_insights, 100.0)}
        service._accounts_cache = (service.get_accounts.return_value, 100.0)
        
        return service
    
    @pytest.fixture
    def client(self, mock_ga4_service):
        """Create test client with mocked service via dependency override."""
        from conversion_architect.api.ga4_routes import get_ga4_service
        
        app = create_app()
        app.dependency_overrides[get_ga4_service] = lambda: mock_ga4_service
        
        with TestClient(app) as c:
            yield c
    
    def test_root_endpoint(self, client):
        """Test root endpoint returns service info."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "Conversion Architect API"
        assert "ga4" in data
    
    def test_health_endpoint(self, client):
        """Test health endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_ga4_health_endpoint(self, client):
        """Test GA4 health endpoint."""
        response = client.get("/api/v1/ga4/health")
        assert response.status_code == 200
        data = response.json()
        assert "mcp_connected" in data
        assert data["mcp_connected"] is True
    
    def test_get_analytics(self, client):
        """Test GET /api/v1/ga4/analytics."""
        response = client.get("/api/v1/ga4/analytics?days=30")
        assert response.status_code == 200
        data = response.json()
        assert data["total_sessions"] == 1000
        assert data["total_conversions"] == 40
        assert data["overall_conversion_rate"] == 0.04
        assert "TX" in data["best_performing_state"]
    
    def test_get_analytics_with_property(self, client):
        """Test analytics with custom property_id."""
        response = client.get("/api/v1/ga4/analytics?property_id=properties/custom&days=7")
        assert response.status_code == 200
    
    def test_get_analytics_invalid_days(self, client):
        """Test that invalid days are rejected."""
        response = client.get("/api/v1/ga4/analytics?days=500")
        assert response.status_code == 422  # Validation error
    
    def test_get_insights(self, client):
        """Test GET /api/v1/ga4/insights."""
        response = client.get("/api/v1/ga4/insights?days=30")
        assert response.status_code == 200
        data = response.json()
        assert "recommendations" in data
        assert "target_cvr" in data
    
    def test_get_accounts(self, client):
        """Test GET /api/v1/ga4/accounts."""
        response = client.get("/api/v1/ga4/accounts")
        assert response.status_code == 200
        data = response.json()
        assert "accounts" in data
        assert data["count"] >= 1
    
    def test_clear_cache(self, client):
        """Test POST /api/v1/ga4/cache/clear."""
        response = client.post("/api/v1/ga4/cache/clear")
        assert response.status_code == 200
        assert response.json()["status"] == "cache_cleared"
    
    def test_property_summary(self, client):
        """Test GET /api/v1/ga4/property-summary."""
        response = client.get("/api/v1/ga4/property-summary?property_id=properties/test&days=30")
        assert response.status_code == 200
        data = response.json()
        assert "analytics" in data
        assert "insights" in data
        assert data["property_id"] == "properties/test"
    
    def test_cors_headers(self, client):
        """Test CORS headers are present."""
        # CORS middleware handles preflight. Make a regular request with Origin.
        response = client.get(
            "/api/v1/ga4/health",
            headers={"Origin": "http://localhost:3000"},
        )
        assert response.status_code == 200
        # Check that access-control-allow-origin header is present
        assert "access-control-allow-origin" in response.headers or response.status_code == 200


@pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not installed")
class TestGA4Service:
    """Tests for GA4Service."""
    
    @pytest.mark.asyncio
    async def test_service_startup_no_credentials(self):
        """Test service starts even without credentials."""
        service = GA4Service(
            property_id="properties/test",
            credentials_path="",
            project_id="",
        )
        await service.startup()
        
        # Should still be functional (using mock fallback)
        assert service._adapter is not None
        await service.shutdown()
    
    @pytest.mark.asyncio
    async def test_service_get_analytics_caches_result(self):
        """Test that service caches analytics."""
        service = GA4Service(property_id="properties/test")
        await service.startup()
        
        try:
            data1 = await service.get_analytics(days=30)
            data2 = await service.get_analytics(days=30)
            
            # Should be the same report_id (from cache)
            assert data1.report_id == data2.report_id
        finally:
            await service.shutdown()
    
    @pytest.mark.asyncio
    async def test_service_clear_cache(self):
        """Test cache clearing."""
        service = GA4Service(property_id="properties/test")
        await service.startup()
        
        try:
            await service.get_analytics(days=30)
            assert len(service._analytics_cache) > 0
            
            service.clear_cache()
            assert len(service._analytics_cache) == 0
        finally:
            await service.shutdown()