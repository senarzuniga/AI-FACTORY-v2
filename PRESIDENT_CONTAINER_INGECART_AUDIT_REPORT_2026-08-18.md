# President Container Group · Informe de auditoría técnica y de flujo · INGECART

**Fecha:** 2026-08-18  
**Cliente:** President Container Group (Middletown, NY)  
**Objeto:** establecer una base de auditoría técnica, operativa y de flujo para una futura automatización de salida/fin de línea, con foco en capacidad, OEE, disponibilidad, buffer, gestión de WIP, logística y estructura de mantenimiento.  
**Enfoque:** auditoría basada en evidencia, benchmarks de desempeño y reglas de flujo industrial, alineadas con el marco operacional de misión y validación.  
**Formato:** versión nueva, independiente del contenido existente del repositorio.

## 1. Resumen ejecutivo

La auditoría técnica no debe limitarse a detectar averías visibles. Debe descubrir el sistema real de pérdidas de capacidad: bloqueo de salida, starvation, rehandling, ajustes repetitivos, flujo poco disciplinado, mala coordinación entre máquinas, mantenimiento reactivo y falta de criterios de prioridad.

Los dos ejemplos aportados (Sullana/United/Agnati y la auditoría de la parte húmeda de Asitrade) muestran la misma lógica operativa:

- los problemas se acumulan durante meses;
- la máquina sigue funcionando, pero no con la capacidad que debería;
- la raíz no es solo mecánica, sino también de proceso, control, mantenimiento, balance y gestión del flujo;
- la solución no es “más velocidad” sino restaurar alineación, disciplina de proceso y capacidad útil.

La auditoría INGECART debe ser un diagnóstico de flujo industrial, no solo de estado físico. Por ello, la metodología debe medir:

1. capacidad real por línea y por turno;
2. tiempo bloqueado en salida / entrada;
3. starvation de líneas downstream;
4. calidad y estabilidad del material;
5. índice de rehandling y movimientos no productivos;
6. OEE de cada estación y del tramo completo;
7. nivel de mantenimiento preventivo y correctivo;
8. impacto del personal y del entrenamiento en la operación.

## 2. Qué analiza una auditoría INGECART

La base de datos de auditoría debe estructurarse en 10 capas de análisis:

### 2.1. Estado físico y mecánico
- alineación global y local;
- paralelismo entre unidades;
- holguras, desgaste, rodillos, soportes y transmisión;
- condición de cuchillas, cliché, placas, tintas, corrugado y zonas de encolado;
- estado de alimentación, salida, tramitación y seguridad.

### 2.2. Estado operativo y de proceso
- velocidad real sostenible;
- tiempos de setup;
- tiempos de bloqueo y microparadas;
- calidad de la pasada y la cola del papel;
- estabilidad de la línea durante picos de carga.

### 2.3. Balance de flujo
- starvation y blockage por estación;
- tampones de WIP y su efecto real;
- congestión en salidas y entradas;
- sincronización entre máquinas y logística interna;
- efecto de un punto único de salida sobre la línea completa.

### 2.4. Control y automatización
- PLC, VFD, servos, comunicación, alarmas, señales de proceso;
- estado de software e interface con MES, WMS, ERP;
- coordinación entre decisiones manuales y automatización;
- capacidad de recuperación ante fallos y modos degradados.

### 2.5. Mantenimiento
- rutas preventivas y correctivas;
- disponibilidad de repuestos;
- historial de averías y tiempo medio de reparación;
- nivel de gestión TPM, calibración y limpieza;
- criticidad de cada equipo por impacto en flujo.

### 2.6. Personal y competencias
- nivel técnico del operador;
- capacidad de ajuste y mantenimiento;
- nivel de supervisión y entrenamiento;
- seguridad y rigor operativo;
- efectividad de la formación para mejorar OEE y estabilidad.

### 2.7. Calidad y pérdidas
- mermas por material, defectos y retrabajos;
- pérdida por alineación, entramado, curvado y otros defectos;
- impacto de tintas, clichés y plate curvature;
- pérdida por tiempo de espera/ajuste.

### 2.8. Logística interna y WIP
- gestión de pallets, bundles, interlayers, consumibles y residuos;
- flujo de materiales auxiliares;
- almacenamiento intermedio; WIP móvil vs fijo;
- rutas de movimiento, prioridad y usos de AMR/tridentes.

### 2.9. Riesgo financiero y de inversión
- coste de averías y demoras;
- coste de paros y retrasos en producción;
- coste por m², por tonelada, por caja, por carga y por hora de parada;
- coste del mantenimiento reactivo frente a la inversión en corrección estructural.

### 2.10. Entregables de auditoría y base de decisión
- mapa de flujo actual;
- árbol de pérdidas por estación;
- ranking de bloqueos y causas;
- plan de intervención priorizado;
- ROIs orientativos por mejora;
- plan de mantenimiento y entrenamiento;
- especificación técnica para automatización y mejora de flujo.

## 3. Cómo se mide en una auditoría técnica

Una auditoría industrial debe convertir observación en números. Los indicadores clave deben medirse por turno, por máquina y por tramo.

### 3.1. Indicadores de flujo
- tiempo de bloqueo por causa;
- starvation por estación;
- tiempo de espera por destino no disponible;
- rehandling y trabajos artificiales para compensar desalineación;
- buffer operativo (WIP) y presión de flujo.

### 3.2. Indicadores de productividad
- cajas / hora buenas;
- bundles / hora; pallets / hora;
- ft²/h; toneladas/h; toneladas/mes;
- tiempo medio de setup y cambio de producto;
- frecuencia de cambio y duración real.

### 3.3. Indicadores de calidad
- defectos por m²;
- merma por material o retrabajo;
- defectos de alineación y de curvado;
- incidencia de papel o hueco / mal contacto.

### 3.4. Indicadores de mantenimiento
- MTBF y MTTR por equipo;
- tasa de averías por sección;
- porcentaje de tareas preventivas cumplidas;
- stock crítico de repuestos y lead time;
- porcentaje de tareas de ajuste pendientes.

### 3.5. Indicadores de OEE
La OEE debe analizarse por sección y por flujo:

- Availability: tiempo disponible menos paradas no planificadas.
- Performance: velocidad real respecto a la velocidad objetivo.
- Quality: producto bueno frente a total producido.

La base de cálculo puede ser:

OEE = Availability × Performance × Quality

Indicadores recomendados:

- OEE de la estación o convertidora: objetivo +5 a +12 pp por mejora del flujo.
- OEE del tramo logístico: objetivo +3 a +6 pp con automatización y WIP disciplinado.
- OEE de la zona de salida final: +6 a +12 pp si se corrige bloqueo y gestión de buffer.

## 4. Qué se obtiene de una auditoría

### 4.1. Evidencia técnica
- diagnóstico estructural;
- causas raíz por zona;
- prioritización real de intervención;
- criterio para decisión de inversión.

### 4.2. Evidencia operativa
- cuánta capacidad se pierde hoy;
- dónde se pierde;
- qué partes del sistema pueden recuperarse sin nueva inversión;
- qué puntos exigen automatización o redesign.

### 4.3. Evidencia económica
- ahorro directo por menos para y menos pérdidas;
- reducción de horas improductivas;
- mejora de calidad y menor merma;
- mejor uso de WIP y de espacio;
- reducción de necesidad de movimiento manual y mayor seguridad.

### 4.4. Evidencia de gestión
- procedimiento para establecer plan de acción;
- formación y TPM;
- control de áreas críticas;
- avance con auditoría y seguimiento periódico.

## 5. Entregables mínimos de una auditoría INGECART

Todo proyecto de auditoría debe generar estos entregables:

1. Informe técnico de diagnóstico.
2. Mapa de flujo actual con puntos críticos.
3. Mapa de pérdidas y causas raíz.
4. Matriz de equipos con criticidad, MTBF, MTTR, riesgo y prioridad.
5. KPI iniciales y benchmark de comparación.
6. Plan de mejoras prioritarias.
7. Propuesta de mejora de flujo / WIP / automatización / logística.
8. Estimación de impacto en OEE, throughput y costo operacional.
9. Plan de mantenimiento y entrenamiento.
10. Roadmap de implementación por fases.

## 6. Mejora tipo en base a benchmarking

Las auditorías muestran que, si se corrigen los puntos críticos de flujo y mantenimiento, los resultados esperables suelen estar dentro de estos rangos:

| Área | Mejora orientativa | Comentario |
|---|---:|---|
| Alineación y paralelismo | 10-25% | mejora de velocidad y calidad |
| Gestión de WIP | 15-35% | menos bloqueos y más continuidad |
| Reducción de starvation | 60-87% | especialmente con WIP y logística automatizada |
| OEE útil del tramo | +3 a +6 pp | sin ampliar capacidad nominal |
| Producción adicional anual | +4.2M m | escenario de flujo mejorado |
| Ahorro operativo anual | ~€309k | referencia orientativa |
| Reducción de rehandling | 30-60% | menos movimientos no productivos |
| Tiempo de setup / ajuste | 20-50% | si se normaliza el proceso |
| Disponibilidad | +8 a +15% | por menos bloqueos y menos cambio de turno |
| Personal indirecto / tareas manuales | -25 a -60% | según automatización y logística |

## 7. Mejora por perfiles de auditoría (Ejemplos de referencia)

### 7.1. Auditoría de mantenimiento y diagnóstico técnico
Enfoque:
- alineación;
- rodillos y transmisiones;
- prevención y corrección;
- holguras y estado de encuadernación / encolado;
- carga y riesgos de seguridad.

Resultados esperables:
- menos roturas;
- más estabilidad de velocidad;
- menos ajustes manuales;
- mejor MTBF;
- mejor OEE.

### 7.2. Auditoría de flujo y logística
Enfoque:
- salida de convertidora;
- WIP, buffer y routing;
- AMR, tridentes, transfer;
- logística hacia FG y consumo;
- sincronización de procesos.

Resultados esperables:
- reducción de starvation;
- menos bloqueos en salidas;
- más continuidad y previsibilidad;
- mejor salida a downstream;
- mejor servicio a FFG / segunda pasada / expedición.

### 7.3. Auditoría de organización y competencias
Enfoque:
- capacidad del mantenimiento;
- nivel operativo;
- seguridad;
- entrenamiento;
- seguimiento de protocolos;
- disciplina de la mejora.

Resultados esperables:
- menos errores operativos;
- mejor ajuste de máquinas;
- mejores tiempos de setup;
- mejor uso del personal;
- menos dependencias del “hombre clave”.

## 8. Base de datos de puntos clave para auditorías

### 8.1. Puntos técnicos críticos
- desalineación global;
- paralelismo incorrecto;
- rodillos no compensados;
- holguras en transmisión / rodamientos;
- mala posición de encuadernado / pre calentador;
- contacto no adecuado del papel;
- defectos de cliché, inks, plate curvature;
- problemas en splicer / waste system;
- equipos fuera de calibración.

### 8.2. Puntos de flujo crítico
- salida con congestión;
- WIP sin criterio de prioridad;
- buffer que convierten el problema en acumulación;
- falta de reserva de destino;
- transfer manual y no automatizado;
- no sincronización con AGV / AMR.

### 8.3. Puntos de gestión
- mantenimiento reactivo;
- falta de repuestos;
- ausencia de rutas preventivas;
- falta de supervisión de correcciones;
- falta de entrenamiento y estándares operativos;
- no seguimiento de OEE / bloqueos / calidad.

## 9. Metodología recomendada para President Container

### Fase 1 – Descubrimiento
- revisión del área de salida, WIP y entregas;
- análisis de flujo por máquina;
- time study de setup, paradas y bloqueos;
- identificación de single points of failure.

### Fase 2 – Medición
- medir OEE por línea, por turno y por tipo de pedido;
- cuantificar bloqueos, starvation, rehandling, setup y mermas;
- registrar eventos y tiempos por causa;
- realizar medición de capacidad con mix real.

### Fase 3 – Diagnóstico
- priorizar condiciones de mantenimiento y de flujo;
- mapear impacto del transporte, WIP, flejado y salida final;
- correlacionar tiempo perdido con modo de operación.

### Fase 4 – Diseño de mejora
- definir quick wins;
- definir cambios de control y logística;
- definir automatización necesaria para eliminar bloqueo del flujo;
- producir roadmap de inversión por fases.

### Fase 5 – Validación
- comprobación de OEE, throughput y disponibilidad;
- validación de mejoras con p50/p95 y p99 de bloqueo;
- revisión del plan con equipos de producción, mantenimiento y seguridad.

## 10. Conclusión

La auditoría INGECART debe ir más allá del “estado de la máquina”. Debe diagnosticar la capacidad real del sistema, la disciplina del flujo, la fuerza del mantenimiento y la calidad de la operación. La lección clave de los ejemplos mostrados es clara: los equipos pueden funcionar, pero si no se corrige la base del flujo y del mantenimiento, la pérdida de capacidad se replica en cada turno.

Por ello, para President Container, la auditoría debe generar una base de decisión no solo técnica, sino industrial y financiera, con foco en:

- flujo continuo;
- reducción de starvation y bloqueo;
- mejora de OEE y producción útil;
- gestión disciplinada del WIP;
- reducción de trabajo manual y de movimientos no productivos;
- palanca real para inversión automatizada y escalable.

## 11. Referencias de producto relevantes para la solución de flujo

- Automatic transfer / intralogistics transfer: https://senarzuniga.github.io/ingesite.github.io/solutions/intralogistics-automatic-transfer.html
- AMR intralogistics: https://senarzuniga.github.io/ingesite.github.io/solutions/amr-intralogistics.html
- Plug & Play palletizer: https://senarzuniga.github.io/ingesite.github.io/solutions/plug-play-palletizer.html
- Heavy duty palletizer: https://senarzuniga.github.io/ingesite.github.io/solutions/heavy-duty-palletizer.html
- RFID reel management: https://senarzuniga.github.io/ingesite.github.io/solutions/rfid-reel-management-system.html
- Ingetrans: https://senarzuniga.github.io/ingesite.github.io/solutions/ingetrans.html

## 12. Mandato de validación y evidencia

La auditoría debe seguir el principio de validación y evidencia:

- Cada hallazgo debe tener fuente o medición.
- Cada mejora debe tener KPI de salida.
- Cada hipótesis debe tener impacto estimado en OEE / output / seguridad / costo.
- Cada decisión debe dejar una base reutilizable para futuras auditorías.

Esto es lo que convierte una auditoría en un documento de decisión industrial, no solo en una lista de observaciones.
