---
card_id: research.hf.seedance_prompt_scrape
type: visual-technique
title: Scraped Seedance prompt dataset
status: BLOCKED
knowledge_schema: '1.0'
generated: true
technique_id: research.hf.seedance_prompt_scrape
category: research
selectable: false
priority: 0
phases:
- research
intents:
- provider_prompting
- training_dataset
- scraped_prompts
tags:
- huggingface
- provenance_risk
- blocked
provider_scopes:
- SEEDANCE_MANUAL
render_runtimes:
- ANY
source_path: ''
canonical_source: config/visual-technique-registry.yaml
---

# Scraped Seedance prompt dataset

## Purpose

Scraped prompt collection blocked from ingestion because source rights and embedded content provenance are uncertain.

## Selection cues

- provider_prompting
- training_dataset
- scraped_prompts

## Directing instructions

- Do not import the dataset wholesale or treat scraped examples as cleared training material.

## Constraints and failure modes

- Status: `BLOCKED`
- Selectable: `false`
- Human opt-in: `true`
- License review: `true`
- Network required: `true`

## Route and runtime use

Providers:
- SEEDANCE_MANUAL

Runtimes:
- ANY

## Source and provenance

```json
{
  "type": "huggingface",
  "label": "GokuScraper Seedance prompts",
  "license": "CC-BY-4.0_WITH_PROVENANCE_RISK",
  "manifest_id": "hf.seedance_prompt_scrape"
}
```

## Canonical record

```json
{
  "id": "research.hf.seedance_prompt_scrape",
  "name": "Scraped Seedance prompt dataset",
  "description": "Scraped prompt collection blocked from ingestion because source rights and embedded content provenance are uncertain.",
  "category": "research",
  "status": "BLOCKED",
  "selectable": false,
  "priority": 0,
  "phases": [
    "research"
  ],
  "intents": [
    "provider_prompting",
    "training_dataset",
    "scraped_prompts"
  ],
  "tags": [
    "huggingface",
    "provenance_risk",
    "blocked"
  ],
  "provider_scopes": [
    "SEEDANCE_MANUAL"
  ],
  "render_runtimes": [
    "ANY"
  ],
  "source": {
    "type": "huggingface",
    "label": "GokuScraper Seedance prompts",
    "license": "CC-BY-4.0_WITH_PROVENANCE_RISK",
    "manifest_id": "hf.seedance_prompt_scrape"
  },
  "activation": {
    "default_allowed": false,
    "requires_human_opt_in": true,
    "requires_license_review": true,
    "requires_network": true
  },
  "directives": [
    "Do not import the dataset wholesale or treat scraped examples as cleared training material."
  ]
}
```

## Related knowledge

- [[06-SOURCES/hugging-face/hf.seedance_prompt_scrape|hf.seedance_prompt_scrape]]

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
