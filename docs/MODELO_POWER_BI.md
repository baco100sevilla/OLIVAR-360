# Modelo Power BI · OLIVAR 360°

[Volver al proyecto](../README.md) · [Guía de Python](../scripts/README.md) · [Metodología](METODOLOGIA.md)

Documentación técnica del modelo `OLIVAR_360_Simulador`. Fecha de cierre documental: **19/11/2026**.

## Alcance y evidencia

La auditoría verificada de referencia registra **42 tablas, 62 relaciones y 40 objetos de medida, uno sin expresión**. Una consulta de solo lectura a los metadatos del motor de la copia abierta `OLIVAR_360_Simulador_CORRECCION_TIPOS`, realizada para esta documentación, confirma esos recuentos y permite describir relaciones y expresiones reales. La coincidencia de recuentos no demuestra que ambas versiones sean idénticas ni valida los valores de la corrección decimal.

Se distinguen tres niveles de evidencia:

- **Comprobado en esta revisión:** inventario y expresiones del motor consultado mediante `TMSCHEMA_TABLES`, `TMSCHEMA_RELATIONSHIPS`, `TMSCHEMA_COLUMNS` y `TMSCHEMA_MEASURES`; páginas del PBIX guardado leídas sin modificarlo; capturas y documentación del repositorio.
- **Documentado previamente:** fuentes, granularidad de negocio, reglas de preparación y ejemplos de resultados de la [metodología](METODOLOGIA.md), el [diccionario](DICCIONARIO_BASICO.md) y los [resultados y limitaciones](RESULTADOS_Y_LIMITACIONES.md). No se repitieron sus pruebas de negocio.
- **Pendiente:** agregación de lluvia multiprovincial y validación final de la corrección decimal. Recuperar una expresión o comprobar un tipo declarado no equivale a conciliar sus resultados con la fuente.

El diseño inicial de 19 tablas de negocio y 40 relaciones y la maqueta histórica Astra corresponden a entregas anteriores. No describen por sí solos el estado del simulador actual.

## Las cuatro páginas de presentación

| Página | Contenido y filtros | Interpretación y captura |
| --- | --- | --- |
| 01 · Panorama del sector | Producción de aceite, precio de referencia, variaciones entre campañas, evolución histórica y ranking provincial. Selección de campaña para los KPI. | Producción en t; precio provincial medio simple en €/kg. Las series pueden conservar todas las campañas. [Captura 01](../imagenes/01_panorama.png). |
| 02 · Costes y rentabilidad | Campaña, tipología, escenario y volumen de aceite en t; precio, coste, margen unitario y margen total simulado. | Costes estimados y resultados hipotéticos. La captura usa 10 t; el ejemplo de 20 t en resultados es otro escenario. [Captura 02](../imagenes/02_costes.png). |
| 03 · Clima, cosecha y precios | Campaña y provincia; precipitación, calor, producción, dispersión por provincia-cosecha y evolución de lluvia/precio. | Hasta 48 provincia-cosechas; el scatter usa valores absolutos. No representa directamente la correlación ajustada dentro de provincia. [Captura 03](../imagenes/03_clima.png). |
| 04 · Competitividad del olivar | Año natural de comercio, importaciones españolas desde Túnez, valor unitario y costes andaluces por tipología en 2024/25. | España–Túnez y Andalucía tienen ámbitos y periodos distintos. El año comercial no cambia automáticamente la campaña de costes. [Captura 04](../imagenes/04_competitividad.png). |

Las cuatro páginas de presentación del PBIX guardado tienen lienzo de 1920 × 1080. El archivo contiene además dos páginas ocultas: `VALIDACIÓN SIMULADOR` y `AUD · Validación sectorial`. Son auxiliares; no se cuentan como páginas de presentación ni prueban por su mera existencia que todas las validaciones estén cerradas.

En comercio, el comportamiento documentado sin selección de año agrega 2020–2026 en KPI, mientras los históricos muestran 2020–2025. Deben leerse siempre el filtro y la provisionalidad.

## Inventario del modelo

| Grupo | Cantidad | Tablas |
| --- | ---: | --- |
| Dimensiones de negocio | 8 | `DimTerritorio`, `DimCampana`, `DimAno`, `DimCultivo`, `DimTipologia`, `DimTrimestreCampana`, `DimEscenario`, `DimFuente`. |
| Hechos | 12 | Los once hechos del núcleo dimensional más `FactComercioTunez`; detalle en la sección de granularidad. |
| Dataset de análisis | 1 | `dataset_analitico`. |
| Contenedor de medidas | 1 | `tabla medidas DAX`. |
| Parámetro del simulador | 1 | `Volumen aceite t`. |
| Calendarios automáticos ocultos | 19 | 18 tablas `LocalDateTable_…` y una plantilla `DateTableTemplate_…`. |
| **Total** | **42** | **23 tablas visibles y 19 ocultas.** |

Los 40 objetos de medida se distribuyen así: 38 en `tabla medidas DAX`, uno en `DimAno` y uno en `Volumen aceite t`. El objeto `'tabla medidas DAX'[Medida]` no tiene expresión: hay **39 expresiones disponibles**, no 40 KPI operativos certificados. La ubicación de una medida en una tabla no crea una relación ni determina su contexto de filtro.

## Granularidad, unidades y aditividad

Los granos siguientes describen la semántica documentada de cada tabla; esta revisión de metadatos no repite pruebas de unicidad ni recuentos de filas de los datos.

| Tabla | Unidad de observación | Regla de uso |
| --- | --- | --- |
| `FactProduccionAceite` | Provincia × campaña | Aceite industrial en t. Sumar provincias comparables dentro de una campaña. |
| `FactPrecioAceite` | Provincia × campaña | €/kg; usar `PrecioObservadoEURKg`. La media simple omite blancos y no pondera ventas. |
| `FactProduccionAgricola` | Provincia × año de referencia, con cultivo identificado | Aceituna agrícola en t; separar los conceptos de producción y los cambios de clasificación. |
| `FactSuperficie` | Provincia × año | ha de olivar total; no sumar años ni duplicar con sus desgloses. |
| `FactRegimenHidrico` | Provincia × año × aptitud del cultivo | ha de secano/regadío; no sumar componentes junto a un total solapado. |
| `FactLluviaTrimestre` | Provincia × campaña × trimestre de campaña | mm, métodos A/B, cobertura y alertas. Acumular trimestres compatibles; no sumar provincias como lluvia regional. |
| `FactTemperatura` | Provincia × campaña | Conteos y porcentajes de observaciones de estaciones; días medios por estación no son días únicos de una provincia. |
| `FactCostesEstimados` | Andalucía × campaña × tipología | Coste técnico estimado en €/ha y €/kg. No es contabilidad de explotaciones ni un importe sumable. |
| `FactCostesEscenarios` | Andalucía × campaña × tipología × escenario | Hipótesis alternativas de coste. Seleccionar una combinación; no sumar escenarios. |
| `FactCostesReferencia` | Territorio × periodo de estudio × tipología | Referencias puntuales o rangos; mantener país, periodo, unidad y condiciones de comparabilidad. |
| `FactExistencias` | España × campaña | Stock inicial/final en t; no sumar cierres entre campañas ni repartirlos entre provincias. |
| `dataset_analitico` | Provincia × cosecha objetivo | Ventanas climáticas antecedentes y producción; 48 combinaciones documentadas, ocho provincias × seis cosechas. |
| `FactComercioTunez` | Año natural × flujo × país × TARIC | España importa desde Túnez, TARIC 1509; sumar euros y kilos antes de calcular €/kg. |
| `Volumen aceite t` | Valor del parámetro de volumen | Entrada hipotética, no producción observada ni tabla de transacciones. |

Las campañas principales abarcan 2020/21–2025/26. Los trimestres de campaña son octubre–diciembre, enero–marzo, abril–junio y julio–septiembre. El comercio usa años naturales 2020–2026; no se equipara 2025 con 2025/26.

`DimTerritorio` conserva miembros distintos para España, Andalucía y cada provincia. Seleccionar el miembro regional `ES-AN` no incluye automáticamente sus provincias. Los atributos territoriales permiten agruparlas, pero no cambian el nivel real de costes o existencias.

## Relaciones y propagación de filtros

Las **62 relaciones** se descomponen en:

| Conjunto | Número | Estado y dirección |
| --- | ---: | --- |
| Núcleo dimensional | 40 | Activas, muchos a uno, filtro único desde la dimensión hacia el hecho. |
| Dimensiones hacia `dataset_analitico` | 2 | Activas, muchos a uno, filtro único desde territorio y campaña. |
| Calendarios automáticos | 18 | Activas, muchos a uno, filtro único desde cada calendario hacia su columna de fecha. |
| Enlaces auxiliares entre hechos/dataset | 2 | Inactivos, uno a uno, configurados con filtro bidireccional. |
| **Total** | **62** | **60 activas y 2 inactivas.** |

### Núcleo dimensional: 40 relaciones

Cada clave de la siguiente tabla representa una relación activa independiente. El extremo de dimensión es el lado uno.

| Tabla de hechos | Claves relacionadas con dimensiones | Número |
| --- | --- | ---: |
| `FactProduccionAceite` | Territorio, Campaña, Fuente | 3 |
| `FactProduccionAgricola` | Territorio, Año, Cultivo, Fuente | 4 |
| `FactPrecioAceite` | Territorio, Campaña, Fuente | 3 |
| `FactSuperficie` | Territorio, Año, Fuente | 3 |
| `FactRegimenHidrico` | Territorio, Año, Cultivo, Fuente | 4 |
| `FactLluviaTrimestre` | Territorio, Campaña, Trimestre, Fuente | 4 |
| `FactTemperatura` | Territorio, Campaña, Fuente | 3 |
| `FactCostesEstimados` | Territorio, Campaña, Tipología, Fuente | 4 |
| `FactCostesEscenarios` | Territorio, Campaña, Tipología, Escenario, Fuente | 5 |
| `FactCostesReferencia` | Territorio, Año, Tipología, Fuente | 4 |
| `FactExistencias` | Territorio, Campaña, Fuente | 3 |

Correspondencias exactas de claves:

| Clave del hecho | Dimensión y clave del lado uno |
| --- | --- |
| `TerritorioId` | `DimTerritorio[TerritorioId]` |
| `CampanaId` | `DimCampana[CampanaId]` |
| `AnoReferencia` | `DimAno[AnoReferencia]` |
| `CultivoId` | `DimCultivo[CultivoId]` |
| `TipologiaId` | `DimTipologia[TipologiaId]` |
| `EscenarioId` | `DimEscenario[EscenarioId]` |
| `TrimestreCampana` | `DimTrimestreCampana[TrimestreCampana]` |
| `FuenteModeloId` | `DimFuente[FuenteId]` |

`dataset_analitico` añade dos relaciones activas mediante `TerritorioId` y `CampanaId` con las mismas dimensiones. No hay una relación directa entre `DimAno` y `DimCampana`.

### Calendarios y relaciones auxiliares

Las 18 relaciones automáticas enlazan cada columna siguiente con `[Date]` de su calendario local independiente:

| Tabla | Columnas de fecha | Relaciones |
| --- | --- | ---: |
| `DimCampana` | `Inicio`, `Fin` | 2 |
| `FactLluviaTrimestre` | `Inicio`, `Fin` | 2 |
| `FactTemperatura` | `Inicio`, `Fin` | 2 |
| `FactExistencias` | `FechaExistenciasIniciales`, `FechaExistenciasFinales`, `ActualizacionPublicacion`, `FechaConsulta` | 4 |
| `dataset_analitico` | `AN_Inicio`, `AN_Fin`, `AJ_Inicio`, `AJ_Fin`, `MAY_Inicio`, `MAY_Fin`, `OM_Inicio`, `OM_Fin` | 8 |

La plantilla automática no añade una relación. Estos calendarios no constituyen un puente homologado entre año natural y campaña.

Los dos enlaces inactivos son:

| Extremo en `dataset_analitico` | Otro extremo | Configuración |
| --- | --- | --- |
| `ProduccionAceiteT` | `FactProduccionAceite[ProduccionAceiteT]` | 1:1, bidireccional, inactiva. |
| `FilaExcel` | `FactPrecioAceite[FilaExcel]` | 1:1, bidireccional, inactiva. |

No propagan filtros por defecto. Un importe de producción y una posición de fila no sustituyen una clave estable de negocio; cualquier uso o activación requiere revisar propósito y unicidad. No debe describirse todo el modelo como libre de enlaces entre hechos: estos dos objetos existen aunque estén inactivos.

### Tablas sin relaciones y efectos en los filtros

- `FactComercioTunez` no tiene relaciones en el inventario consultado. Su año se selecciona con `periodo_anio` de la propia tabla; `DimAno`, campaña y provincia no la filtran mediante relaciones.
- `Volumen aceite t` es un parámetro desconectado. Las medidas del simulador leen su selección y convierten toneladas a kilos.
- `tabla medidas DAX` es un contenedor sin relaciones. Las expresiones determinan qué hechos y filtros intervienen.

Las interacciones configuradas entre visuales pueden añadir diferencias al contexto que llega a una medida. Las capturas ilustran selecciones concretas; no acreditan todas las combinaciones de filtros.

## Cinco medidas DAX reales

Las siguientes expresiones se transcriben de `'tabla medidas DAX'` en el motor consultado. Son una selección de las 39 expresiones disponibles, con sus nombres reales; no se han reescrito como propuestas ni ejecutado para certificar resultados durante este cierre documental.

### 1. Producción de aceite

```dax
Producción Aceite (t) =
SUM ( FactProduccionAceite[ProduccionAceiteT] )
```

Suma toneladas en el contexto vigente. La expresión no exige una sola campaña: sin esa selección puede sumar varias. Su uso como producción de una campaña depende del filtro del visual.

### 2. Precio provincial medio

```dax
Precio Aceite Media Provincial (€/kg) =
AVERAGE (
    FactPrecioAceite[PrecioObservadoEURKg]
)
```

Media aritmética de los precios observados no vacíos. Con una campaña seleccionada representa la media simple de las provincias disponibles; con varias campañas cambia el conjunto de filas promediado. No pondera producción ni ventas. El tratamiento documentado deja fuera del campo observado los seis valores de Cádiz y conserva sus originales para trazabilidad.

### 3. Precipitación acumulada

```dax
Precipitación acumulada (mm) =
SUM ( FactLluviaTrimestre[PrecipitacionAmm] )
```

Suma filas del método A. Con una provincia y campaña puede acumular los trimestres de esa campaña; con varias provincias también suma sus mm. **La expresión base no protege frente a agregación territorial indebida.**

Existe además `Precipitación KPI (mm)`, que exige una campaña y una provincia mediante `HASONEVALUE` y devuelve blanco en otro caso. Esa protección de la tarjeta no se extiende automáticamente a visuales que utilizan la medida base. El riesgo multiprovincial continúa abierto.

### 4. Margen económico total del simulador

```dax
Sim Margen económico total (€) =
VAR Margen = [Sim Margen estimado (€/kg)]
VAR Volumen = [Sim Volumen (kg)]
RETURN
    IF (
        NOT ISBLANK ( Margen )
            && NOT ISBLANK ( Volumen ),
        Margen * Volumen
    )
```

El margen unitario es la diferencia entre `Sim Precio de referencia (€/kg)` y `Sim Coste de producción (€/kg)`. Las dependencias reales aplican estas reglas:

- El precio exige una campaña, retira filtros de `DimTerritorio` y promedia únicamente filas clasificadas como `PRECIO_PROVINCIAL_PUBLICADO`.
- El coste exige campaña, tipología y escenario únicos; retira el filtro territorial, fija `ES-AN` y solo devuelve coste si queda exactamente una fila en `FactCostesEscenarios`.
- `Sim Volumen (kg)` usa la selección de `Volumen aceite t` y multiplica por 1.000. Sin filtro usa 10 t; una selección filtrada sin valor único devuelve blanco.
- La multiplicación utiliza el margen sin redondear. Los decimales mostrados en tarjetas no deben reutilizarse para reconstruir un total exacto.

El resultado es hipotético. La etiqueta interna «Datos comparables» indica que las dependencias del simulador aportan valores; no certifica equivalencia económica de precios y costes ni beneficio real.

### 5. Valor unitario de importación

```dax
Valor unitario importación (€/kg) =
DIVIDE (
    SUM ( 'FactComercioTunez'[euros] ),
    SUM ( 'FactComercioTunez'[kilos] )
)
```

Cociente entre euros totales y kilos totales del contexto comercial. `DIVIDE` devuelve blanco si el denominador es cero o está vacío. El agregado de varios años debe conservar ese cociente de totales, no sumar o promediar sin ponderación los valores unitarios anuales.

Las otras conversiones comerciales documentadas son kilos / 1.000 para t y euros / 1.000.000 para M€. Este valor unitario no es precio al agricultor, coste tunecino ni margen industrial.

## Fuentes y preparación

La procedencia de negocio se documenta en [Metodología](METODOLOGIA.md). Esta entrega no vuelve a descargar fuentes ni certifica sus publicaciones originales.

| Dominio | Fuente o artefacto documentado | Tratamiento y cautela |
| --- | --- | --- |
| Aceite y precios | Libro `Produccion_Precios_Aceite_Oliva_Andalucia_2020_2026.xlsx`, hoja `Cruce con aceite`; referencias sectoriales y MAPA-SIMO. | Separar producción industrial y precios admisibles. 2025/26 provisional; no asumir precio efectivo de venta. |
| Superficies y cosecha agrícola | Series y contrastes Junta de Andalucía/MAPA del paquete de superficies. | Año de referencia propio, cambios de clasificación desde 2023 y datos provisionales; no convertir automáticamente a campaña comercial. |
| Clima | RAIF y capas derivadas de calidad, lluvia trimestral y temperatura. | Método A: media de acumulados de estaciones elegibles; B: suma de medias diarias con denominador variable. Conservar cobertura, exclusiones y extremos pendientes. |
| Análisis antecedente | `dataset_analitico`, derivado de clima y producción por cosecha objetivo. | Ventanas antecedentes explícitas. La correlación ajustada y el scatter de magnitudes absolutas son análisis distintos. |
| Costes | `Costes_Olivar_Andalucia_2020_2026_MAESTRO_MECANIZACION_ACTUALIZADO.xlsx`. | Separar estimaciones oficiales, escenarios dinámicos, producción media y mecanización. |
| Referencias de costes | AEMO 2026 y estudio regional de Zaghouan. | Referencia técnica nacional española frente a muestra regional tunecina; periodos, productos y conversiones no necesariamente homogéneos. |
| Comercio | Extracción DataComex, España desde Túnez, TARIC 1509; `periodo_anio`, `periodo_provisional`, `euros`, `kilos`. | Año natural; 2024–2025 etiquetados provisionales en la fuente utilizada y 2026 provisional/incompleto. |
| Existencias | Serie nacional documentada en `FactExistencias` y trazabilidad mediante `DimFuente`. | España, no Andalucía; confirmar publicación y fecha antes de reutilizarla como dato actualizado. |

Los archivos originales no se distribuyen en este repositorio. `DimFuente` mantiene la procedencia del modelo; sus rutas locales y los textos privados de las fuentes no se trasladan a esta documentación.

## Costes estimados y alcance del simulador

`FactCostesEstimados`, `FactCostesEscenarios` y `FactCostesReferencia` responden a preguntas diferentes. Un coste oficial estimado sigue siendo una estimación; un escenario no completa automáticamente un hueco de la serie oficial; una referencia AEMO o Zaghouan no es un coste observado de Andalucía.

`DINAMICO_PROXY` utiliza supuestos técnicos y productividad/rendimiento de referencia 2022/23. Los costes de 2025/26 incorporan información parcial según la documentación de origen. No representan una media regional ponderada de explotaciones.

Para 2024/25, las seis tipologías del escenario muestran aproximadamente **1,56–5,40 €/kg**. Para 2025/26, `CONV: Secano mecanizable`, el ejemplo documentado muestra precio **3,9233 €/kg**, coste **5,3878 €/kg** y margen **−1,4645 €/kg**. La captura de 10 t muestra **−14.645,15 €**; el ejemplo de 20 t de [Resultados y limitaciones](RESULTADOS_Y_LIMITACIONES.md) muestra **−29.290,29 €**. Son referencias visuales/documentales, no resultados recalculados aquí ni evidencia de cierre de la incidencia decimal.

No se suman costes unitarios entre tipologías ni se atribuye el resultado simulado a pérdidas observadas. Comparar ese coste con el valor unitario de importación requiere conservar diferencias de territorio, calidad, periodo, canal y definición económica.

## Limitaciones y riesgos pendientes

| Riesgo o límite | Estado y efecto | Criterio de cierre o tratamiento |
| --- | --- | --- |
| **Agregación de lluvia multiprovincial** | **Pendiente.** La medida base usa `SUM` y puede sumar mm entre provincias o campañas. La guarda de la tarjeta no protege todos los visuales. | Revisar cada uso de la medida con una provincia, varias y todas; comprobar una y varias campañas. Definir si el agregado debe ser blanco o una media explícitamente justificada, con cobertura y pesos documentados. Conciliar el resultado con la base antes de darlo por resuelto. |
| **Validación final de la corrección decimal** | **Pendiente.** Hay una copia de trabajo de corrección de tipos; leer su esquema y expresiones no verifica importación, magnitud ni persistencia de los valores. | Conciliar valores fuente → Power Query → columna del modelo → medida → visual, bajo los mismos filtros. Revisar separador decimal y configuración regional, precisión, nulos y escala 0–100 frente a fracción. Verificar tras actualización y reapertura en una revisión autorizada. |
| Objeto `Medida` sin expresión | Un objeto de metadatos carece de cálculo; no debe contarse como KPI funcional. | Determinar su propósito y referencias antes de completarlo o retirarlo en una intervención separada. |
| Dos enlaces auxiliares inactivos | Configurados sobre producción y fila de Excel, con cardinalidad 1:1 bidireccional. | Mantener documentado su estado; revisar claves, finalidad y posibles ambigüedades antes de cualquier activación. |
| Umbrales térmicos | Las capturas rotulan >35 °C y >40 °C, mientras varios nombres de medidas conservan ≥. | Contrastar la definición del campo de origen y armonizar nombres/etiquetas; el nombre de una medida no demuestra el umbral calculado. |
| Cobertura y calidad climática | Panel de estaciones cambiante, exclusiones y extremos pendientes; cobertura no equivale a representatividad del olivar. | Conservar estados, denominadores y sensibilidad. No presentar lluvia como disponibilidad hídrica de raíces ni asociaciones como causalidad. |
| Comparabilidad económica y temporal | Costes de escenario, precios provinciales e importaciones españolas tienen universos distintos. | Rotular ámbitos y periodos; no atribuir pérdidas andaluzas a las importaciones ni inferir costes tunecinos del valor comercial. |
| Provisionalidad y reproducibilidad | 2025/26 y 2026 pueden revisarse; faltan los datos originales y el PBIX en el paquete público. | Mantener fechas/estados y distinguir documentación, script reproducible y validación completa del informe. |

La comprobación decimal debe incluir precios, costes, lluvia, porcentajes y conversiones kg/t y €/M€, con valores de referencia y tolerancias explícitas. Cambiar únicamente el formato de una tarjeta no corrige un valor importado con escala incorrecta.

El análisis ajustado documentado de lluvia anual antecedente y logaritmo de producción (`r = +0,655`) no es la correlación regional de seis campañas calculada por el script del repositorio ni la relación visual del scatter. Véanse [Metodología](METODOLOGIA.md) y [Fórmulas y alcance del script](../scripts/README.md#fórmulas-y-alcance).

## Reproducción y conservación

Este repositorio contiene documentación, cuatro capturas y un script de análisis regional con sus pruebas. La [guía de scripts](../scripts/README.md) explica entorno, entrada Excel autorizada, validaciones y ejecución; ese script no reconstruye las 42 tablas ni ejecuta las medidas DAX del simulador.

Para reproducir el informe completo se necesitan las fuentes autorizadas, sus transformaciones, el modelo y la configuración de visuales/filtros. Esta documentación no incluye una exportación íntegra de Power Query, TMDL o todos los datos. No se afirma reproducibilidad completa del PBIX a partir del paquete.

El cierre documental conserva imágenes y documentos anteriores. No modifica PBIX, consultas, medidas, scripts Python ni datos; tampoco actualiza el modelo, ejecuta Git o publica contenido. Se revisan estructura Markdown, enlaces locales y posibles datos privados del paquete, sin extender esa revisión al historial del repositorio.

Las listas de pendientes de documentos anteriores conservan su contexto histórico. La existencia actual de las cuatro capturas está comprobada; los dos riesgos principales de este documento permanecen abiertos.

