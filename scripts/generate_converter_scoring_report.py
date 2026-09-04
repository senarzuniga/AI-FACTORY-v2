"""Generate converter/palletizer scoring report for corrugated simulation planning."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "knowledge" / "corrugated_equipment" / "converter_equipment_catalog_v1.json"
OUT_PATH = ROOT / "docs" / "converter_equipment_scoring_report.md"


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def norm(value: float, min_v: float, max_v: float) -> float:
    if max_v <= min_v:
        return 0.0
    return clamp((value - min_v) / (max_v - min_v))


def average_pair(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def compute_scores(items: list[dict]) -> list[dict]:
    throughput_values = []
    changeover_values = []
    oee_values = []

    for item in items:
        throughput_values.append(float(item["throughput"]["benchmark_nominal"]))
        changeover_values.append(float(item["changeover"]["average_minutes"]))
        oee_values.append(average_pair(item["operations"]["oee_typical_percent"]))

    t_min, t_max = min(throughput_values), max(throughput_values)
    c_min, c_max = min(changeover_values), max(changeover_values)
    o_min, o_max = min(oee_values), max(oee_values)

    scored = []
    for item in items:
        throughput = float(item["throughput"]["benchmark_nominal"])
        changeover = float(item["changeover"]["average_minutes"])
        oee_mid = average_pair(item["operations"]["oee_typical_percent"])

        throughput_score = norm(throughput, t_min, t_max)
        changeover_score = 1.0 - norm(changeover, c_min, c_max)
        oee_score = norm(oee_mid, o_min, o_max)

        amr_fit = float(
            item.get("amr_logistics_fit", {}).get("wip_cell_proximity_fit")
            or item.get("amr_logistics_fit", {}).get("pallet_handoff_fit")
            or 0.5
        )

        capex = item.get("capex_reference", {})
        capex_candidates = []
        for key in ("used_range_eur", "new_system_range_eur"):
            val = capex.get(key)
            if isinstance(val, list) and len(val) == 2:
                capex_candidates.append((float(val[0]) + float(val[1])) / 2.0)
        capex_mid = min(capex_candidates) if capex_candidates else 1_000_000.0

        # Inverse affordability score against broad envelope for planning.
        affordability = 1.0 - norm(capex_mid, 150_000.0, 6_500_000.0)

        # Weighted final score for early stage hypothesis prioritization.
        final_score = (
            throughput_score * 0.28
            + changeover_score * 0.17
            + oee_score * 0.2
            + amr_fit * 0.25
            + affordability * 0.1
        )

        scored.append(
            {
                "id": item["id"],
                "oem": item["oem"],
                "model": item["model"],
                "category": item["category"],
                "throughput_nominal": throughput,
                "changeover_avg_min": changeover,
                "oee_mid": round(oee_mid, 2),
                "amr_fit": round(amr_fit, 3),
                "affordability": round(affordability, 3),
                "score": round(final_score, 4),
            }
        )

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored


def to_markdown_table(rows: list[dict]) -> str:
    header = (
        "| Rank | OEM | Model | Category | Score | Throughput Nominal | Changeover Avg (min) | OEE Mid (%) | AMR Fit | Affordability |\n"
        "|---:|---|---|---|---:|---:|---:|---:|---:|---:|\n"
    )
    body = []
    for idx, row in enumerate(rows, start=1):
        body.append(
            "| {rank} | {oem} | {model} | {category} | {score:.3f} | {thr:.0f} | {chg:.1f} | {oee:.1f} | {amr:.3f} | {aff:.3f} |".format(
                rank=idx,
                oem=row["oem"],
                model=row["model"],
                category=row["category"],
                score=row["score"],
                thr=row["throughput_nominal"],
                chg=row["changeover_avg_min"],
                oee=row["oee_mid"],
                amr=row["amr_fit"],
                aff=row["affordability"],
            )
        )
    return header + "\n".join(body) + "\n"


def main() -> int:
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    equipment = catalog.get("equipment", [])

    converters = [
        item for item in equipment
        if item.get("category") in {"flexo_folder_gluer", "high_speed_flexo_folder_gluer", "rotary_die_cutter"}
    ]
    palletizers = [item for item in equipment if item.get("category") == "robotic_palletizer"]

    scored_converters = compute_scores(converters)
    scored_palletizers = compute_scores(palletizers)

    report = [
        "# Converter Equipment Scoring Report",
        "",
        "Auto-generated ranking for hypothesis prioritization in corrugated plant simulation.",
        "",
        "## Scoring Weights",
        "",
        "- Throughput: 28%",
        "- Changeover: 17%",
        "- OEE baseline: 20%",
        "- AMR/WIP logistics fit: 25%",
        "- Affordability: 10%",
        "",
        "## Converter Ranking",
        "",
        to_markdown_table(scored_converters),
        "",
        "## Robotic Palletizer Ranking",
        "",
        to_markdown_table(scored_palletizers),
        "",
        "## Notes",
        "",
        "- Scores are for scenario prioritization, not final procurement decisions.",
        "- Validate with OEM quotes, acceptance tests and plant-specific constraints.",
    ]

    OUT_PATH.write_text("\n".join(report), encoding="utf-8")
    print(f"[converter-scoring] Wrote {OUT_PATH.relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
