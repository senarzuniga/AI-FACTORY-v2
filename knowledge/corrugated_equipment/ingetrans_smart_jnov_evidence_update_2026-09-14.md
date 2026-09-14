# INGETRANS Smart — Síntesis de la última información trabajada sobre ruedas inteligentes JNOV TECH

**Fecha de consolidación:** 14 de septiembre de 2026  
**Fuentes primarias analizadas (texto completo extraído):**

| Ref | Documento | Naturaleza | Fecha doc. | Páginas |
|---|---|---|---|---|
| SRC-JNOV-OVW | `JNOV TECH General overview exter 2023 EN _compressed.pdf` | Presentación corporativa externa | 01/2023 | 28 |
| SRC-JNOV-PRC | `agv system JNOV TECH Info PRC-23-099.pdf` | Propuesta técnico-comercial MDS dirigida a **MTORRES** | 09/08/2023 | 56 |

**Trabajo previo INGECART localizado:** `INGETRANS_SMART_TECHNICAL_PRODUCT_REPORT_2026-09-10.html` y `knowledge/corrugated_equipment/ingetrans_smart_product_assumptions_and_evidence_2026-09-10.json` (definición de producto Smart Manual / Guided / Orchestrated basada en la tecnología Modulo Smart Weels). No existen documentos posteriores al 10/09/2026 sobre INGETRANS Smart en los repositorios ni en `INGECART/PRODUCTO/INGETRANS`.

---

## 1. Hallazgos nuevos respecto a la base de evidencia del 10/09/2026

| # | Hallazgo | Impacto para INGETRANS Smart |
|---|---|---|
| 1 | La oferta PRC-23-099 **no fue emitida a INGECART sino a MTORRES** (9 ago 2023), validez 1 mes. | Los precios son referencia histórica de terceros; INGECART debe solicitar oferta propia. |
| 2 | Precio unitario **MDS-2x4TP: 40.894 € (x1) / 31.187 € (x10)** — descuento de volumen del 23,7 %. Kit completo con baterías, mando y guardapiés: **45.803 €** (x1) / **35.832 €/ud** (x10). | Base de coste realista para la variante Smart Manual por carro. |
| 3 | **Modo semiautomático (seguimiento de línea)**: 5.496 € por sensor óptico integrado en DDW (2 por kit → 10.992 €), licencia LIC-0002 incluida; **generación de trayectorias no incluida**. | Smart Guided añade ≈ +24 % sobre el kit base; el desarrollo de rutas es alcance INGECART o del PLC maestro. |
| 4 | **Plazo: entrega T0+24 semanas**, puesta en marcha T0+26 semanas; kick-off T0+1 s, revisión de integración T0+6 s. | El lead time de JNOV domina el plan de entrega de cualquier piloto Smart. |
| 5 | **Roadmap JNOV** (overview 2023): navegación asistida MDS (seguimiento de trayectorias complejas, posicionamiento fino automático), Multi-MDS para líneas de montaje, **AGV MDS** como hito 2024-2025, DDW 8T industrializado, MDS 1T. | La evolución "Smart Orchestrated" depende de que JNOV libere AGV MDS; hoy solo existe semi-auto con PLC externo. |
| 6 | Certificación: **cuasi-máquina** (Directiva 2006/42/CE) + EMC 2014/30/UE. Excluye explícitamente la certificación CE de la máquina completa. | Confirma CL-03 del JSON: la CE final del carro INGETRANS Smart es responsabilidad de INGECART. |
| 7 | Requisitos de suelo: **DIN 18202 tabla 3 línea 3 (4 mm/1 m, 10 mm/4 m)**, hormigón/asfalto, pendiente 3 %, escalón 5 % del Ø rueda, presión de contacto > 10 N/mm². | Criterio de auditoría de planta obligatorio antes de ofertar Smart. |
| 8 | Ruedas orientables auxiliares: el MDS debe soportar **> 50 % de la masa total**; resistencia de rodadura ≤ 1,5 %, arranque y giro ≤ 3 %; no exceder 70 % de la capacidad del castor. | Condiciona el diseño del bastidor portabobinas (reparto de cargas). |
| 9 | Supervisión/mando por PLC cliente vía **EtherNet/IP (PROFINET bajo pedido)** con fichero EDS; variables: consigna de velocidad y dirección, estado, modo, batería, movimiento, número de fallo. | Define la interfaz de telemetría INGETRANS Smart → DEP (ver §5). |
| 10 | Radio: IEEE 802.15.4, 2.405-2.480 MHz, DSSS, 15 canales (11-25), alcance ~200 m, tasa mínima > 50 kbps, ruido < -80 dBm. Pérdida de radio → SS1. | Requiere estudio de coexistencia Wi-Fi en planta de corrugado. |
| 11 | Baterías Li-ion: 1 por DDW, 600 ciclos de carga, garantía 12 meses; equipo 24 meses. Autonomía de referencia "1000 m" por batería. | Dimensionar recorrido diario de bobinas frente a la autonomía real. |
| 12 | Compensación dinámica de suelo irregular solo con DDW-xTL (elevación integrada), opción 910 €. | Si se elige TL (bastidor con elevación), se recomienda activar esta opción. |

---

## 2. Especificaciones técnicas consolidadas — DDW-4TP (fuente SRC-JNOV-PRC §3.5)

| Parámetro | Valor |
|---|---|
| Dimensiones DDW | 370 × 530 × 305 mm |
| Huella total | Ø 550 mm (575 mm con guardapiés) |
| Altura libre al suelo | 29 mm (20 mm con guardapiés) |
| Rueda | Poliuretano Ø 250 mm, perfil curvo, llanta sustituible |
| Peso | 60 kg |
| Velocidad | 1 mm/s – 2 km/h (overview 2023 indica hasta 2,5 km/h) |
| Capacidad de carga / remolque | 4.000 kg / 4.000 kg |
| Fuerza de tracción nominal / máx. | 1,6 kN / 4,5 kN |
| Protección | IP54 |
| Pendiente admisible | 3 % |
| Vida nominal | 2.500 km o 10.000 h |
| Temperatura de servicio | 0 °C a +40 °C; HR máx. 85 % |
| Precarga (versión TP) | Ajuste de fábrica 50-60 % de la capacidad; recorrido ±20 mm; tornillos de embrague para elevar 5 mm |
| Articulación | ±4° para adaptación al suelo |
| Conexión | 1 cable híbrido potencia+señal, conector M23, Ø 15,5 mm, radio mín. 73/148 mm |
| Seguridad | SS1 PLd (cat. 1 IEC 60204-1), STO en variadores, freno de seguridad sin tensión, paro de emergencia PLd/Cat 3 en mando |
| Fijación | Brida con centraje; versión 4T = 8 × M12 |

**Gama de capacidades JNOV (overview 2023):** DDW 1 T, 2 T (2024), 4 T, 8 T (S2/2023). Sistemas MDS de 1 a 60 t combinando ruedas. Referencias en servicio: MDS 2x4TP (plataformas aeronáuticas 6-8 t, preserie > 50 unidades), MDS 4x8TL (rotor Haliade-X, 32 t), MDS 30 t aeronáutica MRO.

---

## 3. Modos de operación y guiado disponibles

**Incluidos en licencia básica LIC-0001:** Crab (longitudinal/transversal), Car (dirección en ambos ejes centrada en la carga), Autorotación (giro sobre el centro geométrico), Elevación (solo TL).

**Opción semiautomática LIC-0002:** seguimiento de línea pintada mate (azul RAL 5015, verde RAL 6032, rojo RAL 3001; ancho 10-40 mm, defecto 18 mm) o **línea DataMatrix (hasta 10.000 m)**; cámara 2D, campo 117 × 75 mm; resolución ±1 mm (pintada) / ±0,1 mm (DataMatrix); radio mínimo de curva 0,5 m. El operario controla solo la velocidad; códigos de control/posición disparan acciones (cambio de velocidad, parada en posición, giro a ángulo, decisión de ramal, cambio de modo, cambio de sistema de coordenadas). Planificador descentralizado con PLC externo para gestión de flota vía EtherNet/IP.

**No disponible en 2023:** navegación libre (SLAM/LiDAR) ni AGV autónomo; figura en roadmap como "AGV MDS".

---

## 4. Estructura de coste de referencia para INGETRANS Smart (por carro portabobinas)

Precios JNOV 2023 (EXW Pujaudran, sin transporte ni integración). Requieren actualización mediante oferta propia a INGECART.

| Nivel Smart | Composición JNOV | x1 | x10 (ud.) |
|---|---|---:|---:|
| **Smart Manual** | MDS-2x4TP + 2 baterías + mando + 4 guardapiés | 45.803 € | 35.832 € |
| **Smart Guided** | Anterior + 2 sensores ópticos + LIC-0002 | 56.795 € | 46.824 € |
| **Smart Orchestrated** | Anterior + opción mando/supervisión por PLC (a cotizar) + generación de trayectorias (no incluida) + gestión de flota INGECART | a cotizar | a cotizar |

Opciones relevantes: seta de emergencia en armario 147 €; entrada auxiliar de sensor 150 €; entrada de seguridad auxiliar 150 €; hombre muerto 537 €; multiemparejamiento hasta 32 receptores 317 €; compensación de suelo 910 €; modo custom de rotación 1.925 €. Servicios: puesta en marcha 2 días 1.600 €; formación 2 días 1.600 €; asistencia 800 €/día o 3.200 €/semana. Cinta y códigos DataMatrix: 24 €/m.

Condiciones: pago 45/50/5; garantía 24 meses (baterías 12); EXW.

---

## 5. Interfaz de datos INGETRANS Smart → Digital Ecosystem Platform

La opción "Supervisión por PLC cliente" expone por EtherNet/IP: modo operativo actual, nivel de batería, movimiento en curso y número de fallo activo. La opción "Mando por PLC" añade consignas de velocidad/dirección y realimentación de estado. Esto encaja directamente con la especificación de captura ya definida para el HD Palletizer (`Digital-Ecosystem-Platform/docs/hd_palletizer_data_capture_spec_v1.md`): estados on-change + heartbeat, contadores monótonos y eventos con `source_ts`.

Señales mínimas recomendadas para Smart: `mds.mode`, `mds.state`, `mds.fault_code`, `mds.battery_pct[n]`, `mds.speed_setpoint`, `mds.speed_actual`, `mds.heading`, `mds.position_code_id` (DataMatrix), `mds.line_lost`, `mds.estop`, `mds.radio_quality`, `mds.odometer_m`, `mds.lift_load_kg` (TL), `mission_id` desde el PLC maestro INGECART.

---

## 6. Contradicciones y límites detectados

| Id | Cuestión | Resolución propuesta |
|---|---|---|
| CL-04 | Velocidad máxima: 2 km/h (PRC-23-099) vs 2,5 km/h (overview 2023). | Usar 2 km/h como valor contractual del DDW-4TP; 2,5 km/h queda como dato de gama. |
| CL-05 | Los precios son de agosto 2023 y para MTORRES; validez expirada. | Tratarlos como "referencia histórica" en ASE; solicitar cotización INGECART antes de ofertar. |
| CL-06 | La autonomía "1000 m" por batería no está definida en condiciones (carga, suelo, ciclo). | Exigir curva de autonomía vs carga en la nueva oferta; dimensionar 1 batería/DDW + reserva. |
| CL-07 | La generación de trayectorias y la gestión de flota no forman parte del suministro JNOV. | Definirlas como alcance INGECART (PLC maestro / WCS) en Smart Guided y Orchestrated. |
| CL-08 | Requisito DIN 18202 y presión > 10 N/mm² pueden no cumplirse en plantas antiguas de corrugado. | Incorporar auditoría de suelo como prerequisito comercial del producto Smart. |

---

## 7. Estado de madurez actualizado de INGETRANS Smart

| Elemento | Estado |
|---|---|
| Base tecnológica (DDW/MDS) | Validada por documentación de proveedor y referencias industriales en servicio |
| Arquitectura de tres niveles Smart | Coherente con licencias LIC-0001 / LIC-0002 / PLC externo |
| Coste de plataforma de tracción | Referencia 2023 disponible; cotización INGECART pendiente |
| Bastidor portabobinas y reparto de cargas | Pendiente (regla > 50 % masa sobre MDS, castores ≤ 70 %) |
| Navegación autónoma libre | No disponible en proveedor; roadmap AGV MDS |
| Seguridad máquina completa | Pendiente (CE completa a cargo de INGECART) |
| Interfaz de datos a DEP | Definible vía EtherNet/IP; opción a cotizar |

## 8. Acciones recomendadas

1. Solicitar a JNOV TECH oferta actualizada a nombre de INGECART para MDS-2x4TP y MDS-2x4TL (x1 y x5), incluyendo LIC-0002, supervisión por PLC y curva de autonomía.
2. Diseñar el carro portabobinas de referencia (bobina < 3.500 kg, Ø 1.500 mm) verificando reparto de masa y castores conforme a §3.15.4 de la oferta.
3. Definir el estándar de trayectorias DataMatrix para el corredor de roll stands y la lógica de misiones en PLC maestro INGECART.
4. Añadir en ASE la variante "INGETRANS Smart" con las tres bandas de coste de §4 marcadas como referencia histórica 2023.
5. Alinear el catálogo de señales Smart (§5) con `TYPE_LIBRARY` de DEP en la siguiente iteración.
