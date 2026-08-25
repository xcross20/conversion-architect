"""
Conversion Architect Providers
"""
from conversion_architect.providers.design_pattern_provider import (
    DesignPatternProvider,
    PatternQuery,
    DesignPatternProviderError,
    PatternNotFoundError,
    ProviderUnavailableError,
)
from conversion_architect.providers.motionsites import MotionSitesProvider, create_motionsites_provider
from conversion_architect.providers.fixture_provider import FixtureProvider, create_fixture_provider
from conversion_architect.providers.framer import (
    FramerProvider,
    FramerProviderError,
    AuthError,
    DeploymentError,
    PromotionDeniedError,
    create_framer_provider,
)
from conversion_architect.providers.ga4_mcp_client import (
    GA4MCPClient,
    GA4MCPClientError,
    create_ga4_mcp_client,
)

__all__ = [
    # Base classes
    "DesignPatternProvider",
    "PatternQuery",
    "DesignPatternProviderError",
    "PatternNotFoundError",
    "ProviderUnavailableError",
    "FramerProvider",
    "FramerProviderError",
    "AuthError",
    "DeploymentError",
    "PromotionDeniedError",
    # Implementations
    "MotionSitesProvider",
    "create_motionsites_provider",
    "FixtureProvider",
    "create_fixture_provider",
    "create_framer_provider",
    # GA4 MCP
    "GA4MCPClient",
    "GA4MCPClientError",
    "create_ga4_mcp_client",
]