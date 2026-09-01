# IO Flow Specification Schema

Use this reference when creating an IO Flow, adding or restructuring entry points, or checking whether a document is complete.

## Design goals

An IO Flow must let product, design, engineering, operations, and verification teams answer four questions without reconstructing intent from chat history:

1. Where can a request enter the system?
2. How is the request classified at that entry point?
3. Which ordered services or actors handle each class?
4. What is decided, unresolved, or implemented today?

The body language should match the user's request or the existing document. Keep stable identifiers and frontmatter keys in the canonical form below so tooling can inspect the file.

## Required frontmatter

```yaml
---
title: "<product or capability> IO Flow"
document_id: "io-flow-<stable-slug>"
version: "0.1.0"
status: "draft"
language: "en"
owners:
  - "unspecified"
last_updated: "YYYY-MM-DD"
last_updated_by: "unspecified"
source_refs:
  - "<path, URL, issue, or source label>"
translations: []
---
```

Rules:

- `document_id` remains stable across title changes.
- `version` is semantic and follows the lifecycle reference.
- `status` is one of `draft`, `in_review`, `confirmed`, `implemented`, or `deprecated`.
- `language` is `en` or `zh-CN`. English/Chinese companion files share the same `document_id`, version, stable IDs, and flow semantics.
- A translated companion adds `translation_of: "<relative path to source>"`; either variant may list companion files under `translations`.
- Use an explicit identity only when it is known. Use `unspecified` rather than guessing an author or owner.
- `last_updated` describes the content update, not a validator run or formatting pass.
- `source_refs` should be specific enough for another collaborator to find the basis for the flow. It may be an empty list only when no source is available.

## Required document sections

### 1. Purpose and Scope

State the problem boundary, intended readers, included entry points, and important exclusions. Do not turn implementation speculation into scope.

### 2. Classification Defaults

Record team-level defaults only when a source establishes them. Entry-point rules override these defaults. If no cross-entry default exists, say that classification is defined per entry point.

### 3. Progress Overview

Use one row per entry point and include at least:

| ID | Entry Point | Types | Status | Owner | Last Updated | Open Items |
|---|---|---|---|---|---|---|
| EP-01 | Example | A, B | draft | unspecified | YYYY-MM-DD | 1 |

The table is a projection of the detailed sections, not an independently maintained opinion. Recalculate it after every material edit.

### 4. Entry Points

Use a stable heading and metadata block for every entry:

```markdown
### EP-01 — <Entry point name>

| Field | Value |
|---|---|
| Location | <where the entry appears> |
| Function | <what outcome it enables> |
| Trigger / Input | <event, payload, or user action> |
| Expected Output | <observable result> |
| Status | draft |
| Owner | unspecified |

**Classification Basis**

<Dimension, thresholds, precedence rules, and why they apply to this entry.>
```

Each entry point must have one or more locally scoped types. The labels need not be uniform across entry points.

```markdown
#### Type A — <Meaningful label>

**Definition**

<Positive criteria, relevant exclusions, data/history needs, complexity or cost signals, and expected response behavior when known.>

**Examples**

- <Representative request>
- <Boundary or counter-example when useful>

**Loop**

<Entry/Input> → <Interpretation or Routing Service> → <Execution Service> → <Verification or Output> → <User/System Output>
```

Type quality rules:

- Criteria must be usable for routing, not merely labels such as "simple" or "complex" without a decision rule.
- Types should be mutually distinguishable and cover the intended request space where the source supports that conclusion. Record overlaps or gaps as open decisions.
- Examples demonstrate the rule; they do not replace it.
- The main-path loop is ordered and names the actor or service responsible for each step.
- Show a database update, queue, notification, analytics event, or other side effect only when evidence supports it. Label asynchronous branches explicitly rather than placing them ambiguously in the synchronous path.
- Add optional branch/error notes or a step-detail table when the source contains meaningful alternate paths, failure handling, inputs/outputs, or verification gates. Do not fabricate them to make the document look complete.

### 5. Flow Visualizations

Include a `Flow Visualizations` or `流程可视化` section with at least one fenced Mermaid diagram. Every detailed `EP-NN` must be represented or explicitly marked as incomplete.

- Treat the detailed loops as the source of truth and the visual as a derived projection.
- Prefer a flowchart for request classification and ordered routing. Split dense flows instead of shrinking meaning into an unreadable diagram.
- Use stable camelCase node IDs and short labels. Localize labels for the document language while preserving stable `EP-NN` and Type identifiers.
- Show unresolved structure as an explicit TBD node or note; never infer a missing service, edge, or metric.
- Generate quantitative charts only when authoritative numeric data, units, and time boundaries exist.

Read [visualization-and-translation.md](visualization-and-translation.md) for rendering and bilingual synchronization rules.

### 6. Open Decisions and Assumptions

Use an actionable table:

| ID | Entry / Type | Kind | Question or Assumption | Owner | Blocking | Target Date |
|---|---|---|---|---|---|---|
| OD-01 | EP-01 / Type A | question | Is persistence required after output? | unspecified | yes | unspecified |

Use stable `OD-NN` identifiers. Mark assumptions clearly and link resolved items to the version/change-log entry that resolved them rather than silently deleting their history.

### 7. Change Log

Use newest-first order:

| Version | Date | Author | Scope | Change | Rationale / Source |
|---|---|---|---|---|---|
| 0.1.0 | YYYY-MM-DD | unspecified | initial | Created initial flow | <source> |

The current frontmatter version must appear exactly once as the newest version entry.

## Completeness checks

Before handoff, verify:

- Every progress row maps to one detailed `EP-NN` section and every detailed entry appears in the overview.
- Every entry has location, function, classification basis, at least one type, status, and owner.
- Every type has a decision-grade definition, examples, and an ordered loop.
- The visualization section contains Mermaid and covers every entry point without contradicting the detailed loops.
- Entry-specific thresholds override any team default explicitly.
- Open decisions capture material uncertainty; confirmed or implemented sections have no unresolved blocking TBDs.
- The document version, update date/byline, item states, and newest change-log row agree.
- A translated companion has the same `document_id`, version, entry/type IDs, open-decision IDs, and loop-node order as its source.
