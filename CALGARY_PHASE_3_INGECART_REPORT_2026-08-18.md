# Calgary · Fase 3 · Ingecart

## 1. Resumen ejecutivo

La Fase 3 convierte la logística de apoyo en un servicio productivo. Esto significa que el WIP no se gestiona por improvisación ni por un operador que busca material y destino, sino por prioridad, capacidad y trazabilidad. La diferencia crucial es que el sistema deja de depender de la reacción manual y pasa a operar con decisiones gestionadas por software.

El esquema funcional de la Fase 3 se sustenta en WIP móvil, AMR, reserva de destino y control del flujo por prioridad. La Fase 3 no solo mueve material; define el criterio por el que la planta decide qué material debe ir a dónde y cuándo. Ese nivel de control es el que evita el bloqueo por posición vacía, la espera por falta de destino y la pérdida de capacidad útil.

## 2. Arquitectura del sistema

- WCS / Ingetrans coordina demanda y reserva de destino
- Fleet manager asigna AMR y gestiona rutas, tráfico y charging
- PLC y estaciones validan presencia, secuencia, handoff y seguridad

## 3. WIP automatizado

La gestión automatizada del WIP cambia la lógica del almacén intermedio. En vez de acumular material sin criterio, la planta busca mantener un flujo útil y trazable, con prioridad según urgencia de producción y destino real. Esto reduce la congestión, la búsqueda y la retirada manual de cargas.

## 4. Flota AMR

La flota AMR no es un “equipo auxiliar”. Es la capa que hace posible la continuidad: reasigna palets, materiales auxiliares, interlayers, cores y soportes de flujo entre procesos sin saturar la línea principal. El valor real aparece cuando la logística sirve a la producción antes de que se produzca el bloqueo.

## 5. Diagrama adicional de WIP con AMR

El diagrama de WIP con AMR es clave para explicar la lógica del sistema: la planta no funciona por acumulación sino por asignación racional, destino reservado y misión guiada por prioridad y estado del flujo.

## 6. KPI objetivo

- starvation logístico: -60% a -87%
- tiempo de búsqueda: -50% a -80%
- capacidad de WIP: +30%
- OEE total: +6 pp orientativo
- disponibilidad de flota: alta y previsibles

## 7. Economía

El valor de la Fase 3 está en la recuperación de capacidad útil y en la reducción de bloqueos. El ahorro real surge cuando la logística deja de ser una causa de pérdida de producción y pasa a sostener la continuidad del sistema. Si no se valida con datos de disponibilidad, charging, p50/p95 y prioridad, el valor del AMR puede estar sobreestimado.

## 8. Conclusión

La Fase 3 tiene un papel decisivo: conecta la línea, el WIP y la logística en un modelo operacional sostenible. Es la fase que convierte a la planta en un sistema productivo y trazable, no en un conjunto de áreas que funcionan por reacción manual. La Fase 3 es la capa que hace viable la continuidad del flujo en un entorno de alta variabilidad y servicio exigente.
