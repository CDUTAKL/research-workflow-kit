"""Audit research skills for missing files and outdated workflow assumptions."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


REFERENCE_RE = re.compile(r"(?:^|[`'\s(])((?:references|scripts|examples|templates)/[A-Za-z0-9_./-]+)")
OUTDATED_PATTERNS = {
    "mobaxterm_required": re.compile(r"\bMobaXterm\b", re.IGNORECASE),
    "canva_default": re.compile(r"\bCanva\b.*\b(default|required|primary)\b", re.IGNORECASE),
    "word_required": re.compile(r"\bMicrosoft Word\b.*\b(required|default|must)\b", re.IGNORECASE),
    "local_gpu_required": re.compile(r"\blocal(?:_mac)?\b.*\bGPU\b.*\b(required|assumed|default)\b", re.IGNORECASE),
}
SAFE_ASSUMPTION_PHRASES = (
    "not assumed",
    "do not assume",
    "optional",
    "windows-only",
    "not treat",
    "no gpu",
    "gpu work is not assumed",
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def referenced_paths(text: str) -> list[str]:
    refs: list[str] = []
    for match in REFERENCE_RE.findall(text):
        clean = match.rstrip(".,);:")
        if clean not in refs:
            refs.append(clean)
    return refs


def scan_outdated_assumptions(root: Path) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    scan_roots = [root / "README.md", root / "docs", root / "skills"]
    files: list[Path] = []
    for item in scan_roots:
        if item.is_file():
            files.append(item)
        elif item.exists():
            files.extend(path for path in item.rglob("*.md") if ".git" not in path.parts)
    for path in files:
        rel = path.relative_to(root).as_posix()
        for line_no, line in enumerate(read_text(path).splitlines(), start=1):
            for key, pattern in OUTDATED_PATTERNS.items():
                lowered = line.lower()
                if pattern.search(line) and not any(phrase in lowered for phrase in SAFE_ASSUMPTION_PHRASES):
                    findings.append({"type": key, "path": rel, "line": str(line_no), "text": line.strip()})
    return findings


def audit_repo(root: Path) -> dict[str, object]:
    root = root.resolve()
    skills_dir = root / "skills"
    missing_skill_files: list[str] = []
    broken_references: list[dict[str, str]] = []
    missing_scripts: list[dict[str, str]] = []

    skill_dirs = sorted(path for path in skills_dir.iterdir() if path.is_dir()) if skills_dir.exists() else []
    for skill_dir in skill_dirs:
        skill_md = skill_dir / "SKILL.md"
        skill_name = skill_dir.name
        if not skill_md.exists():
            missing_skill_files.append(skill_name)
            continue
        text = read_text(skill_md)
        for rel_ref in referenced_paths(text):
            candidate = skill_dir / rel_ref
            root_candidate = root / rel_ref
            if candidate.exists() or root_candidate.exists():
                continue
            issue = {"skill": skill_name, "path": rel_ref}
            if rel_ref.startswith("scripts/"):
                missing_scripts.append(issue)
            else:
                broken_references.append(issue)

    outdated = scan_outdated_assumptions(root)
    summary = {
        "totalSkills": len(skill_dirs),
        "missingSkillFiles": len(missing_skill_files),
        "brokenReferences": len(broken_references),
        "missingScripts": len(missing_scripts),
        "outdatedAssumptions": len(outdated),
    }
    return {
        "summary": summary,
        "missingSkillFiles": missing_skill_files,
        "brokenReferences": broken_references,
        "missingScripts": missing_scripts,
        "outdatedAssumptions": outdated,
    }


def render_report(result: dict[str, object]) -> str:
    summary = result["summary"]  # type: ignore[index]
    lines = [
        "# Skill Audit Report",
        "",
        "## Summary",
        "",
        f"- total skills: {summary['totalSkills']}",
        f"- missing SKILL.md files: {summary['missingSkillFiles']}",
        f"- broken references: {summary['brokenReferences']}",
        f"- missing scripts: {summary['missingScripts']}",
        f"- outdated assumptions: {summary['outdatedAssumptions']}",
        "",
    ]
    sections = [
        ("Missing SKILL.md", result["missingSkillFiles"]),
        ("Broken References", result["brokenReferences"]),
        ("Missing Scripts", result["missingScripts"]),
        ("Outdated Assumptions", result["outdatedAssumptions"]),
    ]
    for title, values in sections:
        lines.extend([f"## {title}", ""])
        if values:
            for item in values:  # type: ignore[assignment]
                if isinstance(item, dict):
                    lines.append("- " + " | ".join(f"{key}={value}" for key, value in item.items()))
                else:
                    lines.append(f"- {item}")
        else:
            lines.append("- none")
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit bundled research skills for structural consistency.")
    parser.add_argument("--root", default=".", help="Repository root to audit.")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of a Markdown-like report.")
    parser.add_argument("--write-report", nargs="?", const="docs/thesis/skill-audit-report.md")
    parser.add_argument("--warn-only", action="store_true")
    args = parser.parse_args()

    root = Path(args.root)
    result = audit_repo(root)
    summary = result["summary"]  # type: ignore[index]
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(render_report(result).rstrip())

    if args.write_report:
        out = root / args.write_report
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render_report(result), encoding="utf-8")
        print(f"\nwrote skill audit report: {out}")

    has_errors = summary["missingSkillFiles"] or summary["brokenReferences"] or summary["missingScripts"]  # type: ignore[index]
    if has_errors and not args.warn_only:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
