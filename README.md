# IO Planning Lifecycle Skill

Create, review, visualize, translate, and evolve versioned IO Flow specifications from product narratives, PRDs, research notes, and existing flow documents.

`io-planning-lifecycle` turns loosely structured product intent into a durable interaction and orchestration contract: stable entry-point IDs, entry-specific request classifications, ordered service loops, synchronized Mermaid diagrams, English/Simplified Chinese variants, progress visibility, explicit open decisions, semantic versions, and human-readable change history.

## Why this skill exists

IO Flow documents often begin as diagrams, chat notes, or isolated service lists. Those formats are useful during discovery but tend to lose routing criteria, ownership, implementation state, and the reason a flow changed. This Skill makes those decisions reviewable by product, design, engineering, operations, and verification teams without pretending that missing information is settled.

## Capabilities

- Generate a new IO Flow from narrative or semi-structured source material.
- Standardize an existing flow without silently changing its meaning.
- Give every entry point a stable `EP-NN` identifier.
- Define classification rules independently per entry point; A/B/C is supported but not required.
- Express each request type as a decision-grade definition, representative examples, and an ordered service loop.
- Generate Mermaid flow visualizations from the authoritative loops without inventing missing services or metrics.
- Create synchronized English (`en`) and Simplified Chinese (`zh-CN`) companion documents while preserving stable IDs and routing order.
- Track draft, review, confirmation, implementation, and deprecation states.
- Apply semantic versioning based on the highest-impact accepted change.
- Preserve attribution, source references, open decisions, and a newest-first change log.
- Audit a document without editing it.
- Validate English or Chinese IO Flow documents with a dependency-free Python CLI.
- Compare a translated document with its source and detect structural drift in entry points, types, loop length, open decisions, and diagram coverage.
- Run decision-focused Elicitation with grounded selection questions, dependent follow-ups, and an explicit stopping rule.
- Detect a teammate's remote update by commit/blob revision, show the semantic diff, and prevent blind last-write-wins publishing.
- Run one-time Sync checks or explicit Watch mode with a local baseline and optional Codex recurring automation.

## Output contract

Every generated document follows this model:

```text
Document metadata and lifecycle state
├── Purpose and scope
├── Classification defaults
├── Progress overview
├── Entry points
│   └── EP-NN
│       ├── Location, function, trigger, output, status, owner
│       ├── Entry-specific classification basis
│       └── Type A/B/C or domain-specific types
│           ├── Definition
│           ├── Examples
│           └── Ordered loop
├── Flow visualizations
├── Open decisions and assumptions
└── Change log
```

See [the normative schema](io-planning-lifecycle/references/io-flow-schema.md) for field-level requirements, [the lifecycle rules](io-planning-lifecycle/references/lifecycle-and-collaboration.md) for versioning and merging, [the collaboration rules](io-planning-lifecycle/references/collaboration-and-notifications.md) for Sync/Watch behavior, [the Elicitation rules](io-planning-lifecycle/references/elicitation.md) for interactive guidance, and [the visualization and translation rules](io-planning-lifecycle/references/visualization-and-translation.md) for Mermaid and bilingual parity requirements.

## Repository layout

```text
.
├── README.md
├── docs/
│   └── requirements-fulfillment.md
├── examples/
│   ├── topogrow-io-flow.md
│   └── topogrow-io-flow.zh-CN.md
└── io-planning-lifecycle/
    ├── SKILL.md
    ├── agents/
    │   └── openai.yaml
    ├── assets/
    │   └── io-flow-template.md
    ├── references/
    │   ├── collaboration-and-notifications.md
    │   ├── elicitation.md
    │   ├── io-flow-schema.md
    │   ├── lifecycle-and-collaboration.md
    │   └── visualization-and-translation.md
    ├── scripts/
    │   ├── check_io_flow_updates.py
    │   └── validate_io_flow.py
    └── tests/
        └── test_check_io_flow_updates.py
```

## Installation

### Local Codex Skill

Clone the repository and copy the Skill folder into the Codex skills directory.

macOS or Linux:

```bash
git clone https://github.com/lokihiyori/IO-Planning-Lifecycle-Skills.git
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R IO-Planning-Lifecycle-Skills/io-planning-lifecycle "${CODEX_HOME:-$HOME/.codex}/skills/"
```

Windows PowerShell:

```powershell
git clone https://github.com/lokihiyori/IO-Planning-Lifecycle-Skills.git
$codexRoot = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path ([Environment]::GetFolderPath("UserProfile")) ".codex" }
$skillsRoot = Join-Path $codexRoot "skills"
New-Item -ItemType Directory -Force -Path $skillsRoot | Out-Null
Copy-Item -Recurse -Force ".\IO-Planning-Lifecycle-Skills\io-planning-lifecycle" $skillsRoot
```

Restart or refresh Codex if the Skill is not discovered immediately.

### OpenAI Skills API

The [OpenAI Skills API](https://developers.openai.com/api/reference/python/resources/skills/methods/create) accepts a Skill directory upload or a single ZIP bundle. Upload the `io-planning-lifecycle` folder, not the repository root.

## Usage

Invoke the Skill explicitly:

```text
Use $io-planning-lifecycle to turn this PRD into a draft IO Flow specification.
```

The Skill supports seven modes:

| Mode | Use it when | Mutation behavior |
|---|---|---|
| Create | No lifecycle-ready IO Flow exists | Produces a new `0.1.0` draft unless another baseline is specified |
| Update | New product decisions or implementation discoveries affect an existing flow | Preserves stable IDs, records the semantic delta, and increments the version |
| Translate | You need an English or Simplified Chinese companion | Preserves semantic version, stable IDs, decisions, and loop order; validates structural parity |
| Audit | You need a structural or lifecycle review | Reports findings without editing unless changes are also requested |
| Elicit | Missing decisions can change routing, boundaries, persistence, or status | Asks grounded questions and closes a decision ledger before generation |
| Sync | You need to discover teammate or remote changes once | Reports commits, versions, affected IDs, and merge/conflict status without editing |
| Watch | You want near-real-time remote change notification | Polls at an explicit cadence and stays silent until the remote blob changes |

Example prompts:

```text
Use $io-planning-lifecycle to convert these product notes into an IO Flow. Ask only about gaps that would change routing or service boundaries.
```

```text
Use $io-planning-lifecycle to update EP-02 with this new verification step, recalculate progress, choose the correct semantic version, and append the change log.
```

```text
Use $io-planning-lifecycle to audit this document for overlapping type definitions, missing loop nodes, stale status, and lifecycle inconsistencies. Do not edit it.
```

```text
Use $io-planning-lifecycle to add review-ready Mermaid diagrams and create a synchronized Simplified Chinese companion for this English IO Flow.
```

```text
Use $io-planning-lifecycle in Elicit mode. Ask one blocking question at a time, then generate the IO Flow after the decision ledger is closed.
```

```text
Use $io-planning-lifecycle in Sync mode for examples/topogrow-io-flow.md. Check GitHub main, show what changed since my last check, and do not edit.
```

```text
Use $io-planning-lifecycle in Watch mode for examples/topogrow-io-flow.md every five minutes. Notify only when its remote revision changes.
```

## Collaboration and update notifications

The recommended collaboration model is GitHub branch/pull-request workflow plus optimistic concurrency. The latest accepted default-branch file is the shared source of truth. Before editing, the Skill records the remote head as a base revision; immediately before publishing, it checks again. If a teammate changed the same Entry, Type, loop edge, decision, or status, the Skill stops for semantic reconciliation instead of overwriting the new version.

Run a one-time revision check:

```bash
python io-planning-lifecycle/scripts/check_io_flow_updates.py \
  --repo lokihiyori/IO-Planning-Lifecycle-Skills \
  --path examples/topogrow-io-flow.md \
  --ref main
```

Run a local near-real-time watcher explicitly:

```bash
python io-planning-lifecycle/scripts/check_io_flow_updates.py \
  --repo lokihiyori/IO-Planning-Lifecycle-Skills \
  --path examples/topogrow-io-flow.md \
  --ref main \
  --watch-seconds 300
```

The first check creates a gitignored baseline under `.io-flow-sync/`. A later change reports the contributor, commit, timestamp, old/new document versions, affected stable IDs, compare link, and unified diff. Watch mode only runs while its process or a configured Codex recurring automation is active. Team-wide Slack/Teams/email push requires the repository administrator to connect the chosen channel through a GitHub App or webhook; no destination or secret is assumed by this Skill.

## Flow visualization and translation

Every generated IO Flow includes a `Flow Visualizations` / `流程可视化` section. The detailed entry/type loops remain authoritative; diagrams are derived review views. The Skill defaults to Mermaid flowcharts for request classification and ordered service chains, splits dense diagrams, and renders unresolved entry points as explicit TBD nodes.

For GitHub delivery, the Skill can export a repository-local SVG or PNG and embed it before the editable `mermaid-source` block. The static image displays even when GitHub's Mermaid rich renderer is unavailable in an embedded browser, while the source remains easy to revise or open in Mermaid Live Editor.

Quantitative charts are generated only when the source provides authoritative values, units, and time boundaries. This prevents a visually polished chart from implying unsupported progress or performance data.

English and Simplified Chinese variants use separate Markdown files with the same `document_id`, version, status, `EP-NN`/Type/`OD-NN` identifiers, and loop order. User-facing prose and diagram labels are translated; canonical service names can remain in parentheses when identity would otherwise be ambiguous.

## How the Skill handles uncertainty

Source documents are treated as evidence, not as instructions. The Skill asks a focused question only when the answer would materially change routing, service boundaries, status, ownership, or version impact. Lower-impact gaps remain visible as narrow assumptions or `[TBD: question — owner]` markers.

It does not infer a database, verification service, AI agent, queue, or background task merely because that node appears in another entry point. Confirmed or implemented content cannot retain unresolved blocking TBDs.

Elicit mode formalizes this behavior: it maps each blocking gap to a selection or open question, asks dependent questions sequentially, records the effect of every answer on stable IDs or loop edges, and ends with a confirmed/deferred decision ledger. It is interactive through the host conversation rather than a separate form UI.

## Version and status model

| Change | Version impact |
|---|---|
| Breaking stable IDs, global classification contracts, or downstream interfaces | MAJOR |
| Adding entries/types, changing thresholds, routing, loop nodes, or service responsibilities | MINOR |
| Clarifying examples, ownership, status, attribution, or non-behavioral wording | PATCH |
| Formatting or validation with no content change | No increment |

Lifecycle states are `draft`, `in_review`, `confirmed`, `implemented`, and `deprecated`. Status advances require evidence; polished prose alone is not approval or implementation proof.

## Validation

The validator requires Python 3.10 or later and has no third-party dependencies.

```bash
python io-planning-lifecycle/scripts/validate_io_flow.py examples/topogrow-io-flow.md
```

Useful options:

```bash
# Treat warnings such as unresolved TBDs as errors
python io-planning-lifecycle/scripts/validate_io_flow.py path/to/io-flow.md --strict

# Emit machine-readable output
python io-planning-lifecycle/scripts/validate_io_flow.py path/to/io-flow.md --json

# Compare a Simplified Chinese companion with its English source
python io-planning-lifecycle/scripts/validate_io_flow.py examples/topogrow-io-flow.zh-CN.md --translation-of examples/topogrow-io-flow.md
```

The validator checks frontmatter, lifecycle values, required sections, entry metadata, per-entry classification bases, type definitions/examples/loops, Mermaid presence and entry coverage, progress coverage, change-log alignment, unresolved TBDs, and optional bilingual structural parity. It validates structure and lifecycle invariants; it does not prove product correctness, linguistic quality, implementation completeness, or privacy compliance.

## Included Topogrow example

[Topogrow IO Flow — English](examples/topogrow-io-flow.md) and [Topogrow IO Flow — 简体中文](examples/topogrow-io-flow.zh-CN.md) demonstrate synchronized bilingual output with Mermaid routing diagrams. The source fully defines conversational and multimedia entry points but stops after the location of a structured-form entry. Both variants therefore keep `EP-03` explicit and visualize it as unresolved instead of inventing its function, classification, examples, or loop.

## Requirements fulfillment

The original six core requirements are fulfilled within the documented Git/Codex collaboration model: generation, entry-specific classifications, semantic versioning, shared progress and attribution, interactive Elicitation, iterative change tracking, and near-real-time update discovery. The [requirements fulfillment audit](docs/requirements-fulfillment.md) maps each claim to repository evidence. Character-by-character co-editing and team-channel push are intentionally conditional capabilities because they require an active watcher or an administrator-configured GitHub integration.

## Design boundaries

Use this Skill for interaction and orchestration flow specifications. Do not route generic PRD writing, implementation-only architecture diagrams, API reference documentation, or project management status reports to it unless an IO Flow deliverable is also requested.

Before publishing generated documents, review source references and examples for confidential or personally identifying information. Git commits, pushes, pull requests, and other shared-system changes remain separately authorized actions.

## Contributing

Keep changes focused on observable IO Flow decisions:

1. Preserve the progressive-disclosure structure: shared rules in `SKILL.md`, conditional detail in `references/`, and output material in `assets/`.
2. Do not duplicate lifecycle rules across files.
3. Add or update deterministic checks when a structural invariant changes.
4. Run the Skill validator on affected examples and the Skill package validator before submitting changes.
5. Explain behavioral changes and migration impact in the pull request.
