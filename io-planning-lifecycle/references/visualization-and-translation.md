# IO Flow Visualization and Translation Rules

Use this reference when generating or updating Mermaid diagrams, quantitative charts, or English/Simplified Chinese companion documents.

## Visualizations are projections

The detailed `Entry Points` section is authoritative. A diagram helps readers inspect the flow; it does not create product decisions.

1. Build the detailed entry/type loops first.
2. Choose the smallest visual that exposes the important routing relationship.
3. Generate the visual from confirmed loop nodes and branches.
4. Cross-check every edge against the detailed loop before handoff.

Every `EP-NN` must appear in `Flow Visualizations` / `流程可视化`. If an entry is incomplete, show one explicit TBD node rather than inventing a route.

## Diagram and chart selection

| Need | Preferred representation |
|---|---|
| Request classification, process, pipeline, or ordered service chain | Mermaid `flowchart` |
| Actor or service handoffs over time | Mermaid `sequenceDiagram` |
| Named lifecycle states and transitions | Mermaid `stateDiagram-v2` |
| Dated implementation schedule | Mermaid `gantt`, only with sourced dates |
| Progress or performance chart | A chart only with authoritative numeric values, units, and time boundaries |

Use `flowchart LR` for short sequential paths and `flowchart TD` for wide branching structures. Split a diagram when it approaches 25 nodes or when multiple branches become difficult to trace.

Mermaid requirements:

- Use camelCase node IDs without spaces; do not use reserved IDs such as `end`, `graph`, or `subgraph`.
- Keep labels short and wrap labels containing punctuation in quotes.
- Do not use emoji, HTML tags, or the literal `\n` escape in labels.
- Use normal arrows for the main path and dotted arrows only for evidenced asynchronous or optional behavior.
- Keep `EP-NN`, Type labels, and unresolved decision IDs visible in surrounding text or labels for traceability.
- Do not imply status through color alone. If styling is used, pair it with a readable label.

## Portable static rendering

For GitHub-hosted deliverables, prefer a repository-local SVG because GitHub's Mermaid rich renderer can be unavailable in embedded or restricted browsers.

1. Keep the diagram source as the canonical editable visual projection.
2. Export a semantically equivalent SVG, or PNG when SVG is not supported, into a nearby `assets/` directory.
3. Embed the static image with a relative Markdown link before the source block and write meaningful alt text that names the represented entry points.
4. Store editable source in a `mermaid-source` fence so GitHub displays it as code instead of invoking its rich renderer. Use a normal `mermaid` fence only when dynamic rendering is explicitly preferred and verified in the target environment.
5. Re-export and review the image whenever nodes, edges, labels, language, or unresolved states change. Confirm that text is readable, arrows are unambiguous, and TBD states remain visually explicit.

Do not reference a machine-local absolute path, data URL, temporary host, or session-bound URL. A static image is a delivery fallback, not a second source of truth.

## English and Simplified Chinese companions

Use separate Markdown files for the two language variants. This keeps review diffs readable and lets teams link directly to their preferred language.

Required invariants across a pair:

- Same `document_id`, semantic `version`, lifecycle `status`, and source meaning.
- Same entry-point order and `EP-NN` identifiers.
- Same Type identifiers and routing precedence.
- Same ordered loop-node count and service identity for each entry/type.
- Same `OD-NN` set and blocking state.
- Same visualization coverage, with localized user-facing labels.

Use `language: "en"` or `language: "zh-CN"`. Add `translation_of` to the translated companion and list the companion under `translations` when maintaining both files in one repository.

Translate headings, definitions, examples, decision text, and diagram labels. Preserve canonical service identity by writing a localized name followed by the established English name in parentheses when a translated label could be ambiguous, for example `验证服务（Verification Service）`. Do not translate stable IDs, version values, file references, API names, or code symbols.

## Translation workflow

1. Validate the source document first.
2. Copy its structure and metadata, then set the target `language` and `translation_of` values.
3. Translate prose and labels without adding examples, services, thresholds, owners, or decisions.
4. Compare entry/type IDs, loop order, decision IDs, and visualization coverage.
5. Run:

```bash
python scripts/validate_io_flow.py translated.md --translation-of source.md
```

Structural parity does not prove linguistic quality. For confirmed or implemented documents, obtain a bilingual domain review when terminology can affect routing, safety, legal meaning, or implementation responsibility.
