"""
DeploymentRef Schema
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class DeploymentStatus(str, Enum):
    PENDING = "pending"
    BUILDING = "building"
    PREVIEW_LIVE = "preview_live"
    DEPLOYED = "deployed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class DeploymentEnvironment(str, Enum):
    PREVIEW = "preview"
    STAGING = "staging"
    PRODUCTION = "production"


class DeploymentRef(BaseModel):
    """DeploymentRef is a handle for tracking deployment state.
    
    This is NOT the deployment itself — it's a reference that tracks
    where a genome has been deployed and its current status.
    """
    
    # Identity
    deployment_id: str = Field(..., description="Unique deployment identifier")
    genome_id: str = Field(..., description="Source genome ID")
    
    # Environment
    environment: DeploymentEnvironment = Field(..., description="Deployment environment")
    
    # Provider references
    provider: str = Field(default="framer", description="Deployment provider (framer, webflow, etc.)")
    provider_project_id: str | None = Field(None, description="Provider's project ID")
    provider_branch_id: str | None = Field(None, description="Provider's branch ID")
    provider_deployment_id: str | None = Field(None, description="Provider's deployment ID")
    
    # URLs
    preview_url: str | None = Field(None, description="Preview URL")
    production_url: str | None = Field(None, description="Production URL (if deployed)")
    custom_domain: str | None = Field(None, description="Custom domain (if configured)")
    
    # Status
    status: DeploymentStatus = Field(default=DeploymentStatus.PENDING)
    build_logs: list[str] = Field(default_factory=list)
    error_message: str | None = Field(None, description="Error message if failed")
    
    # History
    previous_deployment_id: str | None = Field(None, description="Previous deployment for rollback")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deployed_at: datetime | None = Field(None, description="When successfully deployed")
    
    # Authority checks
    can_promote: bool = Field(default=False, description="Can be promoted to production")
    promotion_blocked_reason: str | None = Field(
        None,
        description="Reason promotion is blocked (if applicable)"
    )
    
    # Metadata
    meta_data: dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "deployment_id": "deploy_hvac_001_preview",
                "genome_id": "genome_hvac_emergency_001",
                "environment": "preview",
                "provider": "framer",
                "provider_project_id": "proj_abc123",
                "provider_branch_id": "branch_preview_hvac_001",
                "preview_url": "https://hvac-preview.framer.app",
                "status": "preview_live",
                "can_promote": True,
                "promotion_blocked_reason": None
            }
        }
