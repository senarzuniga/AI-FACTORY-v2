# Calgary Fase 2: informe de paletización Plug & Play

**Objetivo:** estabilizar la evacuación y paletización de EMBA y Martin, manteniendo la secuencia productiva existente.

## 1. Alcance

- célula Plug & Play en EMBA seleccionada;
- célula Plug & Play en Martin seleccionada;
- gestión de recetas, bundle, interlayer y patrón;
- pallet exit automático;
- llamada de recogida al WCS;
- registro de estado, producción, alarmas y calidad.

## 2. Mecanismo de mejora

Una FFG pierde output útil cuando la descarga no absorbe su ritmo, aunque la máquina pueda producir más. La célula automática reduce esa restricción mediante un ciclo repetible y una señal anticipada de pallet completo.

Beneficios esperados:

- menor blocked time de EMBA/Martin;
- producción más estable entre turnos;
- pallets repetibles y menor daño;
- menos manipulación y correcciones;
- cambio de receta documentado;
- pickup coordinado con WCS/AMR;
- independencia de la variabilidad del paletizado manual.

## 3. Capacidad y compatibilidad

Datos de propuesta pendientes de oferta firmada y FAT:

- 12 bundles/min de producción estable con interlayers;
- pallet hasta 1.200 x 1.200 x 2.300 mm;
- bundle entre 250 x 250 y 700 x 900 mm;
- footprint nominal 3 x 3 m.

No debe seleccionarse la célula por una única velocidad. La matriz de aceptación debe cruzar SKU, dimensiones, peso, bundles/pallet, estabilidad, patrón, interlayer, calidad del cartón y ritmo de salida.

## 4. Integración

Estados mínimos al WCS/MES:

- ready, running, starved, blocked, fault y manual;
- recipe loaded y recipe mismatch;
- pallet present, pallet complete y pickup requested;
- contador bueno/rechazado;
- código de orden, SKU, lote y pallet;
- disponibilidad y motivo de parada.

El WCS no controla el proceso de seguridad de la célula; coordina demanda, recogida y prioridad. Los PLC locales conservan secuencia e interlocks seguros.

## 5. Hipótesis económica

- EMBA: 1 puesto/turno x 4 turnos x CAD 80.000 = CAD 320.000/año bruto;
- Martin: 1 puesto/turno x 4 turnos x CAD 80.000 = CAD 320.000/año bruto;
- total propuesto: CAD 640.000/año.

No es todavía ahorro de caja. Finance debe confirmar coste cargado, tarea eliminada, mecanismo de realización y ausencia de solape con Fase 1. El business case añade output recuperado, daño evitado y OPEX incremental.

## 6. KPIs y gates

- bundles/min sostenidos por familia SKU;
- pallet cycle p50/p95;
- first-pass pallet acceptance;
- blocked minutes de la FFG por descarga;
- cambio de receta;
- intervención manual por pallet;
- disponibilidad y MTTR;
- daño y rework;
- tiempo pallet-completo a pickup.

Liberar cada línea de forma independiente después de FAT y SAT. El éxito en EMBA no se extrapola automáticamente a Martin si cambian formatos, ritmo o patrón.

## 7. Conclusión

Fase 2 convierte la salida de línea en un proceso estándar y medible. Su valor principal es proteger la producción sostenida y preparar cargas consistentes para la logística automática de Fase 3. La implantación debe hacerse por línea y SKU matrix, no por una cifra nominal común.
