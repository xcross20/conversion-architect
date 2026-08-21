# Family Signatures

## Portfolio Master Family (portfolio_v1)

The canonical design family defining stable grammar rules for all landing pages.

### Headline Grammar

```yaml
h1_structure: benefit_statement | hook | number_lead
max_length: 70
min_length: 20
tone_markers: [urgent, clarifying, social]
allowed_formats:
  - command_verb
  - question_open
  - number_lead
  - superlative
  - how_to
prohibited_patterns:
  - passive_voice
  - question_mark_ending
  - all_caps
```

### CTA Grammar

```yaml
primary_size:
  min_width: 200
  height: 56
  max_height: 64
shape: rounded
border_radius: 8
contrast_ratio: 4.5  # WCAG AA
```

### Spacing Rhythm

```yaml
base_unit: 8
rhythm: [8, 16, 24, 32, 48, 64, 96, 128]
max_content_width: 1200
```

### Proof Grammar

```yaml
testimonial_format: problem_agitation_solution
star_placement: left_aligned
author_format: "{name}, {location}"
attribution_required: true
```

### Mobile Grammar

```yaml
sticky_bar: true
sticky_height: 64
touch_target_min: 44
```
