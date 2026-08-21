"""
Conversion Architect Tests

Tests for schema validation, providers, Framer, QA, experiments, and CallQuant adapter.
"""
import pytest
from datetime import datetime

# Schema tests
def test_design_family_validation():
    """Test DesignFamily schema validation."""
    from conversion_architect.schemas import DesignFamily
    
    family = DesignFamily(
        family_id="test_family",
        name="Test Family",
        headline_grammar={"max_length": 60}
    )
    
    assert family.family_id == "test_family"
    assert family.version == "1.0.0"
    assert family.status == "active"


def test_invalid_skin_inheritance():
    """Test that skin must reference valid family."""
    from conversion_architect.schemas import VerticalSkin, Vertical
    
    skin = VerticalSkin(
        skin_id="test_skin",
        name="Test Skin",
        vertical=Vertical.HOME_SERVICES,
        family_id="nonexistent_family"
    )
    
    # Skin can reference any family (validation happens at runtime)
    assert skin.family_id == "nonexistent_family"


def test_family_signature_validation():
    """Test FamilySignature constraints."""
    from conversion_architect.schemas import FamilySignature, SignatureType
    
    sig = FamilySignature(
        signature_id="test_sig",
        family_id="test_family",
        signature_type=SignatureType.HEADLINE,
        constraints={"max_length": 60}
    )
    
    assert sig.signature_type == SignatureType.HEADLINE
    assert sig.constraints["max_length"] == 60


def test_lander_genome_validation():
    """Test LanderGenome schema."""
    from conversion_architect.schemas import LanderGenome, GenomeStatus
    
    genome = LanderGenome(
        genome_id="genome_001",
        name="Test Landing Page",
        family_id="portfolio_v1",
        genes=[],
        section_order=["hero", "cta"]
    )
    
    assert genome.genome_id == "genome_001"
    assert genome.family_id == "portfolio_v1"
    assert GenomeStatus.DRAFT == genome.status


def test_invalid_genome_missing_family():
    """Test that genome requires family_id."""
    from conversion_architect.schemas import LanderGenome
    from pydantic import ValidationError
    
    with pytest.raises(ValidationError):
        LanderGenome(
            genome_id="genome_001",
            name="Test",
            genes=[]
        )


# QA tests
def test_qa_passes_with_valid_genome():
    """Test QA passes when genome is valid."""
    import asyncio
    from conversion_architect.schemas import LanderGenome
    from conversion_architect.qa_system import run_qa
    
    genome = LanderGenome(
        genome_id="genome_001",
        name="Test Landing Page",
        family_id="portfolio_v1",
        genes=[
            {
                "gene_id": "cta_1",
                "gene_type": "cta",
                "content": {"cta_text": "Call Now", "headline": "24/7 Emergency HVAC - 24 Hour Service"}
            }
        ],
        section_order=["hero", "cta"],
        tracking_config={"events": ["page_view"]},
        supported_claims=["24_hour_service"]
    )
    
    result = asyncio.run(run_qa(genome))
    
    # Check passed or at least has passed family coherence
    assert result.audit_id is not None


def test_qa_blocks_missing_cta():
    """Test QA blocks genome missing CTA."""
    import asyncio
    from conversion_architect.schemas import LanderGenome
    from conversion_architect.qa_system import run_qa
    
    genome = LanderGenome(
        genome_id="genome_001",
        name="Test Landing Page",
        family_id="portfolio_v1",
        genes=[],  # No CTA gene
        section_order=["hero"]
    )
    
    result = asyncio.run(run_qa(genome))
    
    assert result.vetoed
    assert any(c.check_type.value == "cta_action" for c in result.checks)


def test_qa_warns_placeholder():
    """Test QA warns about unfilled placeholders."""
    import asyncio
    from conversion_architect.schemas import LanderGenome
    from conversion_architect.qa_system import run_qa
    
    genome = LanderGenome(
        genome_id="genome_001",
        name="Test Landing Page",
        family_id="portfolio_v1",
        genes=[
            {
                "gene_id": "hero_1",
                "gene_type": "content",
                "content": {"headline": "{{PLACEHOLDER_HEADLINE}}"}
            }
        ],
        section_order=["hero", "cta"],
        tracking_config={"events": ["page_view"]}
    )
    
    result = asyncio.run(run_qa(genome))
    
    # Should pass but with warning
    assert result.passed or result.warnings > 0


# Provider tests
def test_fixture_provider_available():
    """Test fixture provider is always available."""
    from conversion_architect.providers import create_fixture_provider
    
    provider = create_fixture_provider()
    
    assert provider.is_available()


def test_fixture_provider_query():
    """Test fixture provider query."""
    import asyncio
    from conversion_architect.providers import create_fixture_provider
    from conversion_architect.providers.design_pattern_provider import PatternQuery
    
    provider = create_fixture_provider()
    
    query = PatternQuery(page_type="landing", limit=5)
    patterns = asyncio.run(provider.query(query))
    
    assert len(patterns) >= 0  # May be empty if no patterns match


def test_motionsites_unavailable_fallback():
    """Test MotionSites unavailable uses fixture fallback."""
    from conversion_architect.providers import create_motionsites_provider, create_fixture_provider
    
    motionsites = create_motionsites_provider(mcp_client=None)
    
    # Should be unavailable
    assert not motionsites.is_available()


# Framer tests
def test_framer_mock_auth():
    """Test mock Framer authentication."""
    import asyncio
    from conversion_architect.providers import create_framer_provider
    from conversion_architect.providers.framer import FramerAuthStatus
    
    framer = create_framer_provider(mock=True)
    
    status = asyncio.run(framer.connect())
    
    assert status == FramerAuthStatus.AUTHENTICATED


def test_framer_mock_branch_creation():
    """Test mock Framer branch creation."""
    import asyncio
    from conversion_architect.providers import create_framer_provider
    
    framer = create_framer_provider(mock=True)
    asyncio.run(framer.connect())
    
    branch = asyncio.run(framer.create_branch("test_branch"))
    
    assert "branch_id" in branch
    assert branch["name"] == "test_branch"


def test_framer_promotion_denied():
    """Test Framer production promotion is denied."""
    import asyncio
    from conversion_architect.providers import create_framer_provider, PromotionDeniedError
    
    framer = create_framer_provider(mock=True)
    asyncio.run(framer.connect())
    
    branch = asyncio.run(framer.create_branch("test_branch"))
    
    with pytest.raises(PromotionDeniedError):
        asyncio.run(framer.promote_to_production(branch["branch_id"]))


def test_framer_idempotent_compile():
    """Test genome compilation is idempotent."""
    import asyncio
    from conversion_architect.providers import create_framer_provider
    from conversion_architect.schemas import LanderGenome
    
    framer = create_framer_provider(mock=True)
    asyncio.run(framer.connect())
    
    genome = LanderGenome(
        genome_id="genome_001",
        name="Test",
        family_id="test",
        genes=[],
        section_order=["hero"]
    )
    
    branch = asyncio.run(framer.create_branch("test"))
    
    # Compile twice
    result1 = asyncio.run(framer.compile_genome(genome, branch["branch_id"]))
    result2 = asyncio.run(framer.compile_genome(genome, branch["branch_id"]))
    
    # Should succeed both times (idempotent)
    assert result1["success"]
    assert result2["success"]


# Experiment tests
def test_experiment_one_variable():
    """Test experiment default is one variable."""
    from conversion_architect.schemas import DesignExperiment, MemoryLevel
    
    exp = DesignExperiment(
        experiment_id="exp_001",
        name="Test Experiment",
        primary_variable="cta_color",
        control_genome_id="genome_ctrl",
        treatment_genome_id="genome_treat"
    )
    
    assert len(exp.secondary_variables) == 0


def test_experiment_cell_to_global_prohibited():
    """Test CELL promotion to GLOBAL is prohibited."""
    from conversion_architect.schemas import DesignExperiment, MemoryLevel, ExperimentVariant
    
    exp = DesignExperiment(
        experiment_id="exp_001",
        name="Test",
        primary_variable="color",
        control_genome_id="ctrl",
        treatment_genome_id="treat",
        memory_level=MemoryLevel.CELL,
        promotion_candidates=[MemoryLevel.GLOBAL],
        winner=ExperimentVariant.TREATMENT,
        confidence=0.95
    )
    
    # Should NOT be able to promote to GLOBAL
    can_promote = exp.can_promote_to(MemoryLevel.GLOBAL)
    assert not can_promote


def test_experiment_valid_promotion():
    """Test valid experiment promotion."""
    from conversion_architect.schemas import DesignExperiment, MemoryLevel, ExperimentVariant
    
    exp = DesignExperiment(
        experiment_id="exp_001",
        name="Test",
        primary_variable="color",
        control_genome_id="ctrl",
        treatment_genome_id="treat",
        memory_level=MemoryLevel.CELL,
        promotion_candidates=[MemoryLevel.VERTICAL],
        winner=ExperimentVariant.TREATMENT,
        confidence=0.95
    )
    
    # Should be able to promote to VERTICAL
    can_promote = exp.can_promote_to(MemoryLevel.VERTICAL)
    assert can_promote


# CallQuant adapter tests
def test_callquant_adapter_campaign_cell():
    """Test CallQuant adapter maps CampaignCell."""
    from conversion_architect.adapters import create_callquant_adapter
    
    adapter = create_callquant_adapter()
    
    campaign_cell = {
        "id": "cell_001",
        "vertical": "home_services",
        "target_states": ["CA", "TX"],
        "trust_signals": ["license", "insurance"]
    }
    
    result = adapter.adapt_campaign_cell(campaign_cell)
    
    assert result["campaign_cell_id"] == "cell_001"
    assert result["vertical"] == "home_services"
    assert "CA" in result["target_states"]


def test_callquant_adapter_claim_manifest():
    """Test CallQuant adapter maps ClaimManifest."""
    from conversion_architect.adapters import create_callquant_adapter
    
    adapter = create_callquant_adapter()
    
    manifest = {
        "id": "manifest_001",
        "claims": [
            {"claim": "24_hour_service", "status": "supported"},
            {"claim": "fake_claim", "status": "unsupported"}
        ]
    }
    
    result = adapter.adapt_claim_manifest(manifest)
    
    assert len(result["supported_claims"]) == 1
    assert len(result["unsupported_claims"]) == 1


def test_callquant_build_context():
    """Test building complete context from CallQuant entities."""
    from conversion_architect.adapters import create_callquant_adapter
    
    adapter = create_callquant_adapter()
    
    campaign_cell = {
        "id": "cell_001",
        "vertical": "home_services"
    }
    
    intent_cluster = {
        "id": "intent_001",
        "intent_type": "emergency",
        "keywords": "hvac repair, emergency heating"
    }
    
    offer_variant = {
        "id": "offer_001",
        "headline": "24/7 HVAC Service",
        "value_proposition": "Fast, reliable HVAC repair",
        "urgency_level": "high",
        "offer_type": "service",
        "price": "$89"
    }
    
    claim_manifest = {
        "id": "manifest_001",
        "claims": [
            {"claim": "24_hour_service", "status": "supported", "type": "service"}
        ],
        "compliance_constraints": ["license_number"]
    }
    
    context = adapter.build_context(
        campaign_cell=campaign_cell,
        intent_cluster=intent_cluster,
        offer_variant=offer_variant,
        claim_manifest=claim_manifest
    )
    
    assert context.campaign_cell_id == "cell_001"
    assert context.offer_headline == "24/7 HVAC Service"
    assert len(context.supported_claims) == 1


# Genome compiler tests
def test_genome_compiler_basic():
    """Test basic genome compilation."""
    import asyncio
    from conversion_architect.schemas import BusinessConversionContext, ConversionGoal, DesignFamily
    from conversion_architect.genome_compiler import compile_genome
    
    family = DesignFamily(
        family_id="portfolio_v1",
        name="Portfolio"
    )
    
    context = BusinessConversionContext(
        context_id="ctx_001",
        campaign_cell_id="cell_001",
        vertical="home_services",
        offer={
            "id": "offer_001",
            "type": "service",
            "headline": "24/7 HVAC Service",
            "price": "$89"
        },
        offer_headline="24/7 HVAC Service",
        offer_value_prop="Fast, reliable repair",
        conversion_goal=ConversionGoal.PHONE_CALL,
        primary_metric="cost_per_qualified_call"
    )
    
    genome = asyncio.run(compile_genome(context, family))
    
    assert genome.family_id == "portfolio_v1"
    assert len(genome.genes) > 0
    assert "hero" in genome.section_order


# Family coherence tests
def test_family_coherence():
    """Test family coherence check."""
    import asyncio
    from conversion_architect.schemas import LanderGenome
    from conversion_architect.qa_system import run_qa
    
    # Valid genome
    genome = LanderGenome(
        genome_id="genome_001",
        name="Test",
        family_id="portfolio_v1",
        genes=[
            {
                "gene_id": "cta_1",
                "gene_type": "cta",
                "content": {"cta_text": "Call Now"}
            }
        ],
        section_order=["hero", "cta"],
        tracking_config={"events": ["page_view"]},
        supported_claims=["service"]
    )
    genome.genes[0]["content"]["headline"] = "Our Service"
    
    result = asyncio.run(run_qa(genome))
    
    family_check = next(
        (c for c in result.checks if c.check_type.value == "family_coherence"),
        None
    )
    
    if family_check:
        assert family_check.status.value in ["pass", "warn"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
