#!/usr/bin/env python3
"""Validate the structural and lifecycle invariants of an IO Flow Markdown file."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


ALLOWED_STATUSES = {"draft", "in_review", "confirmed", "implemented", "deprecated"}
SUPPORTED_LANGUAGES = {"en", "zh-CN"}
REQUIRED_FRONTMATTER = {
    "title",
    "document_id",
    "version",
    "status",
    "language",
    "owners",
    "last_updated",
    "last_updated_by",
    "source_refs",
}
REQUIRED_SECTIONS = {
    "purpose": {"purpose and scope", "目的与范围", "范围与目标"},
    "classification": {"classification defaults", "默认分级规则", "分级默认值"},
    "progress": {"progress overview", "进度总览"},
    "entries": {"entry points", "入口点"},
    "visualizations": {"flow visualizations", "流程可视化"},
    "decisions": {"open decisions and assumptions", "待确认事项与假设", "开放问题与假设"},
    "changelog": {"change log", "changelog", "变更记录"},
}


@dataclass(frozen=True)
class Issue:
    severity: str
    code: str
    message: str
    line: int | None = None


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def normalize_heading(value: str) -> str:
    value = re.sub(r"\s+#+\s*$", "", value.strip())
    value = re.sub(r"^\d+(?:\.\d+)*[.)]?\s*", "", value)
    return re.sub(r"\s+", " ", value).casefold()


def extract_frontmatter(text: str) -> tuple[dict[str, str], int, list[Issue]]:
    match = re.match(r"\A---\s*\n(?P<body>.*?)\n---\s*(?:\n|\Z)", text, re.DOTALL)
    if not match:
        return {}, 0, [Issue("error", "frontmatter.missing", "File must begin with YAML frontmatter.", 1)]

    fields: dict[str, str] = {}
    body = match.group("body")
    body_offset = match.start("body")
    issues: list[Issue] = []
    for item in re.finditer(r"(?m)^(?P<key>[A-Za-z_][A-Za-z0-9_-]*):(?:\s*(?P<value>.*))?$", body):
        key = item.group("key")
        if key in fields:
            issues.append(
                Issue(
                    "error",
                    "frontmatter.duplicate_key",
                    f"Frontmatter key '{key}' appears more than once.",
                    line_number(text, body_offset + item.start()),
                )
            )
        fields[key] = (item.group("value") or "").strip().strip('"\'')
    return fields, match.end(), issues


def section_headings(text: str) -> dict[str, tuple[int, str]]:
    found: dict[str, tuple[int, str]] = {}
    for match in re.finditer(r"(?m)^##\s+(?!#)(.+?)\s*$", text):
        found[normalize_heading(match.group(1))] = (match.start(), match.group(1).strip())
    return found


def find_required_section(
    headings: dict[str, tuple[int, str]], aliases: Iterable[str]
) -> tuple[int, str] | None:
    for alias in aliases:
        if alias.casefold() in headings:
            return headings[alias.casefold()]
    return None


def find_marker(block: str, aliases: Iterable[str]) -> re.Match[str] | None:
    names = "|".join(re.escape(alias) for alias in aliases)
    return re.search(rf"(?im)^\s*\*\*(?:{names})\*\*\s*:?[ \t]*$", block)


def validate_frontmatter(fields: dict[str, str]) -> list[Issue]:
    issues: list[Issue] = []
    for key in sorted(REQUIRED_FRONTMATTER - fields.keys()):
        issues.append(Issue("error", "frontmatter.required", f"Missing frontmatter key '{key}'.", 1))

    version = fields.get("version", "")
    if version and not re.fullmatch(r"(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)", version):
        issues.append(Issue("error", "frontmatter.version", f"Version '{version}' is not MAJOR.MINOR.PATCH.", 1))

    status = fields.get("status", "")
    if status and status not in ALLOWED_STATUSES:
        allowed = ", ".join(sorted(ALLOWED_STATUSES))
        issues.append(Issue("error", "frontmatter.status", f"Status '{status}' is invalid; use one of: {allowed}.", 1))

    language = fields.get("language", "")
    if language and language not in SUPPORTED_LANGUAGES:
        allowed = ", ".join(sorted(SUPPORTED_LANGUAGES))
        issues.append(Issue("error", "frontmatter.language", f"Language '{language}' is invalid; use one of: {allowed}.", 1))

    updated = fields.get("last_updated", "")
    if updated:
        try:
            dt.date.fromisoformat(updated)
        except ValueError:
            issues.append(Issue("error", "frontmatter.date", f"last_updated '{updated}' is not YYYY-MM-DD.", 1))
    return issues


def validate_sections(text: str) -> tuple[dict[str, tuple[int, str]], list[Issue]]:
    headings = section_headings(text)
    resolved: dict[str, tuple[int, str]] = {}
    issues: list[Issue] = []
    for key, aliases in REQUIRED_SECTIONS.items():
        found = find_required_section(headings, aliases)
        if found is None:
            issues.append(Issue("error", "section.required", f"Missing required section '{key}'."))
        else:
            resolved[key] = found
    return resolved, issues


def validate_entries(text: str, progress_start: int | None) -> list[Issue]:
    issues: list[Issue] = []
    entry_matches = list(re.finditer(r"(?m)^###\s+(EP-\d{2,})\b[^\n]*$", text))
    if not entry_matches:
        return [Issue("error", "entry.missing", "At least one '### EP-NN' entry point is required.")]

    ids = [match.group(1) for match in entry_matches]
    for entry_id in sorted({item for item in ids if ids.count(item) > 1}):
        issues.append(Issue("error", "entry.duplicate_id", f"Entry ID '{entry_id}' appears more than once."))

    progress_block = ""
    if progress_start is not None:
        next_section = re.search(r"(?m)^##\s+(?!#)", text[progress_start + 3 :])
        progress_end = progress_start + 3 + next_section.start() if next_section else len(text)
        progress_block = text[progress_start:progress_end]

    for index, match in enumerate(entry_matches):
        entry_id = match.group(1)
        end = entry_matches[index + 1].start() if index + 1 < len(entry_matches) else len(text)
        next_section = re.search(r"(?m)^##\s+(?!#)", text[match.end() : end])
        if next_section:
            end = match.end() + next_section.start()
        block = text[match.start() : end]
        base_line = line_number(text, match.start())

        for label, pattern in {
            "Location": r"(?im)^\|\s*(?:Location|位置)(?:\s*/\s*(?:Location|位置))?\s*\|",
            "Function": r"(?im)^\|\s*(?:Function|功能)(?:\s*/\s*(?:Function|功能))?\s*\|",
            "Status": r"(?im)^\|\s*(?:Status|状态)(?:\s*/\s*(?:Status|状态))?\s*\|",
            "Owner": r"(?im)^\|\s*(?:Owner|负责人)(?:\s*/\s*(?:Owner|负责人))?\s*\|",
        }.items():
            if not re.search(pattern, block):
                issues.append(Issue("error", "entry.field", f"{entry_id} is missing the '{label}' metadata row.", base_line))

        if not find_marker(block, {"Classification Basis", "分类依据", "分级标准"}):
            issues.append(Issue("error", "entry.classification", f"{entry_id} is missing an entry-specific classification basis.", base_line))

        type_matches = list(re.finditer(r"(?im)^####\s+(?:Type\s+|类型\s*)([A-Za-z0-9_-]+)\b[^\n]*$", block))
        if not type_matches:
            issues.append(Issue("error", "type.missing", f"{entry_id} must contain at least one type.", base_line))

        for type_index, type_match in enumerate(type_matches):
            type_id = type_match.group(1)
            type_end = type_matches[type_index + 1].start() if type_index + 1 < len(type_matches) else len(block)
            type_block = block[type_match.start() : type_end]
            type_line = base_line + block.count("\n", 0, type_match.start())

            if not find_marker(type_block, {"Definition", "定义"}):
                issues.append(Issue("error", "type.definition", f"{entry_id} / Type {type_id} is missing Definition.", type_line))
            if not find_marker(type_block, {"Examples", "Example", "示例"}):
                issues.append(Issue("error", "type.examples", f"{entry_id} / Type {type_id} is missing Examples.", type_line))
            loop_marker = find_marker(type_block, {"Loop", "处理链路", "服务链路"})
            if not loop_marker:
                issues.append(Issue("error", "type.loop", f"{entry_id} / Type {type_id} is missing Loop.", type_line))
            else:
                loop_body = type_block[loop_marker.end() :]
                next_marker = re.search(r"(?m)^\s*\*\*[^*]+\*\*", loop_body)
                if next_marker:
                    loop_body = loop_body[: next_marker.start()]
                if "→" not in loop_body and "->" not in loop_body:
                    issues.append(Issue("error", "type.loop_order", f"{entry_id} / Type {type_id} loop must contain an ordered arrow chain.", type_line))

        if progress_block and not re.search(rf"(?m)^\|\s*{re.escape(entry_id)}\s*\|", progress_block):
            issues.append(Issue("error", "progress.missing_entry", f"Progress Overview has no row for {entry_id}."))
    return issues


def get_section_block(text: str, start: int) -> str:
    next_section = re.search(r"(?m)^##\s+(?!#)", text[start + 3 :])
    end = start + 3 + next_section.start() if next_section else len(text)
    return text[start:end]


def validate_visualizations(text: str, sections: dict[str, tuple[int, str]]) -> list[Issue]:
    if "visualizations" not in sections:
        return []

    issues: list[Issue] = []
    start = sections["visualizations"][0]
    block = get_section_block(text, start)
    mermaid_blocks = re.findall(r"(?ms)^```mermaid(?:-source)?\s*\n(.*?)^```\s*$", block)
    if not mermaid_blocks:
        return [
            Issue(
                "error",
                "visualization.mermaid_missing",
                "Flow Visualizations must contain at least one fenced Mermaid or mermaid-source diagram.",
                line_number(text, start),
            )
        ]

    portable_sources = re.findall(r"(?ms)^```mermaid-source\s*\n(.*?)^```\s*$", block)
    static_images = re.findall(r"(?i)!\[[^\]]*\]\(([^)]+\.(?:svg|png))(?:\s+[^)]*)?\)", block)
    if portable_sources and not static_images:
        issues.append(
            Issue(
                "error",
                "visualization.static_missing",
                "A mermaid-source block requires an embedded repository-local SVG or PNG fallback.",
                line_number(text, start),
            )
        )

    supported = re.compile(r"^\s*(?:flowchart\s+(?:LR|RL|TB|TD)|sequenceDiagram|stateDiagram(?:-v2)?|erDiagram|gantt)\b")
    for diagram in mermaid_blocks:
        diagram_line = line_number(text, text.find(diagram, start))
        if not supported.search(diagram):
            issues.append(
                Issue(
                    "error",
                    "visualization.type",
                    "Mermaid diagram must use a supported flowchart, sequence, state, ER, or Gantt declaration.",
                    diagram_line,
                )
            )
        if "\\n" in diagram or re.search(r"<\/?[A-Za-z][^>]*>", diagram):
            issues.append(
                Issue(
                    "error",
                    "visualization.label_syntax",
                    "Mermaid labels must not contain literal \\n escapes or HTML tags.",
                    diagram_line,
                )
            )

    entry_ids = [match.group(1) for match in re.finditer(r"(?m)^###\s+(EP-\d{2,})\b", text)]
    for entry_id in entry_ids:
        if not re.search(rf"(?<![A-Za-z0-9-]){re.escape(entry_id)}(?![A-Za-z0-9-])", block):
            issues.append(
                Issue(
                    "error",
                    "visualization.missing_entry",
                    f"Flow Visualizations does not reference {entry_id}.",
                    line_number(text, start),
                )
            )
    return issues


def extract_flow_structure(text: str) -> list[tuple[str, list[tuple[str, int]]]]:
    structure: list[tuple[str, list[tuple[str, int]]]] = []
    entry_matches = list(re.finditer(r"(?m)^###\s+(EP-\d{2,})\b[^\n]*$", text))
    for index, entry_match in enumerate(entry_matches):
        end = entry_matches[index + 1].start() if index + 1 < len(entry_matches) else len(text)
        next_section = re.search(r"(?m)^##\s+(?!#)", text[entry_match.end() : end])
        if next_section:
            end = entry_match.end() + next_section.start()
        entry_block = text[entry_match.start() : end]
        type_matches = list(re.finditer(r"(?im)^####\s+(?:Type\s+|类型\s*)([A-Za-z0-9_-]+)\b[^\n]*$", entry_block))
        types: list[tuple[str, int]] = []
        for type_index, type_match in enumerate(type_matches):
            type_end = type_matches[type_index + 1].start() if type_index + 1 < len(type_matches) else len(entry_block)
            type_block = entry_block[type_match.start() : type_end]
            loop_marker = find_marker(type_block, {"Loop", "处理链路", "服务链路"})
            node_count = 0
            if loop_marker:
                loop_body = type_block[loop_marker.end() :]
                next_marker = re.search(r"(?m)^\s*(?:\*\*[^*]+\*\*|#{1,6}\s+)", loop_body)
                if next_marker:
                    loop_body = loop_body[: next_marker.start()]
                arrow = "→" if "→" in loop_body else "->" if "->" in loop_body else None
                if arrow:
                    node_count = len([node.strip() for node in loop_body.split(arrow) if node.strip()])
            types.append((type_match.group(1), node_count))
        structure.append((entry_match.group(1), types))
    return structure


def extract_decision_ids(text: str) -> list[str]:
    return [match.group(1) for match in re.finditer(r"(?m)^\|\s*(OD-\d{2,})\s*\|", text)]


def validate_translation(target_path: Path, source_path: Path) -> list[Issue]:
    issues: list[Issue] = []
    try:
        target_text = target_path.read_text(encoding="utf-8-sig")
        source_text = source_path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError) as exc:
        return [Issue("error", "translation.read", f"Cannot compare translation pair: {exc}")]

    target_fields, _, _ = extract_frontmatter(target_text)
    source_fields, _, _ = extract_frontmatter(source_text)

    for key in ("document_id", "version", "status"):
        if target_fields.get(key) != source_fields.get(key):
            issues.append(
                Issue(
                    "error",
                    f"translation.{key}",
                    f"Translation and source must use the same {key}; got '{target_fields.get(key)}' and '{source_fields.get(key)}'.",
                    1,
                )
            )

    language_pair = {target_fields.get("language"), source_fields.get("language")}
    if language_pair != SUPPORTED_LANGUAGES:
        issues.append(
            Issue(
                "error",
                "translation.language_pair",
                "Translation comparison requires one 'en' document and one 'zh-CN' document.",
                1,
            )
        )

    translation_ref = target_fields.get("translation_of", "")
    if not translation_ref:
        issues.append(Issue("error", "translation.reference", "Translated document must define frontmatter 'translation_of'.", 1))
    else:
        resolved_ref = (target_path.parent / translation_ref).resolve()
        if resolved_ref != source_path.resolve():
            issues.append(
                Issue(
                    "error",
                    "translation.reference",
                    f"translation_of resolves to '{resolved_ref}', not the supplied source '{source_path.resolve()}'.",
                    1,
                )
            )

    target_structure = extract_flow_structure(target_text)
    source_structure = extract_flow_structure(source_text)
    target_entries = [entry_id for entry_id, _ in target_structure]
    source_entries = [entry_id for entry_id, _ in source_structure]
    if target_entries != source_entries:
        issues.append(
            Issue(
                "error",
                "translation.entry_structure",
                f"Entry-point order differs; translation has {target_entries}, source has {source_entries}.",
            )
        )

    target_map = dict(target_structure)
    source_map = dict(source_structure)
    for entry_id in sorted(target_map.keys() & source_map.keys()):
        target_types = target_map[entry_id]
        source_types = source_map[entry_id]
        target_type_ids = [type_id for type_id, _ in target_types]
        source_type_ids = [type_id for type_id, _ in source_types]
        if target_type_ids != source_type_ids:
            issues.append(
                Issue(
                    "error",
                    "translation.type_structure",
                    f"{entry_id} type order differs; translation has {target_type_ids}, source has {source_type_ids}.",
                )
            )
        target_counts = dict(target_types)
        source_counts = dict(source_types)
        for type_id in sorted(target_counts.keys() & source_counts.keys()):
            if target_counts[type_id] != source_counts[type_id]:
                issues.append(
                    Issue(
                        "error",
                        "translation.loop_structure",
                        f"{entry_id} / Type {type_id} loop has {target_counts[type_id]} node(s) in the translation and {source_counts[type_id]} in the source.",
                    )
                )

    target_decisions = extract_decision_ids(target_text)
    source_decisions = extract_decision_ids(source_text)
    if target_decisions != source_decisions:
        issues.append(
            Issue(
                "error",
                "translation.decision_structure",
                f"Open-decision IDs differ; translation has {target_decisions}, source has {source_decisions}.",
            )
        )

    target_diagrams = len(re.findall(r"(?m)^```mermaid(?:-source)?\s*$", target_text))
    source_diagrams = len(re.findall(r"(?m)^```mermaid(?:-source)?\s*$", source_text))
    if target_diagrams != source_diagrams:
        issues.append(
            Issue(
                "error",
                "translation.visualization_structure",
                f"Mermaid diagram count differs; translation has {target_diagrams}, source has {source_diagrams}.",
            )
        )
    target_static_images = len(re.findall(r"(?i)!\[[^\]]*\]\([^)]+\.(?:svg|png)(?:\s+[^)]*)?\)", target_text))
    source_static_images = len(re.findall(r"(?i)!\[[^\]]*\]\([^)]+\.(?:svg|png)(?:\s+[^)]*)?\)", source_text))
    if target_static_images != source_static_images:
        issues.append(
            Issue(
                "error",
                "translation.static_visualization_structure",
                f"Static visualization count differs; translation has {target_static_images}, source has {source_static_images}.",
            )
        )
    return issues


def validate_lifecycle(text: str, fields: dict[str, str], sections: dict[str, tuple[int, str]]) -> list[Issue]:
    issues: list[Issue] = []
    version = fields.get("version")
    if version and "changelog" in sections:
        start = sections["changelog"][0]
        end_match = re.search(r"(?m)^##\s+(?!#)", text[start + 3 :])
        end = start + 3 + end_match.start() if end_match else len(text)
        changelog = text[start:end]
        if len(re.findall(rf"(?<![0-9.]){re.escape(version)}(?![0-9.])", changelog)) != 1:
            issues.append(Issue("error", "changelog.current_version", f"Change Log must contain current version '{version}' exactly once."))

    tbd_matches = list(re.finditer(r"(?i)(?:\[\s*)?TBD\b", text))
    if tbd_matches:
        status = fields.get("status")
        severity = "error" if status in {"confirmed", "implemented"} else "warning"
        issues.append(
            Issue(
                severity,
                "lifecycle.tbd",
                f"Document contains {len(tbd_matches)} unresolved TBD marker(s).",
                line_number(text, tbd_matches[0].start()),
            )
        )
    return issues


def validate(path: Path, strict: bool = False) -> list[Issue]:
    try:
        text = path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError) as exc:
        return [Issue("error", "file.read", f"Cannot read '{path}': {exc}")]

    fields, _, issues = extract_frontmatter(text)
    issues.extend(validate_frontmatter(fields))
    sections, section_issues = validate_sections(text)
    issues.extend(section_issues)
    progress_start = sections.get("progress", (None, ""))[0]
    issues.extend(validate_entries(text, progress_start))
    issues.extend(validate_visualizations(text, sections))
    issues.extend(validate_lifecycle(text, fields, sections))

    if strict:
        issues = [
            Issue("error", issue.code, issue.message, issue.line) if issue.severity == "warning" else issue
            for issue in issues
        ]
    return issues


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("document", type=Path, help="IO Flow Markdown file to validate")
    parser.add_argument("--strict", action="store_true", help="Treat warnings, including unresolved TBDs, as errors")
    parser.add_argument("--json", action="store_true", dest="as_json", help="Emit machine-readable JSON")
    parser.add_argument(
        "--translation-of",
        type=Path,
        help="Compare this document with its English or Simplified Chinese source",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    issues = validate(args.document, strict=args.strict)
    if args.translation_of:
        source_issues = validate(args.translation_of, strict=args.strict)
        issues.extend(
            Issue(
                issue.severity,
                f"translation.source.{issue.code}",
                f"Source '{args.translation_of}': {issue.message}",
                issue.line,
            )
            for issue in source_issues
        )
        issues.extend(validate_translation(args.document, args.translation_of))
    errors = sum(issue.severity == "error" for issue in issues)
    warnings = sum(issue.severity == "warning" for issue in issues)

    if args.as_json:
        print(
            json.dumps(
                {
                    "path": str(args.document),
                    "translation_of": str(args.translation_of) if args.translation_of else None,
                    "valid": errors == 0,
                    "errors": errors,
                    "warnings": warnings,
                    "issues": [asdict(issue) for issue in issues],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    elif issues:
        for issue in issues:
            location = f":{issue.line}" if issue.line else ""
            print(f"{args.document}{location}: {issue.severity.upper()} {issue.code}: {issue.message}")
        print(f"Validation finished with {errors} error(s) and {warnings} warning(s).")
    else:
        print(f"{args.document}: valid IO Flow specification")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
