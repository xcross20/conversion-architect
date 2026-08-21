"""
Design Pattern Provider

Abstraction layer for design pattern sources (MotionSites MCP).
Provides fixture/fallback provider for CI/offline environments.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any
from pydantic import BaseModel, Field

from conversion_architect.schemas import DesignPattern


class PatternQuery(BaseModel):
    """Query parameters for design pattern search."""
    page_type: str | None = None
    section_type: str | None = None
    desired_perceptions: list[str] = Field(default_factory=list)
    vertical: str | None = None
    conversion_goal: str | None = None
    limit: int = Field(default=10)


class DesignPatternProvider(ABC):
    """Abstract base for design pattern providers.
    
    Implementations include:
    - MotionSitesProvider: Real patterns from MotionSites MCP
    - FixtureProvider: Fallback patterns for CI/offline
    """
    
    @abstractmethod
    async def query(self, query: PatternQuery) -> list[DesignPattern]:
        """Query patterns matching criteria."""
        pass
    
    @abstractmethod
    async def get(self, pattern_id: str) -> DesignPattern | None:
        """Get a specific pattern by ID."""
        pass
    
    @abstractmethod
    async def list_sections(self, page_type: str) -> list[str]:
        """List available section types for a page type."""
        pass
    
    @abstractmethod
    async def health_check(self) -> dict[str, Any]:
        """Check provider health and availability."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is currently available."""
        pass


class DesignPatternProviderError(Exception):
    """Error from design pattern provider."""
    pass


class PatternNotFoundError(DesignPatternProviderError):
    """Pattern not found in provider."""
    pass


class ProviderUnavailableError(DesignPatternProviderError):
    """Provider is not available."""
    pass
