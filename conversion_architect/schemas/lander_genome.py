"""
LanderGenome Schema
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class GenomeStatus(str, Enum):
    DRAFT = "draft"
    COMPILED = "compiled"
    QA_PASSED = "qa_passed"
    QA_FAILED = "qa_failed"
    PREVIEW_READY = "preview_ready"
    DEPLOYED = "deployed"
    ARCHIVED = "archived"


class DeploymentEnvironment(str, Enum):
    PREVIEW = "preview"
    STAGING = "staging"
    PRODUCTION = "production"


class LanderGenome(BaseModel):
    """LanderGenome is the canonical output of the Conversion Architect.
    
    A genome is a complete, validated specification for a landing page.
    It is NOT a Framer object — Framer is an output target.
    
    The genome can be compiled into Framer, Webflow, or any other
    landing page system that supports the gene structure.
    """
    
    # Identity
    genome_id: str = Field(..., description="Unique genome identifier")
    name: str = Field(..., description="Human-readable genome name")
    version: str = Field(default="1.0.0")
    
    # Context
    family_id: str = Field(..., description="Design family ID")
    skin_id: str | None = Field(None, description="Vertical skin ID")
    
    # Source mapping (from CallQuant)
    campaign_cell_id: str | None = Field(None, description="Source campaign cell")
    intent_cluster_id: str | None = Field(None, description="Source intent cluster")
    offer_variant_id: str | None = Field(None, description="Source offer variant")
    claim_manifest_id: str | None = Field(None, description="Source claim manifest")
    experiment_id: str | None = Field(None, description="Design experiment ID")
    
    # Genes (components)
    genes: list[dict[str, Any]] = Field(
        default_factory=list,
        description="List of genome genes"
    )
    section_order: list[str] = Field(
        default_factory=list,
        description="Ordered list of page sections"
    )
    
    # Claims validation
    supported_claims: list[str] = Field(
        default_factory=list,
        description="Claims this genome makes"
    )
    unsupported_claims: list[str] = Field(
        default_factory=list,
        description="Claims explicitly excluded"
    )
    claim_source: str | None = Field(
        None,
        description="Source claim manifest ID"
    )
    
    # Tracking
    tracking_config: dict[str, Any] = Field(
        default_factory=dict,
        description="UTM, pixel, and event tracking configuration"
    )
    click_to_call_config: dict[str, Any] | None = Field(
        None,
        description="Click-to-call phone number and routing"
    )
    
    # Compliance
    disclosures: list[str] = Field(
        default_factory=list,
        description="Required legal disclosures"
    )
    compliance_status: str = Field(default="pending")
    
    # QA
    qa_status: GenomeStatus = Field(default=GenomeStatus.DRAFT)
    qa_audit_id: str | None = Field(None, description="Latest QA audit ID")
    qa_issues: list[dict[str, Any]] = Field(default_factory=list)
    
    # Status
    status: GenomeStatus = Field(default=GenomeStatus.DRAFT)
    validation_errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    
    # Deployment
    deployment_ref: dict[str, Any] | None = Field(None, description="Deployment reference")
    preview_url: str | None = Field(None, description="Preview URL")
    production_url: str | None = Field(None, description="Production URL")
    
    # Economics
    primary_metric: str | None = Field(
        None,
        description="Primary economic metric (e.g., cost_per_call, conversion_rate)"
    )
    target_metric_value: float | None = Field(
        None,
        description="Target value for primary metric"
    )
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str = Field(default="system")
    meta_data: dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "genome_id": "genome_hvac_emergency_001",
                "name": "HVAC Emergency Landing Page v1",
                "version": "1.0.0",
                "family_id": "portfolio_v1",
                "skin_id": "emergency_home_services_v1",
                "campaign_cell_id": "cell_hvac_emergency",
                "intent_cluster_id": "intent_hvac_emergency",
                "offer_variant_id": "offer_hvac_24hr",
                "claim_manifest_id": "manifest_hvac_001",
                "genes": [
                    {
                        "gene_id": "hero_g1",
                        "gene_type": "content",
                        "section": "hero",
                        "content": {
                            "headline": "24/7 Emergency HVAC Service",
                            "subheadline": "Licensed, Insured"
                        }
                    }
                ],
                "section_order": ["hero", "trust_badges", "benefits", "cta", "footer"],
                "supported_claims": ["24_hour_service", "licensed", "insured"],
                "tracking_config": {
                    "utm_source": "google",
                    "utm_medium": "cpc",
                    "events": ["page_view", "cta_click", "phone_call"]
                },
                "click_to_call_config": {
                    "number": "+1-800-HVAC-NOW",
                    "tracking_enabled": True
                },
                "disclosures": ["license_001", "service_area"],
                "qa_status": "qa_passed",
                "status": "preview_ready",
                "primary_metric": "cost_per_qualified_call",
                "target_metric_value": 75.0
            }
        }
