"""Derive the English chart generator from the Spanish one by replacing label literals (UTF-8 safe)."""

from pathlib import Path

SRC = Path(r"C:\Users\isena\Documents\GitHub\AI-FACTORY-v2\tools\proposals\build_mastercorr_capacity_charts.py")
DST = Path(r"C:\Users\isena\Documents\GitHub\AI-FACTORY-v2\tools\proposals\build_mastercorr_capacity_charts_en.py")

R = {
    '"Horas productivas del carro"': '"Productive carriage hours"',
    '"h/día"': '"h/day"',
    '"Bobinas entregadas"': '"Reels delivered"',
    '"bobinas/día"': '"reels/day"',
    '"Actividad diaria del INGETRANS — 16 jun a 14 sep 2026"': '"INGETRANS daily activity — 16 Jun to 14 Sep 2026"',
    '"saturación 85 %"': '"saturation 85 %"',
    '"Ocupación horaria (%)"': '"Hourly occupancy (%)"',
    '"horas"': '"hours"',
    '"Distribución de ocupación horaria"': '"Hourly occupancy distribution"',
    '"Hora del día"': '"Hour of day"',
    '"ocupación media %"': '"mean occupancy %"',
    '"Perfil por hora del día"': '"Hour-of-day profile"',
    '"Entregas"': '"Deliveries"',
    '"Retornos"': '"Returns"',
    '"Movimientos por splicer (90 días)"': '"Movements per splicer (90 days)"',
    '"Movimientos por vía"': '"Movements per track"',
    '"Actual (1 corrugadora)"': '"Current (1 corrugator)"',
    '"+ corrugadora al 50 % (sincrónica)"': '"+ corrugator at 50 % (synchronous)"',
    '"+ corrugadora igual (independiente)"': '"+ equal corrugator (independent)"',
    '"+ corrugadora igual (sincrónica)"': '"+ equal corrugator (synchronous)"',
    '"umbral de saturación 85 %"': '"saturation threshold 85 %"',
    '"% de horas operativas (ordenadas de menor a mayor ocupación)"': '"% of operating hours (sorted by increasing occupancy)"',
    '"ocupación horaria %"': '"hourly occupancy %"',
    '"Curva de duración de ocupación — escenarios de segunda corrugadora"': '"Occupancy duration curve — second-corrugator scenarios"',
    '(W / "mastercorr_imgs.json")': '(W / "mastercorr_imgs_en.json")',
}

s = SRC.read_text(encoding="utf-8")
missing = [k for k in R if k not in s]
if missing:
    raise SystemExit(f"missing literals: {missing}")
for a, b in R.items():
    s = s.replace(a, b)
DST.write_text(s, encoding="utf-8")
print("english chart script written")
