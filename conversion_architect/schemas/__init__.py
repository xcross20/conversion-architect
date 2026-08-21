"""
Conversion Architect Schemas
"""
# Design family
from conversion_architect.schemas.design_family import DesignFamily, DesignFamilyStatus

# Family signature
from conversion_architect.schemas.family_signature import FamilySignature, SignatureType, ValidationLevel

# Vertical skin
from conversion_architect.schemas.vertical_skin import VerticalSkin, Vertical, SkinStatus

# Design pattern
from conversion_architect.schemas.design_pattern import DesignPattern, PageType, SectionType, DesiredPerception

# Lander genome
from conversion_architect.schemas.lander_genome import LanderGenome, GenomeStatus, DeploymentEnvironment

# Genome gene
from conversion_architect.schemas.genome_gene import GenomeGene, GeneType, GeneStatus

# Deployment ref
from conversion_architect.schemas.deployment_ref import DeploymentRef, DeploymentStatus

# QA audit
from conversion_architect.schemas.qa_audit import QAAudit, QACheck, QASeverity, QACheckType, QACheckStatus

# Design experiment
from conversion_architect.schemas.design_experiment import DesignExperiment, ExperimentStatus, ExperimentVariant, MemoryLevel

# Business context
from conversion_architect.schemas.business_context import BusinessConversionContext, ConversionGoal, UrgencyLevel

__all__ = [
    # Design family
    "DesignFamily",
    "DesignFamilyStatus",
    # Family signature
    "FamilySignature",
    "SignatureType",
    "ValidationLevel",
    # Vertical skin
    "VerticalSkin",
    "Vertical",
    "SkinStatus",
    # Design pattern
    "DesignPattern",
    "PageType",
    "SectionType",
    "DesiredPerception",
    # Lander genome
    "LanderGenome",
    "GenomeStatus",
    "DeploymentEnvironment",
    # Genome gene
    "GenomeGene",
    "GeneType",
    "GeneStatus",
    # Deployment ref
    "DeploymentRef",
    "DeploymentStatus",
    # QA audit
    "QAAudit",
    "QACheck",
    "QASeverity",
    "QACheckType",
    "QACheckStatus",
    # Design experiment
    "DesignExperiment",
    "ExperimentStatus",
    "ExperimentVariant",
    "MemoryLevel",
    # Business context
    "BusinessConversionContext",
    "ConversionGoal",
    "UrgencyLevel",
]
