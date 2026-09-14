"""Generate the INGETRANS Smart product report (R2, IGC-DW basis) using the style, format and
structure of the INGECART technical document "INGETRANS_smart_technical data.html".

The <style> block is copied verbatim from the reference so the WeasyPrint page furniture
(header band, footer, page numbers) and the screen preview behave identically.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

REFERENCE = Path(r"C:\Users\isena\Documents\INGECART\PRODUCTO\INGETRANS\INGETRANS_smart_technical data.html")
BASELINE = Path(r"C:\Users\isena\Documents\GitHub\AI-FACTORY-v2\knowledge\corrugated_equipment\ingetrans_smart_technical_baseline_R2_2026-09-14.json")
PREVIOUS_REPORT = Path(r"C:\Users\isena\Documents\INGECART\MARKETING\ARTWORK\INGETRANS\INGETRANS_SMART_TECHNICAL_PRODUCT_REPORT_2026-09-10.html")
COVER_IMAGE = Path(r"C:\Users\isena\Documents\INGECART\MARKETING\ARTWORK\INGETRANS\Ingetrans SMART.png")
OUTPUTS = [
    Path(r"C:\Users\isena\Documents\INGECART\MARKETING\ARTWORK\INGETRANS\INGETRANS_SMART_PRODUCT_REPORT_IGC-DW_R2_2026-09-14.html"),
    Path(r"C:\Users\isena\Documents\GitHub\AI-FACTORY-v2\INGETRANS_SMART_PRODUCT_REPORT_IGC-DW_R2_2026-09-14.html"),
]


def reference_style() -> str:
    s = REFERENCE.read_text(encoding="utf-8")
    m = re.search(r"<style>.*?</style>", s, re.S)
    if not m:
        raise SystemExit("Reference <style> block not found")
    return m.group(0)


def embedded_logo() -> str:
    """Reuse the base64 INGECART logo already embedded in the previous report so the file is self-contained."""
    s = PREVIOUS_REPORT.read_text(encoding="utf-8")
    m = re.search(r'src="(data:image/png;base64,[A-Za-z0-9+/=]+)"[^>]*alt="Ingecart logo"', s)
    return m.group(1) if m else "logo.png"


def embedded_cover_image() -> str:
    import base64
    import io

    from PIL import Image

    im = Image.open(COVER_IMAGE)
    im.thumbnail((1200, 1200))
    buf = io.BytesIO()
    im.convert("RGB").save(buf, "JPEG", quality=80)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def table(headers, rows, cls="", first_col_width=None):
    th = "".join(f"<th>{h}</th>" for h in headers)
    body = []
    for r in rows:
        tds = []
        for i, c in enumerate(r):
            style = f' style="width:{first_col_width}"' if (i == 0 and first_col_width) else ""
            tds.append(f"<td{style}>{c}</td>")
        body.append("<tr>" + "".join(tds) + "</tr>")
    cls_attr = f' class="{cls}"' if cls else ""
    return f"<table{cls_attr}><thead><tr>{th}</tr></thead><tbody>{''.join(body)}</tbody></table>"


def sec(n, title, dark=False):
    k = " k" if dark else ""
    return f'<div class="sec{k}"><span class="n">{n}</span>{title}</div>'


def build(b: dict) -> str:
    dw20 = b["drive_wheel_family"]["IGC-DW20"]
    dw100 = b["drive_wheel_family"]["IGC-DW100"]
    bc = b["base_case"]
    mp = b["ingetrans_reel_case_mapping"]
    tt = mp["one_way_travel_s_by_distance"]

    parts = []
    parts.append(f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>INGECART · INGETRANS Smart — Informe técnico de producto R2</title>
{reference_style()}
</head>
<body>
<div class="screen-note">
<b>Vista previa en navegador.</b> Esta es la versión editable. El navegador no reproduce la banda
de cabecera ni el pie corporativo de cada página: eso lo aplica el motor de maquetación al generar
el PDF. Para regenerarlo tras editar:
<code>weasyprint INGETRANS_SMART_PRODUCT_REPORT_IGC-DW_R2_2026-09-14.html salida.pdf</code>
</div>

<!-- ===================== PORTADA ===================== -->
<img src="{embedded_logo()}" class="cover-logo" alt="INGECART">
<div class="cover-kicker">Informe técnico de producto</div>
<div class="cover-title">INGETRANS Smart<br>Alimentación de bobinas sin carril</div>
<div class="cover-rule"></div>
<div class="cover-sub">
Evolución del sistema INGETRANS de suministro y retorno de bobinas a la corrugadora: el carro
transfer pasa de rodar sobre carril embebido y alimentarse por línea de contacto, a circular sobre
la solera existente con ruedas motrices INGECART IGC-DW, navegación láser y batería embarcada.
</div>
<img src="{embedded_cover_image()}" alt="INGETRANS Smart" style="width:100%;margin:4mm 0 2mm 0;border-bottom:1.2pt solid #FF6304;">
<div class="cover-claim">
<b>La misma logística de bobinas. Sin abrir el suelo del corredor.</b><br>
Sin más de 60 m de carril embebido, sin línea Vahle, sin acometida fija a lo largo del recorrido.
La entrega y el retorno automático de bobinas a los roll stands se mantienen; la obra civil y la
infraestructura fija desaparecen.
</div>

<table class="meta" style="margin-top:10mm">
<tbody>
<tr><td>Producto</td><td>INGETRANS Smart — variante rail-less de INGETRANS</td><td>Nº documento</td><td>IS-SMART-R2 · Rev. 2</td></tr>
<tr><td>Aplicación</td><td>Suministro y retorno de bobinas de papel a roll stands de corrugadora</td><td>Fecha</td><td>14/09/2026</td></tr>
<tr><td>Base técnica</td><td>Ruedas motrices IGC-DW20 / IGC-DW100 · navegación láser · 48 V CC LiFePO4</td><td>Sustituye a</td><td>Informe Smart 2026-09-10 (base JNOV)</td></tr>
<tr><td>Documento fuente</td><td>Propuesta técnico-comercial P0001_2026 Rev. 1 — Transbordo sin obra civil</td><td>Estado</td><td>Base de producto validada · sujeta a estudio de aplicación</td></tr>
<tr><td>Emisor</td><td>INGECART · Ingeniería de Producto y Automatización</td><td>Web</td><td>www.ingecart.eu</td></tr>
</tbody>
</table>

<!-- ===================== 01 ONE PAGER ===================== -->
<div class="pb"></div>
{sec("01", "El producto, en una página")}

<table class="two"><tr><td class="l" style="width:50%">
<span class="tag">Situación</span>
<p>INGETRANS automatiza el transporte, la entrega y el retorno de bobinas entre la zona de
intercambio del almacén y los roll stands de la corrugadora con un carro transfer guiado por
carril embebido y alimentado por línea de contacto. Funciona, pero exige abrir la solera del
corredor en más de 60 m, nivelar el carril al milímetro, montar la línea aérea y parar la zona
durante semanas.</p>

<span class="tag o">Producto</span>
<p><b>INGETRANS Smart</b> conserva íntegra la función —recogida en la zona de intercambio,
entrega en la vía del roll stand, retorno de bobinas parciales— y elimina la infraestructura fija.
El carro rueda sobre la solera existente con ruedas motrices <b>IGC-DW</b>, navega por láser
sobre el contorno de la nave, se posiciona en cada estación con referencia local y se alimenta
de una batería LiFePO4 de 48 V con carga de oportunidad. INGECART fabrica la máquina completa
y emite el marcado CE.</p>

<span class="tag">Resultado</span>
<p>Cero carril, cero línea Vahle, instalación en días sin parar el corredor, recorrido editable
por software y un activo móvil que crece añadiendo estaciones o una segunda unidad.</p>
</td><td style="width:50%">

<table class="plain" style="margin-bottom:4mm">
<tbody>
<tr><td style="width:16mm"><span class="big-num">1</span></td><td style="padding-top:1mm"><b>No se toca el suelo</b><br><span class="note">El carro circula sobre el hormigón existente. Sin canal, sin hormigonado, sin curado, sin remate.</span></td></tr>
<tr><td><span class="big-num">2</span></td><td style="padding-top:1mm"><b>No se para la corrugadora</b><br><span class="note">Mapeado, ajuste de estaciones y formación se solapan con la producción. Sin ventana de parada por obra.</span></td></tr>
<tr><td><span class="big-num">3</span></td><td style="padding-top:1mm"><b>El layout deja de estar en hormigón</b><br><span class="note">Añadir un roll stand es dar de alta una estación. Mover la zona de intercambio es editar el mapa.</span></td></tr>
<tr><td><span class="big-num">4</span></td><td style="padding-top:1mm"><b>Sin punto único de fallo eléctrico</b><br><span class="note">Sin línea de contacto ni colector: batería embarcada y un único punto de carga.</span></td></tr>
<tr><td><span class="big-num">5</span></td><td style="padding-top:1mm"><b>Un único responsable</b><br><span class="note">INGECART entrega la máquina completa marcada CE, con expediente técnico, esquemas y servicio.</span></td></tr>
</tbody>
</table>
</td></tr></table>

<table class="kpi-wrap"><tr>
<td><span class="kpi-v">0 m</span><span class="kpi-l">Carril embebido</span></td>
<td><span class="kpi-v">0 m</span><span class="kpi-l">Línea de contacto</span></td>
<td><span class="kpi-v">0,90 m/s</span><span class="kpi-l">Velocidad con IGC-DW20</span></td>
<td><span class="kpi-v">18–20 sem.</span><span class="kpi-l">De pedido a marcado CE</span></td>
</tr></table>

<div class="callout orange">
<b>A quién va dirigido.</b> A plantas de cartón ondulado que quieren la automatización de bobinas de
INGETRANS pero no pueden asumir la obra de vía en el corredor de la corrugadora, operan en edificio
alquilado o con servicios enterrados, prevén cambios de layout o ampliación de roll stands, o
necesitan trazabilidad por movimiento sin congelar la instalación en hormigón.
</div>

<h3 class="sub">Contenido</h3>
<table class="two"><tr><td class="l" style="width:50%">
<table class="plain"><tbody>
<tr><td style="width:8mm">02</td><td>Qué es INGETRANS hoy y qué cambia</td></tr>
<tr><td>03</td><td>Qué se elimina y qué lo sustituye</td></tr>
<tr><td>04</td><td>Comparativa directa INGETRANS / INGETRANS Smart</td></tr>
<tr><td>05</td><td>Cómo funciona una misión de bobina</td></tr>
<tr><td>06</td><td>Capacidad y velocidad</td></tr>
<tr><td>07</td><td>Control abierto, datos y diagnóstico</td></tr>
</tbody></table>
</td><td style="width:50%">
<table class="plain"><tbody>
<tr><td style="width:8mm">08</td><td>Seguridad y marcado CE</td></tr>
<tr><td>09</td><td>Obra civil, instalación y mantenimiento</td></tr>
<tr><td>10</td><td>Preguntas frecuentes</td></tr>
<tr><td>11</td><td>Plan de implantación y datos necesarios</td></tr>
<tr><td>12</td><td>Estado de validación y puntos abiertos</td></tr>
<tr><td>A/B/C</td><td>Anexos: gama IGC-DW, cálculo del caso base y normativa</td></tr>
</tbody></table>
</td></tr></table>
""")

    # 02
    parts.append(f"""
<div class="pb"></div>
{sec("02", "Qué es INGETRANS hoy y qué cambia")}
<p class="lead">INGETRANS es un sistema llave en mano que transporta bobinas de papel desde la zona de
intercambio del almacén hasta las vías de cada roll stand y devuelve automáticamente las bobinas no
consumidas. Elimina las carretillas del área de la corrugadora, sincroniza la entrega con la
planificación y conserva la identidad de cada bobina. Esa función no cambia en INGETRANS Smart.</p>
{table(["Bloque funcional", "INGETRANS (carril)", "INGETRANS Smart"], [
    ["Recogida y entrega de bobina", "Mecanismo de elevación y cierre, ciclo ≈ 6 s por interfaz", "Se conserva sin cambio funcional"],
    ["Zona de intercambio y rampas", "Existentes", "Se conservan; rediseño ligero del vallado por zona móvil"],
    ["Vías a roll stands", "Vías motorizadas, hasta 10 (5 roll stands × 2)", "Se conservan"],
    ["Traslación del carro", "Motor único sobre carril embebido, 80 m/min", "Ruedas motrices IGC-DW sobre solera, 0,90 m/s (54 m/min) con DW20"],
    ["Guiado", "Carril + encóder + finales de carrera", "Navegación láser ±20 mm + referencia de estación ±5 mm"],
    ["Alimentación eléctrica", "Línea de contacto Vahle + colector", "Batería LiFePO4 48 V 200 Ah + carga de oportunidad"],
    ["Control", "PLC Siemens, PROFINET", "PLC Siemens embarcado, CANopen CiA 301/402 a accionamientos, WiFi industrial a planta"],
    ["Interfaz MES/ERP y trazabilidad", "Órdenes, destino, retorno", "Idéntica, ampliada con registro por transbordo y diagnóstico de accionamientos"],
    ["Responsable del marcado CE", "INGECART", "INGECART, fabricante de la máquina completa"],
], first_col_width="34mm")}
<div class="callout">
<b>Lo que no es.</b> INGETRANS Smart no es un AMR genérico adaptado a bobinas ni un kit de ruedas de
tercero montado sobre el carro actual. Es un producto INGECART: chasis portabobinas, ruedas motrices
IGC-DW propias, control, seguridad funcional y conformidad bajo una única responsabilidad.
</div>
""")

    # 03
    parts.append(f"""
<div class="pb"></div>
{sec("03", "Qué se elimina y qué lo sustituye")}
<p class="lead">Un INGETRANS sobre carril son tres proyectos superpuestos: una máquina, una obra y una
instalación eléctrica fija. Sólo el primero aporta valor productivo. INGETRANS Smart elimina los otros dos.</p>
{table(["Elemento eliminado", "Qué implicaba", "Solución INGETRANS Smart"], [
    ["Carriles de rodadura embebidos (más de 60 m en un corredor de 5 roll stands)", "Corte y demolición de solera, canal, armado, hormigonado, curado, nivelación ±2 mm, parada de zona 2–4 semanas", "Ruedas de poliuretano IGC-DW sobre la solera existente; recorrido virtual en el mapa de navegación"],
    ["Línea de contacto Vahle, soportes y colector", "Estructura portante, carril conductor o festón, acometida trifásica, trabajo en altura, escobillas", "Batería LiFePO4 48 V embarcada; cargador automático 48 V / 60 A en un punto de carga"],
    ["Acometida fija a lo largo del recorrido", "Cuadro, protecciones, canalización", "Una toma 230/400 V en la estación de carga"],
    ["Finales de carrera mecánicos", "Ajuste y desgaste", "Códigos de estación, zonas software y escáneres de seguridad"],
    ["Motor de traslación único y reductor", "Punto único de fallo de tracción", "Cuatro conjuntos IGC-DW con tracción, dirección, freno y encóder integrados; intercambiables como unidad"],
    ["Bloque de servicio de montaje de carriles", "Referencia Paige: 14 días, 1 técnico", "No aplica"],
], first_col_width="46mm")}
<h3 class="sub">Lo que el carril sí aportaba — y cómo se resuelve sin él</h3>
{table(["Función del carril", "Solución equivalente"], [
    ["Guiado geométrico del recorrido", "Navegación láser sobre el contorno natural de la nave, con ruta virtual editable"],
    ["Repetibilidad de posición en la vía del roll stand", "Referencia óptica o magnética en cada estación, independiente de la navegación: ±5 mm"],
    ["Reacción de esfuerzos laterales", "Ruedas motrices direccionales con corrección continua de trayectoria en lazo cerrado"],
    ["Alimentación continua", "Batería con carga de oportunidad en cada pausa de ciclo; nunca se detiene con bobina a bordo por falta de energía"],
    ["Delimitación física de la zona de paso", "Escáneres láser de seguridad con campos adaptados a velocidad, bumper, señalización y proyección de zona"],
], first_col_width="52mm")}
""")

    # 04
    parts.append(f"""
<div class="pb"></div>
{sec("04", "Comparativa directa INGETRANS / INGETRANS Smart")}
{table(["Criterio", "INGETRANS sobre carril", "INGETRANS Smart"], [
    ["Obra civil en el corredor", "Necesaria — canal, hormigonado, curado", "Ninguna — rueda sobre la solera existente"],
    ["Alimentación", "Línea de contacto + acometida fija", "Batería embarcada + un punto de carga"],
    ["Plazo de instalación en planta", "Semanas con parada de zona (montaje mecánico 28 d, carriles 14 d)", "Días sin parar la zona; bloque de carriles suprimido"],
    ["Velocidad de traslación", "80 m/min (1,33 m/s)", f"{dw20['travel_speed_m_s']:.2f} m/s ({dw20['travel_speed_m_min']} m/min) con IGC-DW20 · {dw100['travel_speed_m_s']:.2f} m/s con IGC-DW100"],
    ["Precisión de parada", "Mecánica, ±2 a ±5 mm", "±5 mm con referencia de estación"],
    ["Modificar el recorrido o añadir un roll stand", "Nueva obra civil y prolongar carril y línea", "Editar el mapa y dar de alta la estación"],
    ["Reubicar a otra corrugadora o nave", "Inviable en la práctica", "Transportar y remapear"],
    ["Ampliar capacidad", "Segundo carro exige segundo carril", "Segunda unidad en el mismo corredor con gestión de tráfico"],
    ["Mantenimiento", "Carril, escobillas o festón, cadena portacables, reductor", "Bandas de rodadura, batería, limpieza de ópticas"],
    ["Punto único de fallo eléctrico", "Línea de contacto y colector", "Ninguno"],
    ["Trazabilidad", "Señales de posición y órdenes", "Registro por transbordo: hora, origen, destino, estado + diagnóstico de accionamientos"],
    ["Valor residual", "Instalación fija amortizada contra un layout", "Activo móvil reutilizable"],
], first_col_width="40mm")}
<div class="callout">
<b>Dónde sigue ganando el carril.</b> En ciclos muy rápidos y continuos —por encima de unos 60 transbordos
por hora sostenidos— con carga constante y layout congelado a diez años, el carro sobre carril mantiene
ventaja en disponibilidad y coste por ciclo. Una corrugadora de referencia consume 8,8 bobinas/h; está muy
por debajo de ese umbral. Si el estudio de aplicación dice lo contrario, lo diremos.
</div>
""")

    # 05
    parts.append(f"""
<div class="pb"></div>
{sec("05", "Cómo funciona una misión de bobina")}
{table(["Paso", "Fase", "Qué ocurre"], [
    ["1", "Llamada", "El MES/ERP o la lógica de planta INGECART solicita una bobina para un roll stand, o el retorno de una bobina parcial."],
    ["2", "Aproximación", "El carro navega por láser hasta la zona de intercambio y reduce a 0,30 m/s en los últimos metros."],
    ["3", "Posicionamiento", "Ajuste fino contra la referencia de estación hasta ±5 mm, con confirmación mutua antes de habilitar la transferencia."],
    ["4", "Recogida", "Mecanismo INGETRANS de elevación y cierre sobre una o dos bobinas (≈ 6 s)."],
    ["5", "Traslado", "Traslación al roll stand con campos de seguridad activos y velocidad modulada según el entorno."],
    ["6", "Entrega", "Posicionamiento en la vía, descarga sobre el transportador de vía (≈ 6 s) y confirmación al sistema."],
    ["7", "Retorno / reposo", "Recogida opcional de bobina parcial en el viaje de vuelta; retorno a espera o a la estación de carga según nivel de batería."],
], first_col_width="10mm")}
<h3 class="sub">Subsistemas</h3>
{table(["Subsistema", "Contenido"], [
    ["Sistema de control de planta", "Llamadas, confirmaciones, trazabilidad, interfaz MES/ERP — WiFi industrial"],
    ["Navegación y gestión de misión", "Mapa, rutas, destinos, zonas, tráfico"],
    ["PLC embarcado — Siemens", "Secuencia, enclavamientos, diagnóstico, E/S seguras"],
    ["Accionamiento de tracción y dirección", f"Servocontroladores 48 V CC con STO · CANopen CiA 301 / DS 402 · ruedas IGC-DW"],
    ["Mecanismo portabobinas", "Elevación y cierre INGETRANS sobre chasis Smart"],
    ["Cadena de seguridad", "Escáneres delantero y trasero, bumper, setas, velocidad limitada segura"],
    ["Energía embarcada", "Batería LiFePO4 48 V 200 Ah con BMS · cargador automático 48 V / 60 A"],
], first_col_width="46mm")}
<div class="callout orange">
<b>Navegación y posicionamiento son dos cosas distintas.</b> La navegación láser lleva el carro hasta la
estación con ±20 mm —suficiente para circular por el corredor, insuficiente para transferir una bobina a la
vía. El último tramo lo cierra la referencia local de estación, que garantiza los ±5 mm.
</div>
""")

    # 06
    parts.append(f"""
<div class="pb"></div>
{sec("06", "Capacidad y velocidad")}
<p class="lead">INGETRANS Smart es más lento en punta que el carro sobre carril. En cadencia efectiva la
diferencia es menor, porque el ciclo lo dominan las interfaces de recogida y entrega, no el traslado.
Perfil trapezoidal; carril con rampas de 4,5 s, Smart con aceleración de 0,30 m/s²; 6 s + 6 s de interfaz.</p>
{table(["Distancia zona de intercambio → roll stand", "INGETRANS carril (80 m/min)", "INGETRANS Smart (0,90 m/s, IGC-DW20)"], [
    ["12 m (roll stand más cercano)", f"≈ {tt['12 m']['rail_80_m_min']:.0f} s", f"≈ {tt['12 m']['smart_dw20']:.0f} s"],
    ["26 m (recorrido del caso base)", f"≈ {tt['26 m']['rail_80_m_min']:.0f} s", f"≈ {tt['26 m']['smart_dw20']:.0f} s"],
    ["30 m (medio corredor)", f"≈ {tt['30 m']['rail_80_m_min']:.0f} s", f"≈ {tt['30 m']['smart_dw20']:.0f} s"],
    ["60 m (extremo del corredor)", f"≈ {tt['60 m']['rail_80_m_min']:.0f} s", f"≈ {tt['60 m']['smart_dw20']:.0f} s"],
    ["Misión completa 30 m ida y vuelta con recogida y entrega", "≈ 66 s (≈ 54 misiones/h)", "≈ 85 s (≈ 42 misiones/h)"],
], first_col_width="58mm")}
<table class="kpi-wrap"><tr>
<td><span class="kpi-v">8,8</span><span class="kpi-l">Bobinas/h · corrugadora de referencia</span></td>
<td><span class="kpi-v">&lt; 25 %</span><span class="kpi-l">Utilización del carro Smart a 30 m</span></td>
<td><span class="kpi-v">2</span><span class="kpi-l">Bobinas por viaje</span></td>
<td><span class="kpi-v">≈ 60/h</span><span class="kpi-l">Umbral donde el carril gana</span></td>
</tr></table>
<div class="callout">
<b>Regla de producto.</b> INGETRANS Smart se ofrece cuando las misiones pico por hora multiplicadas por el
tiempo de misión Smart quedan por debajo del 60 % del tiempo disponible. El estudio de aplicación simula el
ciclo real de la planta con el gemelo digital INGECART y entrega las bobinas/hora que se pueden esperar.
</div>
<p class="note">Por encima de 10 t de masa total la velocidad se limita a 0,43 m/s (IGC-DW100) por criterio de
estabilidad de la carga: la energía cinética crece con el cuadrado de la velocidad y, en una parada protectora,
el riesgo de desplazamiento de la bobina pasa a ser el factor dimensionante.</p>
""")

    # 07
    parts.append(f"""
<div class="pb"></div>
{sec("07", "Control abierto, datos y diagnóstico")}
<p class="lead">Los accionamientos de las ruedas se comunican por CANopen según CiA 301 y DS 402, el mismo
lenguaje de los servoaccionamientos industriales europeos. El control se ejecuta en un PLC Siemens
convencional; rampas, límites de par, ventanas de posición y velocidades máximas son accesibles y quedan
documentados en la entrega.</p>
{table(["Variable monitorizada", "Uso práctico"], [
    ["Corriente y par reales de cada motor", "Detección de aumento progresivo del esfuerzo: rodadura degradada, rodamiento o solera deteriorada, antes de la avería"],
    ["Velocidad real y de consigna", "Verificación del perfil previsto; detección de deslizamiento"],
    ["Posición real y error de seguimiento", "Alarma temprana de desviación mecánica o pérdida de precisión en estación"],
    ["Temperatura de motor y disipador", "Protección frente a sobrecarga sostenida"],
    ["Tensión de bus", "Estado de batería en carga real, no sólo en reposo"],
    ["Códigos de fallo detallados", "Sobreintensidad, sobre/subtensión, sobretemperatura, encóder, fase, seguimiento, timeout — cada uno con código propio"],
    ["Vigilancia de comunicación", "Supervisión mutua PLC–accionamientos; ante caída del enlace, paso a estado seguro"],
], first_col_width="52mm")}
<h3 class="sub">Señales para la plataforma digital INGECART</h3>
<p>El carro publica estados por cambio con heartbeat, contadores monótonos y eventos con marca de tiempo de origen,
alineado con la especificación de captura de datos de Digital Ecosystem Platform:</p>
<ul>
<li>Tiempos de recogida, entrega y misión (P50/P95); eventos de starvation de roll stand imputables a logística.</li>
<li>Modo automático/manual, estado de carga de batería, tensión de bus, ciclos de carga.</li>
<li>Error de posicionamiento en estación, calidad de localización láser, intrusiones en campo de protección.</li>
<li>Corriente por rueda, error de seguimiento, índice de desgaste de banda, calidad de enlace WiFi, registro de eventos de seguridad.</li>
</ul>
""")

    # 08
    sf_rows = [[f["function"], f["implementation"], f["level"]] for f in b["safety_functions"]]
    sf_rows_es = [
        ["Detección de personas", "Escáneres láser de seguridad delantero y trasero, con campos de protección adaptados a velocidad y sentido de marcha", "PL d Cat. 3"],
        ["Parada de emergencia", "Setas accesibles desde los cuatro lados, doble canal, parada controlada seguida de freno", "PL d Cat. 3"],
        ["Parada por contacto", "Bumper mecánico perimetral como respaldo del escáner", "PL d Cat. 3"],
        ["Velocidad limitada segura", "Vigilancia sobre módulo seguro; reducción forzada en estaciones, cruces y maniobra", "PL d Cat. 3"],
        ["Retención en reposo", "Freno aplicado por muelle y liberado eléctricamente; ante corte de tensión el carro queda retenido", "PL c Cat. 1"],
        ["Bloqueo durante transferencia", "Traslación inhibida mientras hay transferencia en curso o bobina no asegurada", "PL c Cat. 1"],
    ]
    parts.append(f"""
<div class="pb"></div>
{sec("08", "Seguridad y marcado CE")}
<p class="lead">Al retirar el carril desaparece la barrera física entre la máquina y el personal. Esa separación se
sustituye por seguridad funcional certificada conforme a EN ISO 3691-4 y EN ISO 13849. Es donde un proyecto de
este tipo se gana o se pierde, y donde INGECART concentra la ingeniería.</p>
{table(["Función", "Cómo se resuelve", "Nivel"], sf_rows_es, first_col_width="34mm")}
<h3 class="sub">Medidas complementarias</h3>
<table class="two"><tr><td class="l" style="width:50%"><ul>
<li>Baliza luminosa y señal acústica de movimiento.</li>
<li>Proyección luminosa de la zona de barrido sobre el pavimento.</li>
<li>Señalización horizontal del corredor de circulación.</li>
<li>Selector de modo con llave: automático, manual y mantenimiento.</li>
</ul></td><td style="width:50%"><ul>
<li>Consola manual con dispositivo de habilitación de tres posiciones.</li>
<li>Velocidad limitada a 0,30 m/s en modo manual y mantenimiento.</li>
<li>Seccionador de batería bloqueable para consignación.</li>
<li>Registro de eventos de seguridad accesible desde el diagnóstico.</li>
</ul></td></tr></table>
<h3 class="sub">Qué recibe el cliente</h3>
{table(["Elemento", "Contenido"], [
    ["Una máquina, no un conjunto de piezas", "INGECART actúa como fabricante del equipo completo y emite el marcado CE bajo su responsabilidad"],
    ["Expediente técnico completo", "Evaluación de riesgos, cálculo y validación de funciones de seguridad, esquemas EPLAN Electric P8, informe EMC, verificaciones eléctricas"],
    ["Declaración UE de conformidad", "Directiva 2006/42/CE; los equipos entregados desde el 20 de enero de 2027 se declaran según el Reglamento (UE) 2023/1230"],
    ["Documentación de uso", "Manual de instrucciones, manual de mantenimiento, lista de repuestos recomendados y formación a operadores y mantenedores"],
], first_col_width="46mm")}
<div class="callout">
<b>Frenado y estabilidad de la bobina.</b> La lógica de seguridad ejecuta primero un frenado eléctrico controlado y
aplica el freno mecánico al final de la rampa. La deceleración de emergencia se limita a 1,50 m/s² para no desplazar
la carga. Las distancias reales de parada se miden con la bobina del cliente en las pruebas de aceptación.
</div>
""")

    # 09
    ci = b["civil_and_infrastructure_impact"]
    rm = ci["rail_solution_removed_items_26_m_route_eur"]
    ni = ci["new_items_eur"]
    parts.append(f"""
<div class="pb"></div>
{sec("09", "Obra civil, instalación y mantenimiento")}
<h3 class="sub">Partidas que desaparecen</h3>
{table(["Partida de la solución sobre carril", "Orden de magnitud", "Con INGETRANS Smart"], [
    ["Obra civil de rodadura: corte, demolición, canal, armado, hormigonado y remate (recorrido de 26 m)", rm["civil_works"] + " €", "Suprimida"],
    ["Suministro, alineación y nivelación de carril", rm["rail_supply_and_levelling"] + " €", "Suprimida"],
    ["Línea de contacto o festón, estructura portante y acometida trifásica", rm["conductor_line_structure_and_feed"] + " €", "Suprimida"],
    ["Desvío de servicios enterrados e imprevistos de obra", "Riesgo abierto", "Eliminado"],
    ["Parada de zona durante la ejecución", "3–6 semanas", "2–5 días de instalación sin parar"],
    ["Mantenimiento anual de carril, festón y cadena portacables", rm["annual_rail_and_festoon_maintenance"].replace(" per year", " €/año"), "Suprimido"],
    ["<b>Inversión de habilitación evitada</b>", "<b>" + rm["total_enablement_avoided"].replace(" plus lost production", " €") + "</b>", "<b>+ lucro cesante</b>"],
], first_col_width="70mm")}
<p class="note">Rangos orientativos para una instalación tipo en España referidos a un recorrido de 26 m. En un corredor
INGETRANS de más de 60 m las partidas de carril y línea escalan con la longitud. No constituyen oferta; se sustituyen por
las cifras reales de la planta en el estudio de aplicación.</p>
<h3 class="sub">Partidas que aparecen</h3>
{table(["Concepto", "Orden de magnitud", "Naturaleza"], [
    ["Estación de carga automática", ni["charging_station"] + " €", "Inversión"],
    ["Puesta en marcha, mapeado, ajuste y formación", ni["commissioning_mapping_training"] + " €", "Inversión"],
    ["Refuerzo de cobertura inalámbrica, si procede", ni["wireless_coverage_reinforcement"] + " €", "Inversión"],
    ["Sustitución de batería a fin de vida útil", "Año 7–10", "Reposición"],
    ["Sustitución de bandas de rodadura", "Según ciclos", "Consumible"],
    ["Consumo eléctrico en operación", "≈ 1,3 kWh por hora de operación", "Explotación"],
], first_col_width="70mm")}
<h3 class="sub">Mantenimiento comparado</h3>
{table(["Aspecto", "INGETRANS carril", "INGETRANS Smart"], [
    ["Preventivo", "Desgaste, limpieza y alineación de carril; escobillas o festón; cadena portacables; reductor de tracción", "Inspección de bandas de rodadura, limpieza de ópticas de navegación y seguridad, verificación anual de funciones de seguridad, seguimiento de batería"],
    ["Repuestos", "Escobillas, fijaciones de carril, motor de traslación", "Rueda IGC-DW intercambiable como unidad embridada; batería (año 7–10); bandas; ópticas"],
    ["Predictivo", "Limitado", "Corriente, par, temperatura y error de seguimiento por rueda anticipan la intervención"],
    ["Modo degradado", "Carro parado en vía", "Consola manual para evacuar la bobina a bordo; procedimiento de respaldo con carretilla"],
], first_col_width="28mm")}
""")

    # 10 FAQ
    faqs = [
        ("¿Y si el suelo del corredor no está perfecto?", "No hace falta que lo esté. Hormigón industrial en buen estado, sin roturas en la calle de circulación, desnivel local inferior a unos ±5 mm en 2 m y juntas por debajo de 20 mm. Se mide en la visita técnica; los tramos que requieran adecuación se identifican y presupuestan antes de comprometer nada."),
        ("¿Es más lento que INGETRANS sobre carril?", "En punta sí: 0,90 m/s frente a 80 m/min (1,33 m/s). En cadencia efectiva la diferencia es menor porque el ciclo lo dominan las interfaces de recogida y entrega. A 8,8 bobinas/h la utilización del carro queda por debajo del 25 %. El estudio de aplicación simula el ciclo real."),
        ("¿Qué pasa si se queda sin batería con una bobina a bordo?", "No ocurre por diseño: carga de oportunidad en cada pausa mantiene el nivel en banda alta. Al alcanzar la reserva, el carro completa la misión en curso y acude a cargar avisando con antelación."),
        ("¿Es seguro con personal y carretillas en el corredor?", "Es la situación para la que está diseñado: escáneres con campos adaptados a la velocidad, bumper de respaldo, velocidad limitada vigilada, señalización acústica y luminosa. Las distancias de parada se verifican con la bobina real en la aceptación."),
        ("¿Quién responde del marcado CE?", "INGECART, como fabricante del equipo completo. El cliente recibe una máquina marcada, con expediente técnico y declaración UE de conformidad."),
        ("¿Quedo atado a un software propietario?", "No. Los accionamientos hablan CANopen en perfiles estándar y el control se ejecuta sobre PLC Siemens convencional, con parámetros documentados en la entrega."),
        ("¿Puedo añadir un roll stand o mover la zona de intercambio dentro de dos años?", "Sí. Añadir un destino es dar de alta una estación; cambiar el recorrido es editar el mapa. Trasladar el equipo a otra corrugadora requiere transporte, remapeado y ajuste de estaciones. Nada de ello implica obra."),
        ("¿Y si crece la producción?", "Se añade una segunda unidad al mismo corredor con gestión de tráfico. No hay infraestructura que duplicar."),
    ]
    faq_html = "".join(f'<div class="faq"><div class="q">{q}</div><div class="a">{a}</div></div>' for q, a in faqs)
    parts.append(f"""
<div class="pb"></div>
{sec("10", "Preguntas frecuentes")}
{faq_html}
""")

    # 11
    ip = b["implementation_plan_weeks"]
    parts.append(f"""
<div class="pb"></div>
{sec("11", "Plan de implantación y datos necesarios")}
{table(["Fase", "Actividad", "Entregable", "Plazo"], [
    ["F1", "Estudio de aplicación", "Informe de viabilidad, layout propuesto, capacidad verificada con gemelo digital y oferta cerrada", f"{ip['F1_application_study']} sem."],
    ["F2", "Ingeniería de detalle", "Planos del chasis portabobinas, esquemas eléctricos, evaluación de riesgos, lista de materiales", f"{ip['F2_detail_engineering']} sem."],
    ["F3", "Aprovisionamiento y fabricación", "Carro montado y cableado, armario probado", f"{ip['F3_procurement_and_manufacturing']} sem."],
    ["F4", "Pruebas en INGECART", "Protocolo firmado, incluidas distancias de parada con bobina", f"{ip['F4_factory_tests']} sem."],
    ["F5", "Instalación y puesta en marcha", "Mapeado en planta, ajuste de estaciones, integración con vías y MES, formación", f"{ip['F5_installation_and_commissioning']} sem."],
    ["F6", "Conformidad y entrega", "Expediente técnico, declaración UE, marcado CE y acta de recepción", f"{ip['F6_conformity_and_handover']} sem."],
    ["—", "<b>Plazo total estimado</b>", "Desde firma de pedido", f"<b>{ip['total_from_order']} sem.</b>"],
], first_col_width="10mm")}
<h3 class="sub">Datos que confirmamos en la visita</h3>
{table(["Bloque", "Qué confirmamos"], [
    ["Bobina", "Matriz de bobinas: masa máxima, diámetro, ancho, tipo de mandril y altura del centro de gravedad; una o dos bobinas por viaje"],
    ["Recorrido", "Distancia zona de intercambio–roll stands, número de vías, trazado del corredor y obstáculos"],
    ["Productividad", "Bobinas/hora en punta y en media, turnos y disponibilidad exigida"],
    ["Transferencia", "Altura y tolerancia de las vías de roll stand y de la zona de intercambio"],
    ["Solera", "Estado, planitud medida, juntas y pendiente — condiciona precisión y desgaste"],
    ["Entorno humano", "Tránsito de personal y carretillas en el corredor — determina el nivel de las protecciones"],
    ["Eléctrico y red", "Tensión en el punto de carga y cobertura WiFi a lo largo del recorrido"],
    ["Control", "PLC de planta, protocolo disponible, señales y MES/ERP"],
], first_col_width="30mm")}
""")

    # 12 validation status
    parts.append(f"""
<div class="pb"></div>
{sec("12", "Estado de validación y puntos abiertos", dark=True)}
{table(["Elemento", "Estado", "Base"], [
    ["Gama de ruedas IGC-DW20 / IGC-DW100", "Validado", "Documento técnico INGECART P0001_2026 Rev. 1; recálculo independiente coherente (±3 %)"],
    ["Memoria de cálculo del caso base (3,5 t, 26 m)", "Validado", "Tracción, adherencia, potencia, frenado y energía reproducidos; freno mecánico 2,47 m/s² declarado frente a 2,74 recalculado (conservador)"],
    ["Configuración pesada 40 t (4 × IGC-DW100)", "Validado", "Margen de tracción 1,91 reproducido"],
    ["Arquitectura de seguridad y normativa", "Validado", "EN ISO 3691-4, EN ISO 13849, EN 60204-1, EN 61800-5-2, Reglamento (UE) 2023/1230"],
    ["Configuración de ruedas para chasis portabobinas INGETRANS", "Pendiente", "4 × IGC-DW20 (≤ 6 t) o 4 × IGC-DW100 según matriz de bobinas y tara del chasis"],
    ["Interfaz chasis Smart – mecanismo de elevación – vías de roll stand", "Pendiente", "Ingeniería de detalle F2"],
    ["Capacidad en corredor de cliente", "Pendiente", "Gemelo digital sobre layout aprobado (0,90 m/s, aproximación 0,30 m/s)"],
    ["Coste y precio de la variante Smart", "Pendiente", "Escandallo de producto; en Paige se oferta al mismo EXW que INGETRANS carril"],
], first_col_width="52mm")}
<div class="callout orange">
<b>Nota de revisión.</b> Esta revisión R2 sustituye la base técnica del informe del 10/09/2026, que se apoyaba en
módulos de tracción de tercero (JNOV MDS/DDW-4TP, 2 km/h, guiado por línea DataMatrix, cuasi-máquina). La base
vigente es la familia de ruedas motrices propias IGC-DW, navegación láser con referencia de estación, batería
LiFePO4 48 V y marcado CE de máquina completa por INGECART.
</div>
""")

    # Annex A
    c = b["drive_wheel_family"]["common"]
    parts.append(f"""
<div class="pb"></div>
{sec("A", "Anexo — Gama de ruedas motrices IGC-DW", dark=True)}
<p class="lead">La rueda motriz direccional es el elemento que hace posible prescindir del carril: integra tracción,
dirección, reducción, frenado y realimentación en un único conjunto embridado sobre el chasis. Dos tamaños cubren
de 2 a 40 toneladas de masa total.</p>
{table(["Parámetro", "IGC-DW20", "IGC-DW100"], [
    ["Carga máxima por rueda", f"{dw20['max_load_per_wheel_kg']:,} kg".replace(",", "."), f"{dw100['max_load_per_wheel_kg']:,} kg".replace(",", ".")],
    ["Diámetro de rueda", f"Ø {dw20['wheel_diameter_mm']} mm", f"Ø {dw100['wheel_diameter_mm']} mm"],
    ["Potencia motor de tracción", f"{dw20['traction_power_w']:,} W".replace(",", "."), f"{dw100['traction_power_w']:,} W".replace(",", ".")],
    ["Par nominal de tracción", f"{dw20['traction_torque_nm']:.1f} N·m", f"{dw100['traction_torque_nm']:.1f} N·m"],
    ["Velocidad nominal del motor", f"{dw20['motor_speed_rpm']:,} rpm".replace(",", "."), f"{dw100['motor_speed_rpm']:,} rpm".replace(",", ".")],
    ["Relación de reducción", f"1 : {dw20['reduction']}", f"1 : {dw100['reduction']}"],
    ["Velocidad de traslación", f"{dw20['travel_speed_m_s']:.2f} m/s ({dw20['travel_speed_m_min']} m/min)", f"{dw100['travel_speed_m_s']:.2f} m/s ({dw100['travel_speed_m_min']} m/min)"],
    ["Intensidad nominal", f"{dw20['traction_current_a']} A", f"{dw100['traction_current_a']} A"],
    ["Par de freno de estacionamiento", f"{dw20['parking_brake_torque_nm']} N·m", "Según configuración"],
    ["Potencia motor de dirección", f"{dw20['steering_power_w']} W", f"{dw100['steering_power_w']:,} W (S2 60 min)".replace(",", ".")],
    ["Par de dirección", f"{dw20['steering_torque_nm']} N·m", f"{dw100['steering_torque_nm']} N·m"],
    ["Reducción de dirección", f"1 : {dw20['steering_reduction']}", f"1 : {dw100['steering_reduction']}"],
    ["Altura total del conjunto", f"≈ {dw20['height_mm']} mm", f"≈ {dw100['height_mm']} mm"],
    ["Brida de fijación", dw20["flange"].replace(" on diameter ", " · Ø "), dw100["flange"].replace(" on diameter ", " · Ø ")],
], first_col_width="46mm")}
{table(["Característica común", "Valor"], [
    ["Tensión de alimentación", f"{c['supply_v_dc']} V CC"],
    ["Tipo de motor", "Servomotor CC sin escobillas · servicio S1 continuo · rendimiento ≈ 90 %"],
    ["Realimentación", "Encóder incremental 2.500 ppr en tracción · encóder absoluto en dirección"],
    ["Protección / temperatura", "IP65 (excepto eje) · −20 °C a +50 °C"],
    ["Control", "CANopen CiA 301 / DS 402 (recomendado) · CAN 2.0B · RS-485"],
    ["Modos de operación", "Par · velocidad · posición · posición síncrona cíclica · búsqueda de origen"],
], first_col_width="46mm")}
<h3 class="sub">Configuraciones habituales</h3>
{table(["Masa total", "Configuración", "Aplicación típica"], [
    ["≤ 3.500 kg", "2 × IGC-DW20 + 4 ruedas locas", "Palet europeo, bobinas ligeras, cajas. Tracción diferencial con giro sobre el propio eje."],
    ["≤ 6.000 kg", "4 × IGC-DW20 + 4 ruedas locas", "Plataforma 4 × 2 m con tracción y dirección en las cuatro esquinas. <b>Configuración de referencia para el chasis portabobinas INGETRANS Smart.</b>"],
    ["≤ 40.000 kg", "4 × IGC-DW100 + apoyos", "Bobinas de gran formato, dobles bobinas pesadas, utillajes. Velocidad reducida a 0,43 m/s por estabilidad de carga."],
], first_col_width="24mm")}
""")

    # Annex B
    parts.append(f"""
<div class="pb"></div>
{sec("B", "Anexo — Memoria de cálculo del caso base", dark=True)}
<h3 class="sub">B.1 · Datos de partida</h3>
{table(["Concepto", "Valor", "Observación"], [
    ["Dimensiones de plataforma", "2.800 × 1.500 mm", "Plataforma de referencia del documento técnico"],
    ["Carga útil", "2.000 kg", "Caso base; el chasis portabobinas INGETRANS se dimensiona con la matriz de bobinas"],
    ["Tara estimada", "1.500 kg", "Chasis, cubierta, batería y armario"],
    ["Masa total de diseño", "3.500 kg", "Valor de cálculo"],
    ["Recorrido por transbordo", "26 m", "Ida cargada, retorno en vacío"],
    ["Velocidad de traslación", "0,90 m/s", "0,30 m/s en aproximación a estación"],
    ["Aceleración de servicio", "0,30 m/s²", "Criterio de confort de carga"],
    ["Coeficiente de rodadura", "0,025", "Poliuretano sobre hormigón pulido, conservador"],
    ["Pendiente residual", "1,0 %", "Irregularidad de solera industrial"],
], first_col_width="46mm")}
<h3 class="sub">B.2 · Esfuerzo de tracción requerido y disponible</h3>
<div class="formula">
F<sub>rodadura</sub> = f · m · g = 0,025 × 3.500 × 9,81 = 858 N<br>
F<sub>pendiente</sub> = m · g · sen α = 3.500 × 9,81 × 0,010 = 343 N<br>
F<sub>aceleración</sub> = m · a = 3.500 × 0,30 = 1.050 N<br>
F<sub>requerida</sub> = 2.251 N → valor adoptado de diseño: 2.300 N
<hr class="fsep">
Par en rueda = M<sub>motor</sub> × i × η = 5,0 × 44,57 × 0,90 = 200,6 N·m<br>
Esfuerzo por rueda = 200,6 / 0,130 = 1.543 N · con 2 ruedas motrices = 3.086 N<br>
Margen: 3.086 / 2.251 = 1,37 → CUMPLE
</div>
<h3 class="sub">B.3 · Verificación de adherencia</h3>
<div class="formula">
Carga sobre ruedas motrices (≈ 50 % del total) = 1.750 kg → N = 17,17 kN<br>
Esfuerzo máximo transmisible = µ · N = 0,60 × 17,17 = 10,30 kN &gt;&gt; 3,09 kN requeridos → SIN DESLIZAMIENTO
</div>
<h3 class="sub">B.4 · Potencia y frenado</h3>
{table(["Magnitud", "Valor", "Comentario"], [
    ["Potencia mecánica en régimen", "2,03 kW", "Incluida la fase de aceleración"],
    ["Potencia eléctrica absorbida", "≈ 2,39 kW", "Rendimiento de cadena 0,85"],
    ["Potencia instalada", "3,14 kW", "2 × IGC-DW20 · margen 31 %"],
    ["Deceleración de servicio", "0,40 m/s²", "Distancia de parada 1,01 m"],
    ["Parada protectora por escáner", "0,80 m/s²", "0,51 m + 0,14 m de reacción = 0,65 m"],
    ["Campo de protección a configurar", "≥ 1,00 m", "Incluye tolerancia de medida y desgaste de banda"],
    ["Deceleración de emergencia limitada", "1,50 m/s²", "Distancia 0,27 m. Límite por estabilidad de carga"],
    ["Capacidad del freno mecánico", "2,47 m/s²", "14 N·m × 44,57 en 2 ruedas. Reservado a pérdida de alimentación (recálculo INGECART: 2,74 m/s², valor declarado conservador)"],
], first_col_width="52mm")}
<h3 class="sub">B.5 · Energía y autonomía</h3>
{table(["Consumidor por ciclo", "Energía", "Base de cálculo"], [
    ["Traslación 26 m cargada (3.500 kg)", "9,4 Wh", "Rodadura, pendiente y una aceleración"],
    ["Traslación 26 m en vacío (1.500 kg)", "4,6 Wh", "Ídem con masa reducida"],
    ["Transportador / mecanismo de cubierta", "6,7 Wh", "1,5 kW durante 8 s en carga y en descarga"],
    ["Maniobras de dirección", "1,7 Wh", "Reorientación de ruedas en estación"],
    ["Auxiliares de control y seguridad", "8,8 Wh", "350 W durante 90 s de ciclo"],
    ["<b>Total por ciclo</b>", "<b>31,2 Wh</b>", "Valor de diseño adoptado: 35 Wh"],
    ["Batería adoptada", "48 V · 200 Ah", "LiFePO4 con BMS · 9,6 kWh · 80 % útil = 7,68 kWh"],
    ["Ciclos por carga", "≈ 219", "A 35 Wh por ciclo"],
    ["Autonomía a 30 ciclos/h", "7,3 h", "Cubre un turno completo sin recarga"],
    ["Recarga completa", "≈ 3,3 h", "Cargador 48 V / 60 A"],
    ["Consumo medio de red", "≈ 1,3 kWh/h", "A 30 ciclos/h, incluidas pérdidas de conversión"],
], first_col_width="56mm")}
<h3 class="sub">B.6 · Verificación de la configuración pesada (40 t)</h3>
<div class="formula">
Masa total 40.000 kg · 4 × IGC-DW100 · v = 0,43 m/s · a = 0,20 m/s²<br>
F<sub>requerida</sub> = 9.810 + 3.924 + 8.000 = 21.734 N<br>
Esfuerzo por rueda = 24,0 × 120 × 0,90 / 0,250 = 10.368 N → 4 ruedas = 41.472 N<br>
Margen: 41.472 / 21.734 = 1,91 → CUMPLE · Potencia mecánica = 9,35 kW sobre 20 kW instalados
</div>
<p class="note">Los valores de este anexo corresponden al caso base del documento técnico INGECART y han sido reproducidos de
forma independiente. El chasis portabobinas INGETRANS Smart se calcula con la matriz de bobinas del cliente en la fase F2.
Las distancias de parada se verifican con la carga real durante las pruebas de aceptación en fábrica y en planta.</p>
""")

    # Annex C
    parts.append(f"""
<div class="pb"></div>
{sec("C", "Anexo — Normativa aplicada", dark=True)}
{table(["Norma o reglamento", "Aplicación al equipo"], [
    ["Reglamento (UE) 2023/1230", "Reglamento de Máquinas, de aplicación obligatoria desde el 20 de enero de 2027. Los equipos entregados a partir de esa fecha se declaran conforme a este texto y no a la Directiva 2006/42/CE."],
    ["EN ISO 3691-4", "Carretillas de manutención sin conductor y sus sistemas. Norma rectora: detección de personas, distancias de parada, velocidades, marcado, señalización y modos de operación."],
    ["EN 1175", "Requisitos eléctricos de carretillas de manutención. Instalación embarcada de 48 V CC, batería, cargador y protecciones."],
    ["EN ISO 12100", "Metodología de evaluación y reducción de riesgos. Base del expediente técnico."],
    ["EN ISO 13849-1 / -2", "Nivel de prestaciones requerido, diseño de las funciones de seguridad y validación."],
    ["EN 60204-1", "Equipo eléctrico de las máquinas: categorías de parada, protección, conductores y verificaciones finales."],
    ["EN 61800-5-2", "Funciones de seguridad de los accionamientos: STO y, cuando aplique, SS1 y SLS."],
    ["IEC 61439", "Conjuntos de aparamenta de baja tensión. Armario embarcado."],
    ["IEC 81346", "Estructuración y designación de referencia de la documentación."],
    ["Directiva 2014/30/UE", "Compatibilidad electromagnética. Ensayos según la serie IEC 61000."],
    ["EN 619", "Equipos de manutención continua. Transportador de cubierta y vías de roll stand."],
    ["CiA 301 / CiA 402", "Perfiles de comunicación y accionamiento CANopen empleados en tracción y dirección."],
], first_col_width="44mm")}
<p class="note">Documento emitido por el Departamento de Ingeniería de Producto y Automatización de INGECART S.L. Informe técnico de
producto de carácter informativo. Las prestaciones, dimensionados y rangos económicos corresponden al caso base descrito y
quedan sujetos a confirmación en el estudio de aplicación. Rev. 2 — 14/09/2026. Sustituye al informe INGETRANS Smart del
10/09/2026.</p>
</body>
</html>
""")
    return "".join(parts)


def main() -> None:
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    html = build(baseline)
    for out in OUTPUTS:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html, encoding="utf-8")
        print("written", out, len(html))


if __name__ == "__main__":
    main()
