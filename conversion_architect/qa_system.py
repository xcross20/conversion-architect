"""
QA Audit System

Quality assurance for landing page genomes.
QA has veto authority - blocking failures prevent progression.
"""
from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any

from conversion_architect.schemas import (
    QAAudit,
    QACheck,
    QACheckType,
    QACheckStatus,
    QASeverity,
    LanderGenome,
    GenomeStatus,
)

logger = logging.getLogger(__name__)


class QAExecutor:
    """Executes quality assurance checks on genomes.
    
    QA has VETO AUTHORITY - if any BLOCKING checks fail,
    the genome cannot proceed to preview or deployment.
    """
    
    def __init__(self):
        """Initialize QA executor."""
        self._check_registry: dict[QACheckType, Any] = {}
        self._register_default_checks()
    
    def _register_default_checks(self):
        """Register default QA checks."""
        self._check_registry[QACheckType.CTA_ACTION] = self._check_cta_action
        self._check_registry[QACheckType.TRACKING] = self._check_tracking
        self._check_registry[QACheckType.DISCLOSURES] = self._check_disclosures
        self._check_registry[QACheckType.SUPPORTED_CLAIMS] = self._check_supported_claims
        self._check_registry[QACheckType.PLACEHOLDERS] = self._check_placeholders
        self._check_registry[QACheckType.FAMILY_COHERENCE] = self._check_family_coherence
    
    async def execute(self, genome: LanderGenome) -> QAAudit:
        """Execute all QA checks on a genome.
        
        Args:
            genome: LanderGenome to audit
            
        Returns:
            QAAudit with all check results
        """
        audit_id = f"qa_{uuid.uuid4().hex[:12]}"
        started_at = datetime.utcnow()
        
        checks: list[QACheck] = []
        blocking_failures = 0
        warnings = 0
        skipped = 0
        
        for check_type, check_func in self._check_registry.items():
            check = await check_func(genome)
            checks.append(check)
            
            if check.status == QACheckStatus.FAIL and check.severity == QASeverity.BLOCKING:
                blocking_failures += 1
            elif check.status == QACheckStatus.WARN:
                warnings += 1
            elif check.status == QACheckStatus.SKIP:
                skipped += 1
        
        completed_at = datetime.utcnow()
        duration_ms = int((completed_at - started_at).total_seconds() * 1000)
        
        vetoed = blocking_failures > 0
        veto_reason = None
        if vetoed:
            blocking_checks = [c for c in checks if c.severity == QASeverity.BLOCKING and c.status == QACheckStatus.FAIL]
            veto_reason = f"{blocking_failures} blocking check(s) failed: {', '.join(c.message for c in blocking_checks[:3])}"
        
        audit = QAAudit(
            audit_id=audit_id,
            genome_id=genome.genome_id,
            status=QACheckStatus.FAIL if vetoed else QACheckStatus.PASS,
            passed=not vetoed,
            checks=checks,
            blocking_failures=blocking_failures,
            warnings=warnings,
            skipped=skipped,
            vetoed=vetoed,
            veto_reason=veto_reason,
            started_at=started_at,
            completed_at=completed_at,
            duration_ms=duration_ms,
            executed_by="qa_system"
        )
        
        logger.info(f"QA audit {audit_id}: {'PASS' if audit.passed else 'FAIL'} "
                    f"(blocking={blocking_failures}, warnings={warnings})")
        
        return audit
    
    async def _check_cta_action(self, genome: LanderGenome) -> QACheck:
        """Check CTA action configuration."""
        check_id = f"cta_action_{uuid.uuid4().hex[:6]}"
        
        # Find CTA genes
        cta_genes = [g for g in genome.genes if g.get("gene_type") == "cta"]
        
        if not cta_genes:
            return QACheck(
                check_id=check_id,
                check_type=QACheckType.CTA_ACTION,
                severity=QASeverity.BLOCKING,
                status=QACheckStatus.FAIL,
                message="No CTA gene found in genome",
                recommendation="Add at least one CTA gene with action_type and cta_text"
            )
        
        # Check CTA has required fields
        for cta in cta_genes:
            content = cta.get("content", {})
            if not content.get("cta_text"):
                return QACheck(
                    check_id=check_id,
                    check_type=QACheckType.CTA_ACTION,
                    severity=QASeverity.BLOCKING,
                    status=QACheckStatus.FAIL,
                    message="CTA missing cta_text",
                    affected_elements=[cta.get("gene_id", "unknown")]
                )
        
        return QACheck(
            check_id=check_id,
            check_type=QACheckType.CTA_ACTION,
            severity=QASeverity.BLOCKING,
            status=QACheckStatus.PASS,
            message=f"Found {len(cta_genes)} CTA gene(s) with required fields"
        )
    
    async def _check_tracking(self, genome: LanderGenome) -> QACheck:
        """Check tracking configuration."""
        check_id = f"tracking_{uuid.uuid4().hex[:6]}"
        
        tracking = genome.tracking_config or {}
        
        required_fields = ["events"]
        missing = [f for f in required_fields if f not in tracking]
        
        if missing:
            return QACheck(
                check_id=check_id,
                check_type=QACheckType.TRACKING,
                severity=QASeverity.BLOCKING,
                status=QACheckStatus.FAIL,
                message=f"Tracking missing required fields: {', '.join(missing)}",
                recommendation="Add events list to tracking_config"
            )
        
        return QACheck(
            check_id=check_id,
            check_type=QACheckType.TRACKING,
            severity=QASeverity.BLOCKING,
            status=QACheckStatus.PASS,
            message="Tracking configured with required fields"
        )
    
    async def _check_disclosures(self, genome: LanderGenome) -> QACheck:
        """Check required disclosures."""
        check_id = f"disclosures_{uuid.uuid4().hex[:6]}"
        
        disclosures = genome.disclosures or []
        
        # This is a warning, not blocking - disclosures may be optional
        if not disclosures:
            return QACheck(
                check_id=check_id,
                check_type=QACheckType.DISCLOSURES,
                severity=QASeverity.WARNING,
                status=QACheckStatus.WARN,
                message="No disclosures configured",
                recommendation="Add required legal disclosures for the vertical"
            )
        
        return QACheck(
            check_id=check_id,
            check_type=QACheckType.DISCLOSURES,
            severity=QASeverity.WARNING,
            status=QACheckStatus.PASS,
            message=f"Found {len(disclosures)} configured disclosure(s)"
        )
    
    async def _check_supported_claims(self, genome: LanderGenome) -> QACheck:
        """Check that supported claims match genome content."""
        check_id = f"claims_{uuid.uuid4().hex[:6]}"
        
        supported = genome.supported_claims or []
        
        # Verify claims are substantiated in genes
        substantiated = []
        for claim in supported:
            for gene in genome.genes:
                gene_content = str(gene.get("content", {}))
                if claim.lower() in gene_content.lower():
                    substantiated.append(claim)
                    break
        
        unsubstantiated = [c for c in supported if c not in substantiated]
        
        if unsubstantiated:
            return QACheck(
                check_id=check_id,
                check_type=QACheckType.SUPPORTED_CLAIMS,
                severity=QASeverity.BLOCKING,
                status=QACheckStatus.FAIL,
                message=f"Claim(s) not substantiated in content: {', '.join(unsubstantiated)}",
                recommendation="Add content that supports each claimed benefit"
            )
        
        return QACheck(
            check_id=check_id,
            check_type=QACheckType.SUPPORTED_CLAIMS,
            severity=QASeverity.BLOCKING,
            status=QACheckStatus.PASS,
            message=f"All {len(supported)} supported claims are substantiated"
        )
    
    async def _check_placeholders(self, genome: LanderGenome) -> QACheck:
        """Check for unfilled placeholders."""
        check_id = f"placeholders_{uuid.uuid4().hex[:6]}"
        
        placeholders_found = []
        placeholder_patterns = ["{{", "}}", "[PLACEHOLDER]", "TODO", "FIXME"]
        
        for gene in genome.genes:
            content_str = str(gene.get("content", {}))
            for pattern in placeholder_patterns:
                if pattern in content_str:
                    placeholders_found.append({
                        "gene_id": gene.get("gene_id"),
                        "pattern": pattern
                    })
        
        if placeholders_found:
            return QACheck(
                check_id=check_id,
                check_type=QACheckType.PLACEHOLDERS,
                severity=QASeverity.WARNING,
                status=QACheckStatus.WARN,
                message=f"Found {len(placeholders_found)} unfilled placeholder(s)",
                affected_elements=[p["gene_id"] for p in placeholders_found],
                recommendation="Replace all placeholders with actual content"
            )
        
        return QACheck(
            check_id=check_id,
            check_type=QACheckType.PLACEHOLDERS,
            severity=QASeverity.WARNING,
            status=QACheckStatus.PASS,
            message="No unfilled placeholders found"
        )
    
    async def _check_family_coherence(self, genome: LanderGenome) -> QACheck:
        """Check family coherence."""
        check_id = f"family_{uuid.uuid4().hex[:6]}"
        
        # Check genome references valid family
        if not genome.family_id:
            return QACheck(
                check_id=check_id,
                check_type=QACheckType.FAMILY_COHERENCE,
                severity=QASeverity.BLOCKING,
                status=QACheckStatus.FAIL,
                message="Genome missing family_id",
                recommendation="Assign a valid family_id to the genome"
            )
        
        # Check section order is defined
        if not genome.section_order:
            return QACheck(
                check_id=check_id,
                check_type=QACheckType.FAMILY_COHERENCE,
                severity=QASeverity.BLOCKING,
                status=QACheckStatus.FAIL,
                message="Genome missing section_order",
                recommendation="Define section_order with at least hero and cta"
            )
        
        # Check required sections
        required_sections = ["hero", "cta"]
        missing_sections = [s for s in required_sections if s not in genome.section_order]
        
        if missing_sections:
            return QACheck(
                check_id=check_id,
                check_type=QACheckType.FAMILY_COHERENCE,
                severity=QASeverity.BLOCKING,
                status=QACheckStatus.FAIL,
                message=f"Missing required sections: {', '.join(missing_sections)}",
                recommendation=f"Add {', '.join(missing_sections)} to section_order"
            )
        
        return QACheck(
            check_id=check_id,
            check_type=QACheckType.FAMILY_COHERENCE,
            severity=QASeverity.BLOCKING,
            status=QACheckStatus.PASS,
            message="Genome passes family coherence checks"
        )


async def run_qa(genome: LanderGenome) -> QAAudit:
    """Run QA on a genome.
    
    Convenience function.
    """
    executor = QAExecutor()
    return await executor.execute(genome)
