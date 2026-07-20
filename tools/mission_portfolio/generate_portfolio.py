#!/usr/bin/env python3
"""Generador de análisis de Mission Portfolio.

Escribe los artefactos:
- mission_manager/portfolio/mission_portfolio.json
- enterprise_digital_twin/mission_portfolio.json
- docs/mission_portfolio_report.md

Diseñado para ser ejecutado localmente y producir el análisis solicitado.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, List


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]

    # Candidate POCs (raw metric values 0-100 unless noted)
    candidates: List[Dict] = [
        {
            "id": "M-001",
            "title": "Factory Graph Adapter",
            "description": "Adapter to map layouts (assets/layout_*.json) and parsed drawings into KnowledgeGraph / GraphStore.",
            "business_value": 75,
            "engineering_value": 85,
            "knowledge_reuse": 95,
            "architecture_impact": 60,
            "technical_debt_reduction": 60,
            "platform_maturity_increase": 85,
            "future_mission_unlock": 90,
            "expected_roi": 70,
            "implementation_risk": 20,
            "estimated_cost_usd": 10000,
            "estimated_time_weeks": 3,
            "strategic_alignment": 85,
            "dependencies": [],
        },

        {
            "id": "M-002",
            "title": "Simulation Scenario Adapter",
            "description": "Map Factory Graph into ingetrans scenario YAML and run headless simulator for analysis.",
            "business_value": 85,
            "engineering_value": 80,
            "knowledge_reuse": 85,
            "architecture_impact": 65,
            "technical_debt_reduction": 55,
            "platform_maturity_increase": 80,
            "future_mission_unlock": 85,
            "expected_roi": 80,
            "implementation_risk": 30,
            "estimated_cost_usd": 18000,
            "estimated_time_weeks": 6,
            "strategic_alignment": 80,
            "dependencies": ["M-001"],
        },

        {
            "id": "M-003",
            "title": "Document-to-Entity Pipeline (CAD/Drawings Ingest)",
            "description": "Ingest DWG/DXF/PDF/Images, extract machines and layout entities, normalize into Factory Graph contract.",
            "business_value": 80,
            "engineering_value": 75,
            "knowledge_reuse": 70,
            "architecture_impact": 70,
            "technical_debt_reduction": 50,
            "platform_maturity_increase": 70,
            "future_mission_unlock": 75,
            "expected_roi": 65,
            "implementation_risk": 45,
            "estimated_cost_usd": 25000,
            "estimated_time_weeks": 10,
            "strategic_alignment": 75,
            "dependencies": [],
        },

        {
            "id": "M-004",
            "title": "Evidence & Truth Integration",
            "description": "Pipe extraction outputs into EvidenceStore and TruthEngine to version facts and populate KnowledgeGraph.",
            "business_value": 78,
            "engineering_value": 80,
            "knowledge_reuse": 88,
            "architecture_impact": 60,
            "technical_debt_reduction": 75,
            "platform_maturity_increase": 82,
            "future_mission_unlock": 78,
            "expected_roi": 70,
            "implementation_risk": 25,
            "estimated_cost_usd": 12000,
            "estimated_time_weeks": 4,
            "strategic_alignment": 80,
            "dependencies": ["M-003"],
        },

        {
            "id": "M-005",
            "title": "Engineering Copilot (basic)",
            "description": "A question-answering Copilot leveraging the Factory Graph, EvidenceStore and document parsers to answer engineering queries.",
            "business_value": 90,
            "engineering_value": 85,
            "knowledge_reuse": 70,
            "architecture_impact": 70,
            "technical_debt_reduction": 45,
            "platform_maturity_increase": 80,
            "future_mission_unlock": 80,
            "expected_roi": 85,
            "implementation_risk": 50,
            "estimated_cost_usd": 40000,
            "estimated_time_weeks": 12,
            "strategic_alignment": 90,
            "dependencies": ["M-001", "M-004"],
        },

        {
            "id": "M-006",
            "title": "Bottleneck / WIP Analyzer",
            "description": "Analytics module that uses simulator outputs to detect bottlenecks, WIP hotspots and propose mitigations.",
            "business_value": 82,
            "engineering_value": 78,
            "knowledge_reuse": 85,
            "architecture_impact": 60,
            "technical_debt_reduction": 60,
            "platform_maturity_increase": 78,
            "future_mission_unlock": 77,
            "expected_roi": 75,
            "implementation_risk": 30,
            "estimated_cost_usd": 20000,
            "estimated_time_weeks": 8,
            "strategic_alignment": 78,
            "dependencies": ["M-002"],
        },

        {
            "id": "M-007",
            "title": "Offer / Executive Proposal Generator",
            "description": "Combine analytics and reporting to generate executive proposals, ROI estimates and investment roadmaps.",
            "business_value": 88,
            "engineering_value": 72,
            "knowledge_reuse": 78,
            "architecture_impact": 60,
            "technical_debt_reduction": 50,
            "platform_maturity_increase": 70,
            "future_mission_unlock": 70,
            "expected_roi": 82,
            "implementation_risk": 35,
            "estimated_cost_usd": 15000,
            "estimated_time_weeks": 6,
            "strategic_alignment": 85,
            "dependencies": ["M-004", "M-006"],
        },

        {
            "id": "M-008",
            "title": "AMR Opportunity Engine",
            "description": "Analyze transport flows and simulation outputs to identify AMR deployment opportunities and fleet optimization.",
            "business_value": 84,
            "engineering_value": 80,
            "knowledge_reuse": 72,
            "architecture_impact": 75,
            "technical_debt_reduction": 55,
            "platform_maturity_increase": 78,
            "future_mission_unlock": 80,
            "expected_roi": 80,
            "implementation_risk": 40,
            "estimated_cost_usd": 30000,
            "estimated_time_weeks": 12,
            "strategic_alignment": 85,
            "dependencies": ["M-002", "M-003"],
        },
    ]

    metric_keys = [
        "business_value",
        "engineering_value",
        "knowledge_reuse",
        "architecture_impact",
        "technical_debt_reduction",
        "platform_maturity_increase",
        "future_mission_unlock",
        "expected_roi",
        "implementation_risk",
        "strategic_alignment",
    ]

    # Weights (percent -> fraction) used to compute Global Mission Score
    weights_percent = {
        "business_value": 15,
        "engineering_value": 15,
        "knowledge_reuse": 10,
        "architecture_impact": 8,
        "technical_debt_reduction": 7,
        "platform_maturity_increase": 10,
        "future_mission_unlock": 10,
        "expected_roi": 12,
        # implementation_risk is negative in raw; we invert it during scoring
        "implementation_risk": 8,
        "strategic_alignment": 5,
    }

    total_w = sum(weights_percent.values())
    weights = {k: v / total_w for k, v in weights_percent.items()}

    # Normalization (min-max) per metric
    mins = {k: min(c[k] for c in candidates) for k in metric_keys}
    maxs = {k: max(c[k] for c in candidates) for k in metric_keys}

    def normalize(val: float, k: str) -> float:
        mn = mins[k]
        mx = maxs[k]
        if mx <= mn:
            return 0.5
        return (val - mn) / (mx - mn)

    # Compute normalized metrics and global score
    for c in candidates:
        c["normalized"] = {}
        for k in metric_keys:
            c["normalized"][k] = normalize(c[k], k)

        # For implementation risk, lower is better -> invert
        inv_risk = 1.0 - c["normalized"]["implementation_risk"]
        # Weighted sum
        score = 0.0
        for k in metric_keys:
            w = weights.get(k, 0.0)
            val = c["normalized"][k]
            if k == "implementation_risk":
                val = inv_risk
            score += w * val

        c["global_score"] = round(score * 100.0, 2)

    # Build Dependency Graph (edges: prereq -> dependant)
    nodes = {c["id"]: {"id": c["id"], "title": c["title"]} for c in candidates}
    edges = []
    adjacency = {nid: [] for nid in nodes}
    indegree = {nid: 0 for nid in nodes}
    for c in candidates:
        for dep in c.get("dependencies", []):
            edges.append({"from": dep, "to": c["id"]})
            adjacency.setdefault(dep, []).append(c["id"])
            indegree[c["id"]] = indegree.get(c["id"], 0) + 1

    # Topological layers (breadth by dependency depth)
    layers: Dict[int, List[str]] = {}
    queue = [nid for nid, d in indegree.items() if d == 0]
    depth = {nid: 0 for nid in nodes}
    processed = set()
    while queue:
        nid = queue.pop(0)
        processed.add(nid)
        d = depth[nid]
        layers.setdefault(d, []).append(nid)
        for child in adjacency.get(nid, []):
            depth[child] = max(depth.get(child, 0), d + 1)
            indegree[child] -= 1
            if indegree[child] == 0:
                queue.append(child)

    # Future Mission Tree (simple hierarchical representation by depth)
    mission_tree = {"layers": layers}

    # Sort candidates by score descending
    ranked = sorted(candidates, key=lambda x: x["global_score"], reverse=True)

    # Prepare output artifact directories
    mm_dir = repo_root / "mission_manager" / "portfolio"
    edt_dir = repo_root / "enterprise_digital_twin"
    docs_dir = repo_root / "docs"
    ensure_dir(mm_dir)
    ensure_dir(edt_dir)
    ensure_dir(docs_dir)

    # Write JSON portfolio
    portfolio = {
        "portfolio_id": "PORT-001",
        "title": "Strategic Mission Portfolio 1 — Factory Intelligence",
        "generated_at": __import__("datetime").datetime.utcnow().isoformat() + "Z",
        "candidates": candidates,
        "dependency_graph": {"nodes": list(nodes.values()), "edges": edges},
        "mission_tree": mission_tree,
        "ranked": [{"id": c["id"], "title": c["title"], "global_score": c["global_score"]} for c in ranked],
    }

    portfolio_path = mm_dir / "mission_portfolio.json"
    with portfolio_path.open("w", encoding="utf-8") as fh:
        json.dump(portfolio, fh, indent=2, ensure_ascii=False)

    # Also write to enterprise digital twin location
    edt_path = edt_dir / "mission_portfolio.json"
    with edt_path.open("w", encoding="utf-8") as fh:
        json.dump(portfolio, fh, indent=2, ensure_ascii=False)

    # Markdown human-readable report
    md_lines: List[str] = []
    md_lines.append("# Mission Portfolio Analysis — Factory Intelligence")
    md_lines.append("")
    md_lines.append(f"Generated: {portfolio['generated_at']}")
    md_lines.append("")
    md_lines.append("## Ranked candidates (Global Mission Score)")
    md_lines.append("")
    for c in ranked:
        md_lines.append(f"- **{c['id']} — {c['title']}**: Global Score = **{c['global_score']}**")
        md_lines.append(f"  - Description: {c['description']}")
        md_lines.append(f"  - Business Value: {c['business_value']} | Engineering Value: {c['engineering_value']} | Knowledge Reuse: {c['knowledge_reuse']}")
        md_lines.append(f"  - Expected ROI: {c['expected_roi']} | Implementation Risk: {c['implementation_risk']} | Cost: ${c['estimated_cost_usd']:,} | Time: {c['estimated_time_weeks']} weeks")
        md_lines.append("")

    top = ranked[0]
    md_lines.append("## Recommended next POC")
    md_lines.append("")
    md_lines.append(f"**{top['id']} — {top['title']}** selected automatically as highest scoring mission (Global Score = {top['global_score']}).")
    md_lines.append("")
    md_lines.append("## Dependency Graph (edges prereq -> dependant)")
    md_lines.append("")
    for e in edges:
        md_lines.append(f"- {e['from']} -> {e['to']}")
    md_lines.append("")
    md_lines.append("## Future Mission Tree (by dependency depth layers)")
    md_lines.append("")
    for depth_level in sorted(layers.keys()):
        md_lines.append(f"- Layer {depth_level}: {', '.join(layers[depth_level])}")

    report_path = docs_dir / "mission_portfolio_report.md"
    with report_path.open("w", encoding="utf-8") as fh:
        fh.write("\n".join(md_lines))

    print("Mission portfolio written:")
    print(f" - {portfolio_path}")
    print(f" - {edt_path}")
    print(f" - {report_path}")


if __name__ == "__main__":
    main()
