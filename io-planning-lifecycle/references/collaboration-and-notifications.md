# Collaboration, Synchronization, and Notification Rules

Use this reference in **Sync** or **Watch** mode, before editing a GitHub-tracked IO Flow, or when multiple contributors may be working concurrently.

## Recommended collaboration model

GitHub is the shared source of truth. Contributors work on branches or pull requests, while the default branch represents the latest accepted version. The IO Flow frontmatter, progress overview, and change log explain product state; Git commits and pull requests provide exact file history, review notifications, and authorship evidence.

This is optimistic concurrency, not character-by-character co-editing. Near-real-time awareness requires an active watcher, a scheduled Codex heartbeat, or a team notification integration. Do not claim that merely installing the Skill creates background notifications.

## Sync-before-write protocol

For any shared update:

1. Resolve the repository, branch, document path, and current remote commit. Treat that commit as `base_revision` for the work session.
2. Fetch or read the latest remote document before editing. Compare its `document_id`, semantic version, stable IDs, and relevant loop nodes with the local or supplied copy.
3. If the remote advanced since the contributor's copy, summarize intervening commits and semantic changes before applying the new request.
4. Merge non-overlapping stable-ID changes. For incompatible changes to the same Entry, Type, loop edge, decision, or status, stop and present the conflict; never use last-write-wins.
5. Immediately before publishing, check the remote head again. If it differs from `base_revision`, re-run reconciliation against the new head.
6. Publish through a branch/pull request by default for team-owned documents. Direct updates to the default branch require explicit authorization and repository policy support.

A successful fetch is not permission to push, merge, message teammates, or change repository settings.

## Sync mode

**Sync** is a one-time update discovery pass. It reports:

- current and previous commit/blob SHAs;
- commit author, timestamp, message, and URL when available;
- old and new semantic versions;
- affected `EP-NN`, Type, and `OD-NN` identifiers found in the diff;
- whether the local contributor can fast-forward, needs a semantic merge, or has a same-item conflict.

Invoke it with:

```text
Use $io-planning-lifecycle in Sync mode for examples/topogrow-io-flow.md. Check GitHub main, show what changed since my last check, and do not modify the document.
```

The bundled checker provides the deterministic detection layer:

```bash
python io-planning-lifecycle/scripts/check_io_flow_updates.py \
  --repo lokihiyori/IO-Planning-Lifecycle-Skills \
  --path examples/topogrow-io-flow.md \
  --ref main
```

The first run records a local baseline in `.io-flow-sync/`. Later runs emit a unified diff and change metadata only when the remote file changes. Use `--json` for automation.

## Watch mode

**Watch** repeatedly performs Sync and notifies only when the file's remote blob SHA changes.

When the host provides recurring automations, create a thread heartbeat at the user-selected cadence. The heartbeat prompt must name the repository, branch, document paths, notification conditions, and the rule that unchanged checks stay silent. Each teammate who wants a Codex notification must create or subscribe to their own watcher.

When recurring automations are unavailable, a contributor may explicitly start the local watcher:

```bash
python io-planning-lifecycle/scripts/check_io_flow_updates.py \
  --repo lokihiyori/IO-Planning-Lifecycle-Skills \
  --path examples/topogrow-io-flow.md \
  --ref main \
  --watch-seconds 300
```

Do not start an indefinite watcher during an ordinary Create, Update, Translate, or Audit request. The user must explicitly request Watch mode. A terminal watcher stops with `Ctrl+C` and only notifies while that process is running.

## Team-wide push notifications

For instant notifications independent of Codex sessions, connect GitHub push/pull-request webhooks to the team's chosen Slack, Microsoft Teams, email, or incident channel. This requires a destination, repository administration permission, and usually a secret or installed GitHub App. Ask for the channel and authorization at configuration time; never invent a destination, expose a webhook URL, or commit a secret.

Pull-request review requests and GitHub subscriptions are the recommended no-custom-infrastructure team notification path. Repository administrators can add `CODEOWNERS` after the responsible users or teams are known.
