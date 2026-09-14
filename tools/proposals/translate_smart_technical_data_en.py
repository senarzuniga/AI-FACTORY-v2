"""Produce an English twin of INGETRANS_smart_technical data.html.

Only text nodes (including SVG <text>), the @page CSS `content:` strings and the html lang attribute
are translated. Tags, attributes, CSS, SVG geometry, images and byte layout outside text nodes are
kept identical. The script verifies that the non-text skeleton of both files is byte-identical.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

SRC = Path(r"C:\Users\isena\Documents\INGECART\PRODUCTO\INGETRANS\INGETRANS_smart_technical data.html")
DST = Path(r"C:\Users\isena\Documents\INGECART\PRODUCTO\INGETRANS\INGETRANS_smart_technical data_EN.html")
WORK = Path(r"C:\Users\isena\.copilot\session-state\b750502e-8645-40b5-bb33-37f54fafeb4f\files")

CSS_CONTENT_EN = {
    "INGECART · Engineering & Auditing — Propuesta técnico-comercial. Documento confidencial.":
        "INGECART · Engineering & Auditing — Technical and commercial proposal. Confidential document.",
    "Pág. ": "Page ",
    "INGECART S.L. · Pol. Ind. Llaverno 9-10 · 08739 Subirats · Barcelona (España) · +34 938 183 316 · www.ingecart.eu":
        "INGECART S.L. · Pol. Ind. Llaverno 9-10 · 08739 Subirats · Barcelona (Spain) · +34 938 183 316 · www.ingecart.eu",
}
CSS_COUNTER_EN = (' counter(page) " de " counter(pages)', ' counter(page) " of " counter(pages)')


def load_translations() -> dict[str, str]:
    strings = json.loads((WORK / "techdata_strings.json").read_text(encoding="utf-8"))
    mapping: dict[str, str] = {}
    for i in range(4):
        batch = json.loads((WORK / f"techdata_batch_{i}_en.json").read_text(encoding="utf-8"))
        for k, v in batch.items():
            mapping[strings[int(k)]] = v
    missing = [s for s in strings if s not in mapping]
    if missing:
        raise SystemExit(f"{len(missing)} strings without translation, e.g. {missing[:3]!r}")
    return mapping


def edge_ws(s: str) -> tuple[str, str]:
    lead = re.match(r"\s*", s).group(0)
    trail = re.search(r"\s*$", s).group(0)
    return lead, trail


def translate(html: str, mapping: dict[str, str]) -> tuple[str, list[str]]:
    protected = [(m.start(), m.end()) for m in re.finditer(r"<style>.*?</style>|<script>.*?</script>", html, re.S)]

    def is_protected(i: int) -> bool:
        return any(a <= i < b for a, b in protected)

    warnings: list[str] = []
    out: list[str] = []
    pos = 0
    for m in re.finditer(r">([^<>]+)<", html):
        start, end = m.start(1), m.end(1)
        text = m.group(1)
        if is_protected(start) or text not in mapping:
            continue
        new = mapping[text]
        l0, t0 = edge_ws(text)
        l1, t1 = edge_ws(new)
        if (l0, t0) != (l1, t1):
            new = l0 + new.strip() + t0
            warnings.append(f"edge whitespace restored for: {text.strip()[:50]!r}")
        out.append(html[pos:start])
        out.append(new)
        pos = end
    out.append(html[pos:])
    result = "".join(out)

    for es, en in CSS_CONTENT_EN.items():
        if es not in result:
            warnings.append(f"css content not found: {es[:40]!r}")
        result = result.replace(es, en)
    if CSS_COUNTER_EN[0] not in result:
        warnings.append("page counter pattern not found")
    result = result.replace(*CSS_COUNTER_EN)
    result = result.replace('<html lang="es">', '<html lang="en">', 1)
    return result, warnings


def skeleton(html: str) -> str:
    """Everything except text-node content and the translated CSS strings/lang attribute."""
    protected = [(m.start(), m.end()) for m in re.finditer(r"<style>.*?</style>|<script>.*?</script>", html, re.S)]

    def is_protected(i: int) -> bool:
        return any(a <= i < b for a, b in protected)

    parts, pos = [], 0
    for m in re.finditer(r">([^<>]+)<", html):
        if is_protected(m.start(1)):
            continue
        parts.append(html[pos:m.start(1)])
        parts.append("§")
        pos = m.end(1)
    parts.append(html[pos:])
    s = "".join(parts)
    for es, en in CSS_CONTENT_EN.items():
        s = s.replace(es, "§").replace(en, "§")
    s = s.replace(CSS_COUNTER_EN[0], "§").replace(CSS_COUNTER_EN[1], "§")
    s = s.replace('<html lang="es">', "§").replace('<html lang="en">', "§")
    return s


def main() -> int:
    html = SRC.read_text(encoding="utf-8")
    mapping = load_translations()
    en, warnings = translate(html, mapping)
    for w in warnings:
        print("warning:", w)
    same = skeleton(html) == skeleton(en)
    print("skeleton identical:", same)
    if not same:
        return 1
    DST.write_text(en, encoding="utf-8", newline="")
    print("written", DST, len(en))
    return 0


if __name__ == "__main__":
    sys.exit(main())
