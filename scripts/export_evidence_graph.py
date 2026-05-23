"""Export SEC/CLM/EXP/DATA/FIG evidence relationships.

Outputs a JSON graph for machines and a Mermaid graph for quick visual review.
The parser is intentionally lightweight and offline; it reads the Markdown
tables used by the research workflow console.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


THESIS_DIR = Path("docs/thesis")
ID_RE = re.compile(r"\b(?:SEC|CLM|EXP|DATA|FIG)-(?:AUTO-)?[A-Za-z0-9.-]+\b")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def markdown_rows(text: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or not stripped.endswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if cells and all(set(cell) <= {"-", ":"} for cell in cells):
            continue
        rows.append(cells)
    return rows


def ids(text: str) -> list[str]:
    found = ID_RE.findall(text or "")
    return list(dict.fromkeys(found))


def node_kind(node_id: str) -> str:
    return node_id.split("-", 1)[0]


def add_node(nodes: dict[str, dict[str, str]], node_id: str, label: str = "") -> None:
    nodes.setdefault(node_id, {"id": node_id, "kind": node_kind(node_id), "label": label or node_id})


def add_edge(edges: set[tuple[str, str, str]], source: str, target: str, relation: str) -> None:
    if source and target and source != target:
        edges.add((source, target, relation))


def build_graph(thesis_dir: Path = THESIS_DIR) -> dict[str, list[dict[str, str]]]:
    nodes: dict[str, dict[str, str]] = {}
    edges: set[tuple[str, str, str]] = set()

    # Claim evidence map: CLM -> EXP, FIG, SEC, DATA
    for cells in markdown_rows(read_text(thesis_dir / "claim-evidence-map.md")):
        if not cells or not re.fullmatch(r"CLM-[A-Za-z0-9.-]+", cells[0]):
            continue
        claim = cells[0]
        add_node(nodes, claim, cells[1] if len(cells) > 1 else claim)
        for target in ids(" | ".join(cells[2:])):
            add_node(nodes, target)
            add_edge(edges, claim, target, "supported_by")

    # Section citation map: SEC -> CLM when claim ids appear in segment text.
    for cells in markdown_rows(read_text(thesis_dir / "section-citation-map.md")):
        if not cells:
            continue
        if re.fullmatch(r"SEC-[A-Za-z0-9.-]+", cells[0]):
            add_node(nodes, cells[0], cells[1] if len(cells) > 1 else cells[0])
        if re.fullmatch(r"SEG-[A-Za-z0-9.-]+", cells[0]) and len(cells) > 2:
            section = cells[1]
            add_node(nodes, section)
            for claim in ids(cells[2]):
                if claim.startswith("CLM-"):
                    add_node(nodes, claim)
                    add_edge(edges, section, claim, "contains_claim")

    # Experiment registry: EXP -> CLM, DATA, output path node omitted unless an ID exists.
    for cells in markdown_rows(read_text(thesis_dir / "experiment-registry.md")):
        if not cells or not re.fullmatch(r"EXP-(?:AUTO-)?[A-Za-z0-9.-]+", cells[0]):
            continue
        exp = cells[0]
        add_node(nodes, exp, cells[1] if len(cells) > 1 else exp)
        for target in ids(" | ".join(cells[1:])):
            add_node(nodes, target)
            add_edge(edges, exp, target, "records")

    # Data availability: DATA -> CLM/EXP and CLM -> DATA.
    for cells in markdown_rows(read_text(thesis_dir / "data-availability.md")):
        if not cells:
            continue
        if re.fullmatch(r"DATA-[A-Za-z0-9.-]+", cells[0]):
            data_id = cells[0]
            add_node(nodes, data_id, cells[1] if len(cells) > 1 else data_id)
            for target in ids(" | ".join(cells[2:4])):
                add_node(nodes, target)
                add_edge(edges, target, data_id, "uses_data")
        if re.fullmatch(r"CLM-[A-Za-z0-9.-]+", cells[0]):
            claim = cells[0]
            add_node(nodes, claim)
            for target in ids(" | ".join(cells[1:])):
                add_node(nodes, target)
                add_edge(edges, claim, target, "traces_to")

    # Figure plan: FIG -> CLM/DATA/EXP.
    for cells in markdown_rows(read_text(thesis_dir / "figure-plan.md")):
        if not cells or not re.fullmatch(r"FIG-[A-Za-z0-9.-]+", cells[0]):
            continue
        fig = cells[0]
        add_node(nodes, fig, cells[2] if len(cells) > 2 else fig)
        for target in ids(" | ".join(cells[1:])):
            add_node(nodes, target)
            add_edge(edges, fig, target, "visualizes")

    return {
        "nodes": sorted(nodes.values(), key=lambda item: item["id"]),
        "edges": [
            {"source": source, "target": target, "relation": relation}
            for source, target, relation in sorted(edges)
        ],
    }


def mermaid_id(node_id: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]", "_", node_id)


def to_mermaid(graph: dict[str, list[dict[str, str]]]) -> str:
    lines = ["graph LR"]
    for node in graph["nodes"]:
        lines.append(f'  {mermaid_id(node["id"])}["{node["id"]}"]')
    for edge in graph["edges"]:
        lines.append(
            f'  {mermaid_id(edge["source"])} -- "{edge["relation"]}" --> {mermaid_id(edge["target"])}'
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Export thesis evidence graph.")
    parser.add_argument("--thesis-dir", default="docs/thesis")
    parser.add_argument("--out", default="docs/thesis/evidence-graph.json")
    parser.add_argument("--mermaid", default="docs/thesis/evidence-graph.mmd")
    args = parser.parse_args()

    graph = build_graph(Path(args.thesis_dir))
    out = Path(args.out)
    mermaid = Path(args.mermaid)
    out.parent.mkdir(parents=True, exist_ok=True)
    mermaid.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(graph, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    mermaid.write_text(to_mermaid(graph), encoding="utf-8")
    print(f"nodes: {len(graph['nodes'])}  |  edges: {len(graph['edges'])}")
    print(f"wrote: {out}")
    print(f"wrote: {mermaid}")


if __name__ == "__main__":
    main()
