"""English body for the INGETRANS Smart product report R3 (IGC-DW100 only, bilingual edition).

Mirrors section by section the Spanish body produced by build_ingetrans_smart_report_r2.py after the
DW100-only adjustments applied in build_ingetrans_smart_report_r3_bilingual.py.
"""

from __future__ import annotations


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


def body_en(logo_src: str, cover_src: str) -> str:
    p = []
    p.append(f"""
<!-- ===================== COVER ===================== -->
<img src="{logo_src}" class="cover-logo" alt="INGECART">
<div class="cover-kicker">Technical product report</div>
<div class="cover-title">INGETRANS Smart<br>Rail-less reel feeding</div>
<div class="cover-rule"></div>
<div class="cover-sub">
Evolution of the INGETRANS reel supply and return system for the corrugator: the transfer carriage no
longer runs on embedded rails and a conductor line; it travels on the existing floor on INGECART
IGC-DW100 drive and steering wheels, with laser navigation and an on-board battery.
</div>
<img src="{cover_src}" alt="INGETRANS Smart" style="width:100%;margin:4mm 0 2mm 0;border-bottom:1.2pt solid #FF6304;">
<div class="cover-claim">
<b>The same reel logistics. Without opening the corridor floor.</b><br>
No more than 60 m of embedded rail, no Vahle conductor line, no fixed feed along the route. Automatic
reel delivery and return to the roll stands is kept; civil works and fixed infrastructure disappear.
</div>

<table class="meta" style="margin-top:10mm">
<tbody>
<tr><td>Product</td><td>INGETRANS Smart - rail-less variant of INGETRANS</td><td>Document no.</td><td>IS-SMART-R3 · Rev. 3</td></tr>
<tr><td>Application</td><td>Paper reel supply and return to corrugator roll stands</td><td>Date</td><td>14/09/2026</td></tr>
<tr><td>Technical basis</td><td>4 x IGC-DW100 drive wheels · laser navigation · 48 V DC LiFePO4</td><td>Supersedes</td><td>Smart report 2026-09-10 (JNOV basis) and R2 (DW20/DW100)</td></tr>
<tr><td>Source document</td><td>Technical-commercial proposal P0001_2026 Rev. 1 - Transfer without civil works</td><td>Status</td><td>Validated product baseline · subject to application study</td></tr>
<tr><td>Issuer</td><td>INGECART · Product Engineering and Automation</td><td>Web</td><td>www.ingecart.eu</td></tr>
</tbody>
</table>

<!-- ===================== 01 ONE PAGER ===================== -->
<div class="pb"></div>
{sec("01", "The product on one page")}

<table class="two"><tr><td class="l" style="width:50%">
<span class="tag">Situation</span>
<p>INGETRANS automates reel transport, delivery and return between the warehouse exchange area and the
corrugator roll stands with a transfer carriage guided by an embedded rail and powered by a conductor
line. It works, but it requires opening the corridor floor over more than 60 m, levelling the rail to
the millimetre, installing the overhead line and stopping the zone for weeks.</p>

<span class="tag o">Product</span>
<p><b>INGETRANS Smart</b> keeps the full function - pick-up at the exchange area, delivery to the roll-stand
track, return of partial reels - and removes the fixed infrastructure. The carriage runs on the existing
floor on four <b>IGC-DW100</b> drive and steering wheels, navigates by laser on the plant contour, positions
at each station with a local reference and is powered by a 48 V LiFePO4 battery with opportunity charging.
INGECART manufactures the complete machine and issues the CE marking.</p>

<span class="tag">Result</span>
<p>Zero rail, zero Vahle line, installation in days without stopping the corridor, a route editable by
software and a mobile asset that grows by adding stations or a second unit.</p>
</td><td style="width:50%">

<table class="plain" style="margin-bottom:4mm">
<tbody>
<tr><td style="width:16mm"><span class="big-num">1</span></td><td style="padding-top:1mm"><b>The floor is not touched</b><br><span class="note">The carriage runs on the existing concrete. No channel, no concreting, no curing, no finishing.</span></td></tr>
<tr><td><span class="big-num">2</span></td><td style="padding-top:1mm"><b>The corrugator is not stopped</b><br><span class="note">Mapping, station set-up and training overlap with production. No shutdown window for civil works.</span></td></tr>
<tr><td><span class="big-num">3</span></td><td style="padding-top:1mm"><b>The layout is no longer cast in concrete</b><br><span class="note">Adding a roll stand is registering a station. Moving the exchange area is editing the map.</span></td></tr>
<tr><td><span class="big-num">4</span></td><td style="padding-top:1mm"><b>No electrical single point of failure</b><br><span class="note">No conductor line or collector: on-board battery and one charging point.</span></td></tr>
<tr><td><span class="big-num">5</span></td><td style="padding-top:1mm"><b>One responsible party</b><br><span class="note">INGECART delivers the complete CE-marked machine, with technical file, schematics and service.</span></td></tr>
</tbody>
</table>
</td></tr></table>

<table class="kpi-wrap"><tr>
<td><span class="kpi-v">0 m</span><span class="kpi-l">Embedded rail</span></td>
<td><span class="kpi-v">0 m</span><span class="kpi-l">Conductor line</span></td>
<td><span class="kpi-v">0.43 m/s</span><span class="kpi-l">Speed with IGC-DW100</span></td>
<td><span class="kpi-v">18-20 wks</span><span class="kpi-l">From order to CE marking</span></td>
</tr></table>

<div class="callout orange">
<b>Who it is for.</b> Corrugated plants that want INGETRANS reel automation but cannot accept rail civil
works in the corrugator corridor, operate in a rented building or over buried services, expect layout
changes or additional roll stands, or need per-movement traceability without freezing the installation
in concrete.
</div>

<h3 class="sub">Contents</h3>
<table class="two"><tr><td class="l" style="width:50%">
<table class="plain"><tbody>
<tr><td style="width:8mm">02</td><td>What INGETRANS is today and what changes</td></tr>
<tr><td>03</td><td>What is removed and what replaces it</td></tr>
<tr><td>04</td><td>Direct comparison INGETRANS / INGETRANS Smart</td></tr>
<tr><td>05</td><td>How a reel mission works</td></tr>
<tr><td>06</td><td>Capacity and speed</td></tr>
<tr><td>07</td><td>Open control, data and diagnostics</td></tr>
</tbody></table>
</td><td style="width:50%">
<table class="plain"><tbody>
<tr><td style="width:8mm">08</td><td>Safety and CE marking</td></tr>
<tr><td>09</td><td>Civil works, installation and maintenance</td></tr>
<tr><td>10</td><td>Frequently asked questions</td></tr>
<tr><td>11</td><td>Implementation plan and required data</td></tr>
<tr><td>12</td><td>Validation status and open points</td></tr>
<tr><td>A/B/C</td><td>Annexes: IGC-DW range, base-case calculation and standards</td></tr>
</tbody></table>
</td></tr></table>
""")

    p.append(f"""
<div class="pb"></div>
{sec("02", "What INGETRANS is today and what changes")}
<p class="lead">INGETRANS is a turnkey system that transports paper reels from the warehouse exchange area to the
tracks of each roll stand and automatically returns unconsumed reels. It removes forklifts from the corrugator
area, synchronises delivery with planning and preserves the identity of every reel. That function does not
change in INGETRANS Smart.</p>
{table(["Functional block", "INGETRANS (rail)", "INGETRANS Smart"], [
    ["Reel pick-up and delivery", "Lifting and clamping mechanism, about 6 s per interface", "Retained without functional change"],
    ["Exchange area and ramps", "Existing", "Retained; light redesign of fencing for a mobile zone"],
    ["Roll-stand tracks", "Motorised tracks, up to 10 (5 roll stands x 2)", "Retained"],
    ["Carriage travel", "Single motor on embedded rail, 80 m/min", "Four IGC-DW100 drive wheels on the floor, 0.43 m/s (26 m/min)"],
    ["Guidance", "Rail + encoder + limit switches", "Laser navigation +/-20 mm + station reference +/-5 mm"],
    ["Power supply", "Vahle conductor line + collector", "48 V 200 Ah LiFePO4 battery + opportunity charging"],
    ["Control", "Siemens PLC, PROFINET", "On-board Siemens PLC, CANopen CiA 301/402 to drives, industrial Wi-Fi to plant"],
    ["MES/ERP interface and traceability", "Orders, destination, return", "Identical, extended with per-transfer records and drive diagnostics"],
    ["Responsible for CE marking", "INGECART", "INGECART, manufacturer of the complete machine"],
], first_col_width="34mm")}
<div class="callout">
<b>What it is not.</b> INGETRANS Smart is not a generic AMR adapted to reels nor a third-party wheel kit
bolted onto the current carriage. It is an INGECART product: reel carrier chassis, in-house IGC-DW100 drive
wheels, control, functional safety and conformity under a single responsibility.
</div>
""")

    p.append(f"""
<div class="pb"></div>
{sec("03", "What is removed and what replaces it")}
<p class="lead">A rail-guided INGETRANS is three overlapping projects: a machine, a civil work and a fixed
electrical installation. Only the first adds production value. INGETRANS Smart removes the other two.</p>
{table(["Removed element", "What it implied", "INGETRANS Smart solution"], [
    ["Embedded running rails (more than 60 m in a 5-roll-stand corridor)", "Floor cutting and demolition, channel, reinforcement, concreting, curing, +/-2 mm levelling, 2-4 weeks zone shutdown", "IGC-DW100 polyurethane wheels on the existing floor; virtual route in the navigation map"],
    ["Vahle conductor line, supports and collector", "Supporting structure, conductor rail or festoon, three-phase feed, work at height, brushes", "On-board 48 V LiFePO4 battery; automatic 48 V / 60 A charger at one charging point"],
    ["Fixed feed along the route", "Panel, protections, containment", "One 230/400 V outlet at the charging station"],
    ["Mechanical end stops", "Adjustment and wear", "Station codes, software zones and safety scanners"],
    ["Single traction motor and gearbox", "Traction single point of failure", "Four IGC-DW100 units with traction, steering, brake and encoder integrated; exchangeable as a unit"],
    ["Rail installation service block", "Paige reference: 14 days, 1 technician", "Not applicable"],
], first_col_width="46mm")}
<h3 class="sub">What the rail did provide - and how it is solved without it</h3>
{table(["Rail function", "Equivalent solution"], [
    ["Geometric guidance of the route", "Laser navigation on the natural plant contour, with an editable virtual route"],
    ["Position repeatability at the roll-stand track", "Optical or magnetic reference at each station, independent of navigation: +/-5 mm"],
    ["Reaction to lateral forces", "Steerable drive wheels with continuous closed-loop path correction"],
    ["Continuous power", "Battery with opportunity charging at every cycle pause; it never stops with a reel on board for lack of energy"],
    ["Physical delimitation of the travel zone", "Safety laser scanners with speed-dependent fields, bumper, signalling and zone projection"],
], first_col_width="52mm")}
""")

    p.append(f"""
<div class="pb"></div>
{sec("04", "Direct comparison INGETRANS / INGETRANS Smart")}
{table(["Criterion", "Rail-guided INGETRANS", "INGETRANS Smart"], [
    ["Civil works in the corridor", "Required - channel, concreting, curing", "None - runs on the existing floor"],
    ["Power supply", "Conductor line + fixed feed", "On-board battery + one charging point"],
    ["On-site installation time", "Weeks with zone shutdown (mechanical assembly 28 d, rails 14 d)", "Days without stopping the zone; rail block removed"],
    ["Travel speed", "80 m/min (1.33 m/s)", "0.43 m/s (26 m/min) with IGC-DW100 - the only model offered for reel duty"],
    ["Stopping accuracy", "Mechanical, +/-2 to +/-5 mm", "+/-5 mm with station reference"],
    ["Changing the route or adding a roll stand", "New civil works, extend rail and line", "Edit the map and register the station"],
    ["Relocating to another corrugator or hall", "Impractical", "Transport and remap"],
    ["Adding capacity", "Second carriage needs a second rail", "Second unit in the same corridor with traffic management"],
    ["Maintenance", "Rail, brushes or festoon, cable chain, gearbox", "Wheel treads, battery, cleaning of optics"],
    ["Electrical single point of failure", "Conductor line and collector", "None"],
    ["Traceability", "Position signals and orders", "Per-transfer record: time, origin, destination, state + drive diagnostics"],
    ["Residual value", "Fixed installation amortised against one layout", "Reusable mobile asset"],
], first_col_width="40mm")}
<div class="callout">
<b>Where the rail still wins.</b> In very fast, continuous cycles - above about 60 transfers per hour sustained
on short routes, or above about 20-25 single-reel missions per hour on a 60 m corridor at IGC-DW100 speed -
with constant load and a layout frozen for ten years, the rail carriage keeps the advantage in availability and
cost per cycle. A reference corrugator consumes 8.8 reels/h with dual-reel trips available; it is below that
threshold. If the application study says otherwise, we will say so.
</div>
""")

    p.append(f"""
<div class="pb"></div>
{sec("05", "How a reel mission works")}
{table(["Step", "Phase", "What happens"], [
    ["1", "Call", "The MES/ERP or the INGECART plant logic requests a reel for a roll stand, or the return of a partial reel."],
    ["2", "Approach", "The carriage navigates by laser to the exchange area and slows to 0.30 m/s in the last metres."],
    ["3", "Positioning", "Fine adjustment against the station reference to +/-5 mm, with mutual confirmation before enabling the transfer."],
    ["4", "Pick-up", "INGETRANS lifting and clamping mechanism over one or two reels (about 6 s)."],
    ["5", "Travel", "Travel to the roll stand with active safety fields and speed modulated by the surroundings."],
    ["6", "Delivery", "Positioning at the track, discharge onto the track conveyor (about 6 s) and confirmation to the system."],
    ["7", "Return / standby", "Optional pick-up of a partial reel on the way back; return to standby or to the charging station according to battery level."],
], first_col_width="10mm")}
<h3 class="sub">Subsystems</h3>
{table(["Subsystem", "Content"], [
    ["Plant control system", "Calls, confirmations, traceability, MES/ERP interface - industrial Wi-Fi"],
    ["Navigation and mission management", "Map, routes, destinations, zones, traffic"],
    ["On-board PLC - Siemens", "Sequence, interlocks, diagnostics, safe I/O"],
    ["Traction and steering drives", "48 V DC servo drives with STO · CANopen CiA 301 / DS 402 · four IGC-DW100 wheels"],
    ["Reel carrier mechanism", "INGETRANS lifting and clamping on the Smart chassis"],
    ["Safety chain", "Front and rear scanners, bumper, E-stops, safely limited speed"],
    ["On-board energy", "48 V 200 Ah LiFePO4 battery with BMS · automatic 48 V / 60 A charger"],
], first_col_width="46mm")}
<div class="callout orange">
<b>Navigation and positioning are two different things.</b> Laser navigation brings the carriage to the station
within +/-20 mm - enough to travel the corridor, not enough to transfer a reel to a track. The last stretch is
closed by the local station reference, which guarantees +/-5 mm.
</div>
""")

    p.append(f"""
<div class="pb"></div>
{sec("06", "Capacity and speed")}
<p class="lead">INGETRANS Smart is slower in peak speed than the rail carriage. In effective cadence the gap is
smaller because the cycle is dominated by the pick-up and delivery interfaces and by dual-reel trips, not by
travel alone. Trapezoidal profile; rail with 4.5 s ramps, Smart with 0.30 m/s² acceleration; 6 s + 6 s interfaces.</p>
{table(["Distance exchange area to roll stand", "Rail INGETRANS (80 m/min)", "INGETRANS Smart (0.43 m/s, IGC-DW100)"], [
    ["12 m (nearest roll stand)", "approx. 14 s", "approx. 29 s"],
    ["26 m (base-case route)", "approx. 24 s", "approx. 62 s"],
    ["30 m (mid corridor)", "approx. 27 s", "approx. 71 s"],
    ["60 m (far end of corridor)", "approx. 50 s", "approx. 141 s"],
    ["Complete 30 m round-trip mission with pick-up and delivery", "approx. 66 s (approx. 54 missions/h)", "approx. 154 s (approx. 23 missions/h)"],
    ["Complete 60 m round-trip mission with pick-up and delivery", "approx. 111 s (approx. 32 missions/h)", "approx. 294 s (approx. 12 missions/h)"],
], first_col_width="58mm")}
<table class="kpi-wrap"><tr>
<td><span class="kpi-v">8.8</span><span class="kpi-l">Reels/h · reference corrugator</span></td>
<td><span class="kpi-v">&lt; 40 %</span><span class="kpi-l">Smart carriage utilisation at 30 m, single reel</span></td>
<td><span class="kpi-v">2</span><span class="kpi-l">Reels per trip</span></td>
<td><span class="kpi-v">≈ 20-25/h</span><span class="kpi-l">Single-reel missions where rail wins on 60 m</span></td>
</tr></table>
<div class="callout">
<b>Product rule.</b> INGETRANS Smart is offered when peak missions per hour multiplied by the Smart mission time stay
below 60% of available time. With dual-reel trips the number of missions roughly halves. The application study
simulates the real plant cycle with the INGECART digital twin and delivers the reels per hour that can be expected;
if the figure does not cover the demand, rail INGETRANS or a second Smart unit is recommended.
</div>
<p class="note">Speed is deliberately limited to 0.43 m/s with IGC-DW100 for load stability: kinetic energy grows
with the square of speed and, in a protective stop, reel displacement becomes the sizing factor rather than the
available torque.</p>
""")

    p.append(f"""
<div class="pb"></div>
{sec("07", "Open control, data and diagnostics")}
<p class="lead">The wheel drives communicate over CANopen according to CiA 301 and DS 402, the same language as
European industrial servo drives. Control runs on a conventional Siemens PLC; ramps, torque limits, position windows
and maximum speeds are accessible and documented at handover.</p>
{table(["Monitored variable", "Practical use"], [
    ["Actual current and torque of each motor", "Detection of progressive effort increase: degraded rolling, bearing or floor deterioration, before failure"],
    ["Actual and setpoint speed", "Verification of the intended profile; slip detection"],
    ["Actual position and following error", "Early alarm of mechanical deviation or loss of station accuracy"],
    ["Motor and heatsink temperature", "Protection against sustained overload"],
    ["Bus voltage", "Battery state under real load, not only at rest"],
    ["Detailed fault codes", "Overcurrent, over/undervoltage, overtemperature, encoder, phase loss, following error, timeout - each with its own code"],
    ["Communication watchdog", "Mutual supervision PLC-drives; on link loss, transition to safe state"],
], first_col_width="52mm")}
<h3 class="sub">Signals for the INGECART digital platform</h3>
<p>The carriage publishes states on change with heartbeat, monotonic counters and events with source timestamp,
aligned with the Digital Ecosystem Platform data-capture specification:</p>
<ul>
<li>Pick-up, delivery and mission times (P50/P95); roll-stand starvation events attributable to logistics.</li>
<li>Automatic/manual mode, battery state of charge, bus voltage, charge cycles.</li>
<li>Station positioning error, laser localisation quality, protective-field intrusions.</li>
<li>Current per wheel, following error, tread wear index, Wi-Fi link quality, safety event log.</li>
</ul>
""")

    p.append(f"""
<div class="pb"></div>
{sec("08", "Safety and CE marking")}
<p class="lead">Removing the rail removes the physical barrier between the machine and personnel. That separation
is replaced by certified functional safety according to EN ISO 3691-4 and EN ISO 13849. This is where a project of
this kind is won or lost, and where INGECART concentrates its engineering.</p>
{table(["Function", "How it is solved", "Level"], [
    ["Person detection", "Front and rear safety laser scanners with protective fields adapted to speed and direction", "PL d Cat. 3"],
    ["Emergency stop", "Pushbuttons accessible from four sides, dual channel, controlled stop followed by brake", "PL d Cat. 3"],
    ["Contact stop", "Perimeter mechanical bumper as scanner backup", "PL d Cat. 3"],
    ["Safely limited speed", "Monitoring on a safety module; forced reduction at stations, crossings and manoeuvres", "PL d Cat. 3"],
    ["Standstill holding", "Spring-applied, electrically released brake; on power loss the carriage is held", "PL c Cat. 1"],
    ["Transfer interlock", "Travel inhibited while a transfer is in progress or the reel is not secured", "PL c Cat. 1"],
], first_col_width="34mm")}
<h3 class="sub">Complementary measures</h3>
<table class="two"><tr><td class="l" style="width:50%"><ul>
<li>Beacon and acoustic movement signal.</li>
<li>Light projection of the sweep zone on the floor.</li>
<li>Floor marking of the travel corridor.</li>
<li>Key mode selector: automatic, manual and maintenance.</li>
</ul></td><td style="width:50%"><ul>
<li>Manual console with three-position enabling device.</li>
<li>Speed limited to 0.30 m/s in manual and maintenance modes.</li>
<li>Lockable battery disconnector for lockout.</li>
<li>Safety event log accessible from diagnostics.</li>
</ul></td></tr></table>
<h3 class="sub">What the customer receives</h3>
{table(["Element", "Content"], [
    ["A machine, not a set of parts", "INGECART acts as manufacturer of the complete equipment and issues the CE marking under its own responsibility"],
    ["Complete technical file", "Risk assessment, calculation and validation of safety functions, EPLAN Electric P8 schematics, EMC report, electrical verifications"],
    ["EU declaration of conformity", "Directive 2006/42/EC; equipment delivered from 20 January 2027 is declared under Regulation (EU) 2023/1230"],
    ["User documentation", "Instruction manual, maintenance manual, recommended spare-parts list and training for operators and maintainers"],
], first_col_width="46mm")}
<div class="callout">
<b>Braking and reel stability.</b> The safety logic first executes a controlled electrical braking and applies the
mechanical brake at the end of the ramp. Emergency deceleration is limited to 1.50 m/s² so as not to displace the load.
Real stopping distances are measured with the customer's reel during acceptance tests.
</div>
""")

    p.append(f"""
<div class="pb"></div>
{sec("09", "Civil works, installation and maintenance")}
<h3 class="sub">Items that disappear</h3>
{table(["Rail-solution item", "Order of magnitude", "With INGETRANS Smart"], [
    ["Rail civil works: cutting, demolition, channel, reinforcement, concreting and finishing (26 m route)", "18,000 - 35,000 €", "Removed"],
    ["Rail supply, alignment and levelling", "6,000 - 12,000 €", "Removed"],
    ["Conductor line or festoon, supporting structure and three-phase feed", "8,000 - 15,000 €", "Removed"],
    ["Diversion of buried services and construction contingencies", "Open risk", "Eliminated"],
    ["Zone shutdown during execution", "3-6 weeks", "2-5 days of installation without stopping"],
    ["Annual maintenance of rail, festoon and cable chain", "1,500 - 3,000 €/year", "Removed"],
    ["<b>Avoided enablement investment</b>", "<b>32,000 - 62,000 €</b>", "<b>+ lost production</b>"],
], first_col_width="70mm")}
<p class="note">Indicative ranges for a typical Spanish installation on a 26 m route. In an INGETRANS corridor of more than
60 m the rail and line items scale with length. Not an offer; replaced by the real plant figures in the application study.</p>
<h3 class="sub">Items that appear</h3>
{table(["Item", "Order of magnitude", "Nature"], [
    ["Automatic charging station", "3,000 - 5,000 €", "Investment"],
    ["Commissioning, mapping, adjustment and training", "2,000 - 4,000 €", "Investment"],
    ["Wireless coverage reinforcement, if required", "800 - 2,500 €", "Investment"],
    ["Battery replacement at end of life", "Year 7-10", "Replacement"],
    ["Tread replacement", "Per cycles", "Consumable"],
    ["Electricity in operation", "≈ 1.3 kWh per operating hour (reference platform)", "Operating cost"],
], first_col_width="70mm")}
<h3 class="sub">Maintenance compared</h3>
{table(["Aspect", "Rail INGETRANS", "INGETRANS Smart"], [
    ["Preventive", "Rail wear, cleaning and alignment; brushes or festoon; cable chain; traction gearbox", "Tread inspection, cleaning of navigation and safety optics, annual verification of safety functions, battery tracking"],
    ["Spare parts", "Brushes, rail fixings, traction motor", "IGC-DW100 wheel exchangeable as a flanged unit; battery (year 7-10); treads; optics"],
    ["Predictive", "Limited", "Current, torque, temperature and following error per wheel anticipate intervention"],
    ["Degraded mode", "Carriage stopped on the rail", "Manual console to evacuate the reel on board; forklift fallback procedure"],
], first_col_width="28mm")}
""")

    faqs = [
        ("What if the corridor floor is not perfect?", "It does not need to be. Sound industrial concrete without breaks in the travel lane, local deviation below about +/-5 mm over 2 m and joints below 20 mm. It is measured during the technical visit; stretches needing local repair are identified and quoted before any commitment."),
        ("Is it slower than rail INGETRANS?", "In peak speed yes: 0.43 m/s versus 80 m/min (1.33 m/s). In effective cadence the gap is smaller because the cycle is dominated by pick-up and delivery interfaces and dual-reel trips halve the number of missions. At 8.8 reels/h with dual-reel trips the carriage utilisation stays below 25%. The application study simulates the real cycle."),
        ("What if the battery runs out with a reel on board?", "It does not happen by design: opportunity charging at every pause keeps the level in a high band. On reaching the reserve, the carriage completes the mission in progress and goes to charge with advance warning."),
        ("Is it safe with personnel and forklifts in the corridor?", "That is the situation it is designed for: scanners with speed-dependent fields, backup bumper, monitored limited speed, acoustic and light signalling. Stopping distances are verified with the real reel during acceptance."),
        ("Who is responsible for the CE marking?", "INGECART, as manufacturer of the complete equipment. The customer receives a marked machine with technical file and EU declaration of conformity."),
        ("Am I locked into proprietary software?", "No. The drives speak CANopen in standard profiles and control runs on a conventional Siemens PLC, with parameters documented at handover."),
        ("Can I add a roll stand or move the exchange area in two years?", "Yes. Adding a destination is registering a station; changing the route is editing the map. Moving the equipment to another corrugator requires transport, remapping and station adjustment. None of that involves civil works."),
        ("What if production grows?", "A second unit is added to the same corridor with traffic management. There is no infrastructure to duplicate."),
    ]
    faq_html = "".join(f'<div class="faq"><div class="q">{q}</div><div class="a">{a}</div></div>' for q, a in faqs)
    p.append(f"""
<div class="pb"></div>
{sec("10", "Frequently asked questions")}
{faq_html}
""")

    p.append(f"""
<div class="pb"></div>
{sec("11", "Implementation plan and required data")}
{table(["Phase", "Activity", "Deliverable", "Duration"], [
    ["F1", "Application study", "Feasibility report, proposed layout, capacity verified with digital twin and closed offer", "2 wks"],
    ["F2", "Detail engineering", "Reel-carrier chassis drawings, electrical schematics, risk assessment, bill of materials", "4 wks"],
    ["F3", "Procurement and manufacturing", "Carriage assembled and wired, cabinet tested", "10-12 wks"],
    ["F4", "Tests at INGECART", "Signed protocol including stopping distances with reel", "1 wk"],
    ["F5", "Installation and commissioning", "Plant mapping, station adjustment, integration with tracks and MES, training", "1 wk"],
    ["F6", "Conformity and handover", "Technical file, EU declaration, CE marking and acceptance certificate", "1 wk"],
    ["-", "<b>Estimated total</b>", "From order signature", "<b>18-20 wks</b>"],
], first_col_width="10mm")}
<h3 class="sub">Data confirmed during the visit</h3>
{table(["Block", "What we confirm"], [
    ["Reel", "Reel matrix: maximum mass, diameter, width, core type and centre-of-gravity height; one or two reels per trip"],
    ["Route", "Distance exchange area-roll stands, number of tracks, corridor path and obstacles"],
    ["Productivity", "Reels per hour at peak and average, shifts and required availability"],
    ["Transfer", "Height and tolerance of roll-stand tracks and exchange area"],
    ["Floor", "Condition, measured flatness, joints and slope - drives accuracy and wear"],
    ["Human environment", "Personnel and forklift traffic in the corridor - sets the level of protective measures"],
    ["Electrical and network", "Voltage at the charging point and Wi-Fi coverage along the route"],
    ["Control", "Plant PLC, available protocol, signals and MES/ERP"],
], first_col_width="30mm")}
""")

    p.append(f"""
<div class="pb"></div>
{sec("12", "Validation status and open points", dark=True)}
{table(["Element", "Status", "Basis"], [
    ["IGC-DW100 drive wheel", "Validated", "INGECART technical document P0001_2026 Rev. 1; independent recomputation consistent (+/-3%)"],
    ["Base-case calculation (3.5 t, 26 m)", "Validated", "Traction, adhesion, power, braking and energy reproduced; mechanical brake 2.47 m/s² declared vs 2.74 recomputed (conservative)"],
    ["Heavy configuration 40 t (4 x IGC-DW100)", "Validated", "Traction margin 1.91 reproduced; about 8 for an 8 t reel carrier"],
    ["Safety architecture and standards", "Validated", "EN ISO 3691-4, EN ISO 13849, EN 60204-1, EN 61800-5-2, Regulation (EU) 2023/1230"],
    ["Wheel configuration for the INGETRANS reel carrier", "Decided", "4 x IGC-DW100 only (commercial decision CD-01, 14/09/2026); IGC-DW20 not offered for reel duty"],
    ["Smart chassis - lifting mechanism - roll-stand track interface", "Pending", "Detail engineering F2"],
    ["Battery autonomy for the reel profile", "Pending", "Recalculation with four IGC-DW100 and about 8,000 kg total mass in the application study"],
    ["Capacity in the customer corridor", "Pending", "Digital twin on approved layout (0.43 m/s, 0.30 m/s approach, dual-reel share)"],
    ["Cost and price of the Smart variant", "Pending", "Product cost breakdown; Paige offer priced at -5% equipment, -15% services, -80% customer civil works versus rail INGETRANS"],
], first_col_width="52mm")}
<div class="callout orange">
<b>Revision note.</b> This R3 supersedes the report of 10/09/2026 (third-party JNOV MDS/DDW-4TP modules, 2 km/h,
DataMatrix line guidance, partly completed machinery) and the R2 of 14/09/2026 that still listed the IGC-DW20 for
reel duty. The current basis is four INGECART IGC-DW100 drive and steering wheels, laser navigation with station
reference, 48 V LiFePO4 battery and full-machine CE marking by INGECART.
</div>
""")

    p.append(f"""
<div class="pb"></div>
{sec("A", "Annex - IGC-DW drive-wheel range", dark=True)}
<p class="lead">The steerable drive wheel is the element that makes the rail unnecessary: it integrates traction,
steering, reduction, braking and feedback in a single unit flanged to the chassis. The range covers 2 to 40 tonnes of
total mass; <b>for INGETRANS Smart reel duty only the IGC-DW100 is offered.</b></p>
{table(["Parameter", "IGC-DW20 (not offered for reel duty)", "IGC-DW100 (INGETRANS Smart)"], [
    ["Maximum load per wheel", "2,000 kg", "10,000 kg"],
    ["Wheel diameter", "Ø 260 mm", "Ø 500 mm"],
    ["Traction motor power", "1,570 W", "5,000 W"],
    ["Nominal traction torque", "5.0 N·m", "24.0 N·m"],
    ["Nominal motor speed", "3,000 rpm", "2,000 rpm"],
    ["Reduction ratio", "1 : 44.57", "1 : 120"],
    ["Travel speed", "0.90 m/s (54 m/min)", "0.43 m/s (26 m/min)"],
    ["Nominal current", "39 A", "106 A"],
    ["Parking brake torque", "14 N·m", "Per configuration"],
    ["Steering motor power", "750 W", "3,000 W (S2 60 min)"],
    ["Steering torque", "2.39 N·m", "9.6 N·m"],
    ["Steering reduction", "1 : 200", "1 : 310"],
    ["Overall height", "≈ 445 mm", "≈ 623 mm"],
    ["Mounting flange", "12 x M10 · Ø 355 mm", "20 x M12 · Ø 768 mm"],
], first_col_width="46mm")}
{table(["Common characteristic", "Value"], [
    ["Supply voltage", "48 V DC"],
    ["Motor type", "Brushless DC servomotor · S1 continuous duty · efficiency ≈ 90%"],
    ["Feedback", "2,500 ppr incremental encoder on traction · absolute encoder on steering"],
    ["Protection / temperature", "IP65 (except shaft) · -20 °C to +50 °C"],
    ["Control", "CANopen CiA 301 / DS 402 (recommended) · CAN 2.0B · RS-485"],
    ["Operating modes", "Torque · velocity · position · cyclic synchronous position · homing"],
], first_col_width="46mm")}
<h3 class="sub">Configurations</h3>
{table(["Total mass", "Configuration", "Typical application"], [
    ["≤ 3,500 kg", "2 x IGC-DW20 + 4 castors", "Euro pallets, light reels, boxes. Not applicable to INGETRANS Smart."],
    ["≤ 6,000 kg", "4 x IGC-DW20 + 4 castors", "4 x 2 m platform. Not applicable to INGETRANS Smart."],
    ["≤ 40,000 kg", "4 x IGC-DW100 + supports", "<b>INGETRANS Smart reel carrier</b> (single or dual reels below 3,500 kg each plus tare, about 8,000 kg), large-format reels, tooling. Speed limited to 0.43 m/s for load stability."],
], first_col_width="24mm")}
""")

    p.append(f"""
<div class="pb"></div>
{sec("B", "Annex - Base-case calculation", dark=True)}
<h3 class="sub">B.1 · Input data</h3>
{table(["Item", "Value", "Remark"], [
    ["Platform dimensions", "2,800 x 1,500 mm", "Reference platform of the technical document"],
    ["Payload", "2,000 kg", "Base case; the INGETRANS reel carrier is sized with the reel matrix"],
    ["Estimated tare", "1,500 kg", "Chassis, deck, battery and cabinet"],
    ["Design total mass", "3,500 kg", "Calculation value"],
    ["Route per transfer", "26 m", "Loaded outbound, empty return"],
    ["Travel speed", "0.90 m/s (reference platform, DW20)", "0.30 m/s on approach; INGETRANS Smart uses 0.43 m/s with DW100"],
    ["Service acceleration", "0.30 m/s²", "Load comfort criterion"],
    ["Rolling coefficient", "0.025", "Polyurethane on polished concrete, conservative"],
    ["Residual slope", "1.0%", "Industrial floor irregularity"],
], first_col_width="46mm")}
<h3 class="sub">B.2 · Required and available traction</h3>
<div class="formula">
F<sub>rolling</sub> = f · m · g = 0.025 x 3,500 x 9.81 = 858 N<br>
F<sub>slope</sub> = m · g · sin α = 3,500 x 9.81 x 0.010 = 343 N<br>
F<sub>acceleration</sub> = m · a = 3,500 x 0.30 = 1,050 N<br>
F<sub>required</sub> = 2,251 N → design value adopted: 2,300 N
<hr class="fsep">
Wheel torque (DW20) = M<sub>motor</sub> x i x η = 5.0 x 44.57 x 0.90 = 200.6 N·m<br>
Force per wheel = 200.6 / 0.130 = 1,543 N · with 2 drive wheels = 3,086 N · margin 1.37 → PASS
</div>
<h3 class="sub">B.3 · Adhesion check</h3>
<div class="formula">
Load on drive wheels (≈ 50% of total) = 1,750 kg → N = 17.17 kN<br>
Maximum transmissible force = µ · N = 0.60 x 17.17 = 10.30 kN &gt;&gt; 3.09 kN required → NO SLIP
</div>
<h3 class="sub">B.4 · Power and braking</h3>
{table(["Quantity", "Value", "Comment"], [
    ["Mechanical power in service", "2.03 kW", "Including the acceleration phase"],
    ["Electrical power absorbed", "≈ 2.39 kW", "Drivetrain efficiency 0.85"],
    ["Service deceleration", "0.40 m/s²", "Stopping distance 1.01 m"],
    ["Protective stop by scanner", "0.80 m/s²", "0.51 m + 0.14 m reaction = 0.65 m"],
    ["Protective field to configure", "≥ 1.00 m", "Includes measurement tolerance and tread wear"],
    ["Limited emergency deceleration", "1.50 m/s²", "Distance 0.27 m. Limit set by load stability"],
    ["Mechanical brake capability", "2.47 m/s²", "14 N·m x 44.57 on 2 wheels. Reserved for power loss (INGECART recomputation: 2.74 m/s², declared value conservative)"],
], first_col_width="52mm")}
<h3 class="sub">B.5 · Energy and autonomy (reference platform)</h3>
{table(["Consumer per cycle", "Energy", "Basis"], [
    ["26 m loaded travel (3,500 kg)", "9.4 Wh", "Rolling, slope and one acceleration"],
    ["26 m empty travel (1,500 kg)", "4.6 Wh", "Same with reduced mass"],
    ["Deck conveyor / mechanism", "6.7 Wh", "1.5 kW for 8 s at loading and unloading"],
    ["Steering manoeuvres", "1.7 Wh", "Wheel reorientation at station"],
    ["Control and safety auxiliaries", "8.8 Wh", "350 W for a 90 s cycle"],
    ["<b>Total per cycle</b>", "<b>31.2 Wh</b>", "Design value adopted: 35 Wh"],
    ["Battery adopted", "48 V · 200 Ah", "LiFePO4 with BMS · 9.6 kWh · 80% usable = 7.68 kWh"],
    ["Cycles per charge", "≈ 219", "At 35 Wh per cycle"],
    ["Autonomy at 30 cycles/h", "7.3 h", "Covers a full shift without recharge"],
    ["Full recharge", "≈ 3.3 h", "48 V / 60 A charger"],
    ["Average grid consumption", "≈ 1.3 kWh/h", "At 30 cycles/h, including conversion losses"],
], first_col_width="56mm")}
<h3 class="sub">B.6 · IGC-DW100 configuration checks</h3>
<div class="formula">
40 t case: 4 x IGC-DW100 · v = 0.43 m/s · a = 0.20 m/s² → F<sub>required</sub> = 9,810 + 3,924 + 8,000 = 21,734 N<br>
Force per wheel = 24.0 x 120 x 0.90 / 0.250 = 10,368 N → 4 wheels = 41,472 N · margin 1.91 → PASS · 9.35 kW on 20 kW installed
<hr class="fsep">
INGETRANS Smart reel carrier, about 8,000 kg total: F<sub>required</sub> = 1,962 + 785 + 2,400 = 5,147 N · available 41,472 N · margin ≈ 8<br>
Mechanical power at 0.43 m/s ≈ 2.2 kW · autonomy to be recalculated for the customer mission profile
</div>
<p class="note">Values in this annex correspond to the INGECART technical document base case and have been reproduced
independently. The INGETRANS Smart reel carrier is calculated with the customer reel matrix in phase F2. Stopping
distances are verified with the real load during factory and site acceptance tests.</p>
""")

    p.append(f"""
<div class="pb"></div>
{sec("C", "Annex - Applied standards", dark=True)}
{table(["Standard or regulation", "Application to the equipment"], [
    ["Regulation (EU) 2023/1230", "Machinery Regulation, mandatory from 20 January 2027. Equipment delivered from that date is declared under this text and not under Directive 2006/42/EC."],
    ["EN ISO 3691-4", "Driverless industrial trucks and their systems. Governing standard: person detection, stopping distances, speeds, marking, signalling and operating modes."],
    ["EN 1175", "Electrical requirements for industrial trucks. On-board 48 V DC installation, battery, charger and protections."],
    ["EN ISO 12100", "Risk assessment and reduction methodology. Basis of the technical file."],
    ["EN ISO 13849-1 / -2", "Required performance level, design of safety functions and validation."],
    ["EN 60204-1", "Electrical equipment of machines: stop categories, protection, conductors and final verifications."],
    ["EN 61800-5-2", "Safety functions of drives: STO and, where applicable, SS1 and SLS."],
    ["IEC 61439", "Low-voltage switchgear assemblies. On-board cabinet."],
    ["IEC 81346", "Structuring principles and reference designation of the documentation."],
    ["Directive 2014/30/EU", "Electromagnetic compatibility. Tests according to the IEC 61000 series."],
    ["EN 619", "Continuous handling equipment. Deck conveyor and roll-stand tracks."],
    ["CiA 301 / CiA 402", "CANopen communication and drive profiles used for traction and steering."],
], first_col_width="44mm")}
<p class="note">Document issued by the Product Engineering and Automation Department of INGECART S.L. Technical product report
for information. Performance, sizing and economic ranges correspond to the described base case and are subject to
confirmation in the application study. Rev. 3 - 14/09/2026. Supersedes the INGETRANS Smart reports of 10/09/2026 and R2.</p>
""")
    return "".join(p)
