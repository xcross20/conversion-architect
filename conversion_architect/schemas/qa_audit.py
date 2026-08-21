"""
QAAudit Schema
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class QASeverity(str, Enum):
    BLOCKING = "blocking"
    WARNING = "warning"
    INFO = "info"


class QACheckType(str, Enum):
    # Deterministic checks
    CTA_ACTION = "cta_action"
    TRACKING = "tracking"
    DISCLOSURES = "disclosures"
    SUPPORTED_CLAIMS = "supported_claims"
    PLACEHOLDERS = "placeholders"
    FAMILY_COHERENCE = "family_coherence"
    
    # Visual checks
    RESPONSIVE_RENDERING = "responsive_rendering"
    OVERFLOW = "overflow"
    CTA_VISIBILITY = "cta_visibility"
    STICKY_COLLISIONS = "sticky_collisions"
    CONTRAST_ACCESSIBILITY = "contrast_accessibility"
    
    # Deployment checks
    DEPLOYMENT_ISSUES = "deployment_issues"
    
    # Analytics checks
    ANALYTICS_MISSING = "analytics_missing"


class QACheckStatus(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    SKIP = "skip"
    WARN = "warn"


class QACheck(BaseModel):
    """QACheck represents a single quality assurance check."""
    
    check_id: str = Field(..., description="Unique check identifier")
    check_type: QACheckType = Field(..., description="Type of check")
    severity: QASeverity = Field(..., description="Severity level")
    
    # Result
    status: QACheckStatus = Field(..., description="Check result")
    message: str = Field(..., description="Human-readable message")
    details: dict[str, Any] = Field(default_factory=dict)
    
    # Evidence
    screenshot_url: str | None = Field(None, description="Screenshot if visual check")
    affected_elements: list[str] = Field(default_factory=list)
    affected_sections: list[str] = Field(default_factory=list)
    
    # Remediation
    recommendation: str | None = Field(None, description="How to fix")
    auto_fixable: bool = Field(default=False)
    
    # Metadata
    executed_at: datetime = Field(default_factory=datetime.utcnow)
    meta_data: dict[str, Any] = Field(default_factory=dict)


class QAAudit(BaseModel):
    """QAAudit contains the results of all quality checks for a genome.
    
    QA has veto authority — if any BLOCKING checks fail, the genome
    cannot proceed to preview or deployment.
    """
    
    # Identity
    audit_id: str = Field(..., description="Unique audit identifier")
    genome_id: str = Field(..., description="Genome being audited")
    
    # Overall result
    status: QACheckStatus = Field(..., description="Overall audit status")
    passed: bool = Field(..., description="True if all blocking checks passed")
    
    # Checks
    checks: list[QACheck] = Field(default_factory=list)
    
    # Summary
    blocking_failures: int = Field(default=0)
    warnings: int = Field(default=0)
    skipped: int = Field(default=0)
    
    # Veto authority
    vetoed: bool = Field(
        default=False,
        description="True if blocking failures prevent progression"
    )
    veto_reason: str | None = Field(None, description="Reason for veto")
    
    # Environment info
    viewport: str = Field(default="desktop")
    viewport_width: int = Field(default=1280)
    viewport_height: int = Field(default=800)
    
    # Timing
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = Field(None)
    duration_ms: int | None = Field(None)
    
    # QA agent
    executed_by: str = Field(default="qa_system")
    
    # Metadata
    meta_data: dict[str, Any] = Field(default_factory=dict)
    
    def get_blocking_failures(self) -> list[QACheck]:
        """Get all blocking check failures."""
        return [
            c for c in self.checks
            if c.severity == QASeverity.BLOCKING and c.status == QACheckStatus.FAIL
        ]
    
    def get_warnings(self) -> list[QACheck]:
        """Get all warning checks."""
        return [
            c for c in self.checks
            if c.status == QACheckStatus.WARN
        ]
    
    def can_proceed(self) -> bool:
        """Check if genome can proceed to next stage."""
        return not self.vetoed and self.passed
    
    class Config:
        json_schema_extra = {
            "example": {
                "audit_id": "qa_hvac_001",
                "genome_id": "genome_hvac_emergency_001",
                "status": "fail",
                "passed": False,
                "blocking_failures": 1,
                "warnings": 2,
                "vetoed": True,
                "veto_reason": "CTA button not rendering on mobile viewport",
                "checks": [
                    {
                        "check_id": "cta_action_001",
                        "check_type": "cta_action",
                        "severity": "blocking",
                        "status": "fail",
                        "message": "Primary CTA not clickable",
                        "recommendation": "Increase z-index of sticky bar"
                    }
                ]
            }
        }
