"""
DesignExperiment Schema
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ExperimentStatus(str, Enum):
    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class ExperimentVariant(str, Enum):
    CONTROL = "control"
    TREATMENT = "treatment"
    VARIANT_A = "variant_a"
    VARIANT_B = "variant_b"


class MemoryLevel(str, Enum):
    GLOBAL = "global"
    VERTICAL = "vertical"
    CELL = "cell"


class DesignExperiment(BaseModel):
    """DesignExperiment manages A/B testing of landing page genomes.
    
    Design experiments test specific genome variables against each other.
    Default: one dominant variable per experiment.
    
    Memory levels:
    - GLOBAL: Valid across all verticals/cells
    - VERTICAL: Valid for a specific vertical
    - CELL: Valid for a specific campaign cell
    
    RULE: CELL promotion directly to GLOBAL is PROHIBITED.
    """
    
    # Identity
    experiment_id: str = Field(..., description="Unique experiment identifier")
    name: str = Field(..., description="Human-readable experiment name")
    
    # Context
    campaign_cell_id: str | None = Field(None, description="Associated campaign cell")
    vertical: str | None = Field(None, description="Target vertical")
    
    # Variables (one dominant variable default)
    primary_variable: str = Field(..., description="Primary genome variable being tested")
    secondary_variables: list[str] = Field(
        default_factory=list,
        description="Secondary variables (limited)"
    )
    
    # Variants
    control_genome_id: str = Field(..., description="Control genome ID")
    treatment_genome_id: str = Field(..., description="Treatment genome ID")
    traffic_split: dict[str, float] = Field(
        default=lambda: {"control": 50.0, "treatment": 50.0},
        description="Traffic percentage per variant"
    )
    
    # Status
    status: ExperimentStatus = Field(default=ExperimentStatus.DRAFT)
    
    # Results
    control_metrics: dict[str, Any] = Field(default_factory=dict)
    treatment_metrics: dict[str, Any] = Field(default_factory=dict)
    winner: ExperimentVariant | None = Field(None)
    confidence: float | None = Field(None)
    sample_size_reached: int = Field(default=0)
    sample_size_target: int = Field(default=1000)
    
    # Memory level
    memory_level: MemoryLevel = Field(default=MemoryLevel.CELL)
    promotion_candidates: list[MemoryLevel] = Field(
        default_factory=list,
        description="Levels this experiment can promote to"
    )
    promotion_blocked: bool = Field(
        default=False,
        description="True if promotion to GLOBAL is blocked"
    )
    promotion_blocked_reason: str | None = Field(
        None,
        description="Why promotion is blocked"
    )
    
    # Timing
    started_at: datetime | None = Field(None)
    completed_at: datetime | None = Field(None)
    duration_days: int | None = Field(None)
    
    # Primary metric
    primary_metric: str = Field(
        default="conversion_rate",
        description="Primary metric (from BusinessContext)"
    )
    target_improvement: float = Field(
        default=0.10,
        description="Target improvement percentage"
    )
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    meta_data: dict[str, Any] = Field(default_factory=dict)
    
    def can_promote_to(self, level: MemoryLevel) -> bool:
        """Check if experiment can promote to given memory level."""
        if level not in self.promotion_candidates:
            return False
        
        # CELL -> GLOBAL is always prohibited
        if self.memory_level == MemoryLevel.CELL and level == MemoryLevel.GLOBAL:
            return False
        
        # Must have winner with sufficient confidence
        if not self.winner or not self.confidence:
            return False
        
        if self.confidence < 0.95:
            return False
        
        return True
    
    def get_promotion_path(self) -> list[MemoryLevel]:
        """Get valid promotion path from current level."""
        if self.memory_level == MemoryLevel.CELL:
            return [MemoryLevel.VERTICAL]
        elif self.memory_level == MemoryLevel.VERTICAL:
            return [MemoryLevel.GLOBAL]
        return []
    
    class Config:
        json_schema_extra = {
            "example": {
                "experiment_id": "exp_hvac_cta_color",
                "name": "HVAC CTA Color Test",
                "campaign_cell_id": "cell_hvac_emergency",
                "vertical": "home_services",
                "primary_variable": "cta_color",
                "control_genome_id": "genome_hvac_red_cta",
                "treatment_genome_id": "genome_hvac_blue_cta",
                "traffic_split": {"control": 50.0, "treatment": 50.0},
                "status": "running",
                "memory_level": "cell",
                "promotion_candidates": ["vertical"],
                "promotion_blocked": False,
                "primary_metric": "cost_per_qualified_call",
                "target_improvement": 0.15
            }
        }
