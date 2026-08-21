"""
GenomeGene Schema
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class GeneType(str, Enum):
    STRUCTURE = "structure"
    CONTENT = "content"
    STYLE = "style"
    BEHAVIOR = "behavior"
    TRACKING = "tracking"
    CTA = "cta"
    PROOF = "proof"
    COMPLIANCE = "compliance"


class GeneStatus(str, Enum):
    DRAFT = "draft"
    VALIDATED = "validated"
    REJECTED = "rejected"
    ARCHIVED = "archived"


class GenomeGene(BaseModel):
    """GenomeGene represents a single component of a LanderGenome.
    
    Genes are the atomic units of genome composition. Each gene
    controls a specific aspect of the landing page.
    """
    
    # Identity
    gene_id: str = Field(..., description="Unique gene identifier")
    genome_id: str | None = Field(None, description="Parent genome ID")
    gene_type: GeneType = Field(..., description="Type of gene")
    
    # Content
    name: str = Field(..., description="Human-readable gene name")
    section: str = Field(..., description="Page section this gene affects")
    pattern_id: str | None = Field(None, description="Source pattern ID")
    
    # Configuration
    configuration: dict[str, Any] = Field(
        default_factory=dict,
        description="Gene-specific configuration (structure, content, style)"
    )
    content: dict[str, Any] = Field(
        default_factory=dict,
        description="Actual content to render"
    )
    
    # Constraints
    status: GeneStatus = Field(default=GeneStatus.DRAFT)
    validation_errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    
    # Relationships
    slot: str | None = Field(None, description="Content slot this fills")
    dependencies: list[str] = Field(
        default_factory=list,
        description="Gene IDs this gene depends on"
    )
    conflicts: list[str] = Field(
        default_factory=list,
        description="Gene IDs this gene conflicts with"
    )
    
    # Override control
    can_override: list[str] = Field(
        default_factory=list,
        description="What this gene can override (family/skin)"
    )
    is_locked: bool = Field(
        default=False,
        description="If true, cannot be overridden by family/skin"
    )
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    meta_data: dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "gene_id": "hero_headline_g1",
                "genome_id": "genome_hvac_001",
                "gene_type": "content",
                "name": "Hero Headline",
                "section": "hero",
                "pattern_id": "hero_urgency_v1",
                "configuration": {
                    "pattern": "command_verb",
                    "urgency_level": "high"
                },
                "content": {
                    "headline": "24/7 Emergency HVAC Service — Arrives in 45 Minutes",
                    "subheadline": "Licensed, Insured & Serving Your Area"
                },
                "status": "validated",
                "slot": "main_headline",
                "dependencies": [],
                "can_override": ["skin.urgency_tokens"]
            }
        }
