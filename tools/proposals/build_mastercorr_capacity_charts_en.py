"""Generate embedded charts for the Mastercorr INGETRANS capacity report (UTF-8 safe)."""

from __future__ import annotations

import base64
import io
import json
import random
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

W = Path(r"C:\Users\isena\.copilot\session-state\b750502e-8645-40b5-bb33-37f54fafeb4f\files")
d = json.loads((W / "mastercorr_summary.json").read_text(encoding="utf-8"))
ORANGE, DARK, GREY = "#FF6304", "#111111", "#8a8a8a"
plt.rcParams.update({"font.family": "Arial", "font.size": 8, "axes.edgecolor": "#cccccc", "axes.spines.top": False, "axes.spines.right": False})


def b64(fig) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=160, bbox_inches="tight")
    plt.close(fig)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


imgs = {}

days = [datetime.fromisoformat(x[0]) for x in d["daily"]]
bh = [x[1] for x in d["daily"]]
dl = [x[2] for x in d["daily"]]
fig, ax = plt.subplots(figsize=(7.4, 2.6))
ax.bar(days, bh, color=ORANGE, width=0.8, label="Productive carriage hours")
ax.set_ylabel("h/day")
ax2 = ax.twinx()
ax2.plot(days, dl, color=DARK, lw=1.2, marker="o", ms=2, label="Reels delivered")
ax2.set_ylabel("reels/day")
ax2.spines["right"].set_visible(True)
ax.set_title("INGETRANS daily activity — 16 Jun to 14 Sep 2026", loc="left", fontsize=9, fontweight="bold")
fig.legend(loc="upper right", bbox_to_anchor=(0.98, 0.98), frameon=False, fontsize=7)
imgs["daily"] = b64(fig)

occ = [h[1] * 100 for h in d["hourly"]]
fig, ax = plt.subplots(figsize=(3.6, 2.4))
ax.hist(occ, bins=20, range=(0, 100), color=ORANGE, edgecolor="white")
ax.axvline(85, color=DARK, ls="--", lw=1)
ax.text(60, ax.get_ylim()[1] * 0.9, "saturation 85 %", fontsize=7)
ax.set_xlabel("Hourly occupancy (%)")
ax.set_ylabel("hours")
ax.set_title("Hourly occupancy distribution", loc="left", fontsize=9, fontweight="bold")
imgs["hist"] = b64(fig)

hod = [100 * v for v in d["hod_list"]]
fig, ax = plt.subplots(figsize=(3.6, 2.4))
ax.bar(range(24), hod, color=DARK)
ax.set_xlabel("Hour of day")
ax.set_ylabel("mean occupancy %")
ax.set_xticks(range(0, 24, 3))
ax.set_title("Hour-of-day profile", loc="left", fontsize=9, fontweight="bold")
imgs["hod"] = b64(fig)

spl = sorted(d["deliv_spl"], key=int)
dv = [d["deliv_spl"][s] for s in spl]
rv = [d["ret_spl"].get(s, 0) for s in spl]
fig, ax = plt.subplots(figsize=(3.6, 2.4))
x = range(len(spl))
ax.bar([i - 0.2 for i in x], dv, 0.4, color=ORANGE, label="Deliveries")
ax.bar([i + 0.2 for i in x], rv, 0.4, color=DARK, label="Returns")
ax.set_xticks(list(x))
ax.set_xticklabels([f"Splicer {s}" for s in spl])
ax.legend(frameon=False, fontsize=7)
ax.set_title("Movements per splicer (90 days)", loc="left", fontsize=9, fontweight="bold")
imgs["spl"] = b64(fig)

trk = sorted(d["deliv_trk"], key=int)
tv = [d["deliv_trk"][t] for t in trk]
tr = [d["ret_trk"].get(t, 0) for t in trk]
fig, ax = plt.subplots(figsize=(3.6, 2.4))
x = range(len(trk))
ax.bar([i - 0.2 for i in x], tv, 0.4, color=ORANGE, label="Deliveries")
ax.bar([i + 0.2 for i in x], tr, 0.4, color=DARK, label="Returns")
ax.set_xticks(list(x))
ax.set_xticklabels([f"T{t}" for t in trk])
ax.legend(frameon=False, fontsize=7)
ax.set_title("Movements per track", loc="left", fontsize=9, fontweight="bold")
imgs["trk"] = b64(fig)

occ1 = sorted(h[1] * 100 for h in d["hourly"])
n = len(occ1)
xs = [100 * i / n for i in range(n)]
random.seed(42)
base = [h[1] for h in d["hourly"]]
perm = base[:]
random.shuffle(perm)
sB = sorted(min(100, 100 * (a + b)) for a, b in zip(base, perm))
sA = sorted(min(100, 200 * a) for a in base)
sC = sorted(min(100, 150 * a) for a in base)
fig, ax = plt.subplots(figsize=(7.4, 2.8))
ax.plot(xs, occ1, color=DARK, lw=1.6, label="Current (1 corrugator)")
ax.plot(xs, sC, color=GREY, lw=1.2, label="+ corrugator at 50 % (synchronous)")
ax.plot(xs, sB, color=ORANGE, lw=1.4, ls="--", label="+ equal corrugator (independent)")
ax.plot(xs, sA, color=ORANGE, lw=1.6, label="+ equal corrugator (synchronous)")
ax.axhline(85, color="#999", ls=":", lw=1)
ax.text(55, 87, "saturation threshold 85 %", fontsize=7, color="#666")
ax.set_xlabel("% of operating hours (sorted by increasing occupancy)")
ax.set_ylabel("hourly occupancy %")
ax.set_ylim(0, 102)
ax.legend(frameon=False, fontsize=7, loc="upper left", bbox_to_anchor=(0.0, 0.80))
ax.set_title("Occupancy duration curve — second-corrugator scenarios", loc="left", fontsize=9, fontweight="bold")
imgs["scen"] = b64(fig)

(W / "mastercorr_imgs_en.json").write_text(json.dumps(imgs), encoding="utf-8")
print("charts", len(imgs), sum(len(v) for v in imgs.values()) // 1024, "kB")
