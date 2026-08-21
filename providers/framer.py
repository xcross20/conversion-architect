"""
Framer Provider

Abstraction layer for Framer API integration.
Handles branch creation, genome compilation, preview, and deployment.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any
from enum import Enum
from pydantic import BaseModel, Field
import logging

from conversion_architect.schemas import LanderGenome, DeploymentRef

logger = logging.getLogger(__name__)


class FramerAuthStatus(str, Enum):
    AUTHENTICATED = "authenticated"
    UNAUTHENTICATED = "unauthenticated"
    EXPIRED = "expired"


class BranchStatus(str, Enum):
    CREATING = "creating"
    ACTIVE = "active"
    DELETED = "deleted"


class FramerProviderError(Exception):
    """Error from Framer provider."""
    pass


class AuthError(FramerProviderError):
    """Authentication error."""
    pass


class DeploymentError(FramerProviderError):
    """Deployment error."""
    pass


class PromotionDeniedError(FramerProviderError):
    """Production promotion denied (safety check)."""
    pass


class FramerProvider(ABC):
    """Abstract base for Framer API integration.
    
    Handles:
    - Authentication
    - Branch creation for preview
    - Genome compilation/updates
    - Preview publishing
    - Deployment status checking
    - Production promotion (with safety checks)
    - Rollback
    
    SAFETY: All autonomous variants use branch preview.
    Live promotion to production is DENIED in WO-CA-0001.
    """
    
    @abstractmethod
    async def connect(self) -> FramerAuthStatus:
        """Authenticate with Framer API.
        
        Returns:
            Authentication status
        """
        pass
    
    @abstractmethod
    async def create_branch(self, name: str, base_project_id: str | None = None) -> dict[str, Any]:
        """Create a preview branch.
        
        Args:
            name: Branch name
            base_project_id: Optional base project ID
            
        Returns:
            Branch details including ID and status
        """
        pass
    
    @abstractmethod
    async def compile_genome(
        self,
        genome: LanderGenome,
        branch_id: str
    ) -> dict[str, Any]:
        """Compile genome to Framer branch.
        
        Args:
            genome: LanderGenome to compile
            branch_id: Target branch ID
            
        Returns:
            Compilation result
        """
        pass
    
    @abstractmethod
    async def publish_preview(self, branch_id: str) -> str:
        """Publish preview and return URL.
        
        Args:
            branch_id: Branch to publish
            
        Returns:
            Preview URL
        """
        pass
    
    @abstractmethod
    async def get_deployment_status(self, deployment_id: str) -> dict[str, Any]:
        """Get deployment status.
        
        Args:
            deployment_id: Deployment ID to check
            
        Returns:
            Status details
        """
        pass
    
    @abstractmethod
    async def promote_to_production(self, branch_id: str) -> dict[str, Any]:
        """Promote preview to production.
        
        SAFETY: This is DENIED in WO-CA-0001.
        Raises PromotionDeniedError.
        
        Args:
            branch_id: Branch to promote
            
        Raises:
            PromotionDeniedError: Always raised (safety)
        """
        pass
    
    @abstractmethod
    async def rollback(self, deployment_id: str) -> dict[str, Any]:
        """Rollback to previous deployment.
        
        Args:
            deployment_id: Deployment to rollback from
            
        Returns:
            Rollback result
        """
        pass
    
    @abstractmethod
    async def get_changed_paths(self, branch_id: str) -> list[str]:
        """Get changed paths since last deployment.
        
        Args:
            branch_id: Branch to check
            
        Returns:
            List of changed paths
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> dict[str, Any]:
        """Check Framer API health."""
        pass


class MockFramerProvider(FramerProvider):
    """Mock Framer provider for testing/development.
    
    Simulates Framer API behavior without actual API calls.
    """
    
    def __init__(self):
        """Initialize mock provider."""
        self._auth_status = FramerAuthStatus.UNAUTHENTICATED
        self._branches: dict[str, dict[str, Any]] = {}
        self._deployments: dict[str, dict[str, Any]] = {}
        self._compilations: list[dict[str, Any]] = []
        self._next_branch_id = 1
        self._next_deployment_id = 1
    
    async def connect(self) -> FramerAuthStatus:
        """Mock authentication."""
        self._auth_status = FramerAuthStatus.AUTHENTICATED
        logger.info("Mock Framer: authenticated")
        return FramerAuthStatus.AUTHENTICATED
    
    async def create_branch(self, name: str, base_project_id: str | None = None) -> dict[str, Any]:
        """Mock branch creation."""
        branch_id = f"branch_{self._next_branch_id}"
        self._next_branch_id += 1
        
        branch = {
            "branch_id": branch_id,
            "name": name,
            "project_id": base_project_id or "proj_default",
            "status": BranchStatus.ACTIVE.value,
            "created_at": "2026-08-21T00:00:00Z"
        }
        self._branches[branch_id] = branch
        logger.info(f"Mock Framer: created branch {branch_id}")
        return branch
    
    async def compile_genome(
        self,
        genome: LanderGenome,
        branch_id: str
    ) -> dict[str, Any]:
        """Mock genome compilation."""
        result = {
            "success": True,
            "branch_id": branch_id,
            "genome_id": genome.genome_id,
            "genes_compiled": len(genome.genes),
            "sections_created": len(genome.section_order),
            "compilation_id": f"comp_{len(self._compilations) + 1}"
        }
        self._compilations.append(result)
        logger.info(f"Mock Framer: compiled genome {genome.genome_id} to branch {branch_id}")
        return result
    
    async def publish_preview(self, branch_id: str) -> str:
        """Mock preview publishing."""
        preview_url = f"https://{branch_id}.preview.framer.app"
        logger.info(f"Mock Framer: published preview {preview_url}")
        return preview_url
    
    async def get_deployment_status(self, deployment_id: str) -> dict[str, Any]:
        """Mock deployment status."""
        deployment = self._deployments.get(deployment_id, {
            "deployment_id": deployment_id,
            "status": "preview_live",
            "url": f"https://{deployment_id}.preview.framer.app"
        })
        return deployment
    
    async def promote_to_production(self, branch_id: str) -> dict[str, Any]:
        """DENIED - Production promotion not allowed in WO-CA-0001."""
        raise PromotionDeniedError(
            "Production promotion is DENIED in WO-CA-0001. "
            "This is a safety feature. To enable production promotion, "
            "set AUTHORITY=RED for the promote_to_production action."
        )
    
    async def rollback(self, deployment_id: str) -> dict[str, Any]:
        """Mock rollback."""
        logger.info(f"Mock Framer: rolled back deployment {deployment_id}")
        return {
            "success": True,
            "deployment_id": deployment_id,
            "rolled_back_to": "previous"
        }
    
    async def get_changed_paths(self, branch_id: str) -> list[str]:
        """Mock changed paths."""
        return ["/", "/hero", "/features", "/cta"]
    
    async def health_check(self) -> dict[str, Any]:
        """Mock health check."""
        return {
            "available": True,
            "provider": "framer_mock",
            "auth_status": self._auth_status.value,
            "branches_created": len(self._branches)
        }


def create_framer_provider(mock: bool = True) -> FramerProvider:
    """Create Framer provider instance.
    
    Args:
        mock: If True, return MockFramerProvider
        
    Returns:
        FramerProvider instance
    """
    if mock:
        return MockFramerProvider()
    # In production, return RealFramerProvider
    return MockFramerProvider()  # Default to mock for safety
