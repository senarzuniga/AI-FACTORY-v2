# Calgary Fase 3: informe Ingetrans, WIP automático y AMR

**Objetivo:** coordinar digitalmente los flujos existentes de WIP, conversión, salidas FFG y expedición mediante WCS y flota móvil.

## 1. Alcance

- Ingetrans como capa de orquestación del transporte;
- WIP direccionable y movimientos AMR;
- AMR en salidas FFG y engomadora semi-automática;
- tridentes y estaciones de pickup/drop;
- integración ERP/APS-MES/WMS-WCS-fleet manager-PLC;
- prioridades, tráfico, charging, excepciones y degraded mode;
- simulación para dimensionar flota y buffers.

## 2. Mejora del flujo

La fase no crea una nueva ruta productiva. Hace que las rutas actuales sean solicitables, reservables y trazables.

```text
demanda prevista de máquina
-> WCS selecciona carga compatible
-> reserva destino y estación
-> fleet manager asigna AMR
-> pickup con handshake
-> entrega y confirmación de ubicación
-> MES/WMS actualiza estado
```

Esto permite pre-staging, prioridad urgente, recuperación ante ruta bloqueada y uso no lineal del WIP. La línea recibe el material correcto antes de agotarlo y la salida se evacua antes de bloquearla.

## 3. WIP automático

Beneficios a validar:

- +30% de capacidad equivalente por mejor ocupación de suelo;
- +25% de altura de pallet donde estabilidad, producto y seguridad lo permitan;
- menor tiempo de búsqueda y envejecimiento;
- trazabilidad de orden, SKU, pallet y ubicación;
- menos movimientos exploratorios y rehandling;
- flujo por prioridad/due date en lugar de FIFO físico rígido.

La capacidad no se acepta por porcentaje global. Debe calcularse con posiciones válidas, envolvente, altura segura, accesibilidad, mix y ocupación máxima permitida.

## 4. Salidas FFG y mantenimiento

AMR puede evacuar de forma modular sin extender conveyor fijo a todos los destinos. Esto:

- libera espacio de trabajo;
- facilita acceso de mantenimiento;
- reduce MTO futuro asociado a transportadores rígidos;
- permite adaptar frecuencia de pickup al mix;
- acelera evacuación de engomadora semi-automática;
- separa mejor tráfico de producción y carretillas.

No todo conveyor debe eliminarse. Los tramos de alta frecuencia y recorrido estable pueden seguir siendo más eficientes. La decisión se toma por misiones/h, distancia, disponibilidad y coste de ciclo de vida.

## 5. Seguridad y resiliencia

- zoning y rutas segregadas donde sea posible;
- scanners y safe speed por contexto;
- estaciones con presencia, identidad e interlocks;
- gestión de tráfico y deadlock;
- charging sin comprometer cobertura de flota;
- ruta alternativa o buffer seguro ante estación caída;
- procedimientos para pérdida de red, WCS o fleet manager;
- recovery sin perder inventario lógico;
- capacidad degradada definida y ensayada.

## 6. Hipótesis de propuesta

- 9 puestos equivalentes x CAD 80.000 = CAD 720.000/año bruto;
- reducción mínima de 1-2 hojas dañadas por pallet;
- reducción de carretillas y tiempo de carretilla;
- incremento de almacenamiento equivalente y altura indicados arriba.

Los 9 puestos no se suman a fases 1/2 hasta reconciliar tareas. Las hojas evitadas requieren pallets/año, coste por hoja, incidencia por SKU y evidencia antes/después.

## 7. Dimensionamiento por simulación

Inputs:

- matriz origen-destino y distancias;
- misiones/h p50/p95 por franja;
- tiempo de carga/descarga y handshake;
- velocidad cargado/vacío;
- disponibilidad, charging y mantenimiento;
- bloqueos de ruta y cruces;
- políticas de prioridad y WIP;
- picos, cambio de turno y contingencias.

Outputs:

- número de AMR y utilización;
- request-to-delivery p50/p95;
- colas por estación;
- riesgo de starvation/blocking;
- energía y charging;
- throughput degradado con un AMR/estación fuera de servicio.

## 8. KPIs y liberación

- logística-caused starvation;
- misión p50/p95 y success without intervention;
- fleet utilization y charging availability;
- WIP accuracy, age y search time;
- deadlocks y recovery time;
- movimientos manuales desplazados;
- hojas dañadas/pallet;
- near misses e incursiones;
- degraded-mode throughput.

Fase 3 se libera después de usar datos reales de Fase 1, simular alternativas y aprobar risk assessment. El número inicial de AMR no debe fijarse por benchmark genérico.

## 9. Conclusión

Fase 3 convierte automatizaciones locales en un sistema de flujo integral. Su mayor valor es coordinar prioridades, WIP y transporte para sostener producción; la reducción de personal y conveyors debe tratarse como consecuencia validada, no como único criterio de diseño.
