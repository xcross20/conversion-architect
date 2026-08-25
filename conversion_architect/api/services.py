"""
GA4 Service

Owns the GA4MCPClient instance and provides cached access to GA4 data.
Handles connection lifecycle, fallback to mock data, and caching.
"""
from __future__ import annotations

import asyncio
import logging
import time
from datetime import date, timedelta
from typing import Any

from conversion_architect.adapters import GA4Adapter
from conversion_architect.providers import GA4MCPClient, GA4MCPClientError
from conversion_architect.schemas import (
    GA4AnalyticsData,
    GA4ConversionInsights,
    BusinessConversionContext,
)

logger = logging.getLogger(__name__)


class GA4Service:
    """Service that manages GA4 MCP client and adapter.
    
    Provides:
    - Singleton MCP client lifecycle
    - In-memory cache with TTL
    - Fallback to mock data on MCP failure
    - Insights generation
    - Context enrichment
    
    Usage:
        service = GA4Service(
            property_id="properties/123",
            credentials_path="/path/to/creds.json",
            cache_ttl=3600,
        )
        await service.startup()
        
        data = await service.get_analytics(days=30)
        insights = await service.get_insights(property_id="properties/123")
        
        await service.shutdown()
    """
    
    def __init__(
        self,
        property_id: str = "",
        credentials_path: str = "",
        project_id: str = "",
        mcp_command: str = "",
        cache_ttl: int = 3600,
    ):
        """Initialize GA4 service.
        
        Args:
            property_id: Default GA4 property ID
            credentials_path: Path to Google OAuth credentials JSON
            project_id: Google Cloud project ID
            mcp_command: Override MCP server command
            cache_ttl: Cache TTL in seconds
        """
        self._default_property_id = property_id
        self._credentials_path = credentials_path
        self._project_id = project_id
        self._mcp_command = mcp_command
        self._cache_ttl = cache_ttl
        
        self._mcp_client: GA4MCPClient | None = None
        self._adapter: GA4Adapter | None = None
        self._lock = asyncio.Lock()
        
        # Cache: key -> (data, timestamp)
        self._analytics_cache: dict[str, tuple[GA4AnalyticsData, float]] = {}
        self._insights_cache: dict[str, tuple[GA4ConversionInsights, float]] = {}
        self._accounts_cache: tuple[list[dict[str, Any]], float] | None = None
    
    async def startup(self) -> None:
        """Start the GA4 service."""
        try:
            # Build MCP client
            client_kwargs = {}
            if self._credentials_path:
                client_kwargs["credentials_path"] = self._credentials_path
            if self._project_id:
                client_kwargs["project_id"] = self._project_id
            if self._mcp_command:
                client_kwargs["mcp_command"] = self._mcp_command
            
            self._mcp_client = GA4MCPClient(**client_kwargs)
            
            # Try to connect (may fail if no credentials)
            try:
                await self._mcp_client.connect()
                logger.info("GA4 MCP client connected")
            except GA4MCPClientError as e:
                logger.warning(f"GA4 MCP connection failed: {e}. Using mock fallback.")
            
            # Build adapter
            self._adapter = GA4Adapter(
                mcp_client=self._mcp_client,
                property_id=self._default_property_id or "properties/demo",
            )
            
        except Exception as e:
            logger.error(f"GA4 service startup failed: {e}")
            # Don't crash the app; degrade gracefully
            self._mcp_client = None
            self._adapter = GA4Adapter(property_id=self._default_property_id or "properties/demo")
    
    async def shutdown(self) -> None:
        """Shut down the GA4 service."""
        if self._mcp_client and self._mcp_client.is_connected:
            try:
                await self._mcp_client.disconnect()
            except Exception as e:
                logger.warning(f"GA4 MCP disconnect error: {e}")
    
    def _is_cache_valid(self, timestamp: float) -> bool:
        """Check if cache entry is still valid."""
        return (time.time() - timestamp) < self._cache_ttl
    
    async def get_analytics(
        self,
        property_id: str | None = None,
        days: int = 30,
        use_cache: bool = True,
    ) -> GA4AnalyticsData:
        """Fetch GA4 analytics data.
        
        Args:
            property_id: GA4 property ID (overrides default)
            days: Number of days to look back
            use_cache: Whether to use cache
            
        Returns:
            GA4AnalyticsData with conversion metrics
        """
        prop = property_id or self._default_property_id
        if not prop:
            raise ValueError("property_id required")
        
        cache_key = f"{prop}_{days}"
        
        if use_cache and cache_key in self._analytics_cache:
            data, ts = self._analytics_cache[cache_key]
            if self._is_cache_valid(ts):
                logger.info(f"Cache hit for {cache_key}")
                return data
        
        async with self._lock:
            # Double-check after acquiring lock
            if use_cache and cache_key in self._analytics_cache:
                data, ts = self._analytics_cache[cache_key]
                if self._is_cache_valid(ts):
                    return data
            
            # Ensure adapter uses the right property
            if self._adapter and self._adapter._property_id != prop:
                self._adapter._property_id = prop
            
            # Fetch fresh data
            start = date.today() - timedelta(days=days)
            end = date.today()
            
            try:
                data = await self._adapter.fetch_analytics(
                    property_id=prop,
                    start_date=start,
                    end_date=end,
                    use_cache=False,  # We handle caching here
                )
            except Exception as e:
                logger.error(f"Failed to fetch analytics: {e}")
                raise
            
            # Cache result
            self._analytics_cache[cache_key] = (data, time.time())
            
            return data
    
    async def get_insights(
        self,
        property_id: str | None = None,
        days: int = 30,
        use_cache: bool = True,
    ) -> GA4ConversionInsights:
        """Generate conversion insights from GA4 data.
        
        Args:
            property_id: GA4 property ID
            days: Number of days to look back
            use_cache: Whether to use cache
            
        Returns:
            GA4ConversionInsights with recommendations
        """
        prop = property_id or self._default_property_id
        
        cache_key = f"{prop}_{days}"
        if use_cache and cache_key in self._insights_cache:
            insights, ts = self._insights_cache[cache_key]
            if self._is_cache_valid(ts):
                return insights
        
        async with self._lock:
            if use_cache and cache_key in self._insights_cache:
                insights, ts = self._insights_cache[cache_key]
                if self._is_cache_valid(ts):
                    return insights
            
            # Fetch analytics first, then generate insights
            data = await self.get_analytics(property_id=prop, days=days, use_cache=True)
            
            if not self._adapter:
                raise RuntimeError("GA4 adapter not initialized")
            
            insights = await self._adapter.generate_insights(data)
            self._insights_cache[cache_key] = (insights, time.time())
            
            return insights
    
    async def get_accounts(self, use_cache: bool = True) -> list[dict[str, Any]]:
        """List GA4 accounts and properties.
        
        Args:
            use_cache: Whether to use cache
            
        Returns:
            List of account summaries
        """
        if not self._mcp_client:
            return []
        
        if use_cache and self._accounts_cache is not None:
            data, ts = self._accounts_cache
            if self._is_cache_valid(ts):
                return data
        
        async with self._lock:
            if use_cache and self._accounts_cache is not None:
                data, ts = self._accounts_cache
                if self._is_cache_valid(ts):
                    return data
            
            try:
                if not self._mcp_client.is_connected:
                    await self._mcp_client.connect()
                
                accounts = await self._mcp_client.get_account_summaries()
                # accounts might be a string or dict; normalize to list
                if isinstance(accounts, dict):
                    accounts = [accounts]
                elif isinstance(accounts, str):
                    accounts = [{"raw": accounts}]
                elif not isinstance(accounts, list):
                    accounts = []
                
                self._accounts_cache = (accounts, time.time())
                return accounts
            except Exception as e:
                logger.error(f"Failed to list accounts: {e}")
                return []
    
    async def enrich_context(
        self,
        context: BusinessConversionContext,
        property_id: str | None = None,
        days: int = 30,
    ) -> BusinessConversionContext:
        """Enrich a BusinessConversionContext with GA4 data.
        
        Args:
            context: Existing business context
            property_id: GA4 property ID
            days: Days to look back
            
        Returns:
            Enriched BusinessConversionContext
        """
        if not self._adapter:
            return context
        
        data = await self.get_analytics(property_id=property_id, days=days)
        insights = await self.get_insights(property_id=property_id, days=days)
        
        return self._adapter.enrich_context(context, data, insights)
    
    def clear_cache(self) -> None:
        """Clear all caches."""
        self._analytics_cache.clear()
        self._insights_cache.clear()
        self._accounts_cache = None
        if self._adapter:
            self._adapter.clear_cache()
    
    @property
    def mcp_connected(self) -> bool:
        """Check if MCP client is connected."""
        return self._mcp_client is not None and self._mcp_client.is_connected