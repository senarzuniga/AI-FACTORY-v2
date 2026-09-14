"""Build the INGECART-format capacity report for the INGETRANS at Mastercorr from the 90-day transfer log.

Inputs: mastercorr_summary.json, mastercorr_scenarios.json, mastercorr_imgs.json (session workspace).
Style: <style> block of the INGECART technical document + embedded logo, as in the Smart product report.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import build_ingetrans_smart_report_r2 as r2  # noqa: E402  (reference_style, embedded_logo)

W = Path(r"C:\Users\isena\.copilot\session-state\b750502e-8645-40b5-bb33-37f54fafeb4f\files")
OUT = [
    Path(r"C:\Users\isena\Documents\INGECART\PRODUCTO\INGETRANS\DATOS OPERATIVOS MASTERCORR 20 08 2026\INGETRANS_MASTERCORR_CAPACITY_REPORT_90D_2026-09-14.html"),
    Path(r"C:\Users\isena\Documents\GitHub\AI-FACTORY-v2\INGETRANS_MASTERCORR_CAPACITY_REPORT_90D_2026-09-14.html"),
]

d = json.loads((W / "mastercorr_summary.json").read_text(encoding="utf-8"))
s = json.loads((W / "mastercorr_scenarios.json").read_text(encoding="utf-8"))
imgs = json.loads((W / "mastercorr_imgs.json").read_text(encoding="utf-8"))


def pc(x, dec=1):
    return f"{100*x:.{dec}f} %".replace(".", ",")


def n(x, dec=0):
    return f"{x:,.{dec}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def sec(num, title, dark=False):
    return f'<div class="sec{" k" if dark else ""}"><span class="n">{num}</span>{title}</div>'


def table(headers, rows, fcw=None):
    th = "".join(f"<th>{h}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f'<td{" style=\"width:%s\"" % fcw if (i == 0 and fcw) else ""}>{c}</td>' for i, c in enumerate(r)) + "</tr>" for r in rows)
    return f"<table><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table>"


mk = d["mission_kinds"]
ks = d["kind_stats"]
peaks = d["peaks"]
wd_names = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
weekly = d["weekly"]

html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>INGECART · INGETRANS Mastercorr — Informe de capacidad y saturación (90 días)</title>
{r2.reference_style()}
<style>
.chart {{ width:100%; margin:0 0 3mm 0; }}
.chart-half {{ width:100%; }}
</style>
</head>
<body>
<div class="screen-note"><b>Vista previa en navegador.</b> El PDF aplica la banda de cabecera y el pie corporativo de cada página.</div>

<img src="{r2.embedded_logo()}" class="cover-logo" alt="INGECART">
<div class="cover-kicker">Informe de análisis operativo</div>
<div class="cover-title">INGETRANS Mastercorr<br>Capacidad, saturación y reserva</div>
<div class="cover-rule"></div>
<div class="cover-sub">
Análisis de 90 días de registros de estado del carro transfer INGETRANS instalado en Mastercorr
(16 de junio a 14 de septiembre de 2026), con evaluación de la capacidad disponible para atender una
segunda corrugadora en paralelo.
</div>
<div class="cover-claim">
<b>Conclusión en una frase.</b> El INGETRANS trabaja hoy al {pc(d['util_operating'])} de su tiempo operativo y absorbe
picos horarios de hasta el {pc(d['occ_max'])}. Puede atender una segunda corrugadora si la nueva demanda no coincide en
punta con la actual; una segunda corrugadora de igual cadencia y ritmo sincronizado llevaría al carro a saturación
en el {pc(s['A']['sat'])} de las horas y exigiría medidas de secuenciación o un segundo carro.
</div>

<table class="meta" style="margin-top:8mm"><tbody>
<tr><td>Cliente</td><td>Mastercorr</td><td>Nº documento</td><td>IT-MC-CAP-2026-09 · Rev. 1</td></tr>
<tr><td>Equipo</td><td>INGETRANS — carro transfer de bobinas, 5 splicers, 10 vías, estaciones A/B</td><td>Fecha</td><td>14/09/2026</td></tr>
<tr><td>Fuente de datos</td><td>Transfer status-data-2026-09-14 16_36_49.csv — {n(d['events'])} eventos de estado del PLC</td><td>Periodo</td><td>{d['start'][:10]} → {d['end'][:10]} ({d['span_days']:.1f} días)</td></tr>
<tr><td>Método</td><td>Reconstrucción de intervalos de estado, misiones y ocupación horaria; corrección de estados congelados</td><td>Emisor</td><td>INGECART · Ingeniería de Producto</td></tr>
</tbody></table>

<div class="pb"></div>
{sec("01", "Resumen ejecutivo")}
<table class="kpi-wrap"><tr>
<td><span class="kpi-v">{pc(d['util_operating'],0)}</span><span class="kpi-l">Ocupación media en horas operativas</span></td>
<td><span class="kpi-v">{pc(d['occ_p95'],0)}</span><span class="kpi-l">Ocupación horaria P95</span></td>
<td><span class="kpi-v">{pc(d['occ_max'],0)}</span><span class="kpi-l">Pico horario máximo</span></td>
<td><span class="kpi-v">{n(d['deliveries'])}</span><span class="kpi-l">Bobinas entregadas a splicers</span></td>
</tr></table>
<table class="two"><tr><td class="l" style="width:50%">
<span class="tag">Qué se ha medido</span>
<p>El PLC registra cada cambio de estado del carro (recogida, entrega, carga/descarga en almacén y "No Task").
Se han reconstruido <b>{n(d['missions'])} misiones</b> (secuencias de trabajo entre dos estados de reposo) y
<b>{n(d['deliveries'])} entregas</b> de bobina a splicer en {d['span_days']:.0f} días, con {n(d['returns'])} retornos de
bobina parcial al almacén.</p>
<span class="tag o">Cuánto trabaja el carro</span>
<p>Tiempo productivo del carro: <b>{n(d['prod_busy_h'],0)} h</b> sobre {n(d['op_h'],0)} h de planta operativa
(excluidas {d['stops_n']} paradas de planta de más de 6 h que suman {n(d['stops_h'],0)} h). Ocupación media
<b>{pc(d['util_operating'])}</b>; mediana horaria {pc(d['occ_p50'])}; el 90 % de las horas operativas queda por debajo del
{pc(d['occ_p90'],0)}.</p>
</td><td style="width:50%">
<span class="tag">Picos</span>
<p>Pico horario {pc(d['occ_max'])} ({peaks['1'][1][:16]}); pico sostenido de 4 h {pc(peaks['4'][0])}; pico de turno (8 h)
{pc(peaks['8'][0])}; día más cargado {n(d['daily_busy_max'],1)} h de carro y {d['del_day_max']} bobinas entregadas.
Máximo de {d['best60']} misiones en 60 minutos frente a una media de {d['miss_h_mean']:.1f}.</p>
<span class="tag o">Reserva de capacidad</span>
<p>Con la misión media de {n(d['mission_mean'])} s, el carro puede ejecutar unas {s['cap_mean']:.0f} misiones/h al 85 % de
ocupación; hoy ejecuta {d['miss_h_mean']:.1f} de media y {d['miss_h_p95']} en P95. <b>Existe reserva para duplicar la
demanda media</b>, pero no para duplicar las puntas si coinciden en el tiempo.</p>
</td></tr></table>
<div class="callout orange">
<b>Segunda corrugadora.</b> Viable en términos de capacidad media con la infraestructura actual. La decisión depende del
solape de puntas: con demanda independiente (Monte Carlo) la ocupación P95 sube a {pc(s['B']['p95'],0)} y las horas saturadas
son el {pc(s['B']['sat'])}; con demanda sincronizada, P95 = 100 % y {pc(s['A']['sat'])} de horas saturadas. Se recomienda
secuenciación coordinada de cambios de bobina y, si la segunda corrugadora es de igual cadencia, prever un segundo carro
o INGETRANS Smart como refuerzo (ver §07).
</div>

<div class="pb"></div>
{sec("02", "Base de datos y método")}
{table(["Concepto", "Valor", "Observación"], [
    ["Eventos de estado", n(d['events']), "Un registro por cambio de estado del carro; 36 estados distintos"],
    ["Periodo", f"{d['start']} → {d['end']}", f"{d['span_days']:.1f} días naturales"],
    ["Estados de reposo", "'No Task' y código '58'", f"'58' aparece 14 veces (diagnóstico), tratado como reposo"],
    ["Paradas de planta", f"{d['stops_n']} huecos de reposo > 6 h · {n(d['stops_h'],0)} h", "Excluidas del tiempo operativo (fines de semana, paradas)"],
    ["Estados congelados", f"{d['frozen_n']} pasos de tarea > 15 min · {n(d['frozen_h'],0)} h", "Carro con tarea activa durante paradas o incidencias (máx. 37,5 h el 15/08). Recortados a 15 min para la ocupación productiva y reportados aparte como indisponibilidad"],
    ["Tiempo operativo de planta", f"{n(d['op_h'],0)} h", "Periodo − paradas > 6 h − tiempo congelado"],
    ["Horas analizadas", f"{n(d['hours'])} h", "Horas completas dentro del tiempo operativo"],
    ["Misión", "Secuencia de pasos entre dos reposos", "Duración medida como suma de pasos productivos"],
], fcw="40mm")}
<p class="note">Los estados congelados de larga duración no representan trabajo del carro: corresponden a periodos en que la
tarea quedó activa en el PLC durante una parada de planta o una incidencia. Se cuantifican como <b>indisponibilidad con tarea
activa</b> y merecen análisis separado con el registro de alarmas. Sin esta corrección la ocupación bruta sería del
{pc(d['raw_busy_h']*3600/(d['op_h']*3600+d['frozen_h']*3600))}, valor no representativo.</p>

{sec("03", "Actividad y volumen movido")}
<img class="chart" src="{imgs['daily']}" alt="Actividad diaria">
{table(["Indicador", "Valor", "Base"], [
    ["Misiones totales", n(d['missions']), f"{d['miss_h_mean']:.1f}/h de media en horas operativas; P95 {d['miss_h_p95']}/h; máximo {d['miss_h_max']}/h (24 en 60 min deslizantes)"],
    ["Entregas a splicer", n(d['deliveries']), f"{d['del_h_mean']:.1f}/h de media; P95 {d['del_h_p95']}/h; máximo {d['del_h_max']}/h"],
    ["Retornos de bobina parcial", n(d['returns']), f"{100*d['returns']/d['deliveries']:.0f} % de las entregas vuelven parcialmente; alta rotación de anchos"],
    ["Cargas desde almacén", n(d['loads']), "Recogida en zona de intercambio (Loading)"],
    ["Descargas al almacén", n(d['unloads']), "Depósito en zona de intercambio (Unloading)"],
    ["Cargas y descargas combinadas", n(d['combos']), "Ciclo doble en la estación de intercambio"],
    ["Días con actividad", d['days'], f"{d['daily_busy_mean']:.1f} h de carro/día de media; máximo {d['daily_busy_max']:.1f} h"],
    ["Bobinas entregadas por día", f"{d['del_day_mean']:.0f} media · {d['del_day_p90']} P90 · {d['del_day_max']} máx.", "Días con actividad"],
], fcw="44mm")}
<h3 class="sub">Tipos de misión</h3>
{table(["Tipo", "Misiones", "Duración mediana", "P90"], [
    ["Entrega de bobina a splicer", n(mk['deliver reel to splicer']), f"{ks['deliver reel to splicer']['med']:.0f} s", f"{ks['deliver reel to splicer']['p90']:.0f} s"],
    ["Retorno de bobina al almacén", n(mk['return reel to warehouse']), f"{ks['return reel to warehouse']['med']:.0f} s", f"{ks['return reel to warehouse']['p90']:.0f} s"],
    ["Combinada (retorno + entrega)", n(mk['return + deliver (combined)']), f"{ks['return + deliver (combined)']['med']:.0f} s", f"{ks['return + deliver (combined)']['p90']:.0f} s"],
    ["Solo manipulación en almacén", n(mk['warehouse handling only']), f"{ks['warehouse handling only']['med']:.0f} s", f"{ks['warehouse handling only']['p90']:.0f} s"],
    ["<b>Todas</b>", f"<b>{n(d['missions'])}</b>", f"<b>{d['mission_med']:.0f} s</b>", f"<b>{d['mission_p90']:.0f} s</b> (P95 {d['mission_p95']:.0f} s)"],
], fcw="52mm")}
<div class="callout">
<b>Lectura.</b> Solo el {100*mk['return + deliver (combined)']/d['missions']:.0f} % de las misiones combina retorno y entrega en el mismo viaje.
La mayoría de retornos se ejecutan como misión independiente: hay margen para reducir movimientos combinando
retorno y entrega cuando el splicer libera una bobina parcial y solicita la siguiente.
</div>

<div class="pb"></div>
{sec("04", "Ocupación, saturación y picos")}
<table class="two"><tr><td class="l" style="width:50%"><img class="chart-half" src="{imgs['hist']}" alt="Histograma"></td>
<td style="width:50%"><img class="chart-half" src="{imgs['hod']}" alt="Perfil horario"></td></tr></table>
{table(["Métrica de ocupación horaria", "Valor", "Interpretación"], [
    ["Media (horas operativas)", pc(d['occ_mean']), "Carro ocupado 1 de cada 5 minutos operativos"],
    ["Mediana (P50)", pc(d['occ_p50']), "La mitad de las horas está por debajo"],
    ["P75 / P90", f"{pc(d['occ_p75'])} / {pc(d['occ_p90'])}", "Rango habitual de horas cargadas"],
    ["P95 / P99", f"{pc(d['occ_p95'])} / {pc(d['occ_p99'])}", "Puntas de cambio de pedido y retornos acumulados"],
    ["Máximo", f"{pc(d['occ_max'])} ({peaks['1'][1][:16]})", "Ninguna hora alcanza el umbral de saturación del 85 %"],
    ["Horas > 50 % / > 70 % / > 85 %", f"{d['h_gt50']} / {d['h_gt70']} / {d['h_gt85']} de {n(d['hours'])}", f"{100*d['h_gt50']/d['hours']:.1f} % de horas por encima del 50 %"],
    ["Pico sostenido 4 h / 8 h / 24 h", f"{pc(peaks['4'][0])} / {pc(peaks['8'][0])} / {pc(peaks['24'][0])}", f"Turno más cargado: {peaks['8'][1][:16]}"],
    ["Semana más cargada", f"{pc(peaks['168'][0])}", f"Semana desde {peaks['168'][1][:10]}"],
], fcw="52mm")}
<h3 class="sub">Perfil semanal</h3>
{table(["Día", "Ocupación media"] , [[wd_names[int(k)], pc(v)] for k, v in sorted(d['wd'].items(), key=lambda kv: int(kv[0]))], fcw="30mm")}
<p class="note">Perfil plano entre lunes y viernes ({pc(min(v for k,v in d['wd'].items() if int(k)<5))}–{pc(max(v for k,v in d['wd'].items() if int(k)<5))}); sábado
{pc(d['wd']['5'])}; domingo sin actividad significativa. Por hora del día, la banda 01:00–03:00 concentra la mayor ocupación
({pc(max(d['hod_list']))}), coherente con cambios de pedido del turno de noche.</p>
<h3 class="sub">Días de mayor carga</h3>
{table(["Fecha", "Horas de carro", "Bobinas entregadas", "Misiones"], [[t[0], f"{t[1]:.1f} h", t[2], t[3]] for t in d['top_days']], fcw="30mm")}

<div class="pb"></div>
{sec("05", "Distribución por splicer y vía")}
<table class="two"><tr><td class="l" style="width:50%"><img class="chart-half" src="{imgs['spl']}" alt="Splicers"></td>
<td style="width:50%"><img class="chart-half" src="{imgs['trk']}" alt="Vías"></td></tr></table>
{table(["Splicer", "Entregas", "Retornos", "% entregas", "Observación"], [
    [f"Splicer {k}", n(d['deliv_spl'][k]), n(d['ret_spl'].get(k, 0)), pc(d['deliv_spl'][k]/d['deliveries']), obs]
    for k, obs in zip(sorted(d['deliv_spl'], key=int), [
        "Casi sin entregas automáticas y 480 retornos: el splicer 1 se alimenta por otra vía (carga manual o directa) y el INGETRANS solo retira bobinas",
        "Splicer más demandante", "Segundo en demanda", "Demanda media", "Demanda baja; retornos superan a las entregas"])
], fcw="24mm")}
{table(["Vía", "Entregas", "Retornos"], [[f"Track {t}", n(d['deliv_trk'][t]), n(d['ret_trk'].get(t, 0))] for t in sorted(d['deliv_trk'], key=int)], fcw="24mm")}
<div class="callout">
<b>Hallazgos.</b> (1) Los splicers 2 y 3 concentran el {pc((d['deliv_spl']['2']+d['deliv_spl']['3'])/d['deliveries'],0)} de las entregas;
son el cuello de botella de secuenciación. (2) El splicer 1 recibe {d['deliv_spl']['1']} entregas frente a {d['ret_spl']['1']} retornos:
su alimentación no pasa por el INGETRANS y conviene confirmar si es una decisión operativa o una limitación de layout.
(3) La estación B se usa un {100*(d['stB']-d['stA'])/d['stA']:.0f} % más que la A ({n(d['stB'])} frente a {n(d['stA'])} eventos), lo que
indica asimetría en el uso de las dos posiciones del carro y margen para equilibrar viajes dobles.
</div>

{sec("06", "Disponibilidad e incidencias observables")}
{table(["Indicador", "Valor", "Comentario"], [
    ["Paradas de planta (> 6 h sin tarea)", f"{d['stops_n']} · {n(d['stops_h'],0)} h", "Fines de semana y paradas programadas; no imputables al INGETRANS"],
    ["Estados congelados con tarea activa", f"{d['frozen_n']} · {n(d['frozen_h'],0)} h", "El carro quedó en estado de tarea sin completar. Casos mayores: 15/08 (37,5 h, Splicer 2 Track 4), 09/09 (27,3 h, Splicer 4 Track 8), 11/09 (12,4 h, Splicer 3 Track 6)"],
    ["Pasos de tarea de 5 a 15 min", "184 · 25 h", "Interfaces lentas o esperas en estación; candidatos a revisión de handshake con vías"],
    ["Paso de tarea mediano", f"{d['step_median']:.0f} s", f"Media {d['step_mean']:.0f} s; distribución muy asimétrica"],
    ["Hueco entre misiones (reposo) mediano", f"{d['gap_med']:.0f} s", f"P10 {d['gap_p10']:.0f} s: en el 10 % de los casos la siguiente misión arranca casi de inmediato"],
], fcw="52mm")}
<p class="note">Los estados congelados deben cruzarse con el registro de alarmas y modo manual/automático del PLC para separar
paradas de planta con tarea pendiente, intervenciones manuales y fallos del equipo. Su duración total ({n(d['frozen_h'],0)} h) equivale
al {pc(d['frozen_h']/(d['op_h']+d['frozen_h']))} del tiempo operativo ampliado y es el principal indicador de disponibilidad a vigilar.</p>

<div class="pb"></div>
{sec("07", "Capacidad para una segunda corrugadora")}
<p class="lead">La pregunta no es si el carro tiene tiempo libre —lo tiene, cuatro de cada cinco minutos— sino si puede
absorber las <b>puntas simultáneas</b> de dos corrugadoras sin retrasar cambios de bobina. Se han superpuesto sobre la demanda
horaria real tres escenarios de segunda corrugadora.</p>
<img class="chart" src="{imgs['scen']}" alt="Escenarios">
{table(["Escenario", "Ocupación media", "P95 horaria", "P99 horaria", "Horas saturadas (≥ 85 %)", "Lectura"], [
    ["Actual — una corrugadora", pc(d['occ_mean']), pc(d['occ_p95']), pc(d['occ_p99']), f"{d['h_gt85']} ({pc(d['h_gt85']/d['hours'])})", "Sin saturación"],
    ["A · Segunda corrugadora igual, puntas sincronizadas (peor caso)", pc(s['A']['mean']), pc(s['A']['p95']), pc(s['A']['p99']), f"{s['A']['h_sat']} ({pc(s['A']['sat'])})", f"Saturación 1 de cada 10 horas; {s['deferred_A']:.0f} h de trabajo diferido en 90 días"],
    ["B · Segunda corrugadora igual, puntas independientes (Monte Carlo)", pc(s['B']['mean']), pc(s['B']['p95']), pc(s['B']['p99']), pc(s['B']['sat']), "Saturación ocasional; gestionable con prioridades"],
    ["C · Segunda corrugadora al 50 % de cadencia, sincronizada", pc(s['C']['mean']), pc(s['C']['p95']), pc(s['C']['p99']), pc(s['C']['sat']), "Margen suficiente"],
], fcw="52mm")}
<h3 class="sub">Capacidad teórica del carro</h3>
{table(["Parámetro", "Valor", "Base"], [
    ["Duración media de misión", f"{n(d['mission_mean'])} s", "Pasos productivos, sin congelados"],
    ["Duración P95 de misión", f"{n(d['mission_p95'])} s", "Misiones con esperas en estación"],
    ["Capacidad al 85 % con misión media", f"{s['cap_mean']:.0f} misiones/h", "Techo práctico de secuenciación"],
    ["Capacidad al 85 % con misión P95", f"{s['cap_p95']:.0f} misiones/h", "Techo conservador si todas las misiones fueran lentas"],
    ["Demanda actual", f"{d['miss_h_mean']:.1f} misiones/h media · {d['miss_h_p95']} P95 · {d['miss_h_max']} máx.", "Horas operativas"],
    ["Demanda con dos corrugadoras iguales", f"{2*d['miss_h_mean']:.1f} media · hasta {2*d['miss_h_p95']} en P95 sincronizado", "Supera el techo conservador en punta"],
], fcw="52mm")}
<div class="callout orange">
<b>Dictamen.</b> El INGETRANS actual <b>puede gestionar una segunda corrugadora</b> si se cumple una de estas condiciones:
(a) la nueva corrugadora tiene una cadencia igual o inferior a la mitad de la actual; o (b) siendo de cadencia similar, los
cambios de bobina de ambas máquinas se secuencian desde el MES para no coincidir en punta, y se aceptan tiempos de
entrega P95 superiores a los actuales en un 3–4 % de las horas. Si la segunda corrugadora es de igual cadencia y no se
puede coordinar la secuencia, el escenario sincronizado satura el carro el 10 % de las horas y penaliza directamente la
disponibilidad de la corrugadora: en ese caso se recomienda un segundo carro (INGETRANS o INGETRANS Smart en el
corredor de la nueva máquina).
</div>

{sec("08", "Recomendaciones")}
<table class="plain"><tbody>
<tr><td style="width:14mm"><span class="big-num">1</span></td><td><b>Secuenciación de cambios de bobina.</b> Coordinar desde el MES las peticiones de las dos corrugadoras con anticipación (staging) para evitar la coincidencia de puntas; es la medida de mayor efecto y menor coste.</td></tr>
<tr><td><span class="big-num">2</span></td><td><b>Misiones combinadas.</b> Elevar del {100*mk['return + deliver (combined)']/d['missions']:.0f} % actual la proporción de viajes que retiran una bobina parcial y entregan la siguiente en el mismo ciclo; reduce misiones y libera capacidad para la segunda máquina.</td></tr>
<tr><td><span class="big-num">3</span></td><td><b>Equilibrio de estaciones A/B.</b> Analizar la asimetría de uso ({n(d['stB'])} frente a {n(d['stA'])} eventos) para aprovechar el transporte doble.</td></tr>
<tr><td><span class="big-num">4</span></td><td><b>Splicer 1.</b> Confirmar por qué no recibe entregas automáticas ({d['deliv_spl']['1']} en 90 días) y si integrarlo aumentaría la demanda del carro.</td></tr>
<tr><td><span class="big-num">5</span></td><td><b>Disponibilidad.</b> Investigar los {d['frozen_n']} estados congelados ({n(d['frozen_h'],0)} h) cruzando con alarmas y modo manual; definir un timeout de tarea y un código de causa en el PLC.</td></tr>
<tr><td><span class="big-num">6</span></td><td><b>Simulación previa a la decisión.</b> Ejecutar el gemelo digital INGECART con el perfil real de la segunda corrugadora (cadencia, anchos, horarios) sobre este registro para fijar el P95 de entrega contractual antes de comprometer la solución de un solo carro.</td></tr>
<tr><td><span class="big-num">7</span></td><td><b>Instrumentación.</b> Añadir al registro los tiempos de petición (request-to-delivery), causa de parada y estado de batería/energía según la especificación de captura de datos INGECART, para medir starvation de forma directa.</td></tr>
</tbody></table>

{sec("A", "Anexo — Evolución semanal", dark=True)}
{table(["Semana ISO", "Bobinas entregadas", "Horas productivas del carro"], [[f"S{w}", n(c), f"{h:.1f} h"] for w, c, h in weekly], fcw="30mm")}
<p class="note">Las semanas 25 y 37 son parciales. Documento emitido por INGECART · Ingeniería de Producto. Los resultados derivan
exclusivamente del registro de estado del PLC; no incluyen datos de producción de la corrugadora ni de alarmas. Rev. 1 — 14/09/2026.</p>
</body>
</html>
"""

for out in OUT:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print("written", out, len(html))
