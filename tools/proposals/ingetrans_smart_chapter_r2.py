"""INGETRANS Smart chapter content for the Paige proposal - revision R2 (INGECART IGC-DW basis).

Source of truth: knowledge/corrugated_equipment/ingetrans_smart_technical_baseline_R2_2026-09-14.json
derived from INGECART technical document "INGETRANS_smart_technical data.html" (P0001_2026 Rev. 1).
"""

from __future__ import annotations


def build_chapter(ins) -> None:
    ins.heading("5A  BLOCK A-SMART - INGETRANS SMART RAIL-LESS OPTION", 1)
    ins.paragraph("")
    ins.paragraph("INGETRANS Smart - rail-less and battery-powered variant of Block A", bold=True)
    ins.paragraph(
        "INGETRANS Smart delivers the same automatic reel delivery and return function described in Block A, "
        "but removes the elements of INGETRANS that generate the civil work and the fixed infrastructure: the "
        "embedded steel running rails of the transfer carriage, the conductor line (catenary, Vahle type) that "
        "powers the carriage while it moves and the fixed three-phase feed along the route. In INGETRANS Smart the "
        "carriage runs directly on the existing plant floor on INGECART IGC-DW drive and steering wheels, navigates "
        "by laser natural navigation on the plant contour with a local reference at each station for fine "
        "positioning, and is powered by an on-board 48 V DC LiFePO4 battery recharged automatically by "
        "opportunity charging at a single charging position."
    )
    ins.paragraph(
        "The reel pick-up and release mechanism, the exchange area with its ramps, the ten roll-stand tracks, the "
        "control philosophy, the MES/ERP interface and the traceability of Block A are retained. INGECART acts as "
        "manufacturer of the complete machine and issues the CE marking under its own responsibility. Block A-Smart "
        "is offered as an alternative to Block A; the customer selects one of the two configurations."
    )

    ins.heading("5A.1 What is removed and what replaces it", 2)
    ins.table([
        ["Block A element", "Function", "INGETRANS Smart"],
        ["Embedded steel running rails along the more than 60 m travel corridor, with trench, embedded plates and +/-2 mm levelling", "Guide and support the transfer carriage", "Removed. Polyurethane drive wheels run on the existing industrial concrete floor; the route is a virtual path in the navigation map, editable by software."],
        ["Conductor line (Vahle-type catenary or festoon), supporting structure, current collector and three-phase feed along the route", "Power the carriage in motion", "Removed. On-board 48 V 200 Ah LiFePO4 battery with BMS; automatic 48 V / 60 A opportunity charger at one charging position (230/400 V supply)."],
        ["Rail civil works: floor cutting, demolition, channel, reinforcement, concreting, curing and perimeter finishing", "Rail foundation", "Removed. Replaced by a floor condition survey during the technical visit; only local repair where the travel lane is damaged."],
        ["Mechanical end stops and rail-mounted limit switches", "Travel limits", "Replaced by software zones, station references and safety laser scanners."],
        ["Single traction motor and gearbox running on rails", "Carriage traction", "Replaced by IGC-DW drive and steering wheels (traction, steering, reduction, brake and encoders in one flanged unit): 4 x IGC-DW20 for reel duty up to 6,000 kg total mass, or 4 x IGC-DW100 for heavy dual-reel carriers."],
        ["Reel pick-up/lifting mechanism, exchange area, ramps, ten roll-stand tracks", "Reel handling and delivery", "Retained without functional change."],
    ], widths=[2.6, 1.6, 3.8])

    ins.heading("5A.2 Functional scope", 2)
    ins.bullets([
        "Automatic pickup of validated reels from the exchange position, delivery to the selected roll-stand track and return of unused or partially consumed reels, identical to Block A.",
        "Rail-less travel along the corrugator corridor: laser navigation brings the carriage to the station within about +/-20 mm; a local optical or magnetic station reference closes the last metres to +/-5 mm with mutual confirmation before the transfer is enabled.",
        "Transfer sequence per mission: call, approach at reduced speed, fine positioning, synchronised load transfer with the fixed track, travel with active safety fields, positioning and synchronised unloading at destination, return to standby or to the charging position depending on battery level.",
        "Operating modes: automatic, manual with enabling console (0.30 m/s limit) and maintenance, selected by key switch. Manual mode allows evacuation of a reel on board in case of fault.",
        "Battery management integrated in the sequence: opportunity charging in every cycle pause keeps the state of charge in a high band; on reaching the reserve threshold the carriage completes the mission in progress and goes to charge with advance warning. It never stops with a reel on board for lack of energy.",
        "Central HMI, sequence control, alarms, diagnostics, movement history and MES/ERP interface as in Block A, extended with per-transfer records (time, origin, destination, state) and drive diagnostics for predictive maintenance.",
        "Factory acceptance of the complete carriage, including stopping distances measured with the reference load, before shipment.",
    ])

    ins.heading("5A.3 Technical basis", 2)
    ins.table([
        ["Parameter", "Block A (rail-guided)", "Block A-Smart (rail-less) - proposal basis"],
        ["System type", "Surface rail-guided transfer carriage", "Autonomous rail-less carriage on INGECART IGC-DW drive and steering wheels; laser natural navigation plus station reference."],
        ["Drive wheel reference", "-", "IGC-DW20: 2,000 kg per wheel, wheel diameter 260 mm, 1,570 W traction, 750 W steering, 48 V DC, IP65, -20 to +50 C. IGC-DW100: 10,000 kg per wheel, wheel diameter 500 mm, 5,000 W traction, 3,000 W steering."],
        ["Standard configuration for reel duty", "-", "4 x IGC-DW20 plus castors for total mass up to 6,000 kg (four-corner traction and steering: longitudinal, transverse and centre rotation). 4 x IGC-DW100 for total mass up to 40,000 kg."],
        ["Transfer speed", "Reference up to 100-80 m/min", "0.90 m/s (54 m/min) with IGC-DW20; 0.43 m/s (26 m/min) with IGC-DW100. Approach to stations at 0.30 m/s; speed automatically modulated by the safety fields."],
        ["Acceleration / deceleration", "Approx. 1.5 s", "Service acceleration 0.30 m/s2 and service deceleration 0.40 m/s2 (load-comfort criterion); protective stop 0.80 m/s2; limited emergency deceleration 1.50 m/s2 for load stability."],
        ["Positioning accuracy", "Encoder / rail end stops", "+/-20 mm by navigation; +/-5 mm at station by local reference."],
        ["Pickup / drop-off", "Approx. 6 s per interface", "Approx. 6 s per interface (mechanism retained)."],
        ["Reel envelope", "Up to 1,500 mm diameter, up to 2,800 mm width, below 3,500 kg", "Same envelope. Carrier tare plus reel mass define the wheel configuration; drive wheels carry about 50% of total mass for adhesion (mu 0.60 on concrete)."],
        ["Power supply", "Conductor line (Vahle type)", "48 V 200 Ah LiFePO4 battery with BMS (9.6 kWh, 80% usable). Base-case autonomy 7.3 h at 30 cycles/h; full recharge about 3.3 h with 48 V / 60 A charger; average grid consumption about 1.3 kWh per operating hour."],
        ["Floor requirements", "Rail foundation", "Industrial concrete in good condition without breaks in the travel lane; local level deviation below about +/-5 mm over 2 m; expansion joints below 20 mm. Measured during the technical visit."],
        ["Controls", "PLC/HMI, PROFINET", "Siemens PLC on board; drives on CANopen CiA 301 / DS 402 with safe I/O; industrial Wi-Fi link to the INGECART plant control layer for calls, confirmations and traceability. Open parameters documented at handover."],
        ["Safety", "Safety PLC, scanners, interlocks, E-stops", "Front and rear safety laser scanners with speed-dependent fields (PL d Cat. 3), four-side emergency stops (PL d Cat. 3), perimeter bumper (PL d Cat. 3), safely limited speed (PL d Cat. 3), spring-applied holding brake (PL c), transfer interlock (PL c). Protective field at least 1.00 m."],
        ["Environment", "-", "-20 to +50 C for drive units; indoor plant environment."],
        ["Regulatory basis", "-", "Complete machine CE marked by INGECART: Machinery Directive 2006/42/EC, or Regulation (EU) 2023/1230 for deliveries from 20 January 2027; EN ISO 3691-4, EN 1175, EN ISO 13849-1/-2, EN 60204-1, EN 61800-5-2, Directive 2014/30/EU."],
    ], widths=[1.8, 2.2, 4.6])

    ins.heading("5A.4 Capacity and speed assessment", 2)
    ins.paragraph(
        "INGETRANS Smart travels at 54 m/min with IGC-DW20 wheels, against 80 m/min for the rail-guided "
        "carriage. The table compares one-way travel times for the Paige corridor using trapezoidal speed "
        "profiles (rail: 4.5 s ramps; Smart: 0.30 m/s2 acceleration) and the same 6 s pick-up and 6 s drop-off "
        "interfaces. The reference demand of the corrugator model used in Block A is 8.8 reels/hour."
    )
    ins.table([
        ["Distance exchange area to roll stand", "Block A one-way (80 m/min)", "Block A-Smart one-way (0.90 m/s, IGC-DW20)"],
        ["12 m (nearest roll stand)", "approx. 14 s", "approx. 16 s"],
        ["26 m (base-case route)", "approx. 24 s", "approx. 32 s"],
        ["30 m (mid corridor)", "approx. 27 s", "approx. 36 s"],
        ["60 m (far end of corridor)", "approx. 50 s", "approx. 70 s"],
        ["Complete mission, 30 m round trip incl. pick-up and drop-off", "approx. 66 s (approx. 54 missions/h)", "approx. 85 s (approx. 42 missions/h)"],
    ], widths=[3.0, 2.8, 3.6])
    ins.bullets([
        "At 8.8 reels/hour the Smart carriage utilisation stays below 25% even with 30 m average missions; dual-reel transport and simultaneous return of partial reels further reduce the number of missions. Effective cadence is dominated by the transfer interfaces, not by travel.",
        "The rail-guided Block A keeps an advantage only for sustained cycle rates above about 60 transfers/hour with constant load and a frozen layout; the Paige corrugator demand is far below that threshold.",
        "The final capacity statement will be confirmed with the INGECART digital-twin model on the approved Paige layout during the application study, using the same methodology as the Block A benchmark.",
    ])

    ins.heading("5A.5 Civil works, installation and maintenance impact", 2)
    ins.table([
        ["Aspect", "Block A (rail-guided)", "Block A-Smart (rail-less)"],
        ["Civil works", "Floor cutting, demolition, channel, reinforcement, concreting and curing for more than 60 m of running rails; supports for the conductor line", "None. The carriage runs on the existing floor; only local repair where the travel lane is damaged."],
        ["Fixed infrastructure supplied", "Rails, conductor line, current collector, end stops", "One automatic charging station; Wi-Fi coverage check and reinforcement if required"],
        ["Site services", "Rail installation block (14 days, 1 technician) plus mechanical assembly", "Rail installation block removed. Installation, mapping, station adjustment, integration and training in about one week, overlapping with normal plant activity. Mechanical assembly block re-quoted after layout approval."],
        ["Production disruption during installation", "Rail and conductor-line works inside the corrugator corridor with restricted access", "None in the corridor: mapping and station set-up are performed without stopping the zone"],
        ["Future layout changes", "New rail sections, conductor line and civil works", "Edit the navigation map; add a destination by registering a station in software; relocating to another hall requires transport and remapping only"],
        ["Preventive maintenance", "Rail wear, cleaning and alignment; collector brushes or festoon; cable chain; traction gearbox", "Periodic inspection of wheel treads, cleaning of navigation and safety optics, annual verification of safety functions, battery state tracking. Drive diagnostics (current, torque, temperature, following error) anticipate interventions."],
        ["Spare parts", "Collector brushes, rail fixings, traction motor", "Drive wheel exchangeable as a flanged unit; battery pack (replacement expected in year 7-10); treads per cycles; optics"],
        ["Single points of failure", "Conductor line and collector", "None on power supply; manual console mode allows reel evacuation; agreed forklift fallback procedure"],
        ["Aisle and internal traffic", "Permanent rail in the pavement obstructing forklifts and cleaning", "Pavement free when the carriage is not in transit"],
    ], widths=[1.8, 3.2, 3.6])

    ins.heading("5A.6 Safety basis for the rail-less carriage", 2)
    ins.bullets([
        "Removing the rail removes the physical separation between machine and personnel; it is replaced by certified functional safety designed in accordance with EN ISO 3691-4 (driverless industrial trucks) and EN ISO 13849-1/-2.",
        "Safety functions: person detection by front and rear safety laser scanners with protective fields adapted to speed and direction (PL d Cat. 3); emergency stop from four sides with controlled stop followed by brake application (PL d Cat. 3); perimeter mechanical bumper as scanner backup (PL d Cat. 3); safely limited speed monitored on a safety module with forced reduction at stations, crossings and manoeuvres (PL d Cat. 3); spring-applied holding brake (PL c Cat. 1); travel inhibited while a transfer is in progress or the reel is not secured (PL c Cat. 1).",
        "Complementary measures: beacon and acoustic movement signal, light projection of the sweep zone on the floor, floor marking of the travel aisle, key mode selector, manual console with three-position enabling device, 0.30 m/s limit in manual and maintenance modes, lockable battery disconnector for lockout, safety event log accessible from diagnostics.",
        "Braking philosophy: controlled electrical braking first, mechanical brake at the end of the ramp, so the safety function is met without displacing or tipping the reel. Real stopping distances are measured with the customer reel during factory and site acceptance.",
        "INGECART delivers the complete machine with technical file (risk assessment, safety function calculation and validation, electrical schematics in EPLAN Electric P8, EMC report and electrical verifications), EU declaration of conformity, CE marking, instruction and maintenance manuals, spare-parts list and training.",
    ])

    ins.heading("5A.7 Operational value versus Block A", 2)
    ins.bullets([
        "Same automatic reel logistics, same MES/ERP integration and same forklift-free corrugator area as Block A.",
        "Elimination of more than 60 m of embedded rails, of the conductor line and of the fixed feed along the route: no civil works, no zone shutdown for installation, no rail or catenary maintenance.",
        "Layout flexibility: additional roll stands, a relocated exchange area or a second corrugator are served by editing the map and registering stations instead of extending rails; the carriage is a mobile asset that can be relocated or reused.",
        "Capacity scaling by fleet: a second Smart carriage can share the same corridor with traffic management, without duplicating infrastructure.",
        "Open architecture: standard Siemens PLC and CANopen drives with documented parameters; no dependence on a proprietary black box.",
        "Per-transfer traceability and drive diagnostics feed the same request-to-delivery, starvation and availability KPIs used in Block A, plus energy per mission.",
    ])

    ins.heading("5A.8 Site prerequisites for Block A-Smart", 2)
    ins.bullets([
        "Industrial concrete floor in good condition in the travel lane, without breaks or spalling; local level deviation below about +/-5 mm over 2 m; expansion joints below 20 mm wide. Measured by INGECART during the technical visit; any local repair is identified and quoted before commitment.",
        "One charging position with 230/400 V supply for the 48 V / 60 A automatic charger.",
        "Industrial Wi-Fi coverage along the corridor; reinforcement quoted if the coverage check requires it.",
        "Definition of personnel and forklift traffic in the corridor, which sets the level of the protective measures.",
        "Reel matrix (mass, dimensions, support type, centre-of-gravity height) and transfer heights at exchange area and roll-stand tracks.",
    ])

    ins.heading("5A.9 Engineering qualification and price basis", 2)
    ins.bullets([
        "Speed, traction, energy, braking and safety values are INGECART design data for the IGC-DW drive-wheel family and the reference platform (2,800 x 1,500 mm, 3,500 kg design mass, 26 m route) and will be confirmed for the Paige reel carrier in the application study and the Functional Design Specification.",
        "Stopping distances and the performance level of the safety functions are validated with the real reel load during factory and site acceptance, in accordance with EN ISO 3691-4 and EN ISO 13849-2.",
        "The Smart reel carrier, its wheel configuration and mass distribution are engineered by INGECART; the reel envelope of Block A remains the governing design basis.",
        "Block A-Smart supply is offered at the same EXW price as Block A. The rail installation service block (14 days, 1 technician) is not required for Block A-Smart and is removed from the site-services table when this option is selected; the mechanical assembly block is re-quoted after layout approval. Indicative programme from order to CE handover: 18-20 weeks (application study 2, detail engineering 4, manufacturing 10-12, factory tests 1, installation 1, conformity 1).",
        "Block A and Block A-Smart are mutually exclusive alternatives within this proposal.",
    ])
    ins.paragraph("")


EXEC_SUMMARY_BULLET = (
    "Optional Block A-Smart: the same INGETRANS reel logistics on a rail-less, battery-powered autonomous "
    "carriage (INGECART IGC-DW drive wheels, laser navigation, 48 V LiFePO4 battery, CE marked by INGECART), "
    "removing more than 60 m of embedded rails, the conductor line and their civil works."
)

PRICE_NOTE = (
    "Block A-Smart (INGETRANS Smart, rail-less option described in chapter 5A) is offered at the same EXW "
    "supply price as Block A and replaces it when selected. When Block A-Smart is chosen, the rail installation "
    "service block is not applicable and the mechanical assembly block is re-quoted after layout approval."
)
