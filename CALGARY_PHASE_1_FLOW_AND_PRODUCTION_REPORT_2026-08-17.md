# Calgary Fase 1: informe de flujo y producción

**Objetivo:** automatizar las salidas de primera pasada, el transfer norte-sur, los handoffs AGV y la salida FG sin cambiar el modelo de flujo.

## 1. Configuración

El WIP permanece al este y las convertidoras al oeste. McKinley RDC 66 x 130, Koppers RDC 49 y Ward conservan su alimentación y destino. La intervención sustituye tres salidas de rodillos manuales y un transfer empujado por operarios por:

- tres conveyors automáticos;
- un transfer car automático coordinado;
- routing por trabajo hacia FG miniline, Two-Piece o expedición;
- tridente sur de expedición;
- tridente intermedio para segunda pasada;
- tridente norte para WIP intermedio;
- Plug & Play en la salida FG donde sea compatible.

## 2. Mejora productiva

El principal beneficio no es aumentar la velocidad nominal de McKinley, Koppers o Ward. Es elevar su **velocidad sostenible** eliminando esperas de evacuación.

```text
RDC termina carga
-> conveyor confirma carga estable
-> WCS reserva transfer y destino
-> transfer se alinea y ejecuta handshake
-> carga va a segunda pasada, WIP o expedición
-> salida RDC queda libre y confirmada
```

Esto reduce blocked time, variación de ciclo y dependencia del operario. El WCS puede priorizar una orden urgente, proteger una máquina próxima a starvation o enviar a WIP cuando el destino esté ocupado.

## 3. Secuencia e interlocks

Una transferencia automática solo se autoriza cuando:

1. identidad y estado de carga son válidos;
2. destino tiene reserva y capacidad;
3. transfer está alineado dentro de tolerancia;
4. conveyors origen/destino están listos;
5. scanner y envolvente están libres;
6. freno y drives informan estado correcto;
7. ambos equipos aceptan el permiso de transferencia.

Ante fallo, el sistema debe parar de forma segura, conservar identidad/posición y ofrecer recuperación guiada. No se permite movimiento manual sin registrar override y reconciliar estado.

## 4. Tridentes y AGV

- **Sur:** expedición y carga/descarga AGV.
- **Centro:** intercambio entre transfer, segunda pasada y salida.
- **Norte:** WIP intermedio para FG y Two-Piece.

El tridente no es almacenamiento indefinido. Debe operar con capacidad, reserva, timeout y regla de desalojo. El AGV confirma misión, estación, carga y finalización antes de liberar el siguiente movimiento.

## 5. Plug & Play FG

La célula debe estabilizar conteo, interlayers, pallet y salida automática. Los valores 12 bundles/min, 1.200 x 1.200 x 2.300 mm y footprint 3 x 3 m se consideran datos de propuesta pendientes de FAT por familia SKU.

El aumento del 35% se acepta como hipótesis a comprobar. La prueba correcta compara:

- golpes buenos/h antes y después;
- blocked time por evacuación;
- setup y cambio de receta;
- disponibilidad de palletizer;
- producción vendible, no ciclos brutos.

## 6. Business case Fase 1

Valores brutos indicados:

- transfer/conveyors: CAD 320.000/año por 4 puestos equivalentes;
- salida FG: CAD 800.000/año por hasta 10 puestos equivalentes;
- objetivo de payback: <= 2 años.

Estado: **no confirmado**. Deben reconciliarse tareas de conteo, flejado, paletizado y transfer por turno; aplicar factor de realización; añadir CAPEX, OPEX y ramp-up; y evitar contar de nuevo esas tareas en Fase 3.

## 7. Prueba piloto y aceptación

Baseline mínimo de cuatro semanas representativas:

- clearance p50/p95 por cada RDC;
- blocked minutes y causas;
- starvation de FG/Two-Piece;
- toques manuales, viajes y rehandling;
- daños por pallet/carga;
- output bueno por SKU/turno.

FAT/SAT:

- matriz completa de tamaños y pesos;
- colisiones de peticiones simultáneas;
- prioridad urgente y cambio de destino;
- destino lleno, carga descentrada y sensor fallido;
- E-stop, pérdida de red/energía y restart;
- modo manual/degradado y reconciliación de inventario;
- capacidad sostenida con mezcla real.

## 8. Conclusión

Fase 1 es la intervención de mayor valor inmediato porque ataca la interfaz donde tres RDC comparten evacuación y decisión. Debe aprobarse como sistema de recuperación de capacidad y control de flujo, con el ahorro laboral como beneficio adicional condicionado a reconciliación financiera.
