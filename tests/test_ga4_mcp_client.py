"""
Tests for GA4 MCP Client

Tests the MCP client wrapper and integration with analytics-mcp server.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import sys

# Skip these tests if mcp is not available
try:
    from conversion_architect.providers.ga4_mcp_client import (
        GA4MCPClient,
        GA4MCPClientError,
        create_ga4_mcp_client,
    )
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False


@pytest.mark.skipif(not MCP_AVAILABLE, reason="mcp package not installed")
class TestGA4MCPClient:
    """Tests for GA4MCPClient."""
    
    def test_client_finds_mcp_command(self):
        """Test that client finds analytics-mcp command."""
        client = GA4MCPClient()
        assert client._mcp_command is not None
        assert "analytics-mcp" in client._mcp_command or "google-analytics-mcp" in client._mcp_command
    
    def test_client_uses_credentials_from_env(self):
        """Test that client reads credentials from environment."""
        with patch.dict('os.environ', {
            'GOOGLE_APPLICATION_CREDENTIALS': '/path/to/creds.json',
            'GOOGLE_PROJECT_ID': 'test-project',
        }):
            client = GA4MCPClient()
            assert client._credentials_path == '/path/to/creds.json'
            assert client._project_id == 'test-project'
    
    def test_client_uses_explicit_credentials(self):
        """Test that explicit credentials override env."""
        client = GA4MCPClient(
            credentials_path='/explicit/path.json',
            project_id='explicit-project'
        )
        assert client._credentials_path == '/explicit/path.json'
        assert client._project_id == 'explicit-project'
    
    def test_client_not_connected_by_default(self):
        """Test client is not connected at init."""
        client = GA4MCPClient()
        assert client.is_connected is False
    
    def test_create_ga4_mcp_client_factory(self):
        """Test factory function."""
        client = create_ga4_mcp_client(
            credentials_path='/test/creds.json',
            project_id='test-project',
        )
        assert isinstance(client, GA4MCPClient)
        assert client._credentials_path == '/test/creds.json'
        assert client._project_id == 'test-project'
    
    @pytest.mark.asyncio
    async def test_extract_content_from_text_result(self):
        """Test content extraction from text result."""
        client = GA4MCPClient()
        
        # Mock result with text content
        mock_result = MagicMock()
        mock_result.content = [{"text": '{"rows": [], "total": 0}'}]
        
        result = client._extract_content(mock_result)
        assert isinstance(result, dict)
        assert result.get("rows") == []
    
    @pytest.mark.asyncio
    async def test_extract_content_from_string_result(self):
        """Test content extraction when content is a string."""
        client = GA4MCPClient()
        
        mock_result = MagicMock()
        mock_result.content = "simple string"
        
        result = client._extract_content(mock_result)
        assert result == "simple string"
    
    @pytest.mark.asyncio
    async def test_extract_content_passthrough(self):
        """Test content extraction when result has no content attr."""
        client = GA4MCPClient()
        result = {"direct": "data"}
        assert client._extract_content(result) == result


@pytest.mark.skipif(not MCP_AVAILABLE, reason="mcp package not installed")
class TestGA4AdapterWithMCP:
    """Tests for GA4Adapter integration with MCP client."""
    
    @pytest.mark.asyncio
    async def test_adapter_falls_back_to_mock_when_no_client(self):
        """Test adapter uses mock data when no MCP client provided."""
        from conversion_architect.adapters.ga4_adapter import create_ga4_adapter
        
        adapter = create_ga4_adapter(property_id="properties/test")
        data = await adapter.fetch_analytics()
        
        # Should still return data via mock fallback
        assert data.property_id == "properties/test"
        assert data.total_sessions > 0
    
    @pytest.mark.asyncio
    async def test_adapter_uses_mcp_client(self):
        """Test adapter calls MCP client when provided."""
        from conversion_architect.adapters.ga4_adapter import create_ga4_adapter
        
        # Mock MCP client
        mock_client = MagicMock()
        mock_client.is_connected = True
        mock_client.run_report = AsyncMock(return_value={
            "rows": [
                {
                    "values": [
                        "google", "cpc", "campaign_1", "TX", "desktop", "/test",
                        "1000", "50", "0.05", "2500", "0.35", "120", "1500"
                    ]
                }
            ],
            "dimensionHeaders": [
                {"name": "sessionSource"},
                {"name": "sessionMedium"},
                {"name": "sessionCampaignName"},
                {"name": "geoRegion"},
                {"name": "deviceCategory"},
                {"name": "pagePath"},
            ],
            "metricHeaders": [
                {"name": "sessions"},
                {"name": "conversions"},
                {"name": "conversionRate"},
                {"name": "totalRevenue"},
                {"name": "bounceRate"},
                {"name": "averageSessionDuration"},
                {"name": "screenPageViews"},
            ],
        })
        
        adapter = create_ga4_adapter(
            property_id="properties/test",
            mcp_client=mock_client,
        )
        
        data = await adapter.fetch_analytics()
        
        # Should have called MCP client
        mock_client.run_report.assert_called_once()
        
        # Should have parsed data from MCP response
        assert data.total_sessions == 1000
        assert data.total_conversions == 50
        assert data.overall_conversion_rate == pytest.approx(0.05)
        assert data.total_conversion_value == pytest.approx(2500.0)
        assert len(data.keyword_performance) > 0
    
    @pytest.mark.asyncio
    async def test_adapter_falls_back_when_mcp_fails(self):
        """Test adapter falls back to mock when MCP fails."""
        from conversion_architect.adapters.ga4_adapter import create_ga4_adapter
        
        # Mock MCP client that fails
        mock_client = MagicMock()
        mock_client.is_connected = True
        mock_client.run_report = AsyncMock(side_effect=Exception("MCP error"))
        
        adapter = create_ga4_adapter(
            property_id="properties/test",
            mcp_client=mock_client,
        )
        
        # Should not raise, should fall back to mock
        data = await adapter.fetch_analytics()
        
        assert data.property_id == "properties/test"
        assert data.total_sessions > 0  # Mock data
    
    @pytest.mark.asyncio
    async def test_adapter_connects_mcp_if_not_connected(self):
        """Test adapter connects MCP client if not already connected."""
        from conversion_architect.adapters.ga4_adapter import create_ga4_adapter
        
        mock_client = MagicMock()
        mock_client.is_connected = False
        mock_client.connect = AsyncMock()
        mock_client.run_report = AsyncMock(return_value={"rows": []})
        
        adapter = create_ga4_adapter(
            property_id="properties/test",
            mcp_client=mock_client,
        )
        
        await adapter.fetch_analytics()
        
        mock_client.connect.assert_called_once()
        mock_client.run_report.assert_called_once()