# INGETRANS Smart — Informe de producto

**Integración de la tecnología de ruedas motrices JNOV TECH (MDS/DDW) en el sistema INGETRANS de alimentación de bobinas**

**Revisión:** 1.0 — 14 de septiembre de 2026  
**Estado:** definición de producto para decisión de Dirección; base para oferta de piloto  
**Propietario:** Ingeniería de Producto INGECART

---

## 1. Resumen ejecutivo

INGETRANS Smart es la evolución de INGETRANS en la que el carro transfer deja de depender de infraestructura fija: **las ruedas motrices y directrices JNOV (DDW) sustituyen a los carriles metálicos de rodadura, y las baterías Li-ion a bordo sustituyen a la catenaria/línea de contacto (Vahle)** que hoy alimenta eléctricamente al transfer. La función productiva —entrega automática de bobinas a los roll stands de la corrugadora y retorno de bobinas parciales al almacén— se mantiene íntegra; lo que cambia es el modo de moverse y de alimentarse.

Resultado para el cliente:

- **Menos obra civil e infraestructura:** desaparecen carriles empotrados, fijaciones, alineación de vía, catenaria y sus soportes.
- **Instalación más corta:** el bloque de montaje mecánico de INGETRANS (28 días × 4 técnicos) se reduce de forma sustancial al eliminar el tendido de vía y catenaria (estimación de ingeniería, pendiente de validar en piloto).
- **Layout modificable por software:** el recorrido se define con línea DataMatrix o pintada; ampliar un roll stand o mover la zona de intercambio no exige obra.
- **Sin punto único de fallo en la alimentación eléctrica:** no hay línea de contacto que se desgaste ni colector que falle.

Contrapartida técnica que el producto debe gestionar de forma explícita:

- La **velocidad de traslación es menor** (2 km/h contractual en DDW-4TP frente a 80 m/min = 4,8 km/h del transfer actual). En el layout de referencia de 12 m la misión de ida se alarga de ~13,5 s a ~26 s. **Con 8,8 bobinas/h de consumo de referencia, la capacidad sigue cubierta con amplio margen**, pero en plantas de alta cadencia o recorridos largos debe verificarse con simulación antes de ofertar.
- La **autonomía de baterías, la calidad del suelo y el reparto de cargas** pasan a ser requisitos de proyecto, no detalles de instalación.
- La **navegación totalmente libre (AGV)** no está disponible en el proveedor; el producto se ofrece hoy con guiado por línea y orquestación por PLC INGECART.

---

## 2. Qué se elimina y qué lo sustituye

| Elemento del INGETRANS actual | Función | Situación en INGETRANS Smart | Sustituto |
|---|---|---|---|
| Carriles de rodadura (rieles) | Guiar y soportar el carro transfer | **Eliminado** | Ruedas DDW de poliuretano rodando sobre solera; guiado por sensor óptico sobre línea DataMatrix/pintada |
| Catenaria / línea de contacto Vahle | Alimentar eléctricamente el transfer | **Eliminada** | Baterías Li-ion a bordo (1 por DDW) + armario ELC con cargador; estación de carga en parking |
| Colector de corriente y cable de arrastre | Transmitir energía en movimiento | **Eliminado** | Cable híbrido interno M23 entre ELC y cada DDW (dentro del carro) |
| Obra civil de vía (empotrado, nivelación, anclajes) | Soporte de carriles | **Eliminada** | Auditoría de planitud de solera (DIN 18202) |
| Finales de carrera mecánicos en vía | Límite de recorrido | **Sustituidos** | Códigos de posición DataMatrix + escáneres de seguridad + zonas software |
| Motor de traslación único + reductor | Tracción del carro | **Sustituido** | 2 × DDW-4TP (4 motores brushless, tracción diferencial) |
| Vías motorizadas hacia roll stands | Llevar la bobina del transfer al roll stand | **Se mantienen** en la versión base; opción de entrega directa en fase posterior | Vías INGETRANS actuales (59 m/min) |
| Sistema de elevación/cierre sobre bobina | Recoger y soltar bobina (6 s) | **Se mantiene** | Mecanismo INGETRANS sobre nuevo bastidor |
| Zona de intercambio, rampas, vallado | Interfaz con almacén y seguridad | **Se mantienen**, rediseño ligero | Idéntico concepto; vallado adaptado a zona móvil |

Partidas del desglose de coste actual afectadas directamente: **Rieles 20.000 €, Catenaria 20.000 €** (eliminadas) y parte de **Rampa y entrada 50.000 €** y **Fabricación transfer/carenado 87.000 €** (rediseño). En su lugar entra el kit de tracción JNOV (ver §7).

---

## 3. Arquitectura del producto

```
ALMACÉN ──► Zona de intercambio ──► CARRO INGETRANS SMART ──► Vías a roll stands ──► Corrugadora
                                         │
                                         ├─ Bastidor portabobinas INGECART (1 o 2 bobinas, < 3.500 kg c/u)
                                         ├─ Mecanismo de elevación/cierre INGETRANS (6 s pick / 6 s drop)
                                         ├─ 2 × DDW-4TP en diagonal (o 4 × DDW según masa total)
                                         ├─ Castores curvos auxiliares (< 50 % de la masa)
                                         ├─ Armario ELC: control, radio, baterías Li-ion, cargador IEC C14
                                         ├─ Sensores ópticos de guiado (1 por DDW guía) + códigos DataMatrix
                                         ├─ Escáneres láser de seguridad perimetrales (alcance INGECART)
                                         └─ PLC INGECART maestro ── EtherNet/IP ── ELC JNOV
                                                    │
                                                    └── OPC UA / MQTT ──► ERP-MES-WMS · Digital Ecosystem Platform
```

### 3.1 Tracción y dirección (JNOV MDS)

- Rueda DDW-4TP: 370 × 530 × 305 mm, Ø 250 mm poliuretano, 60 kg, 4.000 kg de capacidad por rueda, 1,6 kN nominal / 4,5 kN máx. de tracción, IP54, vida 2.500 km o 10.000 h.
- Precarga integrada (versión TP) con ±20 mm de adaptación al suelo, ajustada al 50-60 % de capacidad; alternativa TL con elevación integrada y compensación dinámica de suelo.
- Modos incluidos: Car, Crab, Autorotación (y Elevación en TL). Movimiento omnidireccional en el corredor.
- Velocidad 1 mm/s – 2 km/h; posicionamiento milimétrico (±1 mm sobre línea pintada, ±0,1 mm sobre DataMatrix).

### 3.2 Energía

- 1 batería Li-ion por DDW, 600 ciclos, garantía 12 meses. Configuración integrada en ELC o extraíble.
- Recarga en parking mediante toma IEC C14 230 V; la gestión de carga se programa entre misiones desde el PLC maestro.
- Referencia de autonomía del proveedor: "1.000 m por batería" sin condiciones declaradas. Con misiones de 60 m ida y vuelta eso equivale a ~16 misiones por carga; **insuficiente como dato de diseño** → exigir curva autonomía-carga en la oferta a INGECART.

### 3.3 Guiado y control

- **Nivel 1 — Smart Manual:** radiomando DSSS 2,4 GHz, modos Car/Crab/Autorotación. Uso para puesta en marcha, mantenimiento y modo degradado.
- **Nivel 2 — Smart Guided:** seguimiento de línea DataMatrix con sensor óptico; códigos de posición disparan parada en roll stand, cambio de velocidad, giro y ramal. Operario solo controla velocidad o el PLC maestro la fija.
- **Nivel 3 — Smart Orchestrated:** PLC INGECART recibe órdenes de ERP/MES, planifica misiones, gobierna velocidad/dirección vía EtherNet/IP y supervisa estado, batería y fallos. La generación de trayectorias y la gestión de flota son **software INGECART**, no del proveedor.

### 3.4 Seguridad

- JNOV suministra SS1 PLd (categoría 1 IEC 60204-1), STO, frenos de seguridad sin tensión, paro de emergencia PLd/Cat 3 en mando y parada por pérdida de radio.
- INGECART añade: escáneres láser de área con campos de aviso/parada, seta en armario, hombre muerto para modo manual, entradas de seguridad auxiliares (2 disponibles), vallado en zona de intercambio y enclavamiento con vías y roll stands.
- Certificación: JNOV entrega **cuasi-máquina** (2006/42/CE + EMC 2014/30/UE). La **evaluación de riesgos y el marcado CE de la máquina completa son de INGECART**, incluyendo ISO 3691-4 para vehículos sin conductor si el producto opera sin operario en la zona.

---

## 4. Especificación técnica de referencia

| Parámetro | INGETRANS actual | INGETRANS Smart (referencia) | Estado |
|---|---|---|---|
| Bobinas por viaje | Hasta 2 | 1–2 según masa total y reparto sobre DDW | Verificado / a dimensionar |
| Peso máximo de bobina | < 3.500 kg | < 3.500 kg (limitado por bastidor y castores) | A confirmar en diseño |
| Diámetro / longitud bobina | 1.500 mm / 1.800 mm | Idéntico | Verificado |
| Velocidad de traslación | 80 m/min (4,8 km/h) | 2 km/h contractual; 2,5 km/h dato de gama | Verificado |
| Rampa aceleración | 4,5 s | Configurable en ELC | Verificado |
| Pick-up / drop-off | 6 s + 6 s | 6 s + 6 s (mecanismo conservado) | Verificado |
| Posicionamiento en vía | Encoder/final de carrera | ±0,1 mm sobre DataMatrix | Verificado proveedor |
| Alimentación | Catenaria Vahle | Baterías Li-ion, 1/DDW | Verificado |
| Infraestructura en suelo | Carriles empotrados | Solera DIN 18202 (4 mm/1 m) + línea DataMatrix | Verificado |
| Pendiente admisible | — | 3 % | Verificado |
| Interfaz control | Siemens S7 | PLC INGECART + EtherNet/IP a ELC (PROFINET bajo pedido) | Verificado |
| Nivel de seguridad tracción | — | SS1 PLd | Verificado |
| Temperatura de servicio | — | 0–40 °C, HR ≤ 85 % | Verificado |

---

## 5. Análisis de capacidad

Modelo trapezoidal con rampas de 4,5 s, pick y drop de 6 s cada uno:

| Distancia zona intercambio → roll stand | Ida actual | Ida Smart 2 km/h | Ida Smart 2,5 km/h |
|---:|---:|---:|---:|
| 12 m (layout de referencia) | 13,5 s | 26,1 s | 21,8 s |
| 30 m | 27,0 s | 58,5 s | 47,7 s |
| 60 m | 49,5 s | 112,5 s | 90,9 s |

Misión completa ida-vuelta a 30 m: **66 s actual (≈54 misiones/h) frente a 129 s Smart (≈28 misiones/h)**. La planta de referencia del gemelo digital consume 8,8 bobinas/h, por lo que Smart mantiene una utilización del carro inferior al 35 % incluso a 30 m; en el layout de 12 m la holgura es mayor. El transporte doble de bobinas y el retorno simultáneo reducen aún más el número de misiones.

**Regla de producto:** INGETRANS Smart se ofrece cuando `misiones_pico/h × tiempo_misión_Smart ≤ 0,6 × 3.600 s`. Por encima de ese umbral se ofrece INGETRANS con carril, o Smart con dos carros.

Energía mecánica de rodadura estimada para 5.000 kg (bobina + bastidor) a 2 km/h con resistencia del 1,5 %: ~0,4 kW; el consumo real incluye elevación, electrónica y pérdidas → dato a medir en piloto.

---

## 6. Requisitos de planta (prerrequisitos comerciales)

1. **Solera:** hormigón o asfalto, planitud DIN 18202 tabla 3 línea 3 (4 mm/1 m, 10 mm/4 m), presión de contacto admisible > 10 N/mm², escalones ≤ 5 % del diámetro de rueda (12 mm), pendiente ≤ 3 %.
2. **Radio:** un canal IEEE 802.15.4 (11–25) disponible, ruido < −80 dBm, > 50 kbps; estudio de coexistencia Wi-Fi.
3. **Línea de guiado:** corredor libre para línea DataMatrix (radio mínimo de curva 0,5 m), protección frente a suciedad de papel y desgaste por carretillas.
4. **Parking y carga:** posición con toma 230 V y espacio para intercambio de batería.
5. **Separación persona-máquina:** zonas de tránsito definidas; escáneres y señalización.
6. **Ambiente:** 0–40 °C, HR ≤ 85 %, sin condensación.

---

## 7. Estructura de coste de referencia (por carro)

Precios JNOV de la oferta PRC-23-099 (agosto 2023, EXW Pujaudran, emitida a un tercero; **referencia histórica, requiere cotización a nombre de INGECART**).

| Bloque | Partida | Ref. x1 | Ref. x10 (ud.) |
|---|---|---:|---:|
| Tracción JNOV | MDS-2x4TP (2 DDW-4TP + ELC-24 + LIC-0001) | 40.894 € | 31.187 € |
| Energía | 2 baterías DDW-4T | 1.804 € | 1.804 € |
| Mando | Radiomando + accesorios | 2.525 € | 2.525 € |
| Protección | 4 guardapiés | 580 € | 316 € |
| **Subtotal Smart Manual** | | **45.803 €** | **35.832 €** |
| Guiado | 2 sensores ópticos + LIC-0002 | 10.992 € | 10.992 € |
| **Subtotal Smart Guided** | | **56.795 €** | **46.824 €** |
| Orquestación | Opción mando/supervisión PLC (a cotizar), compensación de suelo 910 €, seta armario 147 €, entradas seguridad 2 × 150 € | a cotizar | a cotizar |
| Servicios JNOV | Puesta en marcha 1.600 € + formación 1.600 € | 3.200 € | por proyecto |
| Consumibles | Línea DataMatrix 24 €/m | según layout | según layout |

Partidas INGECART que **desaparecen** del INGETRANS actual: rieles 20.000 €, catenaria 20.000 €; se reducen: fabricación de transfer (nuevo bastidor sin rodadura sobre carril), rampa y entrada, montaje mecánico en campo. Partidas **nuevas**: bastidor portabobinas Smart, escáneres de seguridad, software de misiones en PLC maestro, estación de carga, línea DataMatrix.

Estimación de ingeniería del efecto neto sobre coste directo de un INGETRANS de 5 roll stands (478.150 € de materiales actuales): reducción de infraestructura de vía/catenaria (−40.000 €) y de montaje en campo, compensada parcialmente por el kit JNOV (+46.000 a +57.000 €) y seguridad móvil. **El ahorro del cliente está en obra civil, plazo y flexibilidad, no necesariamente en el precio del equipo**; este es el mensaje comercial correcto.

---

## 8. Propuesta de valor y posicionamiento

| Dimensión | INGETRANS (carril) | INGETRANS Smart | Carretilla / AMR genérico |
|---|---|---|---|
| Obra civil | Alta (carriles, catenaria) | Baja (solera + línea) | Nula / baja |
| Plazo de instalación | 28 d mecánico + 14 d commissioning | Reducido (a validar en piloto) | Bajo |
| Cadencia | Alta (80 m/min) | Media (2 km/h) | Variable |
| Flexibilidad de layout | Nula sin obra | Alta (re-trazar línea) | Máxima |
| Capacidad por viaje | 2 bobinas ≤ 3.500 kg | 1–2 bobinas ≤ 3.500 kg | AMR estándar suele quedar por debajo de 3.500 kg |
| Punto único de fallo eléctrico | Catenaria | Ninguno (baterías) | Ninguno |
| Autonomía | Ilimitada | Por batería; gestión de carga | Por batería |
| Coste de relayout futuro | Alto | Bajo | Bajo |
| Madurez | Instalado y medido | Piloto pendiente | Madura |

Mensaje base: *"INGETRANS Smart entrega la misma automatización de bobinas de INGETRANS sin carriles ni catenaria: se instala sobre la solera existente, se alimenta con baterías y su recorrido se cambia con software."*

Segmentos objetivo: plantas brownfield donde la obra de vía es inviable o interrumpe producción; plantas con cadencia media (< 15 bobinas/h) y recorridos < 40 m; grupos que prevén relayout o ampliación de roll stands.

---

## 9. Hoja de ruta de producto

| Fase | Alcance | Entregable |
|---|---|---|
| 0 — Cotización | Oferta JNOV a INGECART: MDS-2x4TP y 2x4TL, LIC-0002, opción PLC, curva de autonomía | Base de coste válida |
| 1 — Diseño | Bastidor portabobinas, reparto de masas (> 50 % sobre DDW, castores ≤ 70 %), integración mecanismo de elevación, seguridad | Planos, cálculo de cargas, análisis de riesgos |
| 2 — Piloto Smart Guided | 1 carro, 2 roll stands, línea DataMatrix, PLC maestro | Medición de ciclo, autonomía, disponibilidad y consumo |
| 3 — Smart Orchestrated | Integración ERP/MES, gestión de misiones y carga, telemetría a DEP | Producto estándar ofertable |
| 4 — Evolución | Navegación libre cuando JNOV libere "AGV MDS" (roadmap 2024-2025) | Revisión de arquitectura |

Plazo crítico externo: entrega JNOV T0+24 semanas, puesta en marcha T0+26.

---

## 10. KPIs y captura de datos

Alineados con la especificación de captura ya definida en Digital Ecosystem Platform (estados on-change + heartbeat, contadores monótonos, `source_ts`):

- Misiones/h y tiempo de misión P50/P95; `request-to-delivery`.
- Eventos de starvation de roll stand imputables a logística.
- Estado del carro (ISO 22400), modo JNOV, código de fallo, calidad de radio.
- Batería: % por DDW, ciclos, tiempo de carga, energía por misión (kWh/bobina).
- Odómetro por DDW frente a vida nominal 2.500 km / 10.000 h.
- Pérdida de línea, reintentos de posicionamiento, intervenciones manuales.
- Disponibilidad técnica y operativa; MTBF/MTTR.

Interfaz: ELC JNOV → PLC INGECART por EtherNet/IP (modo, batería, movimiento, fallo, consignas) → OPC UA/MQTT → DEP.

---

## 11. Riesgos y mitigaciones

| Riesgo | Impacto | Mitigación |
|---|---|---|
| Velocidad 2 km/h insuficiente en plantas de alta cadencia | Starvation de corrugadora | Regla de dimensionamiento §5; doble bobina; dos carros; mantener INGETRANS carril para alta cadencia |
| Autonomía real inferior a demanda | Paradas por carga | Curva de autonomía contractual; batería por DDW + reserva; carga oportunista entre misiones |
| Solera fuera de DIN 18202 | Pérdida de tracción, desgaste | Auditoría previa; versión TL con compensación dinámica; reparación local de solera |
| Suciedad de papel sobre línea DataMatrix | Pérdida de guiado | Línea protegida, limpieza en plan de mantenimiento, sensor dual, modo degradado manual |
| CE de máquina completa | Bloqueo de entrega | Análisis de riesgos INGECART desde fase 1; ISO 3691-4 si opera sin operario |
| Dependencia de proveedor pequeño (9 personas, 1,1 M€ en 2022) | Continuidad de suministro | Contrato de repuestos, segunda fuente de ruedas motrices, stock crítico |
| Precios 2023 de tercero | Oferta mal costeada | No ofertar hasta cotización propia |

---

## 12. Decisiones solicitadas a Dirección

1. Aprobar el nombre y posicionamiento **INGETRANS Smart** como variante sin carril ni catenaria de INGETRANS.
2. Autorizar la solicitud de oferta a JNOV TECH y el diseño del bastidor de referencia (fase 0–1).
3. Seleccionar planta candidata para piloto Smart Guided con cadencia ≤ 15 bobinas/h y recorrido ≤ 40 m.
4. Fijar la regla comercial: Smart para brownfield/flexibilidad; carril para alta cadencia.

---

## Fuentes

- `INGECART/PRODUCTO/INGETRANS/agv system JNOV TECH Info PRC-23-099.pdf` (oferta técnica-comercial, 09/08/2023).
- `INGECART/PRODUCTO/INGETRANS/JNOV TECH General overview exter 2023 EN _compressed.pdf`.
- `knowledge/corrugated_equipment/ingetrans_smart_jnov_evidence_update_2026-09-14.md` y `ingetrans_smart_product_assumptions_and_evidence_2026-09-10.json`.
- `adaptive-sales-engine/costes productos.txt` (desglose INGETRANS: rieles, catenaria, rampa, montaje).
- Páginas de producto INGETRANS (80 m/min, 59 m/min, 6 s, < 3.500 kg, Ø 1.500 mm).
- `DIGITAL_TWIN_SIMULATION_REPORT_SHORT_RUNS_2026-08-19.txt` (8,8 bobinas/h de referencia).

Las cifras marcadas como estimación de ingeniería o pendientes de piloto no deben trasladarse a oferta sin validación.
