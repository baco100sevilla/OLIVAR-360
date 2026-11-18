# 🫒 OLIVAR 360°

**Análisis del sector oleícola andaluz (2020–2026)**  
*Portfolio de Data Analytics y Business Intelligence · Power BI · Python · SQL/DAX*

> **Estado:** Dashboard de cuatro páginas terminado y revisado visual y funcionalmente (noviembre de 2026). La auditoría de fuentes, supuestos y cálculos se documenta por separado; no debe interpretarse como certificación externa.

## Objetivo

Explorar cómo la variabilidad climática, la producción, los precios y la estructura de costes se relacionan con la situación económica del sector oleícola andaluz; añadir contexto de comercio internacional mediante las importaciones españolas de aceite de oliva desde Túnez.

**Ámbito:** ocho provincias andaluzas, campañas 2020/21–2025/26, y comercio por año natural 2020–2026 (2026 provisional). No se confunden campañas agrícolas con años naturales.

## Dashboard: cuatro páginas

| Página | Contenido |
|---|---|
| 01 · Panorama del sector | Producción regional y provincial, precios de referencia, tendencias y variaciones interanuales. |
| 02 · Costes y rentabilidad | Costes estimados €/kg, escenarios, márgenes estimados y simulador de volumen. |
| 03 · Clima, cosecha y precios | Precipitación, días de calor, producción y gráficos descriptivos de dispersión. |
| 04 · Competitividad del olivar | Importaciones españolas desde Túnez, valor unitario comercial y costes técnicos estimados de Andalucía. |

## Capturas

*Incorporar capturas propias del informe Power BI, sin incluir datos privados ni interfaces de edición.*

| Panorama | Costes | Clima | Competitividad |
|---|---|---|---|
| [Ver captura](imagenes/01_panorama.png) | [Ver captura](imagenes/02_costes.png) | [Ver captura](imagenes/03_clima.png) | [Ver captura](imagenes/04_competitividad.png) |

> Las imágenes están pendientes de añadir a la carpeta `imagenes/`. Los enlaces funcionarán cuando se guarden esos archivos con los nombres indicados.

## Hallazgos ilustrativos

- Producción de aceite 2025/26: **978.508,70 t**, dato provisional; variación interanual mostrada en el dashboard: **−14,75 %**.
- Precio de referencia 2025/26: **3,9233 €/kg**; es la **media simple de los precios provinciales disponibles**, no un precio medio ponderado de transacciones.
- En 2024/25, seis tipologías del escenario de costes andaluz `DINAMICO_PROXY` muestran entre **1,56 y 5,40 €/kg**; **no** son costes reales observados.
- Importaciones españolas desde Túnez: **54.265 t** (2024) y **64.697 t** (2025), aproximadamente **+19,2 %**. El valor unitario pasa de **6,99 a 3,62 €/kg**, aproximadamente **−48,2 %**. Los dos años están etiquetados como provisionales en la fuente utilizada.
- En análisis agroclimático exploratorio, la asociación dentro de provincia entre lluvia anual antecedente y logaritmo de producción tuvo **r = +0,655**. La asociación no demuestra causalidad y **no corresponde directamente al scatter de valores absolutos del dashboard**.

## Metodología y cautelas

Leer [docs/METODOLOGIA.md](docs/METODOLOGIA.md), [docs/RESULTADOS_Y_LIMITACIONES.md](docs/RESULTADOS_Y_LIMITACIONES.md) y [docs/DICCIONARIO_BASICO.md](docs/DICCIONARIO_BASICO.md).

- Separación entre **aceituna agrícola**, **aceite producido**, **precios**, **costes estimados**, **series climáticas** y **comercio exterior**.
- Modelo dimensional de Power BI, con dimensiones de campaña, territorio y tipología; `FactComercioTunez` emplea año natural independiente.
- El coste de producción tunecino **no puede inferirse** a partir del valor unitario de importación; tampoco puede atribuirse una pérdida económica andaluza a esas importaciones con la evidencia disponible.
- Los datos de clima están sujetos a cobertura y controles de calidad; la cobertura de estaciones no equivale a representatividad de superficie de olivar.
- Los umbrales de temperatura y la escala de los porcentajes deben verificarse en el diccionario de la fuente y en las medidas DAX antes de la publicación definitiva.

## Tecnologías

Power BI Desktop, Power Query, DAX, Python/Pandas, pruebas automatizadas, Visual Studio Code y Git/GitHub.

## Reproducibilidad y acceso a los datos

El informe se construyó sobre archivos y scripts locales de trabajo. **Este paquete publica documentación, no todos los datos originales ni un `.pbix` verificado.** Si se decide añadir código, datos autorizados o una versión publicable del PBIX, se revisarán licencias, procedencia, privacidad y tamaño antes de subirlos.

## Autoría y licencia

Proyecto de portfolio personal. **Licencia de código pendiente de decidir**: no se presupone autorización para redistribuir datasets de terceros ni se atribuye al usuario una licencia aún no elegida.
