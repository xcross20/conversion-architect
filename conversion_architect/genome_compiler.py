"""
Genome Compiler

Compiles BusinessConversionContext + ClaimManifest → LanderGenome
"""
from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any

from conversion_architect.schemas import (
    LanderGenome,
    GenomeStatus,
    BusinessConversionContext,
    GenomeGene,
    DesignFamily,
    VerticalSkin,
)

logger = logging.getLogger(__name__)


class GenomeCompilerError(Exception):
    """Error during genome compilation."""
    pass


class GenomeCompiler:
    """Compiles a complete LanderGenome from business context.
    
    The compiler orchestrates:
    1. Load family signature and vertical skin
    2. Map claims to genome content
    3. Apply design patterns to genes
    4. Configure tracking and CTAs
    5. Validate against family coherence
    """
    
    def __init__(
        self,
        family: DesignFamily,
        skin: VerticalSkin | None = None
    ):
        """Initialize compiler.
        
        Args:
            family: Design family to use
            skin: Optional vertical skin override
        """
        self.family = family
        self.skin = skin
    
    async def compile(
        self,
        context: BusinessConversionContext,
        pattern_gene_map: dict[str, dict[str, Any]] | None = None
    ) -> LanderGenome:
        """Compile genome from business context.
        
        Args:
            context: Business conversion context
            pattern_gene_map: Optional mapping of pattern IDs to gene configs
            
        Returns:
            Compiled LanderGenome
        """
        genome_id = f"genome_{uuid.uuid4().hex[:12]}"
        
        # Build genes from context (including GA4 data)
        genes = self._build_genes(context, pattern_gene_map or {})
        
        # Determine section order
        section_order = self._determine_section_order(context)
        
        # Extract supported claims
        supported_claims = [
            c.get("claim", str(c)) for c in context.supported_claims
        ]
        unsupported_claims = [
            c.get("claim", str(c)) for c in context.unsupported_claims
        ]
        
        # Build tracking config (including GA4)
        tracking_config = self._build_tracking_config(context)
        
        # Build click-to-call config
        click_to_call_config = self._build_click_to_call_config(context)
        
        # Build disclosures
        disclosures = self._build_disclosures(context)
        
        genome = LanderGenome(
            genome_id=genome_id,
            name=f"{context.offer_headline} - Landing Page",
            family_id=self.family.family_id,
            skin_id=self.skin.skin_id if self.skin else None,
            
            # Source mapping
            campaign_cell_id=context.campaign_cell_id,
            intent_cluster_id=context.intent_cluster_id,
            offer_variant_id=context.offer.get("id") if isinstance(context.offer, dict) else None,
            claim_manifest_id=context.claim_manifest_id,
            
            # Content
            genes=genes,
            section_order=section_order,
            
            # Claims
            supported_claims=supported_claims,
            unsupported_claims=unsupported_claims,
            claim_source=context.claim_manifest_id,
            
            # Tracking
            tracking_config=tracking_config,
            click_to_call_config=click_to_call_config,
            
            # Compliance
            disclosures=disclosures,
            compliance_status="pending",
            
            # Status
            status=GenomeStatus.COMPILED,
            primary_metric=context.primary_metric,
            target_metric_value=context.target_metric_value,
            
            created_by="genome_compiler"
        )
        
        logger.info(f"Compiled genome {genome_id} for cell {context.campaign_cell_id}")
        return genome
    
    def _build_genes(
        self,
        context: BusinessConversionContext,
        pattern_gene_map: dict[str, dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Build genome genes from context."""
        genes = []
        
        # Hero gene with GA4 keyword insights
        hero_gene = {
            "gene_id": f"hero_{uuid.uuid4().hex[:6]}",
            "gene_type": "content",
            "section": "hero",
            "name": "Hero Headline & Subheadline",
            "configuration": {
                "pattern": pattern_gene_map.get("hero", {}).get("pattern", "command_verb"),
                "keywords": context.top_converting_keywords[:3] if context.top_converting_keywords else [],
                "ga4_optimized": bool(context.ga4_report_id),
            },
            "content": {
                "headline": context.offer_headline,
                "subheadline": context.offer_value_prop
            }
        }
        genes.append(hero_gene)
        
        # CTA gene with GA4 targets
        cta_config = {
            "action_type": context.conversion_goal.value if hasattr(context.conversion_goal, 'value') else str(context.conversion_goal),
            "target_click_rate": context.target_cta_click_rate,
        }
        
        # Add mobile optimization flag if needed
        if context.mobile_friendly_score < 0.8:
            cta_config["mobile_optimized"] = True
            cta_config["large_touch_target"] = True
        
        cta_gene = {
            "gene_id": f"cta_{uuid.uuid4().hex[:6]}",
            "gene_type": "cta",
            "section": "cta",
            "name": "Primary CTA",
            "configuration": cta_config,
            "content": {
                "cta_text": self._get_cta_text(context),
                "phone_number": context.click_to_call_number
            }
        }
        genes.append(cta_gene)
        
        # Trust badges gene
        if context.available_trust_signals:
            trust_gene = {
                "gene_id": f"trust_{uuid.uuid4().hex[:6]}",
                "gene_type": "proof",
                "section": "trust_badges",
                "name": "Trust Signals",
                "content": {
                    "badges": context.available_trust_signals
                }
            }
            genes.append(trust_gene)
        
        # Geo-focused gene if GA4 shows best state
        if context.best_performing_state and context.ga4_report_id:
            geo_gene = {
                "gene_id": f"geo_{uuid.uuid4().hex[:6]}",
                "gene_type": "content",
                "section": "geo_targeting",
                "name": "Geo-Focused Content",
                "configuration": {
                    "primary_state": context.best_performing_state,
                    "geo_optimized": True,
                },
                "content": {
                    "geo_highlight": f"Serving {context.best_performing_state} customers"
                }
            }
            genes.append(geo_gene)
        
        # Urgency gene if trend is improving
        if context.conversion_trend == "improving":
            urgency_gene = {
                "gene_id": f"urgency_{uuid.uuid4().hex[:6]}",
                "gene_type": "content",
                "section": "urgency",
                "name": "Social Proof / Urgency",
                "configuration": {
                    "show_trend": True,
                    "trend_pct": context.conversion_trend_pct,
                },
                "content": {
                    "urgency_message": f"Growing demand - book now to secure your spot"
                }
            }
            genes.append(urgency_gene)
        
        return genes
    
    def _determine_section_order(self, context: BusinessConversionContext) -> list[str]:
        """Determine page section order based on conversion goal."""
        base_order = ["hero", "trust_badges", "benefits", "cta", "footer"]
        
        # Add sections based on context
        if context.conversion_goal.value == "phone_call":  # type: ignore
            # Click-to-call: emphasize urgency and trust
            return ["hero", "trust_badges", "offer_details", "cta", "footer"]
        
        return base_order
    
    def _build_tracking_config(
        self,
        context: BusinessConversionContext
    ) -> dict[str, Any]:
        """Build tracking configuration."""
        config = {
            "utm_source": "callquant",
            "utm_medium": "cpc",
            "campaign_id": context.campaign_cell_id,
            "events": ["page_view", "cta_click", "phone_call"]
        }
        
        if context.experiment_id:
            config["experiment_id"] = context.experiment_id
        
        # GA4 integration
        if context.ga4_property_id:
            config["ga4"] = {
                "property_id": context.ga4_property_id,
                "report_id": context.ga4_report_id,
                "conversion_tracking": {
                    "target_cvr": context.target_cvr,
                    "target_bounce_rate": context.target_bounce_rate,
                },
                "events": [
                    "page_view",
                    "engagement",
                    "cta_click",
                    "phone_call",
                    "form_submit"
                ]
            }
        
        return config
    
    def _build_click_to_call_config(
        self,
        context: BusinessConversionContext
    ) -> dict[str, Any] | None:
        """Build click-to-call configuration."""
        if context.conversion_goal.value != "phone_call":  # type: ignore
            return None
        
        return {
            "number": context.click_to_call_number,
            "tracking_enabled": True,
            "call_routing": "round_robin"  # Default
        }
    
    def _build_disclosures(self, context: BusinessConversionContext) -> list[str]:
        """Build required disclosures."""
        disclosures = []
        
        # Add compliance constraints
        disclosures.extend(context.compliance_constraints)
        
        # Add skin-required disclosures if available
        if self.skin:
            disclosures.extend(self.skin.required_disclosures)
        
        return list(set(disclosures))  # Dedupe
    
    def _get_cta_text(self, context: BusinessConversionContext) -> str:
        """Get appropriate CTA text based on context."""
        if context.conversion_goal.value == "phone_call":  # type: ignore
            return "Call Now"
        elif context.conversion_goal.value == "lead_capture":  # type: ignore
            return "Get Your Free Quote"
        elif context.conversion_goal.value == "appointment":  # type: ignore
            return "Book Appointment"
        
        return "Get Started"


async def compile_genome(
    context: BusinessConversionContext,
    family: DesignFamily,
    skin: VerticalSkin | None = None
) -> LanderGenome:
    """Compile a genome from business context.
    
    Convenience function.
    """
    compiler = GenomeCompiler(family=family, skin=skin)
    return await compiler.compile(context)
