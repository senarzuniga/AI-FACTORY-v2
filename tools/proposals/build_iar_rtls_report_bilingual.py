"""Build the bilingual (ES/EN) INGECART report: IAR Real-Time Roll Location for corrugated warehouses,
based on the MTorres offer 26-05-073V0 with the IAR technical improvements.

Sources analysed (INGECART/PRODUCTO/GESTION DE ALMACEN GPS/ALMACEN INTELIGENTE):
- Of. 26-05-073V0 (Ingecart) Real Time Warehouse Management.pdf (MTorres)
- IAR/IAR_EXECUTIVE_TECHNICAL_ASSESSMENT_REPORT.html
- IAR/RTLS-UWD Documento tecnico_v2.pdf
- IAR/Pozyx_, Sewio_, Eliko_, GrowSpace_Evaluacion_RTLS.pdf, Precios_Eliko.pdf, Eliko_Kit_Alquiler.pdf
Public benchmarks accessed 2026-09-14 (Sewio, Eliko, Pozyx, omlox/PI, ETSI, EUR-Lex).
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import build_ingetrans_smart_report_r2 as r2  # noqa: E402  (reference_style, embedded_logo)

OUT = [
    Path(r"C:\Users\isena\Documents\INGECART\PRODUCTO\GESTION DE ALMACEN GPS\ALMACEN INTELIGENTE\IAR_REAL_TIME_ROLL_LOCATION_REPORT_ES-EN_2026-09-14.html"),
    Path(r"C:\Users\isena\Documents\GitHub\AI-FACTORY-v2\IAR_REAL_TIME_ROLL_LOCATION_REPORT_ES-EN_2026-09-14.html"),
]

SWITCH_CSS = """
<style>
.lang.hidden { display: none; }
.lang-switch { position: fixed; top: 10mm; right: 6mm; z-index: 100; display: flex; gap: 2px; background: #111; padding: 2px; border-radius: 3px; }
.lang-switch button { font-family: Arial, Helvetica, sans-serif; font-size: 8pt; font-weight: bold; letter-spacing: 1pt; color: #ddd; background: transparent; border: 0; padding: 2.2mm 3.4mm; cursor: pointer; text-transform: uppercase; }
.lang-switch button.active { background: #FF6304; color: #fff; }
@media print { .lang-switch { display: none; } }
.src { font-size: 6.9pt; color: #777; }
</style>
"""
SWITCH_HTML = """
<div class="lang-switch" role="tablist" aria-label="Idioma / Language">
  <button type="button" class="active" data-language="es" aria-pressed="true">ES</button>
  <button type="button" data-language="en" aria-pressed="false">EN</button>
</div>
"""
SWITCH_JS = """
<script>
(function () {
  var buttons = document.querySelectorAll('[data-language]');
  var blocks = document.querySelectorAll('.lang');
  function apply(lang) {
    blocks.forEach(function (b) { b.classList.toggle('hidden', !b.classList.contains('lang-' + lang)); });
    buttons.forEach(function (btn) { var on = btn.dataset.language === lang; btn.classList.toggle('active', on); btn.setAttribute('aria-pressed', String(on)); });
    document.documentElement.setAttribute('lang', lang);
    try { localStorage.setItem('iar_report_lang', lang); } catch (e) {}
  }
  buttons.forEach(function (btn) { btn.addEventListener('click', function () { apply(btn.dataset.language); }); });
  var saved = null; try { saved = localStorage.getItem('iar_report_lang'); } catch (e) {}
  var q = (location.search.match(/[?&]lang=(es|en)/) || [])[1];
  apply(q || saved || 'es');
})();
</script>
"""


def sec(n, title, dark=False):
    return f'<div class="sec{" k" if dark else ""}"><span class="n">{n}</span>{title}</div>'


def table(headers, rows, fcw=None):
    th = "".join(f"<th>{h}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f'<td{" style=\"width:%s\"" % fcw if (i == 0 and fcw) else ""}>{c}</td>' for i, c in enumerate(r)) + "</tr>" for r in rows)
    return f"<table><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table>"


LOGO = r2.embedded_logo()

# ------------------------------------------------------------------ SPANISH BODY
ES = f"""
<img src="{LOGO}" class="cover-logo" alt="INGECART">
<div class="cover-kicker">Informe técnico de producto</div>
<div class="cover-title">IAR · Localización en tiempo real<br>de bobinas de papel</div>
<div class="cover-rule"></div>
<div class="cover-sub">
Evolución de la solución de gestión de almacén de bobinas en tiempo real: de la oferta base MTorres
(Of. 26-05-073V0, RTLS de 160 anclas y 3.000 tags con TorresFactory) a la arquitectura IAR de INGECART:
UWB-first con eje Z real, checkpoints RFID de identidad, capa de abstracción de proveedor e integración
MES/WMS preparada para gemelo digital.
</div>
<div class="cover-claim">
<b>Misma función, más precisión, menos dependencia.</b><br>
Localización a nivel de hueco (10–30 cm) en lugar de zona (50 cm, 20–30 zonas), identidad confirmada por RFID
en cada evento crítico, proveedor de radio intercambiable y un TCO a 10 años entre un 26 % y un 50 % inferior
en las arquitecturas recomendadas.
</div>
<table class="meta" style="margin-top:8mm"><tbody>
<tr><td>Producto</td><td>IAR — Intelligent Automatic Roll location (almacén inteligente de bobinas)</td><td>Nº documento</td><td>IAR-RPT-2026-09 · Rev. 1</td></tr>
<tr><td>Base de referencia</td><td>Oferta MTorres Of. 26-05-073V0 — Real Time Warehouse Management Solution</td><td>Fecha</td><td>14/09/2026</td></tr>
<tr><td>Caso de aplicación</td><td>Almacén no automatizado de 80 × 50 m (≈ 4.000 m²), ≈ 3.000 bobinas verticales Ø 1.600 mm apiladas a 3 alturas, techo ≤ 12 m</td><td>Estado</td><td>Definición de producto para decisión · sujeto a benchmark en planta</td></tr>
<tr><td>Fuentes</td><td>Oferta MTorres; IAR Executive Technical Assessment; RTLS-UWB documento técnico v2; fichas Pozyx, Sewio, Eliko, GrowSpace; precios Eliko; fuentes públicas (acceso 14/09/2026)</td><td>Emisor</td><td>INGECART · Ingeniería de Producto</td></tr>
</tbody></table>

<div class="pb"></div>
{sec("01", "Resumen ejecutivo")}
<table class="kpi-wrap"><tr>
<td><span class="kpi-v">10–30 cm</span><span class="kpi-l">Precisión UWB (frente a 50 cm)</span></td>
<td><span class="kpi-v">3D real</span><span class="kpi-l">Eje Z para bobinas apiladas</span></td>
<td><span class="kpi-v">−26 a −50 %</span><span class="kpi-l">TCO a 10 años vs oferta base</span></td>
<td><span class="kpi-v">≈ 1 año</span><span class="kpi-l">Payback estimado</span></td>
</tr></table>
<table class="two"><tr><td class="l" style="width:50%">
<span class="tag">Punto de partida</span>
<p>La oferta MTorres resuelve la visibilidad del almacén con un RTLS de 160 anclas PoE en columnas, 3.000 tags en
insertos de mandril de 4", precisión declarada de hasta 50 cm, 20–30 zonas lógicas por geofencing y la plataforma
TorresFactory con integración MES/SAP. Precio 509.946 € EXW y licencia de 69.000 €/año a partir del quinto año.
Instalación 3 técnicos × 3 semanas y puesta en marcha 12 semanas.</p>
<span class="tag o">Qué cambia IAR</span>
<p>INGECART mantiene el alcance funcional y sustituye la caja cerrada por una arquitectura <b>UWB-first</b> con anclas
a distintas alturas para <b>3D real</b>, <b>checkpoints RFID</b> en recepción, retorno y consumo, una <b>capa de abstracción
de proveedor</b> (omlox/MQTT) que evita el bloqueo tecnológico, y un motor de posición con confianza, filtrado y
diagnóstico. El resultado es localización a nivel de hueco, identidad verificada y libertad de proveedor.</p>
</td><td style="width:50%">
<span class="tag">Cuantificación</span>
<p>Para el almacén de referencia, el beneficio anual estimado pasa de ≈ 340 k€ (base) a ≈ 448 k€ (IAR): menos
tiempo de búsqueda (216 k€), menos bobinas erróneas (80 k€), menor stock de seguridad (47 k€) y recuperación de
retales no trazados (104 k€). El TCO a 10 años baja de 855 k€ a 631 k€ (clase Pozyx) o 429 k€ (clase GrowSpace).</p>
<span class="tag o">Decisión recomendada</span>
<p>Piloto comparativo en el mismo almacén con dos proveedores UWB (Pozyx y GrowSpace) durante 6–8 semanas,
con bobinas reales y turno completo, midiendo precisión X/Y/Z, latencia, disponibilidad y consistencia MES;
adjudicación tras normalizar el TCO a 5 y 10 años.</p>
</td></tr></table>
<div class="callout orange">
<b>Advertencia de rigor.</b> Las cifras de precisión son declaraciones de fabricante (10–30 cm Pozyx; 30 cm Sewio;
30 cm ± 20 cm Eliko) y no tolerancias garantizadas en un almacén con metal, apilado y oclusión. Las cifras económicas
de valor se basan en supuestos explícitos (§07) que deben sustituirse por los datos del cliente en el estudio de aplicación.
</div>

<div class="pb"></div>
{sec("02", "La oferta base MTorres: qué incluye y qué limita")}
{table(["Bloque", "Contenido de la oferta 26-05-073V0", "Observación de ingeniería"], [
    ["Área y alcance", "Almacén no automatizado 80 × 50 m (≈ 4.000 m²), techo ≤ 12 m, ≈ 3.000 bobinas Ø 1.600 mm a 3 alturas; solo identificación, tracking, trazabilidad y visualización", "No modifica procesos ni manipulación; transportadores, desbobinador y zona de mandriles vacíos fuera del RTLS"],
    ["Infraestructura RTLS", "160 anclas PoE en columnas existentes; red PoE incluida; canalizaciones a cargo del cliente", "≈ 25 m² por ancla: densidad muy alta para 4.000 m²; sugiere tecnología de menor alcance o diseño conservador"],
    ["Tags", "3.000 tags en inserto mecánico para mandril de 4\", colocación y retirada manual en recepción y fin de vida; inserto consumible, tag recuperable", "Coste 30.750 € por lote de 500 (≈ 61,5 €/tag); inserción manual añade tarea al carretillero"],
    ["Precisión y zonificación", "Hasta 50 cm; 20–30 zonas lógicas de almacenamiento por geofencing", "Localización a nivel de zona, no de hueco; sin eje Z declarado para apilado"],
    ["Plataforma", "TorresFactory (base) + integración MES/SAP; vistas de recepción, almacén, alarmas y eventos", "Software propietario; licencia 69.000 €/año desde el año 5 (≈ 13,5 % del CAPEX anual)"],
    ["Recepción", "Estación de medición y pesaje del cliente + lectura DataMatrix + asignación automática de tag", "Medición y pesaje fuera del alcance MTorres"],
    ["Servicios", "Instalación 3 técnicos × 3 semanas; commissioning y aceptación 12 semanas en planta", "Plazo de puesta en marcha largo para el alcance"],
    ["Precio", "231.990 € diseño e infraestructura + 184.500 € tags + 93.456 € instalación = 509.946 € EXW", "Tags = 36 % del CAPEX; licencia recurrente no incluida en el precio"],
], fcw="30mm")}
<div class="callout">
<b>Lectura.</b> La oferta es una solución llave en mano coherente, pero con tres limitaciones para el caso de bobinas
apiladas: precisión de zona, sin altura, y dependencia total de un proveedor de radio y software con licencia creciente.
</div>

{sec("03", "Requisitos operacionales del almacén de bobinas")}
{table(["Requisito", "Por qué importa", "Base MTorres", "IAR"], [
    ["Confianza de posición a nivel de hueco bajo estiba densa", "El carretillero debe ir a la bobina correcta, no a la zona", "Zona (50 cm, 20–30 zonas)", "Hueco (10–30 cm) con confianza por posición"],
    ["Eje Z fiable para bobinas apiladas a 3 alturas", "Saber qué bobina de la pila es la buscada", "No declarado", "3D real con anclas a distintas alturas; barómetro/IMU como apoyo"],
    ["Actualización cuasi en tiempo real", "Reducir búsqueda y detectar movimientos no previstos", "Sí (RTLS continuo)", "Sí, con refresco por movimiento y latencia determinista en edge"],
    ["Robustez ante multipath metálico y oclusión", "Bobinas y estanterías metálicas degradan la radio", "Diseño conservador de anclas", "Filtrado de outliers, puntuación de confianza y diagnóstico de salud"],
    ["Identidad inequívoca en eventos críticos", "Evitar bobina errónea en producción", "DataMatrix en recepción", "RFID en recepción, retorno de retal y consumo + DataMatrix"],
    ["Integración transaccional MES/WMS", "Inventario y movimientos consistentes", "TorresFactory ↔ MES/SAP", "Contratos bidireccionales de inventario, movimiento y conciliación; modelo unificado de estado de bobina"],
    ["Escalabilidad y no dependencia", "Réplica en otras plantas y evolución", "Proveedor único", "Capa de abstracción (omlox hub / MQTT) desde la fase 1"],
    ["Preparación para gemelo digital e IA", "Optimización de búsquedas, flujo de carretillas, congestión", "No declarado", "Flujo de estado con marca de tiempo e histórico reproducible"],
], fcw="42mm")}

<div class="pb"></div>
{sec("04", "Tecnologías de posicionamiento: análisis comparado")}
{table(["Tecnología", "Madurez", "Ventajas", "Limitaciones", "Idoneidad almacén bobinas"], [
    ["UWB (TDoA / TWR / AP-TWR)", "Alta", "Precisión 10–30 cm, baja latencia, inmunidad al metal superior", "Geometría y calibración de anclas críticas; sincronización en TDoA", "Muy alta — núcleo"],
    ["BLE AoA", "Media-alta", "Ecosistema amplio, precisión media", "Sensible a reflexiones y oclusión", "Media"],
    ["BLE RSSI / Wi-Fi", "Alta (gruesa)", "Bajo coste, despliegue simple", "1–10 m de varianza", "Baja para hueco exacto"],
    ["RFID", "Muy alta", "Identidad muy robusta, lectura por evento", "No da posición continua", "Alta como capa compañera"],
    ["GPS / RTK", "Muy alta exterior", "Excelente en exterior", "No válido en interior", "Baja"],
    ["Visión", "Media-alta", "Contexto semántico", "Oclusión, polvo, mantenimiento", "Media como refuerzo en zonas críticas"],
    ["Híbrida UWB + RFID (+ visión)", "Alta a nivel arquitectura", "Resiliencia y degradación controlada", "Mayor complejidad de integración", "Muy alta a largo plazo"],
], fcw="34mm")}
<h3 class="sub">Métodos de cálculo UWB</h3>
{table(["Método", "Cómo funciona", "Implicación de instalación", "Proveedores"], [
    ["TDoA", "El tag emite un blink; anclas sincronizadas miden la diferencia de tiempo de llegada", "Requiere sincronización estricta (Ethernet o radio); muy escalable en tags y favorable a batería", "Pozyx, Sewio"],
    ["TWR", "Intercambio ida-vuelta tag-ancla; no requiere sincronizar anclas", "Instalación más simple; refresco algo menor a igual número de anclas", "GrowSpace"],
    ["AP-TWR", "Un ancla activa y el resto escuchan pasivamente: hasta 8× más datos por posicionamiento", "Menos anclas por superficie (≈ 2.500 m² con 4 anclas en espacio abierto)", "Eliko"],
], fcw="24mm")}
<p class="note">Fuentes públicas: Pozyx 10–30 cm; Sewio hasta 30 cm (TDoA), caso Volkswagen 50 cm y 333 ms; Eliko 30 cm ± 20 cm, hasta 75 Hz.
Pozyx v2025.2 incorpora conector omlox hub y precisión configurable por zona (10–30 cm / ≈ 5 m / presencia). Referencias en §12.</p>

<div class="pb"></div>
{sec("05", "Evaluación de proveedores UWB")}
{table(["Proveedor", "Perfil técnico", "Integración", "Modelo económico", "Puntuación IAR"], [
    ["Pozyx (BE)", "UWB TDoA + BLE; 10–30 cm; modos 2.5D y 3D real; > 150.000 trackers; ArcelorMittal, Alcon, Bonduelle", "MQTT local (puerto 1883, JSON X/Y/Z mm), API HTTP, conector omlox hub", "Kit 6.000 €; tag ≈ 45 € en volumen; licencia de plataforma (≈ 3.100 €/año para 200 tags)", "84,0 — opción equilibrada líder"],
    ["GrowSpace (KR)", "UWB TWR; sin sincronización de anclas; hasta 10 Hz; mínimo 4 anclas para 3D", "MQTT JSON X/Y/Z documentado públicamente (GitBook)", "Hardware con precio público (kits desde 359 $), sin licencia recurrente; tags bajo cotización", "80,8 — mejor economía de entrada; requiere endurecimiento industrial"],
    ["Sewio / HID (CZ)", "UWB TDoA; hasta 30 cm; Z por barómetro (beta); Volkswagen, Toyota, Budvar, Bora, SEG", "REST + WebSocket documentados (docs.sewio.net); gemelo digital soportado vía API", "Precios bajo petición; kit 400 m² reutilizable", "76,3 — técnicamente sólido, economía opaca"],
    ["Eliko (EE)", "UWB AP-TWR; 30 cm ± 20 cm; hasta 3 cm en óptimo; Bosch, SKF, Ericsson", "REST + NMEA; documentación bajo contacto", "Ancla 550 €; tag IP67 375 € / IP52 145 €; licencia 120 €/ancla + 30 €/tag al año", "72,8 — fiable, pero coste recurrente por tag penaliza a 3.000 bobinas"],
], fcw="26mm")}
<p class="note">Método de puntuación IAR: ajuste técnico 40 %, madurez industrial 20 %, atractivo económico 25 %, visibilidad de ciclo de vida 10 %, preparación de integración 5 %.
Sensibilidad: si prima el coste del PoC sube GrowSpace; si prima la preparación industrial, Pozyx mantiene el liderazgo.</p>
<div class="callout">
<b>Modelos de licencia.</b> (A) Suscripción anual por tag y plataforma — crece con el número de bobinas y el sistema se apaga si se deja de pagar.
(B) Licencia perpetua + mantenimiento anual porcentual — mayor inversión inicial, factura estable. (C) Hardware abierto sin licencia recurrente —
máxima flexibilidad, requiere más ingeniería propia. Para 3.000 tags el modelo (A) con cuota por tag es el que más penaliza el TCO.
</div>

<div class="pb"></div>
{sec("06", "Arquitectura IAR recomendada")}
{table(["Capa", "Contenido", "Mejora frente a la base"], [
    ["Hardware de posición", "Anclas UWB fijas a distintas alturas (3D real), tags activos en inserto de mandril, RFID en portales de recepción/retorno/consumo, visión opcional en zonas críticas", "Eje Z, identidad verificada, menor densidad de anclas por diseño de radio"],
    ["Comunicaciones", "Red local determinista (PoE) y backbone de eventos (movimiento, inventario, excepciones)", "Latencia predecible; separación adquisición/reconciliación"],
    ["Motor de posición", "Tiempo real con puntuación de confianza, filtrado de outliers, diagnóstico de salud de anclas y tags", "Robustez ante multipath y oclusión; alarmas de deriva de calibración"],
    ["Middleware", "API de abstracción de proveedor (omlox hub / MQTT) y modelo unificado de estado de bobina", "Proveedor de radio intercambiable; protege el roadmap"],
    ["Interfaz MES/WMS", "Contratos bidireccionales de inventario, movimiento y conciliación; recomendación de bobina y validación por carretillero", "Consistencia transaccional; picking guiado"],
    ["Gemelo digital", "Flujo de estado con marca de tiempo e histórico reproducible (replay)", "Base para simulación y optimización"],
    ["Módulos IA (futuro)", "Optimización de búsqueda, flujo de carretillas, predicción de congestión, mantenimiento predictivo", "Valor incremental sin rehacer la plataforma"],
], fcw="30mm")}
<h3 class="sub">Trade-offs de ingeniería resueltos</h3>
<ul>
<li><b>Centralizado vs distribuido:</b> adquisición distribuida con reconciliación centralizada.</li>
<li><b>Proveedor único vs abstracción:</b> abstracción desde la fase 1; el proveedor único acelera el arranque pero bloquea el roadmap.</li>
<li><b>Tags activos vs pasivos:</b> activos UWB para posición continua; RFID pasivo para identidad a coste mínimo.</li>
<li><b>Anclas fijas vs infraestructura móvil:</b> anclas fijas por repetibilidad; anclas en columnas existentes sin obra.</li>
<li><b>Cloud vs edge:</b> edge para latencia determinista; cloud para analítica e histórico.</li>
</ul>

<div class="pb"></div>
{sec("07", "Cuantificación de mejoras y TCO")}
<h3 class="sub">Coste total de propiedad (almacén de referencia, 4.000 m², 3.000 bobinas)</h3>
{table(["Escenario", "Anclas", "Hardware", "CAPEX total", "Licencia anual", "TCO 5 años", "TCO 10 años", "Δ vs base"], [
    ["Base MTorres (oferta)", "160", "incluido", "509.946 €", "69.000 € desde año 5", "509.946 €", "854.946 €", "—"],
    ["IAR clase Pozyx (TDoA, 3D)", "≈ 60", "186.000 €", "415.000 €", "≈ 24.000 €", "511.000 €", "631.000 €", "−26 %"],
    ["IAR clase GrowSpace (TWR, abierto)", "≈ 60", "200.000 €", "429.000 €", "0 €", "429.000 €", "429.000 €", "−50 %"],
    ["IAR clase Eliko (AP-TWR)", "≈ 40", "923.800 €", "1.152.800 €", "94.800 €", "1.532.000 €", "2.006.000 €", "+135 %"],
], fcw="40mm")}
<p class="note">Supuestos IAR: ingeniería e integración INGECART 120.000 €, portales RFID 24.000 €, instalación 60.000 €, piloto comparativo 25.000 €;
tags 45 € (Pozyx), 60 € (GrowSpace, estimado), 300 € (Eliko IP67 con descuento por volumen); anclas 750 € (Pozyx, estimado), 250 € (GrowSpace, estimado), 550 € (Eliko lista);
licencia Pozyx escalada con descuento a ≈ 8 €/tag/año; Eliko 120 €/ancla + 30 €/tag (lista). Densidad de anclas para 3D con techo de 12 m estimada en 60–80 m²/ancla.
Los precios no públicos deben confirmarse con oferta formal; la clase Eliko queda descartada para 3.000 tags salvo negociación de licencia plana.</p>
<h3 class="sub">Beneficio operativo anual estimado</h3>
{table(["Palanca", "Supuesto base", "Base MTorres (zona)", "IAR (hueco + RFID)", "Referencia pública"], [
    ["Tiempo de búsqueda y verificación", "250 movimientos/día, 4 min → 1 min (base) / 0,5 min (IAR), 45 €/h, 330 días", "185.600 €", "216.600 €", "Toyota/Sewio: información de inventario de 8 h a 1 s; 18.000 h-persona/año liberadas"],
    ["Bobina errónea en producción", "1,5 % de 120 picks/día, 150 € por incidente; −70 % base / −90 % IAR", "62.400 €", "80.200 €", "Bora/Sewio: 0 errores de picking en 3 meses, −15 % tiempo de picking; SEG: 95 % → 100 % registros correctos"],
    ["Stock de seguridad", "4,9 M€ de papel; −5 % base / −8 % IAR; coste de posesión 12 %", "29.300 €", "46.800 €", "Toyota/Sewio: stock de seguridad de 8 h a 4 h (−50 %)"],
    ["Retales no trazados", "0,8 % de 26 M€ de consumo; recuperación 30 % base / 50 % IAR", "62.400 €", "104.000 €", "Budvar/Sewio: +19 % utilización virtual del almacén"],
    ["<b>Total anual</b>", "", "<b>≈ 339.600 €</b>", "<b>≈ 447.600 €</b>", ""],
    ["<b>Payback simple</b>", "CAPEX / beneficio neto", "<b>≈ 1,5 años</b>", "<b>≈ 1,0 año</b> (clase Pozyx)", ""],
], fcw="38mm")}
<div class="callout orange">
<b>Cómo leer estas cifras.</b> Los porcentajes de mejora son supuestos de ingeniería anclados en casos publicados por fabricantes, no garantías.
El estudio de aplicación sustituye cada supuesto por el dato real de la planta (movimientos/día, coste hora, incidentes, valor de stock, retal).
El lucro cesante por paradas de corrugadora por bobina no encontrada no está incluido y suele ser la partida mayor.
</div>

<div class="pb"></div>
{sec("08", "Mejoras técnicas IAR frente a la oferta base — tabla de decisión")}
{table(["Criterio", "Base MTorres", "IAR INGECART", "Impacto"], [
    ["Precisión de localización", "Hasta 50 cm; zona lógica", "10–30 cm declarado; hueco", "Búsqueda dirigida a la bobina, no a la zona"],
    ["Altura (eje Z)", "No declarado", "3D real con anclas a varias alturas", "Identifica la bobina correcta dentro de la pila"],
    ["Identidad", "DataMatrix en recepción", "DataMatrix + RFID en recepción, retorno y consumo", "Elimina bobina errónea y cierra el ciclo del retal"],
    ["Densidad de anclas", "160 (≈ 25 m²/ancla)", "≈ 40–60 según método (AP-TWR / TDoA)", "Menos hardware, menos puntos de fallo, menos instalación"],
    ["Dependencia de proveedor", "Plataforma propietaria única", "Abstracción omlox/MQTT; proveedor sustituible", "Protege inversión y réplica internacional"],
    ["Licencia", "69.000 €/año desde año 5", "0–24.000 €/año según clase", "TCO 10 años −26 % a −50 %"],
    ["Integración", "MES/SAP vía TorresFactory", "Contratos MES/WMS + picking guiado + gemelo digital", "Valor operativo, no solo visibilidad"],
    ["Diagnóstico", "Alarmas y eventos", "Confianza por posición, salud de anclas, deriva de calibración", "Mantenimiento predictivo del propio RTLS"],
    ["Puesta en marcha", "3 semanas instalación + 12 semanas commissioning", "Piloto 6–8 semanas + despliegue por fases", "Riesgo controlado antes de comprometer"],
    ["Cumplimiento radio UE", "No detallado", "RED 2014/53/UE, ETSI EN 302 065-2, Decisión (UE) 2024/1467", "Conformidad documentada del producto"],
], fcw="36mm")}

{sec("09", "Riesgos y mitigaciones")}
{table(["Riesgo", "Impacto", "Mitigación"], [
    ["Multipath y oclusión por bobinas metálicas y apilado", "Precisión real peor que la declarada", "Radio survey, piloto con bobinas reales, filtrado por confianza, anclas a varias alturas, RFID como respaldo de identidad"],
    ["Deriva de calibración de anclas", "Pérdida progresiva de precisión", "Diagnóstico de salud, recalibración programada, alarmas de deriva"],
    ["Escalada de costes por licencias por tag", "TCO fuera de control al crecer", "Descartar modelos por tag a 3.000 bobinas; negociar licencia plana o modelo abierto"],
    ["Eje Z en beta (Sewio) o 3D exigente (Pozyx)", "Altura no fiable", "Exigir cifra de precisión Z contractual; barómetro/IMU; validación en piloto"],
    ["Inserto de mandril como consumible", "Coste y tarea manual recurrente", "Diseño INGECART de inserto robusto; estudiar inserción/recuperación automática en fase 2"],
    ["Cobertura Wi-Fi / PoE insuficiente", "Anclas sin red", "Estudio de infraestructura; PoE incluido; canalizaciones acordadas"],
    ["Dependencia de un solo proveedor pequeño", "Continuidad", "Abstracción desde fase 1; segunda fuente validada en el piloto"],
], fcw="44mm")}

<div class="pb"></div>
{sec("10", "Plan de validación e implantación")}
{table(["Fase", "Actividad", "Entregable", "Plazo"], [
    ["F0", "Estudio de aplicación", "Levantamiento del almacén, matriz de bobinas, flujos, radio survey, datos para el caso de negocio", "2 sem."],
    ["F1", "Piloto comparativo mismo sitio", "Kits Pozyx (3D) y GrowSpace en zona de 500–1.000 m², bobinas reales, turno completo; medición X/Y/Z, latencia, disponibilidad, consistencia MES", "6–8 sem."],
    ["F2", "Normalización económica", "TCO a 5 y 10 años con ofertas formales; adjudicación del proveedor de radio", "2 sem."],
    ["F3", "Ingeniería de detalle", "Diseño de anclas, insertos, portales RFID, middleware de abstracción, contratos MES/WMS, expediente de conformidad radio", "6 sem."],
    ["F4", "Despliegue por zonas", "Instalación sobre columnas existentes, comisionado por zona sin parar el almacén", "6–8 sem."],
    ["F5", "Aceptación", "Matriz FAT/SAT: precisión por percentil, tasa de identidad correcta, latencia, disponibilidad, exactitud de inventario", "2 sem."],
], fcw="10mm")}
<h3 class="sub">Criterios de aceptación propuestos</h3>
<ul>
<li>Error de posición P95 ≤ 30 cm en X/Y y asignación correcta de nivel de pila ≥ 98 % en zona de bobinas.</li>
<li>Latencia posición → MES ≤ 2 s en P95; disponibilidad del sistema ≥ 99 % en 30 días.</li>
<li>Identidad correcta en recepción, retorno y consumo ≥ 99,9 % (RFID + DataMatrix).</li>
<li>Exactitud de inventario (conteo físico vs sistema) ≥ 99,5 % tras 30 días.</li>
<li>Cero dependencia de conectividad externa para la operación; degradación controlada documentada.</li>
</ul>

{sec("11", "Normativa y conformidad")}
{table(["Norma / reglamento", "Aplicación"], [
    ["Directiva RED 2014/53/UE", "Equipos radioeléctricos UWB y RFID: salud, seguridad, EMC y uso eficiente del espectro"],
    ["ETSI EN 302 065-2", "Aplicaciones UWB de localización y seguimiento; verificar versión armonizada vigente"],
    ["Decisión de Ejecución (UE) 2024/1467", "Límites UWB 6–8,5 GHz: −41,3 dBm/MHz e.i.r.p. medio y 0 dBm pico; interior potencia mejorada para localización −31,3 dBm/MHz y 10 dBm bajo condiciones"],
    ["omlox (PI) Core Zone v2 / Hub", "Interoperabilidad UWB (IEEE 802.15.4z, UL-TDoA, canal 9) e integración multitecnología"],
    ["Directiva 2006/42/CE · EN ISO 13849 · EN 60204-1", "Estación de recepción y elementos electromecánicos (como declara la oferta base)"],
    ["Reglamento (UE) 2023/1230", "Máquinas entregadas desde el 20/01/2027"],
], fcw="52mm")}

{sec("12", "Fuentes", dark=True)}
<p class="src">Internas: Of. 26-05-073V0 (MTorres) · IAR_EXECUTIVE_TECHNICAL_ASSESSMENT_REPORT.html · RTLS-UWB Documento técnico v2 · Pozyx_/Sewio_/Eliko_/GrowSpace_Evaluacion_RTLS · Precios_Eliko · Eliko_Kit_Alquiler.<br>
Públicas (acceso 14/09/2026): pozyx.io/technology/rtls-explained · pozyx.io/products/software/location-and-sensor-hub · sewio.net/uwb-technology · sewio.net/customer-projects/toyota-motors · sewio.net/customer-projects/bora · sewio.net/customer-projects/seg-automotive · sewio.net (Budweiser Budvar 99 % uptime) · eliko.tech/elikos-active-passive-twr-protocol-explained · eliko.tech/product-new-kio-rtls · eliko.tech/case-study/vechicle-tracking-drives-efficiency-at-bosch · omlox.com · profibus.com/technologies/omlox · etsi.org EN 302 065-2 V2.1.1 · eur-lex.europa.eu 2014/53/UE · eur-lex.europa.eu OJ L 2024/1467.<br>
Las cifras de fabricantes se citan como hechos publicados, no como auditorías independientes. No se localizó publicación primaria de MTorres sobre prestaciones RTLS de TorresFactory ni cifra pública de ROI Pozyx/ArcelorMittal.
Documento emitido por INGECART · Ingeniería de Producto. Rev. 1 — 14/09/2026.</p>
"""

# ------------------------------------------------------------------ ENGLISH BODY
EN = f"""
<img src="{LOGO}" class="cover-logo" alt="INGECART">
<div class="cover-kicker">Technical product report</div>
<div class="cover-title">IAR · Real-time location<br>of paper reels</div>
<div class="cover-rule"></div>
<div class="cover-sub">
Evolution of the real-time reel warehouse management solution: from the MTorres base offer
(Of. 26-05-073V0, RTLS with 160 anchors and 3,000 tags on TorresFactory) to the INGECART IAR architecture:
UWB-first with true Z axis, RFID identity checkpoints, vendor abstraction layer and MES/WMS integration
ready for a digital twin.
</div>
<div class="cover-claim">
<b>Same function, more precision, less dependency.</b><br>
Slot-level location (10–30 cm) instead of zone level (50 cm, 20–30 zones), identity confirmed by RFID at every
critical event, an interchangeable radio vendor and a 10-year TCO 26 % to 50 % lower in the recommended architectures.
</div>
<table class="meta" style="margin-top:8mm"><tbody>
<tr><td>Product</td><td>IAR — Intelligent Automatic Roll location (smart reel warehouse)</td><td>Document no.</td><td>IAR-RPT-2026-09 · Rev. 1</td></tr>
<tr><td>Reference basis</td><td>MTorres offer Of. 26-05-073V0 — Real Time Warehouse Management Solution</td><td>Date</td><td>14/09/2026</td></tr>
<tr><td>Application case</td><td>Non-automated warehouse 80 × 50 m (≈ 4,000 m²), ≈ 3,000 vertical reels Ø 1,600 mm stacked 3-high, ceiling ≤ 12 m</td><td>Status</td><td>Product definition for decision · subject to on-site benchmark</td></tr>
<tr><td>Sources</td><td>MTorres offer; IAR Executive Technical Assessment; RTLS-UWB technical document v2; Pozyx, Sewio, Eliko, GrowSpace sheets; Eliko prices; public sources (accessed 14/09/2026)</td><td>Issuer</td><td>INGECART · Product Engineering</td></tr>
</tbody></table>

<div class="pb"></div>
{sec("01", "Executive summary")}
<table class="kpi-wrap"><tr>
<td><span class="kpi-v">10–30 cm</span><span class="kpi-l">UWB accuracy (vs 50 cm)</span></td>
<td><span class="kpi-v">True 3D</span><span class="kpi-l">Z axis for stacked reels</span></td>
<td><span class="kpi-v">−26 to −50 %</span><span class="kpi-l">10-year TCO vs base offer</span></td>
<td><span class="kpi-v">≈ 1 year</span><span class="kpi-l">Estimated payback</span></td>
</tr></table>
<table class="two"><tr><td class="l" style="width:50%">
<span class="tag">Starting point</span>
<p>The MTorres offer delivers warehouse visibility with an RTLS of 160 PoE anchors on columns, 3,000 tags in 4"
core inserts, declared accuracy of up to 50 cm, 20–30 logical zones by geofencing and the TorresFactory platform with
MES/SAP integration. Price 509,946 € EXW plus a 69,000 €/year licence from year five. Installation 3 technicians ×
3 weeks and commissioning 12 weeks.</p>
<span class="tag o">What IAR changes</span>
<p>INGECART keeps the functional scope and replaces the closed box with a <b>UWB-first</b> architecture using anchors at
different heights for <b>true 3D</b>, <b>RFID checkpoints</b> at receipt, return and consumption, a <b>vendor abstraction
layer</b> (omlox/MQTT) that avoids lock-in, and a positioning engine with confidence scoring, filtering and diagnostics.
The result is slot-level location, verified identity and vendor freedom.</p>
</td><td style="width:50%">
<span class="tag">Quantification</span>
<p>For the reference warehouse the estimated annual benefit rises from ≈ 340 k€ (base) to ≈ 448 k€ (IAR): less search
time (216 k€), fewer wrong reels (80 k€), lower safety stock (47 k€) and recovery of untracked remnants (104 k€).
The 10-year TCO falls from 855 k€ to 631 k€ (Pozyx class) or 429 k€ (GrowSpace class).</p>
<span class="tag o">Recommended decision</span>
<p>Same-site comparative pilot with two UWB vendors (Pozyx and GrowSpace) over 6–8 weeks, with real reels and full
shifts, measuring X/Y/Z accuracy, latency, availability and MES consistency; award after normalising 5- and 10-year TCO.</p>
</td></tr></table>
<div class="callout orange">
<b>Rigour notice.</b> Accuracy figures are manufacturer statements (10–30 cm Pozyx; 30 cm Sewio; 30 cm ± 20 cm Eliko),
not guaranteed tolerances in a warehouse with metal, stacking and occlusion. Value figures rest on explicit assumptions (§07)
to be replaced by customer data in the application study.
</div>

<div class="pb"></div>
{sec("02", "The MTorres base offer: what it includes and what it limits")}
{table(["Block", "Content of offer 26-05-073V0", "Engineering observation"], [
    ["Area and scope", "Non-automated warehouse 80 × 50 m (≈ 4,000 m²), ceiling ≤ 12 m, ≈ 3,000 reels Ø 1,600 mm stacked 3-high; identification, tracking, traceability and visualisation only", "No change to processes or handling; conveyors, unwinder and empty-core area outside the RTLS"],
    ["RTLS infrastructure", "160 PoE anchors on existing columns; PoE network included; conduits by customer", "≈ 25 m² per anchor: very high density for 4,000 m²; suggests shorter-range technology or conservative design"],
    ["Tags", "3,000 tags in a mechanical insert for 4\" cores, manual insertion and removal at receipt and end of life; insert is a consumable, tag recoverable", "Cost 30,750 € per lot of 500 (≈ 61.5 €/tag); manual insertion adds a forklift-driver task"],
    ["Accuracy and zoning", "Up to 50 cm; 20–30 logical storage zones by geofencing", "Zone-level location, not slot level; no Z axis declared for stacking"],
    ["Platform", "TorresFactory (base) + MES/SAP integration; receipt, warehouse, alarms and events views", "Proprietary software; licence 69,000 €/year from year 5 (≈ 13.5 % of CAPEX per year)"],
    ["Receipt", "Customer measuring and weighing station + DataMatrix reading + automatic tag assignment", "Measuring and weighing outside MTorres scope"],
    ["Services", "Installation 3 technicians × 3 weeks; commissioning and acceptance 12 weeks on site", "Long commissioning for the scope"],
    ["Price", "231,990 € design and infrastructure + 184,500 € tags + 93,456 € installation = 509,946 € EXW", "Tags = 36 % of CAPEX; recurring licence not in the price"],
], fcw="30mm")}
<div class="callout">
<b>Reading.</b> The offer is a coherent turnkey solution, but with three limitations for stacked reels: zone-level accuracy,
no height, and full dependence on a single radio and software vendor with a growing licence.
</div>

{sec("03", "Operational requirements of the reel warehouse")}
{table(["Requirement", "Why it matters", "MTorres base", "IAR"], [
    ["Slot-level position confidence under dense stacking", "The driver must go to the right reel, not the zone", "Zone (50 cm, 20–30 zones)", "Slot (10–30 cm) with per-position confidence"],
    ["Reliable Z axis for reels stacked 3-high", "Know which reel in the stack is the one", "Not declared", "True 3D with anchors at several heights; barometer/IMU as support"],
    ["Near-real-time update", "Cut search time and detect unexpected moves", "Yes (continuous RTLS)", "Yes, motion-based refresh and deterministic edge latency"],
    ["Robustness to metallic multipath and occlusion", "Reels and metal racks degrade radio", "Conservative anchor design", "Outlier filtering, confidence scoring and health diagnostics"],
    ["Unambiguous identity at critical events", "Avoid the wrong reel in production", "DataMatrix at receipt", "RFID at receipt, remnant return and consumption + DataMatrix"],
    ["Transactional MES/WMS integration", "Consistent inventory and movements", "TorresFactory ↔ MES/SAP", "Bidirectional inventory, movement and reconciliation contracts; unified roll-state model"],
    ["Scalability and no lock-in", "Replication in other plants and evolution", "Single vendor", "Abstraction layer (omlox hub / MQTT) from phase 1"],
    ["Digital-twin and AI readiness", "Search, forklift-flow and congestion optimisation", "Not declared", "Timestamped state stream and replay-ready history"],
], fcw="42mm")}

<div class="pb"></div>
{sec("04", "Positioning technologies: comparative analysis")}
{table(["Technology", "Maturity", "Advantages", "Limitations", "Fit for reel warehouse"], [
    ["UWB (TDoA / TWR / AP-TWR)", "High", "10–30 cm accuracy, low latency, superior immunity to metal", "Anchor geometry and calibration critical; synchronisation in TDoA", "Very high — core"],
    ["BLE AoA", "Medium-high", "Broad ecosystem, medium accuracy", "Sensitive to reflections and occlusion", "Medium"],
    ["BLE RSSI / Wi-Fi", "High (coarse)", "Low cost, simple deployment", "1–10 m variance", "Low for exact slot"],
    ["RFID", "Very high", "Very robust identity, event-based reading", "No continuous position", "High as companion layer"],
    ["GPS / RTK", "Very high outdoor", "Excellent outdoors", "Not valid indoors", "Low"],
    ["Vision", "Medium-high", "Semantic context", "Occlusion, dust, maintenance", "Medium as augmentation in critical zones"],
    ["Hybrid UWB + RFID (+ vision)", "High at architecture level", "Resilience and controlled degradation", "Higher integration complexity", "Very high long-term"],
], fcw="34mm")}
<h3 class="sub">UWB ranging methods</h3>
{table(["Method", "How it works", "Installation implication", "Vendors"], [
    ["TDoA", "Tag emits a blink; synchronised anchors measure time difference of arrival", "Requires strict synchronisation (Ethernet or radio); very scalable in tags and battery friendly", "Pozyx, Sewio"],
    ["TWR", "Two-way exchange tag-anchor; no anchor synchronisation", "Simpler installation; somewhat lower refresh at equal anchor count", "GrowSpace"],
    ["AP-TWR", "One active anchor, the rest listen passively: up to 8× more data per fix", "Fewer anchors per area (≈ 2,500 m² with 4 anchors in open space)", "Eliko"],
], fcw="24mm")}
<p class="note">Public sources: Pozyx 10–30 cm; Sewio up to 30 cm (TDoA), Volkswagen case 50 cm and 333 ms; Eliko 30 cm ± 20 cm, up to 75 Hz.
Pozyx v2025.2 adds an omlox hub connector and zone-configurable accuracy (10–30 cm / ≈ 5 m / presence). References in §12.</p>

<div class="pb"></div>
{sec("05", "UWB vendor assessment")}
{table(["Vendor", "Technical profile", "Integration", "Economic model", "IAR score"], [
    ["Pozyx (BE)", "UWB TDoA + BLE; 10–30 cm; 2.5D and true 3D modes; > 150,000 trackers; ArcelorMittal, Alcon, Bonduelle", "Local MQTT (port 1883, JSON X/Y/Z mm), HTTP API, omlox hub connector", "Kit 6,000 €; tag ≈ 45 € in volume; platform licence (≈ 3,100 €/year for 200 tags)", "84.0 — leading balanced option"],
    ["GrowSpace (KR)", "UWB TWR; no anchor synchronisation; up to 10 Hz; minimum 4 anchors for 3D", "MQTT JSON X/Y/Z publicly documented (GitBook)", "Hardware with public prices (kits from 359 $), no recurring licence; tags on quotation", "80.8 — best entry economics; needs industrial hardening"],
    ["Sewio / HID (CZ)", "UWB TDoA; up to 30 cm; Z by barometer (beta); Volkswagen, Toyota, Budvar, Bora, SEG", "Documented REST + WebSocket (docs.sewio.net); digital twin supported via API", "Prices on request; 400 m² kit reusable", "76.3 — technically solid, opaque economics"],
    ["Eliko (EE)", "UWB AP-TWR; 30 cm ± 20 cm; down to 3 cm in optimum; Bosch, SKF, Ericsson", "REST + NMEA; documentation on contact", "Anchor 550 €; tag IP67 375 € / IP52 145 €; licence 120 €/anchor + 30 €/tag per year", "72.8 — reliable, but per-tag recurring cost penalises 3,000 reels"],
], fcw="26mm")}
<p class="note">IAR scoring method: technical fit 40 %, industrial maturity 20 %, economic attractiveness 25 %, lifecycle visibility 10 %, integration readiness 5 %.
Sensitivity: if PoC cost prevails GrowSpace rises; if industrial readiness prevails Pozyx keeps the lead.</p>
<div class="callout">
<b>Licence models.</b> (A) Annual subscription per tag and platform — grows with reel count and the system stops if unpaid.
(B) Perpetual licence + annual percentage maintenance — higher initial outlay, stable invoice. (C) Open hardware without recurring licence —
maximum flexibility, more in-house engineering. For 3,000 tags, model (A) with a per-tag fee penalises TCO the most.
</div>

<div class="pb"></div>
{sec("06", "Recommended IAR architecture")}
{table(["Layer", "Content", "Improvement over base"], [
    ["Positioning hardware", "Fixed UWB anchors at several heights (true 3D), active tags in core inserts, RFID at receipt/return/consumption portals, optional vision in critical zones", "Z axis, verified identity, lower anchor density by radio design"],
    ["Communications", "Deterministic local network (PoE) and event backbone (movement, inventory, exceptions)", "Predictable latency; acquisition separated from reconciliation"],
    ["Positioning engine", "Real time with confidence scoring, outlier filtering, anchor and tag health diagnostics", "Robustness to multipath and occlusion; calibration-drift alarms"],
    ["Middleware", "Vendor abstraction API (omlox hub / MQTT) and unified roll-state model", "Interchangeable radio vendor; protects the roadmap"],
    ["MES/WMS interface", "Bidirectional inventory, movement and reconciliation contracts; reel recommendation and driver validation", "Transactional consistency; guided picking"],
    ["Digital twin", "Timestamped state stream and replay-ready history", "Basis for simulation and optimisation"],
    ["AI modules (future)", "Search optimisation, forklift flow, congestion prediction, predictive maintenance", "Incremental value without rebuilding the platform"],
], fcw="30mm")}
<h3 class="sub">Engineering trade-offs resolved</h3>
<ul>
<li><b>Centralised vs distributed:</b> distributed acquisition with centralised reconciliation.</li>
<li><b>Single vendor vs abstraction:</b> abstraction from phase 1; a single vendor speeds start-up but locks the roadmap.</li>
<li><b>Active vs passive tags:</b> active UWB for continuous position; passive RFID for identity at minimum cost.</li>
<li><b>Fixed anchors vs mobile infrastructure:</b> fixed anchors for repeatability; anchors on existing columns without civil works.</li>
<li><b>Cloud vs edge:</b> edge for deterministic latency; cloud for analytics and history.</li>
</ul>

<div class="pb"></div>
{sec("07", "Quantified improvements and TCO")}
<h3 class="sub">Total cost of ownership (reference warehouse, 4,000 m², 3,000 reels)</h3>
{table(["Scenario", "Anchors", "Hardware", "Total CAPEX", "Annual licence", "5-year TCO", "10-year TCO", "Δ vs base"], [
    ["MTorres base (offer)", "160", "included", "509,946 €", "69,000 € from year 5", "509,946 €", "854,946 €", "—"],
    ["IAR Pozyx class (TDoA, 3D)", "≈ 60", "186,000 €", "415,000 €", "≈ 24,000 €", "511,000 €", "631,000 €", "−26 %"],
    ["IAR GrowSpace class (TWR, open)", "≈ 60", "200,000 €", "429,000 €", "0 €", "429,000 €", "429,000 €", "−50 %"],
    ["IAR Eliko class (AP-TWR)", "≈ 40", "923,800 €", "1,152,800 €", "94,800 €", "1,532,000 €", "2,006,000 €", "+135 %"],
], fcw="40mm")}
<p class="note">IAR assumptions: INGECART engineering and integration 120,000 €, RFID portals 24,000 €, installation 60,000 €, comparative pilot 25,000 €;
tags 45 € (Pozyx), 60 € (GrowSpace, estimated), 300 € (Eliko IP67 with volume discount); anchors 750 € (Pozyx, estimated), 250 € (GrowSpace, estimated), 550 € (Eliko list);
Pozyx licence scaled with discount to ≈ 8 €/tag/year; Eliko 120 €/anchor + 30 €/tag (list). Anchor density for 3D under a 12 m ceiling estimated at 60–80 m²/anchor.
Non-public prices must be confirmed by formal quotation; the Eliko class is ruled out for 3,000 tags unless a flat licence is negotiated.</p>
<h3 class="sub">Estimated annual operational benefit</h3>
{table(["Lever", "Base assumption", "MTorres base (zone)", "IAR (slot + RFID)", "Public reference"], [
    ["Search and verification time", "250 movements/day, 4 min → 1 min (base) / 0.5 min (IAR), 45 €/h, 330 days", "185,600 €", "216,600 €", "Toyota/Sewio: inventory information from 8 h to 1 s; 18,000 person-hours/year freed"],
    ["Wrong reel in production", "1.5 % of 120 picks/day, 150 € per incident; −70 % base / −90 % IAR", "62,400 €", "80,200 €", "Bora/Sewio: 0 picking errors in 3 months, −15 % picking time; SEG: 95 % → 100 % correct records"],
    ["Safety stock", "4.9 M€ of paper; −5 % base / −8 % IAR; carrying cost 12 %", "29,300 €", "46,800 €", "Toyota/Sewio: safety stock from 8 h to 4 h (−50 %)"],
    ["Untracked remnants", "0.8 % of 26 M€ consumption; recovery 30 % base / 50 % IAR", "62,400 €", "104,000 €", "Budvar/Sewio: +19 % virtual warehouse utilisation"],
    ["<b>Annual total</b>", "", "<b>≈ 339,600 €</b>", "<b>≈ 447,600 €</b>", ""],
    ["<b>Simple payback</b>", "CAPEX / net benefit", "<b>≈ 1.5 years</b>", "<b>≈ 1.0 year</b> (Pozyx class)", ""],
], fcw="38mm")}
<div class="callout orange">
<b>How to read these figures.</b> Improvement percentages are engineering assumptions anchored in manufacturer-published cases, not guarantees.
The application study replaces each assumption with real plant data (movements/day, hourly cost, incidents, stock value, remnants).
Lost production from corrugator stops due to reels not found is not included and is usually the largest item.
</div>

<div class="pb"></div>
{sec("08", "IAR technical improvements versus the base offer — decision table")}
{table(["Criterion", "MTorres base", "INGECART IAR", "Impact"], [
    ["Location accuracy", "Up to 50 cm; logical zone", "10–30 cm declared; slot", "Search directed to the reel, not the zone"],
    ["Height (Z axis)", "Not declared", "True 3D with anchors at several heights", "Identifies the right reel within the stack"],
    ["Identity", "DataMatrix at receipt", "DataMatrix + RFID at receipt, return and consumption", "Eliminates wrong reels and closes the remnant loop"],
    ["Anchor density", "160 (≈ 25 m²/anchor)", "≈ 40–60 depending on method (AP-TWR / TDoA)", "Less hardware, fewer failure points, less installation"],
    ["Vendor dependency", "Single proprietary platform", "omlox/MQTT abstraction; replaceable vendor", "Protects investment and international replication"],
    ["Licence", "69,000 €/year from year 5", "0–24,000 €/year by class", "10-year TCO −26 % to −50 %"],
    ["Integration", "MES/SAP via TorresFactory", "MES/WMS contracts + guided picking + digital twin", "Operational value, not only visibility"],
    ["Diagnostics", "Alarms and events", "Per-position confidence, anchor health, calibration drift", "Predictive maintenance of the RTLS itself"],
    ["Commissioning", "3 weeks installation + 12 weeks commissioning", "6–8 week pilot + phased roll-out", "Controlled risk before commitment"],
    ["EU radio compliance", "Not detailed", "RED 2014/53/EU, ETSI EN 302 065-2, Decision (EU) 2024/1467", "Documented product conformity"],
], fcw="36mm")}

{sec("09", "Risks and mitigations")}
{table(["Risk", "Impact", "Mitigation"], [
    ["Multipath and occlusion from metallic reels and stacking", "Real accuracy worse than declared", "Radio survey, pilot with real reels, confidence filtering, anchors at several heights, RFID as identity backup"],
    ["Anchor calibration drift", "Progressive accuracy loss", "Health diagnostics, scheduled recalibration, drift alarms"],
    ["Cost escalation from per-tag licences", "TCO out of control as fleet grows", "Rule out per-tag models at 3,000 reels; negotiate flat licence or open model"],
    ["Z axis in beta (Sewio) or demanding 3D (Pozyx)", "Unreliable height", "Require contractual Z accuracy figure; barometer/IMU; pilot validation"],
    ["Core insert as consumable", "Recurring cost and manual task", "Robust INGECART insert design; study automatic insertion/recovery in phase 2"],
    ["Insufficient Wi-Fi / PoE coverage", "Anchors without network", "Infrastructure study; PoE included; agreed conduits"],
    ["Dependence on a single small vendor", "Continuity", "Abstraction from phase 1; second source validated in the pilot"],
], fcw="44mm")}

<div class="pb"></div>
{sec("10", "Validation and implementation plan")}
{table(["Phase", "Activity", "Deliverable", "Duration"], [
    ["F0", "Application study", "Warehouse survey, reel matrix, flows, radio survey, data for the business case", "2 wks"],
    ["F1", "Same-site comparative pilot", "Pozyx (3D) and GrowSpace kits in a 500–1,000 m² zone, real reels, full shift; X/Y/Z accuracy, latency, availability, MES consistency", "6–8 wks"],
    ["F2", "Economic normalisation", "5- and 10-year TCO with formal quotations; radio vendor award", "2 wks"],
    ["F3", "Detail engineering", "Anchor design, inserts, RFID portals, abstraction middleware, MES/WMS contracts, radio conformity file", "6 wks"],
    ["F4", "Zone-by-zone roll-out", "Installation on existing columns, commissioning per zone without stopping the warehouse", "6–8 wks"],
    ["F5", "Acceptance", "FAT/SAT matrix: accuracy by percentile, correct-identity rate, latency, availability, inventory accuracy", "2 wks"],
], fcw="10mm")}
<h3 class="sub">Proposed acceptance criteria</h3>
<ul>
<li>P95 position error ≤ 30 cm in X/Y and correct stack-level assignment ≥ 98 % in the reel zone.</li>
<li>Position → MES latency ≤ 2 s at P95; system availability ≥ 99 % over 30 days.</li>
<li>Correct identity at receipt, return and consumption ≥ 99.9 % (RFID + DataMatrix).</li>
<li>Inventory accuracy (physical count vs system) ≥ 99.5 % after 30 days.</li>
<li>No dependence on external connectivity for operation; documented controlled degradation.</li>
</ul>

{sec("11", "Standards and compliance")}
{table(["Standard / regulation", "Application"], [
    ["RED Directive 2014/53/EU", "UWB and RFID radio equipment: health, safety, EMC and efficient spectrum use"],
    ["ETSI EN 302 065-2", "UWB location and tracking applications; verify the harmonised version in force"],
    ["Implementing Decision (EU) 2024/1467", "UWB limits 6–8.5 GHz: −41.3 dBm/MHz e.i.r.p. mean and 0 dBm peak; indoor enhanced power for localisation −31.3 dBm/MHz and 10 dBm under conditions"],
    ["omlox (PI) Core Zone v2 / Hub", "UWB interoperability (IEEE 802.15.4z, UL-TDoA, channel 9) and multi-technology integration"],
    ["Directive 2006/42/EC · EN ISO 13849 · EN 60204-1", "Receipt station and electromechanical elements (as declared in the base offer)"],
    ["Regulation (EU) 2023/1230", "Machinery delivered from 20/01/2027"],
], fcw="52mm")}

{sec("12", "Sources", dark=True)}
<p class="src">Internal: Of. 26-05-073V0 (MTorres) · IAR_EXECUTIVE_TECHNICAL_ASSESSMENT_REPORT.html · RTLS-UWB technical document v2 · Pozyx_/Sewio_/Eliko_/GrowSpace_Evaluacion_RTLS · Precios_Eliko · Eliko_Kit_Alquiler.<br>
Public (accessed 14/09/2026): pozyx.io/technology/rtls-explained · pozyx.io/products/software/location-and-sensor-hub · sewio.net/uwb-technology · sewio.net/customer-projects/toyota-motors · sewio.net/customer-projects/bora · sewio.net/customer-projects/seg-automotive · sewio.net (Budweiser Budvar 99 % uptime) · eliko.tech/elikos-active-passive-twr-protocol-explained · eliko.tech/product-new-kio-rtls · eliko.tech/case-study/vechicle-tracking-drives-efficiency-at-bosch · omlox.com · profibus.com/technologies/omlox · etsi.org EN 302 065-2 V2.1.1 · eur-lex.europa.eu 2014/53/EU · eur-lex.europa.eu OJ L 2024/1467.<br>
Manufacturer figures are cited as published facts, not independent audits. No primary MTorres publication on TorresFactory RTLS performance and no public Pozyx/ArcelorMittal ROI figure were found.
Issued by INGECART · Product Engineering. Rev. 1 — 14/09/2026.</p>
"""

HTML = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>INGECART · IAR Real-Time Roll Location — Informe técnico / Technical report</title>
{r2.reference_style()}
{SWITCH_CSS}
</head>
<body>
{SWITCH_HTML}
<div class="screen-note"><b>Vista previa / Browser preview.</b> Selector ES/EN arriba a la derecha; el PDF imprime el idioma visible. ES/EN switch top-right; the PDF prints the visible language.</div>
<div class="lang lang-es">
{ES}
</div>
<div class="lang lang-en hidden">
{EN}
</div>
{SWITCH_JS}
</body>
</html>
"""

for out in OUT:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(HTML, encoding="utf-8")
    print("written", out, len(HTML))
