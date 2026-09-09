# Especificación Técnica del Sistema Ingetrans
## Datos Validados - v1.0.0

**Fecha de validación:** 2026-09-01T10:58:05.543+02:00  
**Estado de validación:** VALIDADO  
**Estado de aprobación:** APROBADO  
**Departamento responsable:** Ingeniería

---

## 1. Descripción General del Sistema

### 1.1 Tipo de Sistema
- **Clasificación:** Superficie
- **Descripción:** Sistema de carreta de transferencia guiada por riel con pistas de carrete fijo dedicadas
- **Aplicación:** Transferencia de carretes en líneas de producción industrial

### 1.2 Especificaciones de Diseño
El sistema Ingetrans es un sistema de transporte automatizado diseñado para mover carretes de material entre estaciones de trabajo utilizando rieles guía fijos y tecnología de control industrial.

---

## 2. Parámetros Operacionales

### 2.1 Velocidad de Transferencia
| Parámetro | Valor | Unidad | Estado |
|-----------|-------|--------|--------|
| **Valor nominal de referencia** | 80 - 100 | m/min | Activo |
| **Nota importante** | Valor final sujeto a layout aprobado y zonas de seguridad | - | - |

**Especificaciones:**
- Velocidad mínima: 80 m/min
- Velocidad máxima: 100 m/min
- Velocidad nominal recomendada: 90 m/min
- La velocidad final será determinada durante la aprobación del layout y considerando todas las zonas de seguridad

### 2.2 Velocidad de Pista
| Parámetro | Valor | Unidad | Estado |
|-----------|-------|--------|--------|
| **Valor nominal de referencia** | 12 - 19 | m/min | Activo |
| **Tipo** | Velocidad de movimiento de rieles | - | - |

**Especificaciones:**
- Velocidad mínima: 12 m/min
- Velocidad máxima: 19 m/min
- Velocidad nominal recomendada: 15.5 m/min
- Esta velocidad corresponde al movimiento de las pistas de carrete fijo

### 2.3 Aceleración/Desaceleración
| Parámetro | Valor | Unidad | Estado |
|-----------|-------|--------|--------|
| **Rampa de aceleración** | 1.5 | segundos | Activo |
| **Rampa de desaceleración** | 1.5 | segundos | Activo |

**Especificaciones:**
- Tiempo de aceleración desde parada hasta velocidad nominal: 1.5 segundos
- Tiempo de desaceleración desde velocidad nominal hasta parada: 1.5 segundos
- Perfil de aceleración: Lineal (sujeto a verificación en comisionamiento)

### 2.4 Operación de Recogida/Entrega
| Parámetro | Valor | Unidad | Estado |
|-----------|-------|--------|--------|
| **Tiempo de acción de transferencia** | 6 | segundos por interfaz | Activo |
| **Aplicabilidad** | Cada punto de recogida o entrega | - | - |

**Especificaciones:**
- Tiempo requerido para operación de recogida: 6 segundos
- Tiempo requerido para operación de entrega: 6 segundos
- Total estimado por interfaz: 6 segundos
- Incluye: posicionamiento, enganche, desenganche, y retiro de carrete

---

## 3. Especificaciones Físicas del Carrete

### 3.1 Envolvente del Carrete
| Parámetro | Valor Máximo | Unidad | Estado |
|-----------|--------------|--------|--------|
| **Diámetro** | 1,500 | mm | Activo |
| **Ancho/Largo** | 2,800 | mm | Activo |
| **Peso** | 3,500 | kg | Activo |

**Notas importantes:**
- Todas las dimensiones están sujetas a la matriz de carrete final aprobada
- Los carretes deben cumplir con las tolerancias de fabricación especificadas
- El peso incluye el carrete vacío más carga máxima

### 3.2 Limitaciones y Restricciones
- Los carretes que superen las especificaciones anteriores requerirán re-diseño del sistema
- Se debe validar equilibrio y centro de gravedad antes de operación
- Carretes deformados o dañados no pueden ser transportados

---

## 4. Sistema de Control

### 4.1 Arquitectura de Control
| Componente | Especificación | Estado |
|-----------|----------------|--------|
| **Tipo de arquitectura** | PLC industrial / arquitectura HMI | Activa |
| **Controlador principal** | PLC industrial | Activo |
| **Panel de interfaz** | HMI industrial | Activo |

### 4.2 Comunicación Industrial
| Parámetro | Especificación | Estado |
|-----------|----------------|--------|
| **Protocolo principal** | PROFINET | Activo |
| **Comunicación alternativa** | Comunicaciones industriales estándar | Activa |
| **Señales de interfaz** | Definidas durante fase de ingeniería | Pendiente de definición |

**Especificaciones técnicas:**
- Sistema de control: PLC (Programmable Logic Controller) industrial
- Interfaz de operario: HMI (Human Machine Interface) industrial
- Comunicación en tiempo real: PROFINET
- Velocidad de comunicación: Compatible con tiempos de ciclo de 100 ms o mejor
- Todas las señales de interfaz serán documentadas en detalle durante la fase de ingeniería y comisionamiento

### 4.3 Puntos de Integración
- Conexión a sistemas MES existentes (Manufacturing Execution Systems)
- Integración con sistemas de seguimiento de producción
- Interfaces de comunicación según estándares industriales

---

## 5. Requisitos de Seguridad

### 5.1 Componentes de Seguridad Requeridos
| Componente | Descripción | Estado |
|-----------|-------------|--------|
| **Funciones de PLC de seguridad** | Control de seguridad programable | Activo |
| **Escáneres de área** | Detectores de presencia de personal y obstáculos | Activo |
| **Bloqueos de seguridad** | Interlocks en puntos de acceso | Activo |
| **Paro de emergencia** | Botones de parada de emergencia | Activo |
| **Acceso protegido** | Barreras físicas y control de acceso | Activo |

### 5.2 Estándares de Cumplimiento
- **ISO 13849-1:** Seguridad de maquinaria - Partes de sistemas de control relacionadas con la seguridad
- **ISO 13850:** Sistemas de parada de emergencia
- **EN 61800-5-2:** Variadores de frecuencia - Requisitos de seguridad (si aplica)
- **Regulaciones locales:** Según jurisdicción de instalación

### 5.3 Evaluación de Riesgos
- Evaluación de riesgo final según metodología de seguridad (ISO 12100)
- Niveles de Integridad de Seguridad (SIL) serán determinados durante análisis de riesgos
- Certificación de seguridad requerida antes de comisionamiento
- Auditoría de seguridad anual recomendada

### 5.4 Características de Seguridad Específicas
- **Escáneres de seguridad:** Monitoreo continuo de área de operación
- **Paro de emergencia:** Accesible desde múltiples ubicaciones, accionamiento inmediato
- **Bloqueos:** Impiden acceso durante operación, requieren reinicio manual después de activación
- **Monitoreo:** Sistema de diagnóstico automático de fallas

---

## 6. Especificaciones de Instalación y Comisionamiento

### 6.1 Requerimientos Pre-Instalación
- Inspección de infraestructura de rieles
- Verificación de especificaciones eléctricas
- Calibración de sensores
- Pruebas de aislamiento eléctrico

### 6.2 Procedimiento de Comisionamiento
1. Instalación física de componentes
2. Conexión eléctrica e industrial
3. Programación del PLC con parámetros validados
4. Pruebas de funcionalidad sin carga
5. Pruebas con carretes de referencia
6. Validación de velocidades y tiempos
7. Pruebas de seguridad completas
8. Certificación y cierre de comisionamiento

### 6.3 Documentación Requerida
- Planos de instalación aprobados
- Diagramas de cableado
- Programación del PLC documentada
- Procedimientos operacionales
- Manual de mantenimiento
- Registro de pruebas de comisionamiento

---

## 7. Mantenimiento y Operación

### 7.1 Intervalos de Mantenimiento Recomendados
- **Inspección visual:** Diariamente (antes de inicio de turno)
- **Limpieza de pistas:** Semanalmente
- **Lubricación de rieles:** Mensualmente
- **Calibración de sensores:** Trimestralmente
- **Revisión completa del sistema:** Anualmente

### 7.2 Parámetros Operacionales en Servicio
- Monitoreo continuo de velocidades
- Registros de tiempos de ciclo
- Alertas de anomalías
- Logs de eventos de seguridad

### 7.3 Procedimientos de Parada de Emergencia
- Procedimiento de activación clara y documentada
- Reinicio requiere confirmación de personal autorizado
- Inspección obligatoria después de cada parada de emergencia

---

## 8. Consideraciones de Seguridad Adicionales

### 8.1 Zonas de Peligro
- Zona de transferencia de carrete (requiere acceso controlado)
- Zona de movimiento de pistas (requiere monitoreo continuo)
- Puntos de alimentación/entrega (requiere señalización clara)

### 8.2 Restricciones de Acceso
- Solo personal autorizado y capacitado
- Requiere certificación de operario
- Procedimientos de bloqueo/etiquetado (LOTO) para mantenimiento

### 8.3 Capacitación Requerida
- Operación del sistema
- Procedimientos de emergencia
- Mantenim

iento preventivo
- Solución básica de problemas

---

## 9. Control de Cambios y Validación Continua

### 9.1 Registro de Cambios
Cualquier modificación a estos parámetros debe:
1. Ser documentada formalmente
2. Ser aprobada por Ingeniería
3. Ser re-validada según estos estándares
4. Ser comunicada a todos los usuarios del sistema

### 9.2 Revisión Periódica
- Revisión de parámetros: Anualmente o cuando hay cambios significativos
- Auditoría de seguridad: Anualmente
- Validación de cumplimiento: Tras cambios de legislación

### 9.3 Escalabilidad
Si se requieren modificaciones operacionales o de seguridad:
- Se debe realizar análisis de impacto
- Se requiere re-certificación de seguridad
- Se debe documentar en esta especificación

---

## 10. Anexos

### Anexo A: Glosario de Términos
- **PLC:** Programmable Logic Controller (Controlador Lógico Programable)
- **HMI:** Human Machine Interface (Interfaz Hombre-Máquina)
- **PROFINET:** Protocolo industrial de comunicación en tiempo real
- **SIL:** Safety Integrity Level (Nivel de Integridad de Seguridad)
- **LOTO:** Lockout/Tagout (Bloqueo y Etiquetado)
- **MES:** Manufacturing Execution Systems (Sistemas de Ejecución de Manufactura)

### Anexo B: Referencias Normativas
- ISO 12100:2010 - Seguridad de la maquinaria
- ISO 13849-1:2015 - Partes de sistemas de control relacionadas con la seguridad
- ISO 13850:2015 - Sistemas de parada de emergencia
- EN 61800-5-2:2016 - Variadores de frecuencia
- Regulaciones locales de seguridad industrial

### Anexo C: Información de Contacto
- **Departamento de Ingeniería:** [Por definir]
- **Soporte técnico:** [Por definir]
- **Coordinador de seguridad:** [Por definir]

---

**Documento preparado por:** Sistema de Validación de Datos Ingetrans  
**Fecha de última actualización:** 2026-09-01  
**Versión:** 1.0.0  
**Clasificación:** Especificación Técnica Validada
