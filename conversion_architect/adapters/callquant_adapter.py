"""
CallQuant Adapter

Maps CallQuant entities to Conversion Architect concepts.
Thin adapter - does NOT duplicate WD prompts or design logic.
"""
from __future__ import annotations

import logging
from typing import Any

from conversion_architect.schemas import BusinessConversionContext, ConversionGoal

logger = logging.getLogger(__name__)


class CallQuantAdapter:
    """Adapter that transforms CallQuant entities into Conversion Architect context.
    
    Maps:
    - CampaignCell → design context
    - IntentCluster → vertical/perception goals
    - OfferVariant → offer structure
    - ClaimManifest → claims validation
    - Qualification/compliance → constraints
    - Click-to-call action → CTA spec
    - Experiment IDs → design experiment tracking
    - Economic outcomes → primary metric
    """
    
    def __init__(self):
        """Initialize CallQuant adapter."""
        self._conversion_goal_map = {
            "phone_call": ConversionGoal.PHONE_CALL,
            "form": ConversionGoal.LEAD_CAPTURE,
            "appointment": ConversionGoal.APPOINTMENT,
            "purchase": ConversionGoal.PURCHASE,
            "signup": ConversionGoal.SIGNUP,
        }
    
    def adapt_campaign_cell(
        self,
        campaign_cell: dict[str, Any]
    ) -> dict[str, Any]:
        """Extract design-relevant data from CampaignCell.
        
        Args:
            campaign_cell: CampaignCell data from CallQuant
            
        Returns:
            Adapted context dict
        """
        return {
            "campaign_cell_id": campaign_cell.get("id") or campaign_cell.get("campaign_cell_id"),
            "vertical": campaign_cell.get("vertical"),
            "sub_vertical": campaign_cell.get("sub_category"),
            "target_states": campaign_cell.get("target_states", []),
            "target_zip_codes": campaign_cell.get("target_zip_codes", []),
            "service_area": campaign_cell.get("service_area"),
        }
    
    def adapt_intent_cluster(
        self,
        intent_cluster: dict[str, Any]
    ) -> dict[str, Any]:
        """Extract design goals from IntentCluster.
        
        Args:
            intent_cluster: IntentCluster data from CallQuant
            
        Returns:
            Adapted context dict
        """
        keywords = intent_cluster.get("keywords", [])
        if isinstance(keywords, str):
            keywords = [k.strip() for k in keywords.split(",")]
        
        # Map intent perceptions
        intent_type = intent_cluster.get("intent_type", "")
        perceptions = []
        if "emergency" in intent_type.lower() or "urgent" in intent_type.lower():
            perceptions.extend(["urgency", "speed"])
        if "compare" in intent_type.lower() or "research" in intent_type.lower():
            perceptions.extend(["trust", "value"])
        
        return {
            "intent_cluster_id": intent_cluster.get("id") or intent_cluster.get("intent_cluster_id"),
            "intent_keywords": keywords[:20],  # Limit keywords
            "intent_perceptions": perceptions,
            "conversion_goal": intent_cluster.get("primary_action", "phone_call"),
        }
    
    def adapt_offer_variant(
        self,
        offer_variant: dict[str, Any]
    ) -> dict[str, Any]:
        """Extract offer structure from OfferVariant.
        
        Args:
            offer_variant: OfferVariant data from CallQuant
            
        Returns:
            Adapted context dict
        """
        return {
            "offer_variant_id": offer_variant.get("id") or offer_variant.get("offer_variant_id"),
            "offer": {
                "type": offer_variant.get("offer_type"),
                "price": offer_variant.get("price"),
                "headline": offer_variant.get("headline"),
                "value_prop": offer_variant.get("value_proposition"),
                "guarantee": offer_variant.get("guarantee"),
            },
            "offer_headline": offer_variant.get("headline"),
            "offer_value_prop": offer_variant.get("value_proposition"),
            "offer_urgency": offer_variant.get("urgency_level", "medium"),
        }
    
    def adapt_claim_manifest(
        self,
        claim_manifest: dict[str, Any]
    ) -> dict[str, Any]:
        """Extract validated claims from ClaimManifest.
        
        Args:
            claim_manifest: ClaimManifest data from CallQuant
            
        Returns:
            Adapted context dict
        """
        claims = claim_manifest.get("claims", [])
        
        supported = []
        unsupported = []
        for claim in claims:
            status = claim.get("status", "supported")
            claim_data = {
                "claim": claim.get("claim"),
                "type": claim.get("type"),
            }
            if status == "supported":
                supported.append(claim_data)
            else:
                unsupported.append(claim_data)
        
        return {
            "claim_manifest_id": claim_manifest.get("id") or claim_manifest.get("manifest_id"),
            "supported_claims": supported,
            "unsupported_claims": unsupported,
            "compliance_constraints": claim_manifest.get("compliance_constraints", []),
        }
    
    def adapt_qualification(
        self,
        qualification: dict[str, Any] | None
    ) -> dict[str, Any]:
        """Extract qualification constraints.
        
        Args:
            qualification: Qualification data from CallQuant
            
        Returns:
            Adapted context dict
        """
        if not qualification:
            return {}
        
        return {
            "min_call_duration": qualification.get("min_duration_seconds"),
            "required_states": qualification.get("target_states"),
            "excluded_zip_codes": qualification.get("excluded_zip_codes"),
        }
    
    def adapt_click_to_call(
        self,
        click_to_call_config: dict[str, Any] | None
    ) -> dict[str, Any]:
        """Extract click-to-call configuration.
        
        Args:
            click_to_call_config: Click-to-call config from CallQuant
            
        Returns:
            Adapted context dict
        """
        if not click_to_call_config:
            return {}
        
        return {
            "click_to_call_number": click_to_call_config.get("phone_number"),
            "tracking_enabled": click_to_call_config.get("enable_tracking", True),
            "call_routing": click_to_call_config.get("routing_type", "round_robin"),
        }
    
    def adapt_experiment(
        self,
        experiment: dict[str, Any] | None
    ) -> dict[str, Any]:
        """Extract design experiment tracking.
        
        Args:
            experiment: Experiment data from CallQuant
            
        Returns:
            Adapted context dict
        """
        if not experiment:
            return {}
        
        return {
            "experiment_id": experiment.get("id") or experiment.get("experiment_id"),
            "experiment_type": experiment.get("type"),
            "variants": experiment.get("variants", []),
        }
    
    def adapt_economic_outcome(
        self,
        economic: dict[str, Any]
    ) -> dict[str, Any]:
        """Extract economic metrics from CallQuant.
        
        Args:
            economic: Economic outcome data from CallQuant
            
        Returns:
            Adapted context dict with primary metric
        """
        # Primary metric from CallQuant economics
        primary_metric = economic.get("primary_metric", "cost_per_qualified_call")
        
        # Map to Conversion Architect naming
        metric_map = {
            "cost_per_call": "cost_per_call",
            "cost_per_qualified_call": "cost_per_qualified_call",
            "conversion_rate": "conversion_rate",
            "cpa": "cost_per_acquisition",
            "cpl": "cost_per_lead",
        }
        
        return {
            "primary_metric": metric_map.get(primary_metric, primary_metric),
            "target_metric_value": economic.get("target_value"),
            "current_metric_value": economic.get("current_value"),
            "budget_limit": economic.get("budget_limit"),
        }
    
    def build_context(
        self,
        campaign_cell: dict[str, Any],
        intent_cluster: dict[str, Any],
        offer_variant: dict[str, Any],
        claim_manifest: dict[str, Any],
        qualification: dict[str, Any] | None = None,
        click_to_call_config: dict[str, Any] | None = None,
        experiment: dict[str, Any] | None = None,
        economic: dict[str, Any] | None = None,
    ) -> BusinessConversionContext:
        """Build complete BusinessConversionContext from CallQuant entities.
        
        Args:
            campaign_cell: CampaignCell data
            intent_cluster: IntentCluster data
            offer_variant: OfferVariant data
            claim_manifest: ClaimManifest data
            qualification: Optional qualification constraints
            click_to_call_config: Optional click-to-call config
            experiment: Optional experiment data
            economic: Optional economic outcomes
            
        Returns:
            BusinessConversionContext ready for genome compilation
        """
        from conversion_architect.schemas import BusinessConversionContext as BCC
        
        # Combine all adapted data
        context_data = {}
        
        # Campaign cell
        context_data.update(self.adapt_campaign_cell(campaign_cell))
        
        # Intent cluster
        context_data.update(self.adapt_intent_cluster(intent_cluster))
        
        # Offer variant
        context_data.update(self.adapt_offer_variant(offer_variant))
        
        # Claims
        context_data.update(self.adapt_claim_manifest(claim_manifest))
        
        # Qualification
        if qualification:
            context_data.update(self.adapt_qualification(qualification))
        
        # Click-to-call
        ctc_data = self.adapt_click_to_call(click_to_call_config)
        if ctc_data:
            context_data.update(ctc_data)
        
        # Experiment
        exp_data = self.adapt_experiment(experiment)
        if exp_data:
            context_data.update(exp_data)
        
        # Economics
        if economic:
            context_data.update(self.adapt_economic_outcome(economic))
        
        # Map conversion goal
        conversion_goal_str = context_data.get("conversion_goal", "phone_call")
        conversion_goal = self._conversion_goal_map.get(
            conversion_goal_str,
            ConversionGoal.PHONE_CALL
        )
        context_data["conversion_goal"] = conversion_goal
        
        # Trust signals from campaign
        context_data["available_trust_signals"] = campaign_cell.get(
            "trust_signals",
            ["license_badge", "insurance_badge", "review_stars"]
        )
        
        # Generate context_id if not present
        if "context_id" not in context_data:
            context_data["context_id"] = f"ctx_{context_data.get('campaign_cell_id', 'unknown')}"
        
        return BCC(**context_data)


def create_callquant_adapter() -> CallQuantAdapter:
    """Create CallQuant adapter instance."""
    return CallQuantAdapter()
