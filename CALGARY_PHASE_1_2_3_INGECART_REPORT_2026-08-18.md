# Calgary · Informe ampliado Fase 1 + Fase 2 + Fase 3 · Ingecart

**Fecha:** 2026-08-18  
**Proyecto:** Cascades Calgary, sección de conversión de cartón corrugado  
**Objeto:** defender la viabilidad y el valor industrial de la automatización Ingecart en el flujo de conversión, con foco en Fase 1, Fase 2 y Fase 3  
**Estado:** propuesta técnica y financiera con base en benchmark, lógica de flujo y datos de productividad  
**Moneda:** CAD / USD (conversiones orientativas)

## 1. Resumen ejecutivo

La zona de conversión de Calgary tiene un cuello de botella muy concreto: la salida de las tres convertidoras (McKinley, Koppers y Ward) y el posterior transfer manual de salida que hace de pivote entre conversion, segunda pasada y expedición. El problema no es la velocidad nominal de la máquina, sino la capacidad útil del flujo: cuando las salidas no se evacuan a tiempo, la RDC queda bloqueada, la segunda pasada se queda sin trabajo y la expedición pierde continuidad.

La solución Ingecart no es solo una mejora de una estación aislada. Es una capa operativa que hace tres cosas a la vez:

1. reduce la dependencia del operario;
2. restaura el flujo de salida antes de que aparezca el bloqueo;
3. convierte WIP, transfer, tridentes, AMR y paletización en un sistema sincronizado por software.

En términos de rendimiento, la evidencia del repositorio y de benchmarks del mismo sector apunta a una mejora real de producción y OEE cuando el flujo se desacopla del empuje manual:

- OEE útil del Modelo B / flujo automatizado: +4 a +8 puntos frente a un diseño más rígido
- OEE en escenario con WIP y logística inteligente: +6 puntos como benchmark de referencia
- Reducción de starvation: 60-87%
- Producción adicional anual: +4,2 millones de metros en escenarios referenciados
- Ahorro operativo anual orientativo: ~€309.000/año

Para Calgary, la combinación de transfer car automático, tridentes, AMR, Plug & Play y Ingetrans ofrece una mezcla especialmente potente porque permite operar como un sistema unificado: salida de RDC, disponibilidad de segunda pasada, almacenamiento intermedio, carga de AGV y evacuación de terminado sin “ruido” manual.

## 2. Contexto técnico del proyecto Calgary

El flujo base del proyecto se mantiene igual: WIP a la derecha, conversión a la izquierda, transfer vertical de sur a norte que recoge el WIP y lo entrega a las tres convertidoras:

- McKinley RDC 66" x 130"
- Koppers RDC 49"
- Ward

Tras pasar por esas tres máquinas, cada salida manual y aislada se concentra en un transfer manual y empujado por operarios, que se mueve de sur a norte y alimenta:

- FG miniline
- Automatic Two-Piece Folder Gluer & Stitcher Inline Machine
- o expedición directa

El nuevo diseño reubica el diseño funcional en un modelo integrado:

- tres salidas automáticas y coordinadas bajo un mismo software de gestión;
- transfer car automático gestionado por WCS/PLC;
- tridentes para intercambio con AGV/AMR;
- WIP intermedio para segunda y tercera operación;
- Plug & Play en salida FG o en zonas de paletizado;
- Ingetrans para flujo de material y trazabilidad;
- AMR para WIP y evacuación de mercancía.

La diferencia crucial es que las salidas ya no compiten a ciegas por el mismo punto de transferencia. Ahora el software reserva destino, valida capacidad y estabiliza flujo antes de mover cualquier carga.

## 3. Fortalezas de producto de Ingecart (en el proyecto Calgary)

### 3.1 Transfer car / shuttle transfer

**Resumen de producto:** Transfer car (carro transferidor / lanzadera) para mover cargas de forma segura, ordenada y sincronizada entre la salida de la RDC y el siguiente punto del flujo.

**Fortalezas funcionales:**

- elimina la dependencia operativa directa en el transfer manual;
- desacopla la salida de la RDC del ritmo del operador;
- reduce tiempo de empuje, posicionamiento, rehandling y esperas;
- garantiza reserva de destino antes de mover la carga;
- mejora la disponibilidad del equipo upstream.

**Datos típicos del equipo:**

- carga máxima: 3.000-5.000 kg
- velocidad de traslación: 1,5-2,5 m/s
- velocidad de rodillos: 0,3-0,5 m/s
- ancho útil: 1.800-2.800 mm
- longitud útil: 3.000-5.500 mm
- altura de transporte: 300-450 mm
- precisión de parada: ±2 a ±5 mm

**Valor industrial:** este equipo convierte la salida de la RDC de un punto de congestión a un punto controlado. Al hacerlo, no solo se gana velocidad: se gana estabilidad de flujo y menos riesgo de bloqueo.

### 3.2 Tridentes para intercambio con AGV/AMR

**Resumen de producto:** tridentes automáticos para carga/descarga, intercambio y servicio a AGV/AMR, con interlocks de seguridad y compatibilidad con transfer y WIP.

**Fortalezas funcionales:**

- permiten la coordinación entre AGV y flujo fijo;
- resuelven la entrega/recepción de cargas sin decisiones manuales;
- reducen MTO y movimientos de carretilla elevadora;
- estabilizan el flujo entre WIP intermedio, FG y expedición;
- facilitan el crecimiento futuro del sistema sin cambiar la lógica base.

**Valor industrial:** si el WIP y la expedición se convierten en un servicio automatizado, entonces la convertidora ya no se “siente” la presión de la logística externa.

### 3.3 AMR para WIP y para salidas de FFG

**Resumen de producto:** AMR para almacenamiento intermedio, WIP flexible y evacuación de producto terminado.

**Fortalezas funcionales:**

- aumenta la capacidad de almacenamiento en 2º y 3º proceso aprox. +60% según escenario;
- mejora el uso del suelo y la altura de almacenamiento del pallet;
- disminuye el número de trabajos manuales en transfer y depósito;
- reduce desperdicio por manipulación, “pata de elefante” y daños por rehandling;
- mejora trazabilidad y flujo productivo no lineal.

**Datos clave recogidos del proyecto:**

- Aumento de capacidad almacenaje en 2º y 3º procesos: aprox. +60%
- Aumento de altura de palets: +25%
- Reducción de 3 operarios que mueven palets/transfer por 3 turnos = 9 personas
- ahorro directo estimado: 9 x 80.000 = 720.000 USD/año
- reducción de material dañado: 1-2 hojas por palet frente a 3-5 hojas actuales
- reducción del MTO en conveyors no productivos

**Valor industrial:** AMR permite que el WIP deje de ser un almacenamiento rígido y pasivo para convertirse en un activo dinámico de capacidad.

### 3.4 Plug & Play / Ingepack / paletización compacta

**Resumen de producto:** paletizador Plug & Play con salida automática, interlayers, corrección de patrón y salida de palets compacta.

**Datos funcionales aportados:**

- 12 bundles/min – estable – con interlayers y salida automática
- pallet hasta 1.200 x 1.200 x 2.300 mm
- bundle size: 250 x 250 a 700 x 900 mm
- footprint aproximado: 3 x 3 m

**Fortalezas funcionales:**

- aumenta producción en FG en un 35% mínimo en una media productiva razonable;
- sustituye mano de obra directa en paletizado y flejado
- reduce la congestión de la salida final;
- mejora consistencia del pallet y la calidad del envío;
- permite sincronizar la producción FG con la del sistema de RDC.

**Ahorro operativo estimado:**

- 2 operarios por sección + 1 por paletizado x 4 turnos = 10 personas
- 10 x 80.000 = 800.000 USD/año
- ROI potencial: 1 año si se mide solo ahorro de mano de obra y sin contar el incremento de capacidad

**Valor industrial:** el Plug & Play no es solo una mejor máquina; es la pieza que evita que la última parte del proceso convierta la planta en una isla de congestión.

### 3.5 Ingetrans

**Resumen de producto:** INGETRANS, con trazabilidad de bobinas y flujo bidireccional, integración con ERP-WMS y manejo de la entrada de material en sincronía con la producción.

**Fortalezas funcionales:**

- mejora la disponibilidad de producción con cambios rápidos;
- reduce tiempos de carretilla, MTO y búsqueda;
- mejora seguridad al sacar el trabajo manual del área de operación;
- permite WIP y flujo más disciplinado con trazabilidad del material;
- habilita control central de prioridad y canalización del flujo.

**Datos económicos aportados:**

- presupuesto orientativo: 1.350.000 USD

**Valor industrial:** Ingetrans hace que el material “entre” al sistema en el momento adecuado y con la identidad correcta, lo que reduce pérdida de velocidad y mejora continuidad.

### 3.6 AMR de WIP y de desperdicio

**Resumen de producto:** AMR para intralogística, gestión de residuos, interlayers, cores y apoyo a WIP en procesos medios / terceros.

**Fortalezas funcionales:**

- reduce esfuerzos manuales de transporte no productivo;
- evita bloquear la línea con exceso de residuos o materiales auxiliares;
- mejora la capacidad de gestión del WIP entre procesos;
- tres valores complementarios: continuidad, trazabilidad y flexibilidad.

**Datos del proyecto:**

- Sistema AMR WIP: 950.000-1.100.000 USD
- mejora del almacenamiento y la colocación del material
- reducción de operación manual y de MTO
- reducción de desperdicio por manipulación y ajuste de palets

**Valor industrial:** cada coche AMR no es un “vehículo” aislado; es la forma de mantener abierta la ruta productiva sin crear cuellos de botella en los recorridos de apoyo.

**Gestión de WIP con AMR:** el enfoque de WIP móvil y dinámico se basa en la idea de evitar que el almacén intermedio se convierta en un bloqueador del proceso principal. En la práctica, la gestión con AMR logra: reasignar pallets y soportes por prioridad, reducir esperas por posición vacía, liberar la línea principal de movimiento no productivo y mantener la continuidad del flujo en entornos de alta variabilidad. Esto concuerda con la lógica técnica del informe KUKA AMR WIP Corrugated Technical Report: la mejora no está solo en mover material, sino en mantener flujo, disponibilidad y OEE.

## 4. Fase 1 — actualización funcional y económica

### 4.1 Alcance actualizado

Fase 1 se concentra en el cuello de botella inmediato de Calgary y para ello incorpora:

- transfer car automático de salida de las tres RDC;
- conveyors automáticos y coordinados en la salida de cada RDC;
- routing por prioridad, destino y disponibilidad;
- tridentes para intercambio con AGV/AMR;
- WIP intermedio de segunda/tercera operación;
- Plug & Play en la salida de FG donde la matriz sea compatible;
- coordinación de señales y reservas por software (WCS/flow orchestrator);
- mejora de trazabilidad y control de bloqueos.

### 4.2 Mejora operativa prevista

- reducción de minutos bloqueados por salida manual;
- evacuación antes de que aparezca el bloqueo;
- disminución del starvation de FG y Two-Piece;
- aumento de velocidad sostenible de cada RDC;
- mejor separación entre producción y logística;
- reducción del trabajo manual y menor dependencia del operario;
- mejor acceso para AGV/AMR y reducción del MTO total.

### 4.3 KPI objetivo Fase 1

- OEE útil: +3 a +6 puntos en la zona de salida/transfer
- tiempo de bloqueo por salida: -40% a -65%
- starvation de segunda pasada: -50% a -80%
- tiempos de rehandling: -30% a -50%
- dependencias manuales: -60% a -80%
- disponibilidad del sistema: +8% a +15% por reducción del bloqueo logístico

### 4.4 Impacto económico Fase 1

| Concepto | Base estimada | Comentario |
|---|---:|---|
| Transfer car y conveyors | 1.000.000-1.500.000 USD | depende de longitud, número de puntos y tareas |
| Tridentes / AGV interchange | 250.000-500.000 USD | integración y control |
| Plug & Play FG (si aplica) | 200.000 USD | presupuesto orientativo |
| Ahorro operativo anual | 320.000-1.120.000 USD | mano de obra + menor bloqueo + mayor producción |
| ROI target | 12-24 meses | solo si se validan tareas reales y no hay doble conteo |

**Nota importante:** Si se contabiliza el ahorro de mano de obra en Fase 1 y luego en Fase 2, debe hacerse reconciliación por puesto/turno/área; el mismo “operario” no puede duplicarse entre fases.

## 5. Fase 2 — paletización Plug & Play

### 5.1 Alcance

- EMBA: plug & play compact y automático
- Martin: plug & play compact y automático
- integración con WCS
- salida automática de pallets y trazabilidad

### 5.2 Resultado esperado

- consistencia del patrón y del ritmo
- menor bloqueo en la última etapa del proceso
- menor trabajo no productivo en paletización
- mayor capacidad de salida sin crear congestión
- mejor coordinación con AMR/Ingetrans 

### 5.3 KPI objetivo Fase 2

- producción (pallets) estable: +20% a +35%
- mano de obra directa: -1 operario/turno por línea
- reducción de rework: -30% a -50%
- disponibilidad de salida: +10% a +20%

### 5.4 Ahorro anual estimado Fase 2

- 1 operario x turno x 4 turnos = 4 personas por línea
- 4 x 80.000 = 320.000 USD/año por línea
- si se aplican dos líneas, ahorro bruto orientativo: 640.000 USD/año

## 6. Fase 3 — orquestación integral Ingetrans + AMR + WIP automático

### 6.1 Alcance

- Ingetrans con trazabilidad y flujo sincronizado
- WIP automático con AMR
- AMR salidas FFG y engomadora semi-automática
- prioridad dinámica, routing, tráfico y gestión de excepciones
- integración ERP/APS/MES/WMS/PLC/Fleet Manager

### 6.2 Resultado esperado

- +30% capacidad almacenamiento equivalente por mejor uso del suelo
- +25% altura de palets donde se permita
- reducción de MTO en conveyor y transfer
- prácticamente eliminación de trabajo manual de reubicación
- reducción de material dañado y de hojas desperdiciadas
- mejor disponibilidad general de producción y menor dependencia de la experiencia del operario

### 6.3 KPI objetivo Fase 3

- OEE total del tramo: +6 pp como benchmark orientativo
- starvation logístico: -60% a -87%
- reducción de movimientos no productivos: -40% a -70%
- productividad útil: +5% a +12%
- tiempo de búsqueda y reubicación: -50% a -80%
- trazabilidad total: 100% de cargas con ID, destino y movimiento

### 6.4 Ahorro anual estimado Fase 3

| Concepto | Estimación |
|---|---:|
| AMR WIP | 950.000-1.100.000 USD |
| Ingetrans | 1.350.000 USD |
| reducción de tareas manuales | 720.000 USD/año |
| reducción de desperdicio / hojas dañadas | 100.000-300.000 USD/año |
| beneficio neto total orientativo | 1.5M-2.5M USD/año según alcance final |

## 7. Business case y prevención de doble conteo

La clave del business case no es sumar todos los “ahorros” de cada fase sin distinguir tareas, turnos, áreas y fechas. La regla debe ser estricta:

- cada puesto ahorrado debe ser analizado por turno y por sección;
- cada mejora debe asignarse a una tarea concreta y no a varias simultáneamente;
- si un operador se suprime por transfer, no puede contarse también por Plug & Play;
- la mejora de OEE y throughput debe medirse sobre resultados reales del flujo y no sobre capacidad nominal;
- el ROI debe compararse contra Capex confirmada, mantenimiento, software y soporte.

La evidencia de retorno se basa en tres dimensiones visibles:

1. recuperación de capacidad productiva: menos bloqueos, menos falta de destino, menos rehandling y más continuidad de flujo;
2. mejora de OEE: +3 a +6 puntos netos en el tramo de conversion/logística, con reducción del starvation del 60% al 87%;
3. productividad operativa: más metros útiles por turno, mejor servicio a FG y segunda pasada, menor daño de material y menos trabajo no productivo.

Indicadores de referencia:

- OEE útil del tramo: +3 a +6 pp
- reducción de starvation logístico: -60% a -87%
- producción adicional anual: +4,2 millones de metros
- ahorro operativo anual orientativo: ~€309.000/año
- retorno estimado: 12-24 meses según alcance final, integración y validación de tareas reales

Con esta disciplina, la propuesta de Calgary es económica y estratégica, porque mejora el flujo sin redefinir todo el proceso. El mayor valor no es sustituir trabajo manual por automatización aislada, sino recuperar capacidad y ganancia de rendimiento en el flujo completo, donde la logística y el WIP dejan de ser un freno y se convierten en una capa productiva.

## 8. Conclusión

La automatización de Calgary no debe presentarse como “más maquinaria” sino como una solución de flujo. El valor real aparece cuando:

- las salidas de las RDC dejan de depender del empuje manual;
- el transfer legaliza rutas y destinos por software;
- el WIP deja de ser un cuello y se convierte en una mejor capa de servicio;
- el AMR y el tridente dejan de ser logística de apoyo y pasan a ser parte del sistema productivo;
- la paletización se vuelve repetible, consistente y de alta disponibilidad;
- Ingetrans conecta material, trazabilidad y sincronización con la operación real.

La tesis de mejora industrial para Calgary es clara: el proyecto vale la pena cuando la automatización se utiliza para eliminar bloqueos antes de que ocurran, no para reaccionar después. Eso es lo que hace sostenible la mejora de producción, OEE y ROI.

## 9. Referencias de producto y activos visuales (públicos)

- https://senarzuniga.github.io/ingesite.github.io/#solutions
- https://senarzuniga.github.io/ingesite.github.io/assets/images/weight%20control%20system.jpg
- https://senarzuniga.github.io/ingesite.github.io/assets/images/Industrial%20RFID%20Roll%20Tracking%20Infographic.png
- https://senarzuniga.github.io/ingesite.github.io/assets/images/ingetrans-click.png
- https://senarzuniga.github.io/ingesite.github.io/assets/images/INTRALOGISTICS%20AMR.png
- https://senarzuniga.github.io/ingesite.github.io/assets/images/Ingecart%20SR-1400%20Waste%20System.png
- https://senarzuniga.github.io/ingesite.github.io/assets/images/HEAVY%20DUTY%20PALLETIZER.jpg
- https://senarzuniga.github.io/ingesite.github.io/assets/images/Plug%20and%20Play%20Palletizer.png
- https://senarzuniga.github.io/ingesite.github.io/assets/images/TRUCK%20AUTOLOADING%20INCART.jpg

Estos enlaces son estables fuera del portátil y permiten presentar las soluciones de forma consistente en cualquier entorno.
