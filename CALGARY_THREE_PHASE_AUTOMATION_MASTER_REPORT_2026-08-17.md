# Informe maestro: automatización en tres fases de Cascades Calgary

**Fecha:** 2026-08-17  
**Proyecto:** Cascades Calgary, sección de conversión de cartón corrugado  
**Objeto:** aumentar flujo, producción, trazabilidad y flexibilidad mediante automatización y control integral  
**Estado:** validación de concepto; business case pendiente de CAPEX y baseline aprobados  
**Moneda:** CAD

## 1. Resumen ejecutivo

La propuesta no modifica el modelo de flujo productivo ni la secuencia de procesos. Conserva el WIP al este, las convertidoras al oeste, el transfer de alimentación norte-sur, las tres máquinas de primera pasada, las dos alternativas de segunda pasada y la salida a expedición.

La mejora consiste en sustituir decisiones, movimientos y evacuaciones manuales por una capa coordinada de:

- conveyors automáticos en las salidas de McKinley, Koppers y Ward;
- transfer car automático norte-sur;
- routing por orden, destino y prioridad;
- tridentes para intercambio con AGV/AMR;
- paletización Plug & Play en líneas seleccionadas;
- Ingetrans/WCS, fleet manager e integración ERP/APS-MES/WMS-PLC;
- trazabilidad de cada carga, cola, misión y excepción.

El Factory Graph conserva **13 conexiones productivas**. La automatización añade aristas de control, reservas, handshakes y confirmaciones, no nuevos procesos de fabricación.

La lógica de valor es directa:

1. retirar material antes de que una RDC quede bloqueada;
2. alimentar la segunda pasada antes de que quede sin trabajo;
3. elegir automáticamente segunda pasada, WIP intermedio o expedición;
4. evacuar producto terminado al ritmo real de la línea;
5. cambiar prioridades sin búsquedas, llamadas ni movimientos improvisados;
6. convertir cada movimiento en un evento trazable y medible.

## 2. Situación actual

### 2.1 Flujo preservado

```text
WIP este
  -> transfer de alimentación norte-sur
  -> McKinley RDC 66 x 130 / Koppers RDC 49 / Ward
  -> tres salidas de rodillos
  -> transfer de salida norte-sur
  -> FG miniline / Two-Piece Folder Gluer & Stitcher / expedición
```

### 2.2 Pérdidas operativas a medir

- minutos de RDC bloqueada esperando liberar salida;
- tiempo de empuje, posicionamiento y decisión del transfer manual;
- starvation de FG miniline y línea Two-Piece;
- errores de destino, rehandling y segunda pasada tardía;
- tiempo de búsqueda y edad del WIP;
- daños por manipulación y “pata de elefante”;
- demora de staging en expedición;
- dependencia de disponibilidad y experiencia del operario.

Estas pérdidas todavía no disponen de baseline Calgary aprobado. Por ello, los porcentajes y ahorros del brief se registran como hipótesis de propuesta, no como resultados garantizados.

## 3. Arquitectura de control objetivo

```text
ERP / APS
  órdenes, due dates y prioridades
        |
MES / WMS
  identidad, estado, cantidad y ubicación
        |
INGECART WCS / Flow Orchestrator
  demanda, reservas, routing, colas y excepciones
        |
Fleet Manager + PLC transfer/conveyors/paletizadores
  misiones, tráfico, charging, secuencias e interlocks
        |
Equipos físicos
  RDC, conveyors, transfer, tridentes, AMR y palletizers
```

### 3.1 Reglas funcionales mínimas

- una carga no se libera sin destino reservado;
- una estación no recibe si no confirma capacidad disponible;
- la prioridad se hereda de la orden, pero puede cambiarse con auditoría;
- no se mezclan SKU, orden, lote o estado de calidad;
- los bloqueos generan excepción y alternativa de routing;
- el modo degradado debe mantener producción segura y controlada;
- cada movimiento registra origen, destino, timestamps, resultado y operador/intervención.

## 4. Fase 1: automatización del cuello de botella inmediato

### 4.1 Alcance

- tres conveyors de salida automáticos y coordinados;
- transfer car automático norte-sur bajo el mismo software;
- routing a FG miniline, Two-Piece o expedición;
- tridente sur para carga/descarga AGV;
- tridente intermedio para intercambio y alimentación de segunda pasada;
- tridente norte para WIP intermedio de segunda/tercera operación;
- incorporación Plug & Play en la salida de FG donde la matriz de producto sea compatible.

### 4.2 Aporte al flujo y producción

- reduce el tiempo desde “pila lista” hasta “salida liberada”;
- desacopla la velocidad de la RDC del ritmo de empuje manual;
- evita que las tres salidas compitan sin reglas por el mismo transfer;
- reserva destino antes de mover y reduce rehandling;
- prealimenta segunda pasada según cola, prioridad y disponibilidad;
- habilita expedición y WIP intermedio sin imponer flujo lineal;
- aumenta la velocidad sostenible de RDC, no necesariamente su velocidad mecánica máxima;
- mejora utilización de FG al estabilizar entrada y evacuación.

### 4.3 Transfer car: contrato funcional

Rangos de ingeniería pendientes de oferta y FAT:

- payload: 3.000-5.000 kg;
- traslación: 1,5-2,5 m/s;
- cama de rodillos: 0,3-0,5 m/s;
- ancho: 1.800-2.800 mm;
- longitud: 3.000-5.500 mm;
- altura: 300-450 mm;
- precisión de parada: +/-2 a +/-5 mm.

Inputs mínimos: carga centrada/delantera/trasera, scanner warning/stop, posición absoluta, carga lista en origen, destino listo, finales de carrera, E-stop y drive ready.

Outputs mínimos: dirección/velocidad, rodillos de carga/descarga, freno, baliza/bocina, permiso de transferencia y estados disponible/ocupado/fallo.

Interlocks: alineación, conveyors listos, envolvente libre, safety clear, freno válido, destino con capacidad e identidad de carga correcta.

### 4.4 Hipótesis económicas de propuesta

- transfer y conveyors: 1 puesto/turno, 4 puestos equivalentes, **CAD 320.000/año** a CAD 80.000 por puesto;
- Plug & Play FG: hasta 10 puestos equivalentes, **CAD 800.000/año** propuestos;
- aumento de producción FG: **35% mínimo propuesto** sobre una media de 3.000 golpes/h incluida pérdida por setup y mantenimiento.

Estos valores no son todavía ahorro financiero confirmado. Deben convertirse en tareas-hora únicas, aplicar factor de realización y demostrar que el palletizer no desplaza tareas ya contabilizadas por el transfer o por fase 3.

## 5. Fase 2: expansión de paletización Plug & Play

### 5.1 Alcance

- célula compacta en EMBA seleccionada;
- célula compacta en Martin seleccionada;
- recetas, interlayers, formación de pallet y salida automática;
- llamada de carga terminada al WCS;
- integración de estados, alarmas y trazabilidad.

### 5.2 Aporte

- consistencia del ritmo de salida y patrón de pallet;
- menor bloqueo de línea por evacuación final;
- independencia del ritmo y variabilidad del paletizado manual;
- reducción de daños y rework por pallet defectuoso;
- estandarización de cambios y recetas;
- cargas preparadas para pickup controlado por AMR/Ingetrans.

Valores de propuesta pendientes de FAT: 12 bundles/min, pallet hasta 1.200 x 1.200 x 2.300 mm, bundles entre 250 x 250 y 700 x 900 mm, footprint nominal 3 x 3 m. No se usan como capacidad garantizada hasta validar SKU matrix y oferta firmada.

Hipótesis laboral: 1 puesto/turno por línea y 4 turnos, equivalente a **CAD 320.000/año por EMBA** y **CAD 320.000/año por Martin**. Total bruto propuesto: CAD 640.000/año antes de reconciliación.

## 6. Fase 3: orquestación integral Ingetrans y AMR

### 6.1 Alcance

- transporte coordinado entre WIP, conversión, salidas y expedición;
- WIP automático con AMR y ubicación digital;
- AMR en salidas FFG y engomadora semi-automática;
- prioridades dinámicas, tráfico, charging y excepciones;
- integración ERP/APS, MES/WMS, WCS, fleet manager y PLC;
- simulación previa de flota, buffers y modo degradado.

### 6.2 Aporte

- pre-staging según demanda prevista de máquina;
- menor starvation logístico y mayor estabilidad de velocidad media;
- cambios rápidos al disponer del siguiente trabajo en posición;
- WIP no lineal administrado por prioridad y due date;
- trazabilidad de pallet, orden, lote, ubicación y misión;
- reducción de recorridos de carretilla y zonas de conflicto;
- capacidad modular: rutas y flota pueden ampliarse sin conveyor continuo;
- mejor acceso de mantenimiento al retirar conveyors donde proceda.

Hipótesis de propuesta pendientes de validación:

- +30% de capacidad de almacenaje equivalente por mejor uso de suelo;
- +25% de altura de pallet donde producto, estabilidad y normativa lo permitan;
- 9 puestos equivalentes o CAD 720.000/año por tareas actuales de pallet/transfer;
- evitar 1-2 hojas dañadas por pallet frente a 3-5 observadas actualmente;
- menor MTO al sustituir transportadores rígidos por recursos móviles.

El ahorro de 9 puestos puede solaparse con fases 1 y 2. No se suma hasta reconciliar `fase + rol + turno + tarea + fecha efectiva`.

## 7. Modelo de capacidad

La capacidad recuperada no se calcula aplicando un porcentaje directo a la velocidad nominal. Se calcula por evento:

```text
output recuperado RDC
= minutos bloqueados evitados x velocidad buena sostenida

output recuperado segunda pasada
= minutos de starvation evitados x velocidad buena sostenida

beneficio throughput
= unidades vendibles recuperadas x margen de contribución
```

Para cada escenario se necesitan percentiles p50/p95 de clearance, entrega, cola y recuperación de fallo. El caso base debe utilizar la mediana validada; el caso alto es upside y nunca compromiso.

## 8. Business case y prevención de doble conteo

### 8.1 Beneficio anual neto

```text
mano de obra realizable
+ contribución por output recuperado
+ desperdicio y daño evitado
+ downtime evitado
- OPEX incremental
= beneficio anual neto
```

### 8.2 Escenarios

- **Bajo:** beneficio p25, coste p75 y ramp-up conservador.
- **Base:** beneficio mediano validado y coste esperado aprobado.
- **Alto:** beneficio p75, coste p25; se etiqueta como upside.

### 8.3 Estado del ROI

No es defendible afirmar hoy “ROI menor de dos años” porque faltan:

- CAPEX instalado por fase;
- OPEX de mantenimiento, software y soporte;
- baseline de blocked/starvation/waste;
- matriz de tareas y turnos sin duplicados;
- margen por unidad recuperada;
- resultados de simulación, FAT, SAT y ramp-up.

La afirmación puede convertirse en criterio de diseño: **objetivo de payback <= 2 años**, sujeto a validación financiera.

## 9. KPIs de aceptación

- output clearance p50/p95 por RDC;
- blocked minutes por hora de convertidora;
- starvation minutes de segunda pasada;
- throughput bueno por SKU y turno;
- routing accuracy y cargas reencaminadas;
- WIP age, inventory accuracy y search time;
- misiones AMR p50/p95 y éxito sin intervención;
- automatic-mode availability;
- pallets aceptados a la primera;
- hojas dañadas por pallet;
- intervenciones manuales por 100 cargas;
- seguridad: E-stops, incursiones, near misses y recuperación segura;
- degraded-mode throughput.

## 10. Gates de ejecución

1. **G0 Baseline:** time study, PLC history, producción y matriz rol-tarea.
2. **G1 Concepto/seguridad:** layout medido, control narrative, risk assessment y simulación.
3. **G2 FAT:** matriz SKU, throughput, interlocks, fault recovery e integración de datos.
4. **G3 SAT/ramp-up:** comparación KPI durante ventana representativa.
5. **G4 Liberación siguiente fase:** benefits ledger, riesgos y business case aprobados.

## 11. Recomendación

Proceder con Fase 1 como piloto medido porque actúa sobre el cuello de botella de evacuación más próximo a las RDC y genera la base de software para las fases siguientes. Liberar Fase 2 por línea, no como paquete indiscriminado, después de probar compatibilidad de SKU y capacidad. Liberar Fase 3 solo después de simular flota, tráfico, charging, WIP y modos degradados usando datos obtenidos en Fase 1.

La propuesta tiene una lógica industrial sólida: preserva el proceso, automatiza su ejecución y convierte el flujo en un sistema gobernable. Su valor final debe demostrarse con tiempo recuperado y output bueno, no únicamente con reducción teórica de personas.

## 12. Artefactos de evidencia

- `knowledge/calgary_automation_analysis/calgary_three_phase_assumptions_and_evidence.json`
- `knowledge/calgary_automation_analysis/calgary_three_phase_factory_graph.json`
- `knowledge/calgary_automation_analysis/calgary_three_phase_business_case.json`
- `knowledge/corrugated_equipment/converter_equipment_catalog_v1.json`
