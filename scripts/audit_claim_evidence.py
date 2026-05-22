"""
Claim-evidence cross-check script.

Run before any writing phase (Stage 10). Exit code != 0 means blocking issues
that must be resolved before proceeding to paper writing.

Checks performed:
  1. Every claim must reference at least one piece of evidence.
  2. Every evidence reference must correspond to a real experiment entry.
  3. A claim backed only by failed experiments is unsupported.
  4. (Best-effort) Numeric consistency between claimed numbers and experiment results.

Usage:
    python scripts/audit_claim_evidence.py [--warn-only] [--quiet]

    --warn-only   Treat errors as warnings; always exit 0.
    --quiet       Silent on pass; concise one-liners on issues.  Designed for
                  Stop-hook auto-execution after Stage 9.
"""
import re
import sys
from pathlib import Path

THESIS_DIR = Path("docs/thesis")


# ---------------------------------------------------------------------------
# Parsers
# ---------------------------------------------------------------------------

def parse_claim_evidence_map(text: str) -> list[dict]:
    """Extract all claims and their evidence references from claim-evidence-map.md.

    Expected table format:
        | claim_id | claim_text | evidence_refs | status |
    where evidence_refs may contain one or more comma-separated references like
    "E3.1, E3.2" or experiment IDs like "EXP-001, EXP-002".
    """
    claims: list[dict] = []
    pattern = re.compile(
        r'^\|\s*(C\d+\.\d+)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|',
        re.MULTILINE,
    )
    for match in pattern.finditer(text):
        claim_id = match.group(1).strip()
        claim_text = match.group(2).strip()
        evidence_refs = [
            e.strip() for e in match.group(3).split(",") if e.strip()
        ]
        claims.append(
            {
                "id": claim_id,
                "text": claim_text,
                "evidence_refs": evidence_refs,
            }
        )
    return claims


def parse_experiment_log(text: str) -> dict[str, dict]:
    """Extract all experiment entries and their success/failure status.

    Each experiment block starts with '## EXP-' and contains a line like:
        - **状态**: [成功] / [失败]
    """
    experiments: dict[str, dict] = {}
    blocks = re.split(r"\n## EXP-", text)
    for block in blocks[1:]:  # first split piece is preamble
        exp_id = "EXP-" + block.split("\n", 1)[0].strip()
        status_match = re.search(
            r"\*\*状态\*\*\s*:\s*(.+?)$", block, re.MULTILINE
        )
        status = status_match.group(1).strip() if status_match else "unknown"
        experiments[exp_id] = {
            "success": "[成功]" in status,
            "raw": block,
        }
    return experiments


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def check_orphan_claims(
    claims: list[dict], _experiments: dict[str, dict]
) -> list[str]:
    """Check 1: Every claim must reference at least one piece of evidence."""
    return [c["id"] for c in claims if not c["evidence_refs"]]


def check_missing_evidence(
    claims: list[dict], experiments: dict[str, dict]
) -> list[str]:
    """Check 2: Every evidence ref must correspond to a known experiment."""
    all_refs: set[str] = set()
    for c in claims:
        all_refs.update(c["evidence_refs"])
    return sorted(ref for ref in all_refs if ref not in experiments)


def check_unsupported_claims(
    claims: list[dict], experiments: dict[str, dict]
) -> list[str]:
    """Check 3: A claim backed *only* by failed experiments is unsupported."""
    unsupported: list[str] = []
    for c in claims:
        refs = c["evidence_refs"]
        if not refs:
            continue
        # If no ref is mapped to a known experiment, skip (caught by check 2).
        mapped = [r for r in refs if r in experiments]
        if not mapped:
            continue
        all_failed = all(not experiments[r]["success"] for r in mapped)
        if all_failed:
            unsupported.append(c["id"])
    return unsupported


def check_numeric_consistency(
    claims: list[dict], experiments: dict[str, dict]
) -> list[str]:
    """Check 4 (best-effort): Compare claimed percentages/accuracies against
    numbers found in experiment blocks.

    This check issues *warnings* rather than errors because natural-language
    number extraction is inherently imprecise.
    """
    warnings: list[str] = []
    for c in claims:
        raw_text = c["text"].replace(" ", "")
        pct_matches = re.findall(r"(\d+\.?\d*)\s*%", raw_text)
        if not pct_matches:
            continue
        claimed_pct = max(float(n) for n in pct_matches)
        for ref in c["evidence_refs"]:
            if ref not in experiments:
                continue
            exp_text = experiments[ref]["raw"]
            exp_numbers = re.findall(r"acc[=_]\s*(\d+\.\d+)", exp_text)
            if exp_numbers:
                exp_value = max(float(n) for n in exp_numbers)
                if claimed_pct > exp_value * 100 + 5:
                    warnings.append(
                        f"{c['id']}: claims ~{claimed_pct:.1f}% but "
                        f"experiment {ref} shows {exp_value * 100:.1f}% "
                        f"— possible over-claim"
                    )
    return warnings


def check_data_version_consistency(
    experiments: dict[str, dict]
) -> list[str]:
    """Check 5: Same data_version name, different hash → data drifted."""
    warnings: list[str] = []
    by_version: dict[str, dict[str, list[str]]] = {}
    for exp_id, exp in experiments.items():
        ver_match = re.search(
            r"\*\*数据版本\*\*\s*:\s*(.+?)$", exp["raw"], re.MULTILINE
        )
        hash_match = re.search(
            r"\*\*数据哈希\*\*\s*:\s*`?(.+?)`?\s*$", exp["raw"], re.MULTILINE
        )
        if not ver_match:
            continue
        ver = ver_match.group(1).strip()
        h = hash_match.group(1).strip() if hash_match else "N/A"
        if "N/A" in h:
            continue  # hash not recorded, can't check
        by_version.setdefault(ver, {}).setdefault(h, []).append(exp_id)

    for ver, hash_groups in by_version.items():
        if len(hash_groups) > 1:
            ids_list = [ids for ids in hash_groups.values()]
            warnings.append(
                f"Data version '{ver}' has {len(hash_groups)} different hashes "
                f"across experiments: {ids_list} — results may not be comparable"
            )
    return warnings


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    warn_only = "--warn-only" in sys.argv
    quiet = "--quiet" in sys.argv
    errors: list[str] = []
    warnings: list[str] = []

    cmap_path = THESIS_DIR / "claim-evidence-map.md"
    elog_path = THESIS_DIR / "experiment-log.md"

    # --- In quiet mode, silently skip if claim-evidence-map doesn't exist yet ---
    if not cmap_path.exists():
        if quiet:
            sys.exit(0)
        print(f"ERROR: {cmap_path} not found")
        sys.exit(1)

    claims_text = cmap_path.read_text(encoding="utf-8")
    claims = parse_claim_evidence_map(claims_text)

    # --- Load experiment log ---
    experiments: dict[str, dict] = {}
    if elog_path.exists():
        experiments = parse_experiment_log(elog_path.read_text(encoding="utf-8"))
    else:
        msg = f"{elog_path} not found — skipping experiment-level checks"
        warnings.append(msg)

    # --- Run checks ---
    orphans = check_orphan_claims(claims, experiments)
    if orphans:
        errors.append(f"Claims with no evidence: {', '.join(orphans)}")

    missing = check_missing_evidence(claims, experiments)
    if missing:
        errors.append(
            f"Evidence refs with no matching experiment: {', '.join(missing)}"
        )

    unsupported = check_unsupported_claims(claims, experiments)
    if unsupported:
        errors.append(
            f"Claims backed only by failed experiments: {', '.join(unsupported)}"
        )

    numeric_warnings = check_numeric_consistency(claims, experiments)
    warnings.extend(numeric_warnings)

    data_warnings = check_data_version_consistency(experiments)
    warnings.extend(data_warnings)

    has_issues = bool(errors or warnings)

    # --- Report ---
    if quiet and not has_issues:
        # Clean pass: silent, nothing to report
        sys.exit(0)

    # Full report (always shown in normal mode, or in quiet mode when issues exist)
    print(f"Claims: {len(claims)}  |  Experiments: {len(experiments)}")
    print(f"Errors: {len(errors)}  |  Warnings: {len(warnings)}")
    print("---")

    if warnings:
        print("WARNINGS:")
        for w in warnings:
            print(f"  [!] {w}")

    if errors:
        print("BLOCKING ERRORS:")
        for e in errors:
            print(f"  [x] {e}")
        print()
        if warn_only:
            print(
                "--warn-only set: would block, but exiting 0 for inspection."
            )
            sys.exit(0)
        else:
            print("Fix these before proceeding to writing phase (Stage 10).")
            sys.exit(1)
    else:
        print("All checks passed — ready for writing phase.")
        sys.exit(0)


if __name__ == "__main__":
    main()
