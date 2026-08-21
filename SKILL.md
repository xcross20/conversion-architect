# Conversion Architect Skill

**Version**: 0.1.0  
**Authority**: GREEN (read-only advisory; no production mutations in WO-CA-0001)  
**Scope**: Landing page design system, genome compilation, Framer integration, QA veto

---

## Mission

The Conversion Architect transforms validated offers, claims, and economic outcomes into high-converting landing page genomes. It owns the canonical design domain: **LanderGenome** (not Framer objects). It produces genomes that are QA-verified, family-coherent, and promotion-safe.

---

## Architecture

```
conversion-architect/
├── SKILL.md              # This file
├── docs/                 # Documentation
│   ├── ARCHITECTURE.md   # System design
│   ├── FAMILY_SIGNATURES.md
│   ├── GENOME_COMPILER.md
│   └── QA_SPEC.md
├── schemas/              # Canonical domain models
│   ├── design_family.py
│   ├── family_signature.py
│   ├── vertical_skin.py
│   ├── design_pattern.py
│   ├── lander_genome.py
│   ├── genome_gene.py
│   ├── deployment_ref.py
│   ├── qa_audit.py
│   ├── design_experiment.py
│   └── business_context.py
├── agents/               # WD-01 to WD-06 designer roles
├── providers/            # Design pattern providers
│   ├── design_pattern_provider.py
│   ├── motionsites.py
│   └── framer.py
├── design-system/        # Family signatures, tokens
├── skins/                # Vertical skin definitions
├── prompts/              # Agent prompts
├── benchmarks/           # Test cases
└── tests/                # QA and integration tests
```

---

## Canonical Domain

### Core Entities

| Entity | Description | Canonical? |
|--------|-------------|------------|
| `DesignFamily` | Collection of family signatures | ✓ |
| `FamilySignature` | Grammar rules (headline, CTA, spacing) | ✓ |
| `VerticalSkin` | Vertical-specific visual tokens | ✓ |
| `DesignPattern` | Section/element patterns | ✓ |
| `LanderGenome` | Complete page specification | ✓ |
| `GenomeGene` | Individual genome components | ✓ |
| `DeploymentRef` | Framer/external deployment handle | ✓ |
| `QAAudit` | Quality assurance results | ✓ |
| `DesignExperiment` | A/B test for designs | ✓ |
| `BusinessConversionContext` | Economic and conversion inputs | ✓ |

**Framer objects are NOT canonical** — they are output targets.

---

## Agent Roles (WD-01 to WD-06)

| Role | Mission | Primary Variable |
|------|---------|------------------|
| WD-01 | Visual Identity | Primary color palette |
| WD-02 | Information Architecture | Content hierarchy |
| WD-03 | Conversion Layout | CTA placement and geometry |
| WD-04 | Proof Architecture | Social proof elements |
| WD-05 | Mobile Experience | Responsive behavior |
| WD-06 | Motion Design | Animation patterns |

Each role has:
- Mission statement
- One underlying variable they optimize
- Questions to ask
- Noise/discard rules
- Structured outputs
- Permissions & prohibited actions
- Benchmark cases
- What_would_change_my_mind criteria

---

## Portfolio Families

### Master Family: `portfolio_v1`

Stable signatures:
- Editorial headline grammar (H1 structure, length, tone)
- Primary CTA geometry (size, shape, color contrast)
- Spacing/grid rhythm (8px base unit)
- Proof-card grammar (testimonial format, star placement)
- Mobile sticky-action grammar (bottom bar behavior)

### Included Skins

| Skin | Vertical | Family |
|------|----------|--------|
| `emergency_home_services_v1` | Home services (plumbing, HVAC, electrical) | portfolio_v1 |
| `professional_services_v1` | B2B professional services | portfolio_v1 |

---

## Provider Abstractions

### DesignPatternProvider

Query interface for design patterns:
- `page_type`: landing, squeeze, quiz, etc.
- `section`: hero, features, pricing, etc.
- `desired_perception`: urgency, trust, premium, etc.
- `vertical`: home_services, legal, medical, etc.
- `conversion_goal`: lead_capture, phone_call, appointment

**MotionSites** (MCP): Production provider with real patterns.  
**FixtureProvider**: Fallback for CI/offline environments.

Constraints: MotionSites cannot override offer, claims, economics, accessibility, family signature, or CTA hierarchy.

### FramerProvider

- `connect()`: Authenticate
- `create_branch(name)`: Create preview branch
- `compile_genome(genome, branch)`: Apply genome to branch
- `publish_preview(branch)`: Generate preview URL
- `get_deployment_status()`: Check production status
- `promote_to_production(branch)`: Merge to production (DENIED in WO-CA-0001)
- `rollback(deployment_id)`: Revert to previous

**Safety**: All autonomous variants use branch preview. No live promotion in WO-CA-0001.

---

## QA System

QA has **veto authority** — genomes cannot proceed without passing QA.

### Checks

| Check | Type | Severity |
|-------|------|----------|
| CTA/action | Deterministic | BLOCKING |
| Tracking | Deterministic | BLOCKING |
| Disclosures | Deterministic | BLOCKING |
| Supported claims | Deterministic | BLOCKING |
| Placeholders | Deterministic | WARNING |
| Responsive rendering | Visual | WARNING |
| Overflow | Visual | WARNING |
| CTA visibility | Visual | WARNING |
| Sticky collisions | Visual | WARNING |
| Contrast/accessibility | Visual | WARNING |
| Family coherence | Deterministic | BLOCKING |

---

## Experiments

- Default: **one dominant genome variable** per experiment
- Memory levels: `GLOBAL`, `VERTICAL`, `CELL`
- `CELL` promotion directly to `GLOBAL` is **prohibited**
- Business adapter supplies primary economic metric

---

## CallQuant Integration

A thin adapter inside CallQuant maps:
- `CampaignCell` → design context
- `IntentCluster` → vertical/perception goals
- `OfferVariant` → offer structure
- `ClaimManifest` → claims validation
- Qualification/compliance → constraints
- Click-to-call action → CTA spec
- Experiment IDs → design experiment tracking
- Economic outcomes → primary metric

---

## Authority Matrix

| Action | Authority | Notes |
|--------|-----------|-------|
| Preview branch creation | GREEN | Local workspace |
| Genome compilation | GREEN | Preview only |
| QA execution | GREEN | Read-only analysis |
| Production promotion | RED | Denied in WO-CA-0001 |
| Live domain setup | RED | Denied in WO-CA-0001 |
| Spend (any) | RED | Denied in WO-CA-0001 |

---

## First Work Order: CA-M0 to CA-M4

| Milestone | Deliverables |
|-----------|-------------|
| CA-M0 | Skill skeleton, 6 agent roles |
| CA-M1 | Canonical schemas (all entities) |
| CA-M2 | Portfolio family, 2 skins |
| CA-M3 | MotionSites abstraction, Framer mock |
| CA-M4 | Genome compiler, QA system |

**Out of scope for WO-CA-0001:**
- Live custom domains
- Google Ads spend
- Production traffic switching
- Mass SEO page generation

---

## Definition of Done

- [ ] All tests pass
- [ ] State/docs updated
- [ ] Provider semantics documented
- [ ] Preview reproducible
- [ ] No production authority silently granted
- [ ] Fresh agent can reconstruct why each page has its design
- [ ] CallQuant can request landing page without knowing MotionSites/Framer internals
