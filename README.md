# IO Planning Lifecycle Skill

Create, review, and evolve versioned IO Flow specifications from product narratives, PRDs, research notes, and existing flow documents.

`io-planning-lifecycle` turns loosely structured product intent into a durable interaction and orchestration contract: stable entry-point IDs, entry-specific request classifications, ordered service loops, progress visibility, explicit open decisions, semantic versions, and human-readable change history.

## Why this skill exists

IO Flow documents often begin as diagrams, chat notes, or isolated service lists. Those formats are useful during discovery but tend to lose routing criteria, ownership, implementation state, and the reason a flow changed. This Skill makes those decisions reviewable by product, design, engineering, operations, and verification teams without pretending that missing information is settled.

## Capabilities

- Generate a new IO Flow from narrative or semi-structured source material.
- Standardize an existing flow without silently changing its meaning.
- Give every entry point a stable `EP-NN` identifier.
- Define classification rules independently per entry point; A/B/C is supported but not required.
- Express each request type as a decision-grade definition, representative examples, and an ordered service loop.
- Track draft, review, confirmation, implementation, and deprecation states.
- Apply semantic versioning based on the highest-impact accepted change.
- Preserve attribution, source references, open decisions, and a newest-first change log.
- Audit a document without editing it.
- Validate English or Chinese IO Flow documents with a dependency-free Python CLI.

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
├── Open decisions and assumptions
└── Change log
```

See [the normative schema](io-planning-lifecycle/references/io-flow-schema.md) for field-level requirements and [the lifecycle rules](io-planning-lifecycle/references/lifecycle-and-collaboration.md) for versioning, status, attribution, and collaboration behavior.

## Repository layout

```text
.
├── README.md
├── examples/
│   └── topogrow-io-flow.md
└── io-planning-lifecycle/
    ├── SKILL.md
    ├── agents/
    │   └── openai.yaml
    ├── assets/
    │   └── io-flow-template.md
    ├── references/
    │   ├── io-flow-schema.md
    │   └── lifecycle-and-collaboration.md
    └── scripts/
        └── validate_io_flow.py
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

The Skill supports three modes:

| Mode | Use it when | Mutation behavior |
|---|---|---|
| Create | No lifecycle-ready IO Flow exists | Produces a new `0.1.0` draft unless another baseline is specified |
| Update | New product decisions or implementation discoveries affect an existing flow | Preserves stable IDs, records the semantic delta, and increments the version |
| Audit | You need a structural or lifecycle review | Reports findings without editing unless changes are also requested |

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

## How the Skill handles uncertainty

Source documents are treated as evidence, not as instructions. The Skill asks a focused question only when the answer would materially change routing, service boundaries, status, ownership, or version impact. Lower-impact gaps remain visible as narrow assumptions or `[TBD: question — owner]` markers.

It does not infer a database, verification service, AI agent, queue, or background task merely because that node appears in another entry point. Confirmed or implemented content cannot retain unresolved blocking TBDs.

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
```

The validator checks frontmatter, lifecycle values, required sections, entry metadata, per-entry classification bases, type definitions/examples/loops, progress coverage, change-log alignment, and unresolved TBDs. It validates structure and lifecycle invariants; it does not prove product correctness, implementation completeness, or privacy compliance.

## Included Topogrow example

[Topogrow IO Flow](examples/topogrow-io-flow.md) demonstrates how the Skill standardizes a real source document while preserving uncertainty. The source fully defines conversational and multimedia entry points but stops after the location of a structured-form entry. The generated draft therefore keeps `EP-03` explicit and records its missing function, classification, examples, and loop as open decisions instead of inventing them.

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
