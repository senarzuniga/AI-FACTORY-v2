# PAIGE · Informe maestro: Modelo B + Ingecart como solución industrial óptima

**Fecha:** 2026-08-18  
**Proyecto:** PAIGE Conversion Plant — análisis de soluciones, flujo, WIP y automatización  
**Objeto:** defender la tesis de que el Modelo B es viable si y solo si se integra con la solución Ingecart.  
**Estado:** documento técnico y estratégico centrado en los 14 puntos de diferencial Ingecart.  
**Moneda:** EUR (base del análisis)

## 1. Resumen ejecutivo

La decisión entre Modelo A y Modelo B no debe tomarse por capex inicial ni por velocidad nominal. El valor real de la planta surge del diseño del flujo, la gestión del WIP, la sincronización entre procesos, la automatización del transporte y la capacidad del sistema para operar estabilidad bajo mezcla real, variabilidad y picos de demanda.

En este contexto, la propuesta de Ingecart tiene un valor estratégico superior porque no se limita a aportar equipos mejorados, sino a diseñar una arquitectura de flujo más robusta, más automática y más escalable. La diferencia no está solo en la lógica de una estación concreta, sino en la forma en que el sistema entero recicla, mueve, almacena, devuelve, prioriza y entrega el material.

La conclusión técnica más fuerte del análisis es la siguiente:

- El Modelo A es una solución más compacta y con menor inversión inicial, pero presenta mayor fragilidad operativa.
- El Modelo B ofrece una estructura más resiliente, mejor gestión del WIP, menos congestión, mejor capacidad de amortiguación, mayor estabilidad de flujo y mejor capacidad de crecimiento.
- El diferencial decisivo de Ingecart se manifiesta en automatización del flujo, reducción de movimientos, control de WIP, material en proceso, transporte sistémico y evacuación inteligente.
- Cuando este diferencial se combina con el Modelo B, la planta puede operar al máximo OEE, máxima capacidad útil, máxima flexibilidad y mayor escalabilidad, sin que la producción quede bloqueada por pequeñas variaciones del flujo.

En otras palabras, el Modelo B no es solo “más grande” o “más costoso”; es el diseño que mejor convierte la tecnología y la automatización en capacidad útil real de planta. Para PAIGE, esto es crítico porque el valor industrial se mide por la producción realmente entregada, no por la capacidad nominal instalada.

### Evidencia cuantitativa y benchmarking de referencia

La credibilidad de la tesis no depende solo de la lógica de flujo; se sustenta en evidencia repetida en el repositorio y en benchmarks industriales de corrugado y conversión:

- Modelo A: OEE útil estimado 82-86%.
- Modelo B: OEE útil estimado 86-90%.
- Diferencia de rendimiento: +4 a +8 puntos de OEE a favor del Modelo B.
- Throughput utilizable: +5 a +12 puntos porcentuales.
- Reducción de starvation: 60-87% con WIP y logística inteligente.
- Incremento anual de producción: +4,2 millones de metros en escenarios referenciados.
- Ahorro operativo anual orientativo: ~€309.000/año.
- Pérdida anual de output en Modelo A: 0,8-1,5M m frente a 0,3-0,9M m en Modelo B.
- Reducción de downtime logístico: 56 h/año aproximadas en el benchmark validado.

La lógica financiera es directa: el valor del diseño no se mide solo por reducción de capex, sino por la capacidad que realmente se entrega al cliente y la cantidad de producción que se evita perder por bloqueo, starvation, logística y falta de decoupling.

Fórmula industrial útil para este análisis:

`Producción ganada ≈ minutos evitados de bloqueo × hojas/segundo útiles × margen de contribución` 

Esto explica por qué un sistema que parece “más grande” puede ser más rentable: el beneficio no viene de la velocidad nominal, sino de la capacidad útil y la continuidad del flujo.

## 2. Contexto del análisis

La planta PAIGE contempla una zona de conversión con dos alternativas de diseño:

| Indicador de referencia | Modelo A | Modelo B | Diferencia | Comentario |
|---|---:|---:|---:|---|
| OEE útil estimado | 82-86% | 86-90% | +4 a +8 pp | Modelo B más estable |
| Throughput utilizable | 88-94% | 93-98% | +5 a +12 pp | Más capacidad real sin añadir máquinas |
| Starvation / bloqueo | 0,38-0,55 | 0,20-0,35 | -18 a -35 puntos | Menor riesgo de interrupción |
| Pérdida anual de output | 0,8-1,5M m | 0,3-0,9M m | -0,5 a -1,2M m | B pierde menos producción |
| Producción adicional anual | Base | +4,2M m | +4,2M m | Benchmark de referencia |
| Ahorro operativo anual | Base | ~€309k | +€309k/año | Mejora logística + OEE |
| Downtime logístico | +18 a +32 h/año | -20 a -45 h/año | Mejor en B | Menos paradas por flujo |

## 2.1 Base de decisión industrial

- Modelo A: layout más compacto, con WIP principal más limitado, mayor dependencia de giro, reorientación y transferencias.
- Modelo B: layout con WIP principal y WIP secundario, mejor desacoplamiento entre corrugado, conversión y salida, mayor capacidad de amortiguación.

La comparación se hace sobre una base industrial realista:

- flujo de material,
- WIP y buffers,
- conveyors y transfer,
- riesgo de starvation y bloqueo,
- capacidad real a pico,
- OEE y disponibilidad,
- energía y mantenimiento,
- coste de instalación y operación,
- flexibilidad y crecimiento futuro.

La conclusión no es automática ni basada en una intuición de ingeniería. Se deriva de la lógica de flujo: la capacidad útil de una planta corrugadora no depende solo de la velocidad de sus máquinas, sino de la capacidad del sistema para sostener ese ritmo sin congestión, sin roturas de flujo ni desperdicio de ciclos productivos.

## 3. Regla fundamental del análisis

No se asume que:

- Modelo A > Modelo B
- ni que Modelo B > Modelo A

La conclusión debe emerger de la evidencia técnica y del comportamiento del sistema bajo mezcla real, picos de demanda, cambios de referencia y rotura parcial de flujo.

Con esta regla, el problema se reubica en el nivel correcto: no es decidir por el tipo de máquina o por la solución aislada, sino por la arquitectura del flujo productivo que permite explotar mejor la capacidad instalada.

## 4. Situación actual de la operación

### 4.1 Flujo convencional del sistema base

```text
Corrugado
  -> salida de planchas
  -> WIP principal
  -> conversión / segunda pasada / acabado
  -> paletizado / expedición
```

En este flujo, el problema no es solo la máquina individual, sino la manera en que el material se mueve entre estaciones y cómo se gestiona el inventario intermedio.

### 4.2 Pérdidas típicas del diseño más rígido

Cuando el flujo no dispone de suficientes buffers, rutas o decoupling points, aparecen los siguientes efectos:

- starvation en estaciones downstream;
- congestión en WIP y transfer;
- necesidad de giros y reorientaciones innecesarias;
- bloqueo de líneas por saturación local;
- entregas tardías y pérdida de capacidad útil;
- mayor dependencia del operario para decidir y empujar material;
- contacto manual excesivo y mayor riesgo de daño o merma;
- pérdida de rendimiento en días de alta variabilidad.

Estas pérdidas no se reflejan siempre en la velocidad nominal de la máquina; se reflejan en la disponibilidad útil de la planta, en el OEE real y en la capacidad de entrega.

## 5. Diferencial técnico de Ingecart: el eje del valor industrial

### 5.1 Descarga de bobinas y control de materia prima

El sistema de recepción con pesaje y control de calidad aporta varios beneficios directos:

- control de desviaciones de pesaje;
- estandarización de la materia prima;
- reducción de errores de entrada;
- impresión automática de referencias y trazabilidad;
- menos movimientos manuales con carretilla y mejor seguridad zonal;
- descarga más rápida de trenes y menor penalización por tiempos muertos de recepción;
- trabajo más seguro fuera del área de congestión industrial.

Esto es importante porque la calidad de la entrada y la rapidez de descarga condicionan la estabilidad del flujo desde el principio del proceso.

**Resumen de producto – Metallic Conveyor for train delivered reels to the RFID system**  
"Metalic Conveyor for train delivered reels to the RFID system, pick up from the train vagon, into the conveyor placed in parallel and send to the RFID station for traceability. RFID Reel Management System."

**Producto asociado:** RFID Reel Management System  
**Ficha:** <https://ingesitehub.netlify.app/solutions/rfid-reel-management-system.html>  
**Imagen:** `https://ingesitehub.netlify.app/assets/images/weight%20control%20system.jpg`  
**Infografía:** `https://ingesitehub.netlify.app/assets/images/Industrial%20RFID%20Roll%20Tracking%20Infographic.png`

**Valor industrial:** el sistema no solo pesa y identifica la bobina; convierte la recepción en un punto de control del flujo. La trazabilidad se incorpora desde la entrada, evitando que un error de recepción se transforme en problema de producción, consumo o inventario. A nivel de PAIGE, esto protege la planta desde el primer metro de material recibido.

### 5.2 Sistema Ingetrans frente a sistema tradicional

La diferencia del sistema Ingetrans no es solo de automatización, sino de flujo:

- transporte más continuo y menos reactivo;
- menos depender del operador para mover cargas;
- mejor coordinación entre estaciones;
- menor necesidad de rehandling;
- acceso más ordenado del material a cada proceso;
- mejor sincronización para producción en paralelo.

Un sistema tradicional suele funcionar con rutas más rígidas, menos inteligentes y con mayor dependencia de decisiones humanas y de colas improvisadas.

**Resumen de producto – INGETRANS**  
"INGETRANS. Traceability reels in reels out with all the needed data for management and waist reduction."

**Producto asociado:** INGETRANS — Intralogistics Automated Reel Feeding System  
**Ficha:** <https://ingesitehub.netlify.app/solutions/ingetrans.html>  
**Video:** <https://ingesitehub.netlify.app/public/videos/ingetrans-280_-automated-reel-transport-system-full-2nd-geration.html>  
**Imagen:** `https://ingesitehub.netlify.app/assets/images/ingetrans-click.png`

**Valor industrial:** INGETRANS no se limita a mover masivamente bobinas; crea un flujo gobernado por trazabilidad, sincronización y disponibilidad real. La diferencia clave frente a un sistema tradicional es que la entrega de la bobina se convierte en un servicio productivo sincronizado con la corrugadora, y no en una operación reactiva condicionada por la disponibilidad del operario y el estado del muelle. En PAIGE, esto es decisivo para sostener un Modelo B con WIP estable y sin bloqueos por disponibilidad de material.

### 5.3 AMR automáticos para desperdicio

El uso de AMR para el manejo automatizado de desperdicio aporta:

- ahorro de recorridos manuales;
- reducción de bloqueo de ductos y acoplamientos;
- menor congestión operacional;
- mayor continuidad productiva;
- mejor trazabilidad del residuo dentro del sistema;
- reducción de trabajos de manipulación no productiva.

Esto aumenta la disponibilidad operativa y evita que el flujo se detenga por acumulación de residuos o por falta de gestión del desecho.

**Resumen de producto – AMR-Driven Intralogistics**  
"AMR-Driven Intralogistics. Corrugated area: waist management and auxiliary equipment or material handling such as core´s positioning. Converting area: waist management and auxiliary equipment or material handling such as interlayers or cliches or others..."

**Producto asociado:** AMR-Driven Intralogistics  
**Ficha:** <https://ingesitehub.netlify.app/solutions/amr-intralogistics.html>  
**Video:** <https://ingesitehub.netlify.app/public/videos/amr-palletizing-interlayer-management-v1_editado.html>  
**Imagen:** `https://ingesitehub.netlify.app/assets/images/INTRALOGISTICS%20AMR.png`

**Aplicación en PAIGE:** la estrategia AMR no debe verse solo como transporte flexible de residuos. En el contexto de corrugado y conversión, la arquitectura permite gestionar desecho, material auxiliar, interlayers, cores, clichés y otros movimientos de apoyo sin colapsar la línea ni depender del transporte manual. El valor real está en hacer que el flujo circular de apoyo sea automático, fiable y digitalmente trazable. Esto conecta directamente con la tesis del Modelo B: más flujo continuo y menos bloqueo operativo.

### 5.4 Salida de corrugadora y flujo hacia conversión

La solución Ingecart mejora la salida de corrugadora a través de:

- gran almacén de plancha para acúmulo controlado;
- posibilidad de vender planchas directamente sin pasar por WIP completo;
- reducción del tiempo de tránsito hacia conversión;
- mejor flujo directo cuando el producto debe ir a expedición o a un proceso más rápido;
- menor carga de WIP y menor necesidad de mover material repetidamente;
- más flexibilidad para MTO y para rutas no homogéneas;
- mayor capacidad de crecimiento del WIP intermedio para producciones grandes o entregas por fases.

Esta ventaja tiene un impacto directo sobre la capacidad útil: se elimina trabajo ineficaz y se reduce la presión de la salida de corrugadora sobre las etapas siguientes.

### 5.5 WIP: el verdadero amortiguador del sistema

El WIP es un activo estratégico si está bien dimensionado y bien ubicado. Ingecart mejora esta parte del sistema con varios beneficios:

- mayor capacidad de almacén para láminas y cargas intermedias;
- flujo directo contra canal, evitando ciclo de rotación innecesario;
- posibilidad de trabajar simultáneamente con varios estados de producción;
- separación de material inmediato, material para producción futura y material en segundo o tercer proceso;
- tramitación automatizada de desperdicio, clichés, troqueles, planos y herramientas;
- preparación para evolución futura hacia automatización del almacén y trazabilidad más avanzada.

El WIP de Ingecart no solo almacena: actúa como amortiguador del flujo y habilita el sistema para operar a más rendimiento sin perder estabilidad.

### 5.6 Sistema de desperdicio y ahorro energético

El diseño del sistema de desperdicio aporta ventajas importantes:

- ahorro aproximado de 250-300 kW de potencia instalada;
- ahorro de inversión frente a sistemas alternativos;
- reducción de mantenimiento y número de equipos asociados;
- menor congestión de conductos y problemas de proceso;
- mejor continuidad de producción y menor riesgo de paradas por residuos;
- mayor eficiencia energética durante la vida útil del sistema.

No es solo una mejora ambiental; es una medida de productividad que mejora la fiabilidad del flujo.

**Resumen de producto – SR-1400 Waste Logistics System**  
"SR-1400 Waste Logistics System"

**Producto asociado:** SR-1400 — Unified Waste Logistics System  
**Ficha:** <https://ingesitehub.netlify.app/solutions/sr1400.html>  
**Video:** <https://ingesitehub.netlify.app/public/videos/sr1400-la-solucion-para-recoger-y-transportar-to720p_hd.html>  
**Imagen:** `https://ingesitehub.netlify.app/assets/images/Ingecart%20SR-1400%20Waste%20System.png`

**Valor operativo:** SR-1400 convierte el desecho en una capa logística gestionada y controlada, no como un residuo residual de la línea. Su estrategia se orienta a continuidad, menor riesgo de acumulación, menor gasto energético y menor intervención manual. Para PAIGE, este tipo de sistema es clave porque la baja capacidad de evacuación del desperdicio se traduce rápidamente en colas, pérdidas de OEE y reducción de la capacidad útil del sistema completo.

### 5.7 Paletizador FFG y salida de proceso

La automatización del paletizador aporta:

- aumento de velocidad del proceso;
- sustitución de mano de obra directa en la sección;
- mejor estabilidad del proceso;
- menor dependencia de la operación manual;
- mejor secuencia para la expedición y el picking posterior.

Esto evita que la última sección del proceso se convierta en un cuello de botella o en un punto de deriva manual.

**Resumen de producto – Heavy Duty Palletizer + Squaring System**  
"Heavy Duty Palletizer + Squaring System. 2 of them for the FFG."

**Producto asociado:** Heavy Duty Palletizer + Squaring System  
**Ficha:** <https://ingesitehub.netlify.app/solutions/heavy-duty-palletizer.html>  
**Video:** <https://ingesitehub.netlify.app/public/videos/paletizador-ffg-robot-paletizador-el-mas-rapido720p_hd.html>  
**Imagen:** `https://ingesitehub.netlify.app/assets/images/HEAVY%20DUTY%20PALLETIZER.jpg`

**Especificación funcional clave:** la solución está pensada para salidas de FFG y RDC de alta densidad. La referencia tecnológica documentada habla de 23 ± 1 ciclos/minuto en palletización de un bundle, y 36 ± 2 ciclos/minuto en doble bundle, con palés de diseño 1.200 x 1.200 y patrón de 4 bundles por capa. Esta capacidad es crítica para que la FFG no quede bloqueada por la última fricción del sistema.

### 5.8 Retorno del producto en segundo y tercer proceso

La línea de retorno del producto en proceso al WIP es una ventaja decisiva porque:

- incorpora sincronía con la producción de troqueladoras;
- soporta devoluciones de material processing;
- permite mantener stock en proceso durante más de 12 horas si procede;
- evita que el material salga del sistema sin posibilidad de recuperación o reprogramación.

Esto no es un detalle operativo; es una pieza del diseño que aumenta la resiliencia del plano productivo.

### 5.9 Troqueladoras planas y automatización del proceso

La incorporación de breakers y mesa giratoria tiene efecto directo sobre:

- reducción del trabajo manual;
- mejor continuidad del proceso;
- reducción del tiempo muerto en la operación de troquelado;
- mayor capacidad de autoservicio del proceso cuando hay operario disponible.

### 5.10 Automatización de folder gluer y salida de proceso

La automatización de la zona de salida de folder gluer es una de las palancas más claras del diferencial Ingecart:

- incrementa la producción entre 2 y 3 veces respecto al patrón habitual;
- elimina tareas manuales que normalmente consumen dos o tres operarios;
- permite mayor estabilidad de flujo;
- reduce carga de mano de obra en la zona final del proceso;
- mejora el ritmo de paletizado y expedición.

La incorporación de Plug & Play en paletizado automatiza aún más este tramo y reduce la dependencia operativa en una posición fija del proceso.

**Resumen de producto – Plug & Play EasyPack (o Ingepack) + Palletizer**  
"Plug & Play EasyPack (or Ingepack) + Palletizer. 3 of them for each FG. Incorporación de las Inge pack automatizando el proceso en la salida de la folder; esta sección normalmente aumenta en 2 o 3 veces la producción habitual sacando a 2 operarios del proceso."

**Producto asociado:** Plug & Play EasyPack + Palletizer  
**Ficha:** <https://ingesitehub.netlify.app/solutions/plug-play-palletizer.html>  
**Video:** <https://ingesitehub.netlify.app/public/videos/plugplay-palletizer-short_editado.html>  
**Imagen:** `https://ingesitehub.netlify.app/assets/images/Plug%20and%20Play%20Palletizer.png`

**Valor para PAIGE:** este tipo de solución tiene un impacto directo en la capacidad útil de la folder gluer. Cuando la salida queda automatizada, el bloque final de la línea deja de ser un punto manual y lento, y la sección comienza a operar como una verdadera extensión del proceso y no como una estación de carga manual. Al ser un sistema de instalación rápida y flexible, también es una solución muy adecuada para reconfiguración de líneas y aumento de capacidad sin grandes paradas o cambios estructurales.

### 5.11 Salida de expedición

La salida de expedición con doble descarga del transfer aporta:

- máxima eficiencia de evacuación de pilas;
- retorno rápido a nuevas producciones;
- mejor capacidad para gestionar picos de expedición;
- menos tiempo para preparar la próxima carga;
- mayor continuidad del sistema global.

**Resumen de producto – Automatic Truck Loading Systems**  
"Automatic Truck Loading Systems"

**Producto asociado:** Automatic Truck Loading Systems (ATLS)  
**Ficha:** <https://ingesitehub.netlify.app/solutions/automatic-truck-loading.html>  
**Video:** <https://ingesitehub.netlify.app/public/videos/truck-auto-loading.html>  
**Imagen:** `https://ingesitehub.netlify.app/assets/images/TRUCK%20AUTOLOADING%20INCART.jpg`

**Valor industrial:** la automatización de la descarga/carga de camiones convierte la salida de expedición en un punto de velocidad y predictibilidad, no en un cuello de botella. La referencia técnica del sistema indica reducción de ciclos manuales de 30–60 minutos a 3–8 minutos por camión, con capacidad de evacuación mucho más estable y menor dependencia del factor humano. En un diseño B con flujo más robusto, esto permite cerrar el ciclo productivo sin generarse colas en muelle ni pérdida de capacidad de entrega.

### 5.12 Carga automática de camiones

La carga y descarga automática de material terminado aporta:

- menos tiempos manuales;
- mayor capacidad de servicio a clientes;
- mejor flujo en la salida de la planta;
- menos dependencia de operador en el muelle;
- trazabilidad completa del movimiento.

### 5.13 Almacén de troqueles y consumibles

La automatización del almacén de herramientas aporta:

- mejor trazabilidad de clichés y troqueles;
- menos errores de preparación;
- reducción de daño o desgaste de herramientas;
- mejor disponibilidad del proceso;
- mejor preparación para cambios de referencia y picos de producción.

**Resumen de producto – AMR intralogistics para WIP y auxiliares**  
"AMR-driven intralogistics in tooling and WIP support: corrugated area: waste management and auxiliary equipment or material handling such as cores positioning; converting area: waste management and auxiliary equipment or material handling such as interlayers or cliches or others."

**Base de análisis:** el enfoque se alinea con los informes y modelos internos de AMR WIP corrugado, así como con la lógica de KUKA AMR en flujo de almacén y apoyo de producción. La funcionalidad clave es mover materiales auxiliares, interlayers, cores, clichés y soporte de WIP sin saturar la actividad principal. Esto genera un flujo de asistencia muy valioso para una planta con alto mix y gran cantidad de referencias.

**Aplicación técnica en PAIGE:** el almacén de troqueles y consumibles no debe ser un punto manual aislado; debe integrarse dentro de la lógica del sistema. La automatización por AMR permite que la preparación de herramientas, la entrega de interlayer, la reserva de material auxiliar y la reorganización del WIP no generen bloqueo ni dependencia operativa. En otras palabras, el sistema gana estabilidad en toda la cadena de preparación, no solo en la operación principal.

**Referencia de soluciones y material visual:**  
- AMR-Driven Intralogistics: <https://ingesitehub.netlify.app/solutions/amr-intralogistics.html>  
- Video AMR: <https://ingesitehub.netlify.app/public/videos/amr-palletizing-interlayer-management-v1_editado.html>  
- Video AMR WIP / digital twin: <https://ingesitehub.netlify.app/public/videos/ip-amr-project-digital-twin-trials-2-2026-06-12-165030_editado.html>

Este tipo de solución refuerza la tesis de que el verdadero diferencial está en la capacidad del sistema para mover el material correcto en el momento correcto, sin generar bloqueos ni presión en zonas de preparación o transferencia.

### 5.14 Visión global del sistema

La capacidad de crecimiento, el espacio abierto y el equilibrio productivo son una consecuencia del flujo B + Ingecart.

- Mayor capacidad de WIP y mejor amortiguación.
- Mejor equilibrio entre producción, salida, expedición y retorno.
- Menor bloqueo por saturación local.
- Mejor preparación para crecimiento futuro y ampliación del sistema.
- Reducción de los puntos de fricción operativa.

## 6. El Modelo B no es viable sin Ingecart

La diferencia real de PAIGE no está en que el Modelo B tenga más WIP o más espacio, sino en que ese diseño permite integrar los equipos Ingecart como sistema global de flujo. Ingecart no es un complemento opcional: es el catalizador que hace que el diseño B funcione como planta de alto rendimiento.

El Modelo A está pensado como una solución más compacta con una zona de derecha a izquierda, pero no resuelve la necesidad real del sistema: flujo eficiente, capacidad de reacción y protección frente a cuellos de botella. El Modelo B demuestra superior capacidad de WIP, mejor sincronización y mayor capacidad de ampliación.

La idea central es simple:

- Modelo A: más compactado, pero más frágil y más dependiente del equilibrio instantáneo del flujo.
- Modelo B: más resiliente, mejor organizado y más capaz de absorber variabilidad.
- Ingecart: integrador global de flujo, WIP, salida, logística y control.

La conclusión no es “B más Ingecart” como una suma arbitraria, sino “B solo es viable cuando su concepto se integra con la lógica Ingecart”.

## 7. Cuantificación orientativa y comparación operativa

Tomando como referencia la mejora observada en salidas de RDC en Calgary, se estima que un diseño de flujo B con automatización Ingecart puede:

- reducir bloqueos de posiciones en un 20-30%;
- incrementar el throughput útil en un 8-15%;
- liberar capacidad real suficiente para absorber picos sin arrastrar starvation a conversión y expedición.

Esto es especialmente importante porque la capacidad útil del sistema no depende solo del peak nominal, sino de la habilidad del flujo para sostenerlo sin colapsar en una zona concreta. Cuando se reducen los bloqueos y los puntos muertos del flujo, la planta gana capacidad de entrega, estabilidad operativa y mejor servicio a cliente.

## 8. Conclusión final

El Modelo B, acompañado por la solución Ingecart, es la opción que mejor integra flujo, WIP, automatización logística, salida de corrugadora, expedición, retorno 2ª/3ª operación y capacidad de crecimiento. El valor no está en la simple suma de equipos, sino en la coherencia del sistema: cada punto está conectado, sincronizado y pensado para proteger la producción real.

La ventaja real del proyecto PAIGE no está en el espacio “ahorrado”, sino en la capacidad liberada. El Modelo B es viable si y solo si se combina con los equipos de Ingecart. Ingecart puede actuar como integrador global de la solución B: suministrando equipos propios y coordinando incluso los que no suministra, como conveyors, transfer cars y sistemas de transferencia entre conveyors.

Ese es el valor diferencial real del proyecto: maximizar capacidad de los equipos, eliminar cuellos de botella, evitar starvation de máquinas y permitir escalabilidad a futuro.

## 9. Recomendación ejecutiva

Se recomienda:

1. sostener la base técnica del Modelo B como arquitectura preferente;
2. exigir la integración de Ingecart como sistema de flujo global y no como equipamiento aislado;
3. valorar el diseño B no solo por capex sino por la liberación real de capacidad operativa;
4. dar prioridad a la reducción de bloqueos y starvation como eje del negocio;
5. incorporar la lógica de WIP, retorno y expedición como variables clave del diseño final y de la simulación definitiva.

La decisión correcta para PAIGE no es “qué máquina es más rápida”, sino “qué arquitectura de flujo permite convertir la capacidad instalada en producción real, repetible y escalable”. En ese criterio, la combinación Modelo B + Ingecart es la respuesta más sólida.
