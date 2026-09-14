"""Insert section 09A (removed infrastructure, speed, maintenance) into the INGETRANS Smart HTML report."""

from pathlib import Path

P = Path(r"C:\Users\isena\Documents\GitHub\AI-FACTORY-v2\INGETRANS_SMART_TECHNICAL_PRODUCT_REPORT_2026-09-10.html")

NEW_SECTION = """    <section class="section">
      <div class="lang lang-es">
        <div class="section-header">
          <div class="section-no">09A · Infraestructura eliminada, velocidad y mantenimiento</div>
          <h2>Que desaparece del Ingetrans actual y que cambia en la operacion</h2>
        </div>
        <p>La integracion de las ruedas motrices JNOV (DDW-4TP) elimina las dos infraestructuras fijas que concentran la obra civil y el mantenimiento del transfer: los carriles metalicos de rodadura (mas de 60 m en un corredor tipo de cinco roll stands) y la linea de contacto tipo Vahle que alimenta al carro en movimiento. La energia pasa a baterias Li-ion a bordo y el guiado a una linea DataMatrix sobre la solera.</p>
        <table class="kpi-table">
          <thead><tr><th>Elemento</th><th>Ingetrans (carril)</th><th>Ingetrans Smart</th></tr></thead>
          <tbody>
            <tr><td>Carriles de rodadura</td><td>Mas de 60 m empotrados, zanja, placas, nivelacion</td><td>Eliminados; ruedas de poliuretano sobre solera existente</td></tr>
            <tr><td>Linea de contacto Vahle</td><td>Catenaria, soportes y colector</td><td>Eliminada; 1 bateria Li-ion por rueda, cargador en armario ELC, parking con toma 230 V</td></tr>
            <tr><td>Obra civil</td><td>Zanjas y reparacion de solera en el corredor</td><td>Auditoria de planitud DIN 18202 (4 mm/1 m) y reparacion local</td></tr>
            <tr><td>Servicio de montaje de railes</td><td>Bloque especifico (referencia Paige: 14 dias, 1 tecnico)</td><td>No aplica</td></tr>
            <tr><td>Finales de carrera</td><td>Mecanicos en via</td><td>Codigos de posicion DataMatrix y zonas software</td></tr>
            <tr><td>Traccion</td><td>Motor unico sobre carril</td><td>2 x DDW-4TP, cuatro motores brushless, direccion diferencial, omnidireccional</td></tr>
            <tr><td>Mecanismo de bobina, rampas, vias a roll stands</td><td>Existentes</td><td>Se conservan sin cambio funcional</td></tr>
          </tbody>
        </table>
        <div class="grid">
          <div class="card col-6"><h3>Velocidades</h3><p>Transfer actual 80 m/min (4,8 km/h) frente a 2 km/h contractual del DDW-4TP (2,5 km/h como dato de gama). Ida de 12 m: 14 s frente a 26 s; de 30 m: 27 s frente a 59 s; de 60 m: 50 s frente a 113 s. Mision completa de 30 m con pick y drop: 66 s (54 misiones/h) frente a 129 s (28 misiones/h). Con 8,8 bobinas/h de referencia la utilizacion del carro Smart queda por debajo del 35 %.</p></div>
          <div class="card col-6"><h3>Regla de dimensionamiento</h3><p>Ofrecer Smart cuando misiones pico por hora x tiempo de mision Smart sea inferior al 60 % del tiempo disponible; por encima, mantener Ingetrans con carril o prever un segundo carro. La capacidad final se confirma con el gemelo digital sobre el layout aprobado.</p></div>
          <div class="card col-4"><h3>Seguridad</h3><p>Sistema de traccion con SS1 PLd (cat. 1 IEC 60204-1), STO, frenos sin tension, paro PLd/Cat 3 en mando y parada por perdida de radio. INGECART completa con escaneres de area, seta en armario, hombre muerto, entradas de seguridad y zonas de velocidad segura; CE de maquina completa e ISO 3691-4 a cargo de INGECART.</p></div>
          <div class="card col-4"><h3>Mantenimiento</h3><p>Desaparecen desgaste y alineacion de carril, escobillas de colector y reductor de traccion. Aparecen inspeccion de neumaticos y cambio de llanta, salud y ciclos de bateria (600 ciclos), limpieza de sensor optico y estado de la linea. Rueda intercambiable como unidad con un conector M23.</p></div>
          <div class="card col-4"><h3>Mejoras operativas</h3><p>Sin punto unico de fallo en alimentacion electrica, relayout por software, instalacion menos disruptiva, modo manual por radio como modo degradado y energia por mision medible para KPIs.</p></div>
        </div>
      </div>

      <div class="lang lang-en hidden">
        <div class="section-header">
          <div class="section-no">09A · Removed infrastructure, speed and maintenance</div>
          <h2>What disappears from current Ingetrans and what changes in operation</h2>
        </div>
        <p>Integrating JNOV drive and steering wheels (DDW-4TP) removes the two fixed infrastructures that concentrate civil work and maintenance in the transfer car: the embedded steel running rails (more than 60 m in a typical five-roll-stand corridor) and the Vahle-type conductor line powering the car in motion. Power moves to on-board Li-ion batteries and guidance to a DataMatrix floor line.</p>
        <table class="kpi-table">
          <thead><tr><th>Element</th><th>Ingetrans (rail)</th><th>Ingetrans Smart</th></tr></thead>
          <tbody>
            <tr><td>Running rails</td><td>More than 60 m embedded, trench, plates, levelling</td><td>Removed; polyurethane wheels on the existing floor</td></tr>
            <tr><td>Vahle conductor line</td><td>Catenary, supports and collector</td><td>Removed; one Li-ion battery per wheel, charger in ELC cabinet, parking with 230 V socket</td></tr>
            <tr><td>Civil works</td><td>Trenches and floor repair along the corridor</td><td>DIN 18202 flatness survey (4 mm/1 m) and local repair</td></tr>
            <tr><td>Rail installation service</td><td>Dedicated block (Paige reference: 14 days, 1 technician)</td><td>Not applicable</td></tr>
            <tr><td>End stops</td><td>Mechanical on rail</td><td>DataMatrix position codes and software zones</td></tr>
            <tr><td>Traction</td><td>Single motor on rail</td><td>2 x DDW-4TP, four brushless motors, differential steering, omnidirectional</td></tr>
            <tr><td>Reel mechanism, ramps, roll-stand tracks</td><td>Existing</td><td>Retained without functional change</td></tr>
          </tbody>
        </table>
        <div class="grid">
          <div class="card col-6"><h3>Speeds</h3><p>Current transfer 80 m/min (4.8 km/h) versus 2 km/h contractual for DDW-4TP (2.5 km/h as range value). One-way 12 m: 14 s vs 26 s; 30 m: 27 s vs 59 s; 60 m: 50 s vs 113 s. Full 30 m mission with pick and drop: 66 s (54 missions/h) vs 129 s (28 missions/h). At the 8.8 reels/h reference demand, Smart carriage utilisation stays below 35%.</p></div>
          <div class="card col-6"><h3>Sizing rule</h3><p>Offer Smart when peak missions per hour x Smart mission time is below 60% of available time; above that, keep rail-guided Ingetrans or plan a second carriage. Final capacity is confirmed with the digital twin on the approved layout.</p></div>
          <div class="card col-4"><h3>Safety</h3><p>Drive system with SS1 PLd (cat. 1 IEC 60204-1), STO, power-off brakes, PLd/Cat 3 E-stop on the remote and stop on radio loss. INGECART completes with area scanners, cabinet E-stop, dead-man handle, safety inputs and safe-speed zones; full-machine CE and ISO 3691-4 are INGECART scope.</p></div>
          <div class="card col-4"><h3>Maintenance</h3><p>Rail wear and alignment, collector brushes and traction gearbox disappear. Tyre inspection and rim replacement, battery health and cycles (600 cycles), optical sensor cleaning and floor-line condition appear. Wheel exchangeable as a unit through one M23 connector.</p></div>
          <div class="card col-4"><h3>Operational gains</h3><p>No single point of failure in power supply, software relayout, less disruptive installation, radio manual mode as degraded mode and measurable energy per mission for KPIs.</p></div>
        </div>
      </div>
    </section>

"""


def main() -> None:
    raw = P.read_bytes()
    newline = "\r\n" if b"\r\n" in raw else "\n"
    text = raw.decode("utf-8")
    marker = '<div class="section-no">10 · Configuracion de referencia</div>'
    idx = text.index(marker)
    # walk back to the start of the enclosing <section class="section">
    start = text.rfind('<section class="section">', 0, idx)
    start = text.rfind(newline, 0, start) + len(newline)
    if "09A · Infraestructura eliminada" in text:
        print("section 09A already present")
        return
    block = NEW_SECTION.replace("\n", newline)
    text = text[:start] + block + text[start:]
    P.write_text(text, encoding="utf-8", newline="")
    print("inserted 09A; sections:", text.count('<section class="section">'))


if __name__ == "__main__":
    main()
