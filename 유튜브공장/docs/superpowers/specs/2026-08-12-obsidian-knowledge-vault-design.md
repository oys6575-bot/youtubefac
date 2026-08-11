# Obsidian Knowledge Vault Design

**Date:** 2026-08-12  
**Status:** Proposed for user review  
**Scope:** Isolated YouTube Factory only

## Goal

Build a project-local Obsidian vault that turns **all currently inventoried factory
knowledge** into readable, linked filmmaking knowledge without making every record an
executable skill or loading the whole library into an agent prompt.

The initial import covers:

- 43 visual-technique records;
- 107 installed or preserved skill records;
- 104 tool inventory records;
- 16 pinned GitHub and Hugging Face creative-source records;
- all 23 external evidence links currently cited by the capability audit, including
  six Reddit discussions explicitly labeled as anecdotal signals;
- 6 local-model locks and 10 toolchain locks;
- TopView's 9 capability groups and 12 visible model-family records;
- playbooks and the research documents that explain why each policy exists.

The first release must work as plain Markdown with no Obsidian community plugin,
network service, embedding model, or external database. Obsidian is an optional human
interface over files that Codex, Claude, and OpenMontage can read directly.

## Approved Direction and Alternatives

The user approved the Obsidian-first direction after comparing three approaches:

1. **Obsidian only:** simple and durable, but does not by itself tell an agent which
   pages to load.
2. **LLM wiki only:** convenient semantic search, but creates summary drift and a second
   opaque source of truth.
3. **Obsidian source plus derived LLM retrieval:** chosen. Human-readable Markdown is
   authoritative for expanded knowledge; a later LLM index may be regenerated from it.

Phase 1 implements the chosen architecture through deterministic local lookup. Vector
search and an LLM-generated wiki remain later derived layers, not prerequisites.

## Source-of-Truth Boundaries

The vault does not replace existing control planes:

| Concern | Canonical owner |
|---|---|
| Production state, checkpoints, approvals, outputs | OpenMontage |
| Technique ID, status, route/runtime eligibility, activation policy | `config/visual-technique-registry.yaml` |
| Expanded explanation, examples, cross-links, operating notes | `knowledge/` Obsidian vault |
| Stage behavior and tool execution procedure | `skills/` and `.agents/skills/` |
| External revision and license lock | `vendor/creative-sources/manifest.json` |
| Tool and skill availability/status | `config/tool-inventory.json` and `config/factory-skill-routing.yaml` |
| Model revision and download policy | `config/local-models.lock.json` |

Machine-managed metadata in a card is synchronized from the registry. Human-authored
notes are preserved across synchronization. A card can explain a technique but cannot
make a blocked or on-demand technique executable.

## Vault Structure

```text
knowledge/
├── .obsidian/
│   ├── app.json
│   ├── appearance.json
│   └── core-plugins.json
├── .gitignore
├── 00-START-HERE.md
├── 01-MAPS/
│   ├── Techniques.md
│   ├── Production-Phases.md
│   ├── Providers.md
│   ├── Runtimes.md
│   ├── Skills.md
│   ├── Tools.md
│   ├── Sources.md
│   ├── Models.md
│   └── Status-and-Safety.md
├── 02-TECHNIQUES/
│   ├── camera/
│   ├── continuity/
│   ├── direction/
│   ├── editing/
│   ├── graphics/
│   ├── library/
│   ├── provider/
│   ├── research/
│   ├── runtime/
│   ├── sound/
│   ├── transition/
│   └── typography/
├── 03-PLAYBOOKS/
│   └── Heritage-Forge.md
├── 04-PROVIDERS/
│   ├── TopView-Manual.md
│   ├── Local-LTX.md
│   └── Provider-Isolation.md
├── 05-RUNTIMES/
│   ├── HyperFrames.md
│   ├── Remotion.md
│   └── FFmpeg.md
├── 06-SOURCES/
│   ├── github/
│   ├── hugging-face/
│   ├── official-sites/
│   ├── reddit-signals/
│   └── Source-Manifest.md
├── 07-SKILLS/
│   ├── required/
│   ├── optional/
│   ├── restricted/
│   └── reference-only/
├── 08-TOOLS/
│   └── <capability-family>/
├── 09-MODELS/
│   └── <model-id>.md
├── 10-RESEARCH/
│   ├── Capability-Audit.md
│   └── Evidence-Map.md
├── 90-TEMPLATES/
│   ├── Technique-Card.md
│   ├── Skill-Card.md
│   ├── Tool-Card.md
│   ├── Source-Card.md
│   └── Model-Card.md
└── 99-INBOX/
    └── README.md
```

Obsidian workspace state, caches, and third-party plugin state are ignored. The vault
commits only portable settings and Markdown knowledge.

## Technique Card Contract

Every registry record has exactly one card at:

```text
knowledge/02-TECHNIQUES/<category>/<technique-id>.md
```

The YAML frontmatter contains synchronized policy metadata:

```yaml
type: visual-technique
technique_id: camera.variable_velocity_push
title: Variable-velocity camera push
registry_version: 2026-08-12
category: camera
status: ACTIVE
selectable: true
priority: 99
phases: [visual_plan, animatic, production, compose]
intents: [variable_camera_speed, photo_to_motion, camera_motion, attention_landing]
tags: [speed_ramp, push_in, slow_fast_slow, easing]
provider_scopes: [GENERIC]
render_runtimes: [HYPERFRAMES, REMOTION]
requires_human_opt_in: false
requires_license_review: false
requires_network: false
source_type: local_skill
source_label: HyperFrames nudge curve
source_license: Apache-2.0
source_path: .agents/skills/hyperframes-animation/rules/nudge-curve.md
```

The body uses stable sections:

1. Purpose
2. Selection cues
3. Directing instructions
4. Constraints and failure modes
5. Route and runtime use
6. Source and provenance
7. Related knowledge
8. Production notes

Sections 1–7 are generated from registry facts and deterministic local mappings.
`Production notes` is a human-editable region bounded by explicit markers. Vault sync
must preserve this region byte-for-byte.

## Knowledge Maps

Maps of Content provide useful Obsidian navigation without becoming new policy files.
They are regenerated from the registry and card paths:

- `Techniques.md`: category and status counts with links to all cards.
- `Production-Phases.md`: research through QC, listing eligible techniques.
- `Providers.md`: generic and provider-specific records with isolation warnings.
- `Runtimes.md`: HyperFrames, Remotion, FFmpeg, and route compatibility.
- `Status-and-Safety.md`: definitions of `ACTIVE`, `ON_DEMAND`, `REFERENCE_ONLY`, and
  `BLOCKED`, including the rule that knowledge visibility is not execution approval.

Additional maps expose the full inventory without activating it:

- `Skills.md`: all 107 skills grouped by required, optional, restricted, disabled, and
  reference-only status.
- `Tools.md`: all 104 tools grouped by capability, provider, runtime, and availability.
- `Sources.md`: all pinned creative sources and all URLs cited in the research audit.
- `Models.md`: local model revisions, licenses, expected hardware role, and download
  approval requirements.
- `Evidence-Map.md`: links official claims, GitHub issues, Hugging Face records, and
  Reddit anecdotes to the decisions they informed.

Reddit cards use `evidence_class: ANECDOTAL_SIGNAL` and can inform test size, retry
limits, or risk warnings only. They cannot establish a product fact or production
instruction. Official documentation and immutable revision locks outrank them.

## Cross-Entity Link Contract

The vault is useful only when cards connect to execution context. Every generated card
therefore exposes typed links where the source inventories permit them:

```text
technique -> source skill -> compatible tool -> provider/runtime
technique -> external source -> license/revision -> status
tool -> required skill -> setup/runtime boundary
model -> local tool -> hardware warning -> Human Gate
research signal -> affected decision -> verification requirement
```

Links are derived from registry source paths, tool `agent_skills`, skill-routing names,
provider/runtime fields, local-model locks, and explicit source IDs. A missing relation
is shown as unlinked; it is never guessed by an LLM during sync.

## Local Interfaces

### Library

Create `lib/knowledge_vault.py` with focused interfaces:

```python
load_knowledge_sources(*, root: Path) -> KnowledgeSources
sync_vault(sources: KnowledgeSources, *, root: Path) -> SyncReport
audit_vault(sources: KnowledgeSources, *, root: Path) -> list[str]
resolve_knowledge_pack(
    selection: dict,
    *,
    sources: KnowledgeSources,
    root: Path,
) -> dict
search_vault(
    query: str,
    *,
    entity_types: tuple[str, ...],
    root: Path,
) -> list[dict]
```

`KnowledgeSources` contains the visual-technique registry, skill-routing inventory,
skill-source manifest, tool inventory, creative-source manifest, toolchain lock,
local-model lock, TopView capability catalog, and the audited research documents. The
loader reads only these explicit project-local inputs.

`sync_vault` creates or updates cards and maps while preserving production notes.
`audit_vault` verifies the one-to-one card contract and metadata consistency.
`resolve_knowledge_pack` consumes a selector result; it does not perform another
selection or weaken route policy.

`search_vault` provides deterministic local search across techniques, skills, tools,
models, sources, and research signals. Search visibility never implies activation.

### Command Line

Create `scripts/knowledge-vault.py` with four local-only commands:

```bash
.venv/bin/python scripts/knowledge-vault.py sync
.venv/bin/python scripts/knowledge-vault.py audit
.venv/bin/python scripts/knowledge-vault.py search "material macro"
.venv/bin/python scripts/knowledge-vault.py pack --selection selection.json
```

`pack` prints JSON containing the registry version, selected IDs, card paths, source
paths, load order, and exclusions. An optional `--output` may save the same JSON under
a production project's `artifacts/` directory.

No command launches Obsidian, contacts a provider, spends credits, changes a
checkpoint, or approves a Human Gate.

## Agent and Skill Integration

MK Visual Director continues to select three to seven technique IDs first. It then:

1. audits the registry and vault;
2. resolves a knowledge pack from the already selected IDs;
3. reads only the selected cards;
4. reads an underlying source skill only when the card's source and current task
   require deeper execution detail;
5. records technique IDs in VisualPlan as it does now.

The pack may add linked **support records** after selection:

- the technique card for every selected ID;
- the directly referenced source-skill card and local skill path;
- compatible tool cards only for the already approved provider/runtime route;
- relevant model or provider constraints;
- provenance and risk-signal cards needed for QC.

Support records do not count as additional selected techniques and cannot change the
route. They are returned as paths and short metadata, allowing the agent to read deeper
only when needed. A default load budget prevents more than seven technique cards, seven
skill cards, seven tool cards, and seven source/risk cards from entering one knowledge
pack without an explicit diagnostic request.

The knowledge pack is a retrieval aid, not an executable skill. Existing stage skills
remain small and procedural. The vault holds broad filmmaking knowledge, examples, and
cross-links. This prevents hundreds of overlapping skills and excessive prompt load.

## Synchronization Rules

- Registry IDs and categories determine card paths.
- Skill names and routing statuses determine skill-card paths.
- Tool names and capability families determine tool-card paths.
- Source manifest IDs and normalized research URLs determine source-card identities.
- Model lock IDs determine model-card paths.
- Registry order determines stable map ordering within category groups.
- Sync is idempotent: a second run with unchanged inputs produces no file changes.
- Unknown manually created notes remain under `99-INBOX/` and are never activated.
- Removing a registry record does not silently delete its card. Sync reports it as an
  orphan and audit fails until a human archives or removes it deliberately.
- Renaming an ID creates a new card and reports the old card as an orphan; no automatic
  destructive move occurs.
- Card frontmatter cannot override registry status, provider scope, runtime scope, or
  activation conditions.

## Error Handling

- Missing or malformed vault card: audit and pack fail with the exact technique ID.
- Duplicate card ID: audit fails and lists both paths.
- Frontmatter policy drift: audit reports field-level expected and actual values.
- Missing source file or manifest lock: existing registry audit remains authoritative;
  vault audit also reports the broken card link.
- `ON_DEMAND` record without explicit selector opt-in: pack refuses it.
- `REFERENCE_ONLY` or `BLOCKED` record: pack always refuses it.
- Provider or runtime mismatch: pack refuses rather than substituting another record.
- More than seven selected IDs: pack fails even if the input JSON was hand-edited.
- A related skill, tool, model, or source record with a disabled/restricted status is
  visible in search but omitted from the normal pack with an explicit exclusion reason.
- No selected IDs: pack returns a structured error and never fills the set
  automatically.

## Testing and Acceptance

Automated tests must prove:

1. A fresh sync creates one card for all 43 techniques, 107 skills, 104 tools, 16 pinned
   creative sources, all 23 research-audit URLs, 6 local-model locks, 10 toolchain
   locks, and all inventoried TopView capability/model-family records.
2. Every card frontmatter matches the canonical inventory fields that govern selection,
   availability, licensing, and safety.
3. Sync is byte-stable when nothing changes.
4. Sync preserves text inside the production-notes markers.
5. Maps link to every card without broken internal links, and cross-entity links use
   only explicit inventory relationships.
6. A valid three-to-seven-item selection resolves cards in selector order.
7. TopView packs exclude Higgsfield, Seedance, and local-only provider instructions.
8. On-demand knowledge requires explicit opt-in; reference-only and blocked knowledge
   can never enter a pack.
9. A missing card, duplicate ID, malformed frontmatter, orphan card, provider mismatch,
   runtime mismatch, empty selection, or oversized selection fails clearly.
10. Search finds dormant and reference records without activating them, while a normal
    pack includes only route-safe support records within its load budget.
11. Reddit records remain anecdotal risk signals and cannot enter a pack as factual or
    executable guidance.
12. Portable Obsidian configuration contains no enabled community plugin or machine
    workspace state.
13. The existing visual-technique, VisualPlan, pipeline, and TopView contract tests
    remain green.

Human acceptance requires opening `knowledge/` as an Obsidian vault and confirming:

- `00-START-HERE.md` explains how to navigate and add notes;
- maps and backlinks make camera, transition, edit, typography, sound, provider, and
  runtime knowledge easy to browse;
- a search for `photo_to_motion` reaches the applicable technique cards;
- the cards are useful in plain Markdown outside Obsidian.

## Security, Privacy, and Licensing

- Store no API key, account cookie, provider output, personal workspace path, or paid
  asset in the vault.
- Cards may link to pinned external sources but cannot copy non-permitted large source
  bodies into the repository.
- License and revision remain visible on source-backed cards.
- LLM summaries added later must cite their source card and may never alter registry
  policy automatically.

## Non-Goals for Phase 1

- No Obsidian community plugin installation.
- No Obsidian Sync, cloud publishing, browser automation, or app control.
- No embedding model, vector database, or background indexing daemon.
- No new scraping or bulk copying from GitHub, Reddit, Hugging Face, or YouTube. Every
  source already discovered in the audited inventories is indexed and linked; external
  bodies remain at their pinned or cited locations unless their license and activation
  status permit a later deliberate import.
- No TopView API or automated UI interaction.
- No replacement of OpenMontage, existing skills, VisualPlan, or Human Gates.
- No automatic promotion of inbox notes into selectable production knowledge.

## Future LLM Wiki Extension

A future read-only exporter may create a JSONL index from audited cards. That index is
fully disposable and can feed local embeddings or an LLM wiki. It must always be
regenerable from the vault, include card IDs and revisions, and never become a second
policy source.
