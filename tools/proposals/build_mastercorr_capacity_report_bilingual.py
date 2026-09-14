"""Assemble the bilingual (ES/EN) Mastercorr INGETRANS capacity report with a language switch.

Spanish body = current report body. English body = same markup with text nodes replaced by the
translation map and Spanish charts swapped for the English chart set. A fixed ES/EN switcher
(screen only, persisted, ?lang= query) toggles .lang-es / .lang-en blocks.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

W = Path(r"C:\Users\isena\.copilot\session-state\b750502e-8645-40b5-bb33-37f54fafeb4f\files")
SRC = Path(r"C:\Users\isena\Documents\GitHub\AI-FACTORY-v2\INGETRANS_MASTERCORR_CAPACITY_REPORT_90D_2026-09-14.html")
OUT = [
    Path(r"C:\Users\isena\Documents\INGECART\PRODUCTO\INGETRANS\DATOS OPERATIVOS MASTERCORR 20 08 2026\INGETRANS_MASTERCORR_CAPACITY_REPORT_90D_ES-EN_2026-09-14.html"),
    Path(r"C:\Users\isena\Documents\GitHub\AI-FACTORY-v2\INGETRANS_MASTERCORR_CAPACITY_REPORT_90D_ES-EN_2026-09-14.html"),
]

SWITCHER_CSS = """
<style>
.lang.hidden { display: none; }
.lang-switch { position: fixed; top: 10mm; right: 6mm; z-index: 100; display: flex; gap: 2px; background: #111; padding: 2px; border-radius: 3px; }
.lang-switch button { font-family: Arial, Helvetica, sans-serif; font-size: 8pt; font-weight: bold; letter-spacing: 1pt; color: #ddd; background: transparent; border: 0; padding: 2.2mm 3.4mm; cursor: pointer; text-transform: uppercase; }
.lang-switch button.active { background: #FF6304; color: #fff; }
@media print { .lang-switch { display: none; } }
</style>
"""
SWITCHER_HTML = """
<div class="lang-switch" role="tablist" aria-label="Idioma / Language">
  <button type="button" class="active" data-language="es" aria-pressed="true">ES</button>
  <button type="button" data-language="en" aria-pressed="false">EN</button>
</div>
"""
SWITCHER_JS = """
<script>
(function () {
  var buttons = document.querySelectorAll('[data-language]');
  var blocks = document.querySelectorAll('.lang');
  function apply(lang) {
    blocks.forEach(function (b) { b.classList.toggle('hidden', !b.classList.contains('lang-' + lang)); });
    buttons.forEach(function (btn) {
      var on = btn.dataset.language === lang;
      btn.classList.toggle('active', on);
      btn.setAttribute('aria-pressed', String(on));
    });
    document.documentElement.setAttribute('lang', lang);
    try { localStorage.setItem('ingetrans_mastercorr_report_lang', lang); } catch (e) {}
  }
  buttons.forEach(function (btn) { btn.addEventListener('click', function () { apply(btn.dataset.language); }); });
  var saved = null;
  try { saved = localStorage.getItem('ingetrans_mastercorr_report_lang'); } catch (e) {}
  var fromQuery = (location.search.match(/[?&]lang=(es|en)/) || [])[1];
  apply(fromQuery || saved || 'es');
})();
</script>
"""


def edge_ws(s: str) -> tuple[str, str]:
    return re.match(r"\s*", s).group(0), re.search(r"\s*$", s).group(0)


def main() -> None:
    html = SRC.read_text(encoding="utf-8")
    strings = json.loads((W / "mc_strings.json").read_text(encoding="utf-8"))
    mapping: dict[str, str] = {}
    for i in range(3):
        for k, v in json.loads((W / f"mc_batch_{i}_en.json").read_text(encoding="utf-8")).items():
            mapping[strings[int(k)]] = v
    imgs_es = json.loads((W / "mastercorr_imgs.json").read_text(encoding="utf-8"))
    imgs_en = json.loads((W / "mastercorr_imgs_en.json").read_text(encoding="utf-8"))

    head_end = html.index("<body>") + len("<body>")
    head, body = html[:head_end], html[head_end:html.rindex("</body>")]
    body = re.sub(r'<div class="screen-note">.*?</div>\s*', "", body, count=1, flags=re.S)

    # English body: translate text nodes
    out, pos = [], 0
    for m in re.finditer(r">([^<>]+)<", body):
        t = m.group(1)
        if t in mapping:
            new = mapping[t]
            l0, t0 = edge_ws(t)
            l1, t1 = edge_ws(new)
            if (l0, t0) != (l1, t1):
                new = l0 + new.strip() + t0
            out.append(body[pos:m.start(1)])
            out.append(new)
            pos = m.end(1)
    out.append(body[pos:])
    body_en = "".join(out)
    # labels containing '>' are split by the text-node regex; translate them explicitly
    body_en = body_en.replace("Horas &gt; 50 % / &gt; 70 % / &gt; 85 %", "Hours &gt; 50 % / &gt; 70 % / &gt; 85 %")
    body_en = body_en.replace("Horas > 50 % / > 70 % / > 85 %", "Hours > 50 % / > 70 % / > 85 %")
    for key, es_src in imgs_es.items():
        body_en = body_en.replace(es_src, imgs_en[key])

    head = head.replace("<title>INGECART · INGETRANS Mastercorr — Informe de capacidad y saturación (90 días)</title>",
                        "<title>INGECART · INGETRANS Mastercorr — Capacity and saturation report / Informe de capacidad (90 días)</title>")
    head = head.replace("</head>", SWITCHER_CSS + "</head>")
    note = """
<div class="screen-note"><b>Vista previa / Browser preview.</b> Selector ES/EN arriba a la derecha; el PDF imprime el idioma visible.
ES/EN switch top-right; the PDF prints the visible language.</div>
"""
    final = (head + SWITCHER_HTML + note
             + '\n<div class="lang lang-es">\n' + body + "\n</div>\n"
             + '<div class="lang lang-en hidden">\n' + body_en + "\n</div>\n"
             + SWITCHER_JS + "</body>\n</html>\n")
    for o in OUT:
        o.parent.mkdir(parents=True, exist_ok=True)
        o.write_text(final, encoding="utf-8")
        print("written", o, len(final))
    # residue check
    en_text = re.sub(r"<[^>]+>", " ", re.sub(r"<(style|script)[^>]*>.*?</\1>", "", body_en, flags=re.S))
    res = [w for w in ("ocupación", "bobinas", "misiones", "entregas", "corrugadora", "horas", "carro") if re.search(r"\b" + w + r"\b", en_text, re.I)]
    print("spanish residue in EN body:", res)


if __name__ == "__main__":
    main()
