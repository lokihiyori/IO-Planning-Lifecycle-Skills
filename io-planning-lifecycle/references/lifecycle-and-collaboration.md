# IO Flow Lifecycle and Collaboration Rules

Use this reference when modifying an existing IO Flow, changing lifecycle status, calculating a version, reconciling multiple contributors, or working in Git.

## Version rules

Use semantic versions and select the highest impact present in the accepted change set.

| Impact | Increment | Examples |
|---|---|---|
| Breaking contract | MAJOR | Remove or repurpose a stable entry/type ID; replace the global classification model; change a public flow contract in a way that requires downstream migration |
| Behavioral extension or routing change | MINOR | Add an entry/type; add or remove a loop node; change classification thresholds; alter routing, service responsibility, branch behavior, or integration semantics |
| Non-behavioral clarification | PATCH | Clarify wording or examples; correct source attribution; update owner or progress status; add evidence without changing flow semantics |
| No content change | none | Formatting, link normalization, validator execution, or an audit report with no document edit |

Start a new draft at `0.1.0` unless an existing repository convention or the user specifies another baseline. Do not infer that `confirmed` automatically means `1.0.0`; lifecycle status and version maturity are related but distinct decisions.

For a mixed change, bump once using the highest impact. Reset lower components in the normal semantic-version manner. Explain edge cases rather than forcing a convenient lower increment.

## Change-set protocol

Apply a material update as one coherent change set:

1. Identify the source decision and affected stable IDs.
2. Edit the affected entry/type/loop sections without reformatting unrelated sections.
3. Recalculate the progress overview and open-decision counts.
4. Resolve, retain, or add open decisions explicitly.
5. Choose the version impact and update frontmatter.
6. Add one newest-first change-log row with date, author, scope, change, and rationale/source.
7. Validate the document and summarize the semantic delta.

The change-log row explains product meaning; Git history records file mechanics. Keep both when Git is available.

## Visualization and translation lifecycle

Visualizations are derived projections of the authoritative entry/type loops. Regenerating a visual after a semantic flow change is part of that change set and uses the same version bump. Correcting layout or localization without changing interpreted behavior does not independently bump the IO Flow version.

English and Simplified Chinese companions share one semantic version. Update both variants in the same accepted change set when product meaning changes. A translation-only wording correction keeps the shared version when meaning is unchanged; record the edit in Git and, when useful to readers, in the change log without creating a duplicate current-version row.

If a translation is behind its source, do not label the pair synchronized. Surface the structural mismatch and complete or explicitly defer the translation before a confirmed or implemented handoff.

## Status rules

Allowed item and document statuses:

- `draft`: incomplete, inferred, or actively changing.
- `in_review`: complete enough for named reviewers, with review still pending.
- `confirmed`: the responsible decision-maker or team has explicitly accepted the flow.
- `implemented`: implementation evidence exists and matches the documented behavior.
- `deprecated`: no longer active; retain history and identify the replacement when known.

Never advance status based on polished wording alone. Record the evidence or source for `confirmed` and `implemented`. If a confirmed flow changes behavior, move the affected item back to `draft` or `in_review` unless the new behavior is also explicitly approved.

The document-level status must not hide less mature active content. Use the progress table for mixed item states and describe the aggregation rule when a repository has one.

## Attribution and time

- Use the contributor identity supplied by the user, repository, or authenticated environment.
- If identity is unavailable, use `unspecified` and expose it as a non-blocking metadata gap. Never invent a person or team.
- Use the actual current date in `YYYY-MM-DD` form.
- Attribute generated wording separately from the human/product source of the decision when that distinction matters.

## Concurrent and Git-based collaboration

Before editing:

- Read the current file and inspect local changes. Preserve unrelated uncommitted work.
- If remote synchronization is authorized, compare with the remote state before publishing. Do not pull, rebase, reset, or overwrite merely to make the branch clean.
- Reconcile entries and types by stable ID, not by heading order or text similarity alone.

When two sources change different stable items, merge both and update the shared overview once. When they change the same item incompatibly, present a concise conflict containing the current value, proposed values, affected routing, and decision owner. Do not silently choose one side.

No deletion is implicit. A removed entry/type or loop node must be named in the delta and change log. Preserve deprecated content when teams still need traceability; remove it only when the user or repository policy explicitly calls for removal.

Commit, push, pull-request, issue, and shared-file operations are external mutations. Perform them only when authorized by the current request, then report the branch/commit or equivalent result.

## Review checklist

- Does the semantic delta match the cited decision?
- Were stable IDs preserved or intentionally migrated?
- Is the version impact high enough for the most disruptive change?
- Are overview counts, statuses, dates, authors, and open decisions synchronized?
- Were same-item conflicts and deletions surfaced explicitly?
- Does the validator pass at the strictness appropriate to the lifecycle status?
- Are Mermaid projections and language companions synchronized with the authoritative loops and stable IDs?
