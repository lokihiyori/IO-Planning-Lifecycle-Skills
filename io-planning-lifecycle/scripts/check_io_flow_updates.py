#!/usr/bin/env python3
"""Detect remote IO Flow changes and maintain a local collaboration baseline."""

from __future__ import annotations

import argparse
import base64
import datetime as dt
import difflib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path


USER_AGENT = "io-planning-lifecycle-sync/1.0"
ID_PATTERN = re.compile(r"\b(?:EP-\d{2,}|OD-\d{2,}|Type\s+[A-Za-z0-9_-]+)\b", re.IGNORECASE)
VERSION_PATTERN = re.compile(r"(?m)^version:\s*[\"']?([^\s\"']+)")


@dataclass(frozen=True)
class Snapshot:
    commit_sha: str
    blob_sha: str
    version: str | None
    author: str
    timestamp: str
    message: str
    commit_url: str
    content: str


def api_get(url: str, token: str | None, timeout: int) -> object:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": USER_AGENT,
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.load(response)


def encode_path(path: str) -> str:
    return urllib.parse.quote(path.strip("/"), safe="/")


def latest_snapshot(repo: str, path: str, ref: str, token: str | None, timeout: int) -> Snapshot:
    query = urllib.parse.urlencode({"path": path, "sha": ref, "per_page": 1})
    commits = api_get(f"https://api.github.com/repos/{repo}/commits?{query}", token, timeout)
    if not isinstance(commits, list) or not commits:
        raise RuntimeError(f"No commit found for {repo}:{ref}:{path}")
    commit = commits[0]
    commit_sha = str(commit["sha"])
    details = commit.get("commit", {})
    author = (commit.get("author") or {}).get("login") or (details.get("author") or {}).get("name") or "unknown"
    timestamp = (details.get("author") or {}).get("date") or "unknown"
    message = str(details.get("message") or "").splitlines()[0]
    commit_url = str(commit.get("html_url") or f"https://github.com/{repo}/commit/{commit_sha}")

    content_payload = api_get(
        f"https://api.github.com/repos/{repo}/contents/{encode_path(path)}?ref={urllib.parse.quote(commit_sha)}",
        token,
        timeout,
    )
    if not isinstance(content_payload, dict) or content_payload.get("type") != "file":
        raise RuntimeError(f"Path is not a file: {path}")
    encoded = str(content_payload.get("content") or "").replace("\n", "")
    content = base64.b64decode(encoded).decode("utf-8")
    version_match = VERSION_PATTERN.search(content)
    return Snapshot(
        commit_sha=commit_sha,
        blob_sha=str(content_payload.get("sha") or ""),
        version=version_match.group(1) if version_match else None,
        author=str(author),
        timestamp=str(timestamp),
        message=message,
        commit_url=commit_url,
        content=content,
    )


def snapshot_at_commit(repo: str, path: str, commit_sha: str, token: str | None, timeout: int) -> str | None:
    try:
        payload = api_get(
            f"https://api.github.com/repos/{repo}/contents/{encode_path(path)}?ref={urllib.parse.quote(commit_sha)}",
            token,
            timeout,
        )
        if isinstance(payload, dict) and payload.get("type") == "file":
            encoded = str(payload.get("content") or "").replace("\n", "")
            return base64.b64decode(encoded).decode("utf-8")
    except (RuntimeError, UnicodeDecodeError, urllib.error.HTTPError, urllib.error.URLError):
        return None
    return None


def default_state_file(repo: str, path: str) -> Path:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", f"{repo}--{path}").strip("-")
    return Path(".io-flow-sync") / f"{slug}.json"


def load_state(path: Path) -> dict[str, object] | None:
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else None


def save_state(path: Path, repo: str, document_path: str, ref: str, snapshot: Snapshot) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "repo": repo,
        "path": document_path,
        "ref": ref,
        "last_commit_sha": snapshot.commit_sha,
        "last_blob_sha": snapshot.blob_sha,
        "last_version": snapshot.version,
        "checked_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_change(repo: str, path: str, previous: dict[str, object], current: Snapshot, old_content: str | None) -> dict[str, object]:
    previous_commit = str(previous.get("last_commit_sha") or "")
    previous_version = previous.get("last_version")
    diff_lines: list[str] = []
    if old_content is not None:
        diff_lines = list(
            difflib.unified_diff(
                old_content.splitlines(),
                current.content.splitlines(),
                fromfile=f"{path}@{previous_commit[:12]}",
                tofile=f"{path}@{current.commit_sha[:12]}",
                lineterm="",
            )
        )
    changed_text = "\n".join(
        line[1:] if line.startswith(("+", "-", " ")) else line
        for line in diff_lines
        if not line.startswith(("+++", "---", "@@"))
    )
    return {
        "status": "changed",
        "repo": repo,
        "path": path,
        "previous_commit_sha": previous_commit or None,
        "current_commit_sha": current.commit_sha,
        "previous_blob_sha": previous.get("last_blob_sha"),
        "current_blob_sha": current.blob_sha,
        "previous_version": previous_version,
        "current_version": current.version,
        "author": current.author,
        "timestamp": current.timestamp,
        "message": current.message,
        "commit_url": current.commit_url,
        "compare_url": f"https://github.com/{repo}/compare/{previous_commit}...{current.commit_sha}" if previous_commit else None,
        "affected_ids": sorted(set(ID_PATTERN.findall(changed_text)), key=str.casefold),
        "diff": "\n".join(diff_lines),
    }


def check_once(args: argparse.Namespace) -> tuple[dict[str, object], Snapshot]:
    token = os.environ.get("GITHUB_TOKEN")
    current = latest_snapshot(args.repo, args.path, args.ref, token, args.timeout)
    state_path = Path(args.state_file) if args.state_file else default_state_file(args.repo, args.path)
    previous = load_state(state_path)

    if previous is None:
        result: dict[str, object] = {
            "status": "baseline_initialized",
            "repo": args.repo,
            "path": args.path,
            "current_commit_sha": current.commit_sha,
            "current_blob_sha": current.blob_sha,
            "current_version": current.version,
            "commit_url": current.commit_url,
        }
    elif str(previous.get("last_blob_sha") or "") == current.blob_sha:
        result = {
            "status": "unchanged",
            "repo": args.repo,
            "path": args.path,
            "current_commit_sha": current.commit_sha,
            "current_blob_sha": current.blob_sha,
            "current_version": current.version,
        }
    else:
        old_commit = str(previous.get("last_commit_sha") or "")
        old_content = snapshot_at_commit(args.repo, args.path, old_commit, token, args.timeout) if old_commit else None
        result = build_change(args.repo, args.path, previous, current, old_content)

    if not args.no_record:
        save_state(state_path, args.repo, args.path, args.ref, current)
    result["state_file"] = str(state_path)
    return result, current


def print_result(result: dict[str, object], as_json: bool, quiet_unchanged: bool = False) -> None:
    if as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    status = str(result["status"])
    if status == "unchanged" and quiet_unchanged:
        return
    if status == "baseline_initialized":
        print(f"Baseline initialized: {result['path']} @ {str(result['current_commit_sha'])[:12]} (version {result.get('current_version') or 'unknown'})")
    elif status == "unchanged":
        print(f"No remote change: {result['path']} @ {str(result['current_commit_sha'])[:12]}")
    else:
        print("\a", end="")
        print(f"Remote IO Flow changed: {result['path']}")
        print(f"  commit: {str(result['previous_commit_sha'])[:12]} -> {str(result['current_commit_sha'])[:12]}")
        print(f"  version: {result.get('previous_version') or 'unknown'} -> {result.get('current_version') or 'unknown'}")
        print(f"  author/date: {result['author']} / {result['timestamp']}")
        print(f"  message: {result['message']}")
        if result.get("affected_ids"):
            print(f"  affected IDs: {', '.join(result['affected_ids'])}")
        print(f"  commit: {result['commit_url']}")
        if result.get("compare_url"):
            print(f"  compare: {result['compare_url']}")
        if result.get("diff"):
            print("\n" + str(result["diff"]))


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, help="GitHub repository in owner/name form")
    parser.add_argument("--path", required=True, help="Repository-relative IO Flow path")
    parser.add_argument("--ref", default="main", help="Branch or ref to monitor (default: main)")
    parser.add_argument("--state-file", help="Local JSON baseline path (default: .io-flow-sync/...)")
    parser.add_argument("--watch-seconds", type=int, help="Repeat checks at this interval; 300 is recommended")
    parser.add_argument("--timeout", type=int, default=15, help="GitHub API request timeout in seconds")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    parser.add_argument("--no-record", action="store_true", help="Do not update the local baseline")
    args = parser.parse_args(argv)
    if not re.fullmatch(r"[^/\s]+/[^/\s]+", args.repo):
        parser.error("--repo must use owner/name form")
    if args.watch_seconds is not None and args.watch_seconds < 60:
        parser.error("--watch-seconds must be at least 60 to respect GitHub API limits")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        if args.watch_seconds is None:
            result, _ = check_once(args)
            print_result(result, args.json)
            return 3 if result["status"] == "changed" else 0

        first = True
        while True:
            result, _ = check_once(args)
            print_result(result, args.json, quiet_unchanged=not first)
            first = False
            time.sleep(args.watch_seconds)
    except KeyboardInterrupt:
        print("Watcher stopped.", file=sys.stderr)
        return 0
    except (RuntimeError, UnicodeDecodeError, json.JSONDecodeError, urllib.error.HTTPError, urllib.error.URLError) as exc:
        print(f"Update check failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
