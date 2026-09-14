Agent is idle (waiting for messages). agent_id: rtls-bench, agent_type: research, status: idle, description: Benchmarks públicos RTLS UWB, elapsed: 375s, total_turns: 1, model: gpt-5.6-terra

[Turn 0]
## Corte de evidencia — acceso: 2026-09-14

**Criterio:** cifras de fabricantes y casos comerciales se reportan como **hechos publicados**, no como resultados garantizados ni auditorías independientes.

### 1) UWB industrial: precisión, refresco y método

- **Pozyx — hecho publicado:** UWB ofrece **10–30 cm** de precisión; otra página de producto anuncia “hasta 10 cm” para sus tags/sistema. No localicé una tasa de refresco numérica pública general ni evidencia actual verificable para atribuirle los modos **2.5D/3D** solicitados.  
  Fuente: https://www.pozyx.io/technology/rtls-explained — **Pozyx**, s.f.; acceso 2026-09-14.  
  Fuente: https://www.pozyx.io/products/hardware/hardware-tags — **Pozyx**, s.f.; acceso 2026-09-14.

- **Sewio — hecho publicado:** precisión de hasta **30 cm / 1 ft**. En **TDoA**, el tag emite un *blink* y los anchors sincronizados envían marcas temporales al servidor; Sewio lo presenta como más escalable y favorable para batería. En **TWR**, se mide el tiempo de ida/vuelta; no exige sincronización de relojes, pero requiere intercambios secuenciales y Sewio lo describe como menos escalable y más exigente para batería.  
  Fuentes: https://www.sewio.net/uwb-technology/ — **Sewio Networks**, 2016-04-13, modificado según metadatos; acceso 2026-09-14.  
  https://www.sewio.net/uwb-technology/time-difference-of-arrival/ — **Sewio Networks**, s.f.; acceso 2026-09-14.  
  https://www.sewio.net/uwb-technology/two-way-ranging/ — **Sewio Networks**, s.f.; acceso 2026-09-14.

- **Sewio — hecho publicado:** sus tags incluyen barómetro para detectar altura/eje **Z**; no confirmé la denominación concreta “Z beta”. Un caso Volkswagen publica **50 cm** y refresco de **333 ms**, dato de ese despliegue, no especificación universal.  
  Fuentes: https://www.sewio.net/uwb-tags/ — **Sewio Networks**, s.f.; acceso 2026-09-14.  
  https://www.sewio.net/customer-projects/volkswagen/ — **Sewio Networks**, s.f.; acceso 2026-09-14.

- **Eliko KIO / AP-TWR — hecho publicado:** Eliko declara precisión fiable de **30 cm ±20 cm** en entornos complejos. AP-TWR hace que un anchor participe activamente en el ranging y otros escuchen pasivamente, evitando transmisiones adicionales. Publica hasta **75 Hz**, o **320 Hz** para un caso pequeño de 50 × 50 m; son capacidades condicionadas, no una tasa garantizada para cualquier planta.  
  Fuente: https://eliko.tech/elikos-active-passive-twr-protocol-explained/ — **Eliko**, s.f.; acceso 2026-09-14.

- **Eliko — corrección importante:** “más de **2.500 m²** de espacio abierto” corresponde a una configuración de **cuatro anchors**, no a cobertura por anchor.  
  Fuente: https://eliko.tech/product-new-kio-rtls/ — **Eliko**, s.f.; acceso 2026-09-14.

- **Qorvo/Decawave — hecho publicado verificable indirecto:** Pozyx confirma que su Developer Tag usa el **DW1000**. Eliko refiere que Decawave promocionaba **10 cm** a largo alcance con línea de vista; no debe confundirse con precisión garantizada de un almacén. No pude verificar una cifra primaria pública específica para **DW3000**.  
  Fuentes: https://www.pozyx.io/products/hardware/tags/developer-tag — **Pozyx**, s.f.; acceso 2026-09-14.  
  https://eliko.tech/kio-rtls-micro-positioning/ — **Eliko**, s.f.; acceso 2026-09-14.

**Inferencia para bobinas:** el rango 10–30 cm es una referencia de proveedor, no una tolerancia de diseño asegurada en un almacén de bobinas. Metal, apilado, humedad, geometría, NLoS y ubicación del tag justifican *radio survey* y piloto con bobinas reales. Eliko reconoce degradación por metal, multipath y NLoS.  
Fuente: https://eliko.tech/real-engineering-challenges-of-deploying-uwb-at-scale/ — **Eliko**, s.f.; acceso 2026-09-14.

### 2) omlox

- **Hecho publicado:** omlox es un estándar abierto de localización promovido por **PI (Profibus & Profinet International)**. Define interfaces para **omlox core zone** y **omlox hub**: la Core Zone permite interoperabilidad UWB en una zona; el Hub mapea/expone datos de distintas tecnologías.  
  Fuente: https://omlox.com/ — **omlox / PI**, s.f.; acceso 2026-09-14.

- **Versión:** la documentación pública identifica **Core Zone Specification v2**, basada en IEEE 802.15.4z, UL-TDoA y canal UWB 9. No confirmé una única “versión vigente” equivalente para todas las partes Hub/API.  
  Fuente: https://omlox.com/omlox-explained/omlox-core-zone-and-air-interface/omlox-core-zone-specification-v1-vs-v2 — **omlox / PI**, s.f.; acceso 2026-09-14.

- **Adopción — hecho publicado:** PI indica que más de **60 empresas** aportaron experiencia y soluciones a omlox. No equivale a 60 instalaciones productivas certificadas.  
  Fuente: https://www.profibus.com/technologies/omlox — **PI**, s.f.; acceso 2026-09-14.

- **Pozyx — hecho publicado:** su Platform usa omlox Hub y puede converger UWB, 5G, RFID, Wi‑Fi, BLE y GPS mediante APIs e integración ERP/MES/WMS.  
  Fuente: https://www.pozyx.io/products/software/location-and-sensor-hub — **Pozyx**, s.f.; acceso 2026-09-14.

### 3) Casos publicados de beneficio

| Caso y fuente | Hecho publicado por el proveedor |
|---|---|
| Toyota Motor Manufacturing CZ / Sewio + Asseco CEIT | Información de inventario de **8 h a 1 s**; stock de seguridad de **8 a 4 h (−50%)**; **18.000 h-persona/año** liberadas; retorno declarado en dos años. https://www.sewio.net/customer-projects/toyota-motors/ — **Sewio Networks**, caso de implantación 2018; acceso 2026-09-14. |
| Budweiser Budvar / Sewio | Sustitución de RFID pasivo con **80% uptime** por UWB con **99% uptime**; Sewio atribuye **+19%** de utilización virtual del almacén. https://www.sewio.net/budweiser-budvar-replaces-rfid-powered-forklift-tracking-with-sewio-rtls-to-achieve-99-of-system-uptime-and-cut-down-maintenance-costs/ — **Sewio Networks**, 2019-02-06; acceso 2026-09-14. |
| Bora Italia / Sewio | **−25%** tiempo de inventario; **0 errores de picking durante tres meses**; **−15%** tiempo de picking; **+10%** utilización de almacén. https://www.sewio.net/customer-projects/bora/ — **Sewio Networks**, s.f.; acceso 2026-09-14. |
| SEG Automotive / Sewio | En PoC: **100%** de registros correctos frente a **95%** con RFID; plazo de **6 h a 3 h (−50%)**. https://www.sewio.net/customer-projects/seg-automotive/ — **Sewio Networks**, s.f.; acceso 2026-09-14. |
| Bosch Termotecnologia Aveiro / Eliko | En piloto, potencial para optimizar **un operario por turno**; requisito <50 cm y 1 Hz para más de 20 vehículos; Eliko declara precisión mejor de 50 cm. No publica ROI porcentual. https://eliko.tech/case-study/vechicle-tracking-drives-efficiency-at-bosch/ — **Eliko**, s.f.; acceso 2026-09-14. |

**Ausencia de evidencia:** no localicé una fuente pública primaria verificable de Pozyx/ArcelorMittal con una cifra de ROI; no debe citarse un porcentaje.

### 4) Batería y coste

- **Hecho publicado:** Sewio declara **3–5 años** según refresco, perfil RF y canal; en el caso SEG publica **1,5 años** a refresco de **0,5 s** con batería mayor.  
  Fuentes: https://www.sewio.net/uwb-tags/ — **Sewio Networks**, s.f.; acceso 2026-09-14.  
  https://www.sewio.net/customer-projects/seg-automotive/ — **Sewio Networks**, s.f.; acceso 2026-09-14.

- **Hecho publicado:** Eliko publica para su Tag RTLS 2.0 **cuatro semanas a 1 actualización/s** y **seis meses a 1 actualización/min**.  
  Fuente: https://eliko.tech/eliko-uwb-rtls-tag/ — **Eliko**, s.f.; acceso 2026-09-14.

- **Coste:** no encontré un precio público robusto y comparable de **tag UWB industrial por unidad**. Sewio indica lista de precios bajo solicitud. No conviene extrapolar precios de kits, prototipos o trackers genéricos a tags industriales para bobinas.

### 5) Benchmarks para papel/corrugado

- **Voith — hecho publicado:** OnCare.pmPortal registra automáticamente datos de rolls y fabrics; su ID tagging combina tecnologías radio sin contacto y placas digitales. Los tags se pueden leer con smartphone/app “independientemente del estándar tecnológico”, para historial, mantenimiento y trazabilidad. Es identificación/tracking de activos de máquina de papel, no prueba de RTLS UWB de bobinas de materia prima.  
  Fuente: https://www.voith.com/corp-en/145426.html — **Voith**, s.f.; acceso 2026-09-14.

- **Valmet — hecho publicado:** en APRIL Kerinci, Valmet Asset Manager reúne datos de rollos en una plataforma web y se presenta como apoyo a visibilidad, decisiones y mantenimiento de rolls. Tampoco se identifica como UWB/RFID de almacén de bobinas.  
  Fuente: https://www.valmet.com/search/?q=%22APRIL%22%20%22Kerinci%22%20roll — **Valmet**, s.f.; acceso 2026-09-14.

- **MTorres / TorresFactory:** no encontré una publicación primaria verificable que permita atribuir a MTorres una función RTLS concreta ni métricas de TorresFactory. Debe quedar como dato pendiente, no como benchmark probado.

**Inferencia:** RFID/ID tagging es apropiado para identidad y lectura por evento; UWB añade coordenada y estado casi continuo. Son tecnologías potencialmente complementarias: RFID para identidad/lote y UWB para posición operacional.

### 6) Normativa UE

- **ETSI EN 302 065:** la parte **EN 302 065-2 V2.1.1** trata aplicaciones UWB de localización/tracking; debe verificarse la versión armonizada citada en el Diario Oficial aplicable al producto y fecha de comercialización.  
  Fuente: https://www.etsi.org/deliver/etsi_en/302000_302099/30206502/02.01.01_60/en_30206502v020101p.pdf — **ETSI**, V2.1.1; acceso 2026-09-14.

- **RED:** Directiva **2014/53/UE**, marco para salud/seguridad, compatibilidad electromagnética y uso eficiente del espectro de equipos radioeléctricos.  
  Fuente: https://eur-lex.europa.eu/eli/dir/2014/53/oj — **Parlamento Europeo y Consejo**, 2014-04-16; acceso 2026-09-14.

- **Límites UWB:** la Decisión de Ejecución (UE) **2024/1467**, de 27-05-2024, fija para LT1 en **6–8,5 GHz** una PSD media máxima de **−41,3 dBm/MHz e.i.r.p.** y potencia pico máxima de **0 dBm e.i.r.p.** (ventana de 50 MHz). Para dispositivos de potencia mejorada en interior de radiodeterminación/localización/tracking en esa banda: **−31,3 dBm/MHz** y **10 dBm**, bajo las condiciones de su anexo.  
  Fuente: https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=OJ:L_202401467 — **Comisión Europea**, 2024-05-27; acceso 2026-09-14.

- **Precaución:** el resumen de Sewio expresa el cambio como dBm/**Hz**; el texto legal usa dBm/**MHz**. Para ingeniería de cumplimiento deben utilizarse las tablas y condiciones de la Decisión, no la unidad del blog.  
  Fuente: https://www.sewio.net/what-the-new-uwb-eu-regulation-mean-for-the-world-of-rtls/ — **Sewio Networks**, 2024-06-27; acceso 2026-09-14.