# Metodología · OLIVAR 360°

## 1. Preguntas de análisis

1. ¿Cómo evolucionaron producción y precios del aceite de oliva en Andalucía entre 2020/21 y 2025/26?
2. ¿Qué patrones descriptivos aparecen entre clima, precipitación y producción?
3. ¿Qué diferencias muestran los costes técnicos estimados entre sistemas de cultivo?
4. ¿Cómo evolucionó el volumen y valor unitario de las importaciones españolas desde Túnez?

## 2. Unidades y periodos

| Dominio | Unidad de observación | Periodo |
|---|---|---|
| Producción, precios y clima regional | Provincia × campaña | 2020/21–2025/26 |
| Costes | Campaña × tipología × escenario | Según dato y escenario, con análisis 2024/25 y 2025/26 |
| Comercio España–Túnez | Año natural × flujo × país × TARIC | 2020–2026 (2026 provisional) |
| Agroclima exploratorio | Provincia × cosecha objetivo | 48 combinaciones, 8 × 6 |

Los gráficos históricos pueden conservar las seis campañas mientras que los KPI responden a la campaña seleccionada. En comercio, KPI sin selección de año representan el agregado 2020–2026; gráficos históricos se limitan a 2020–2025.

## 3. Fuentes e identificación

- Datos de producción y precios sectoriales procesados en `Produccion_Precios_Aceite_Oliva_Andalucia_2020_2026.xlsx`, con revisión de metodología de MAPA-SIMO.
- Series climáticas de la Red de Alerta e Información Fitosanitaria de Andalucía (RAIF), con evaluación de cobertura y anomalías.
- Fichas de costes de olivar y escenarios del libro local `Costes_Olivar_Andalucia_2020_2026_MAESTRO_MECANIZACION_ACTUALIZADO.xlsx`.
- AEMO 2026 como referencia técnica nacional, **no equivalente a un coste regional observado**.
- DataComex, importaciones españolas desde Túnez, TARIC 1509, columnas `periodo_anio`, `periodo_provisional`, `euros`, `kilos`.
- Estudio regional Zaghouan: referencias heterogéneas, no empleadas para afirmar un coste tunecino nacional comparable.

Los archivos originales y sus condiciones de redistribución deben revisarse antes de publicar datos brutos.

## 4. Transformaciones y KPI

- Producción de aceite en toneladas, distinguiéndola de producción de aceituna.
- Precio de referencia: media simple de precios provinciales disponibles; **no** ponderada por volumen.
- Variación: comparación frente a la campaña anterior bajo la definición del indicador.
- Margen estimado (€/kg): precio de referencia (€/kg) menos coste estimado (€/kg).
- Margen total simulado (€): margen no redondeado (€/kg) × volumen simulado (t) × 1.000.
- Importaciones (t): `SUM(kilos) / 1000`.
- Valor comercial (M€): `SUM(euros) / 1000000`.
- Valor unitario importado (€/kg): `SUM(euros) / SUM(kilos)`. Esta razón debe calcularse sobre totales, **no sumar ni promediar sin ponderación los valores anuales**.

## 5. Clima y correlaciones

La lluvia provincial en mm **no debe sumarse entre provincias para interpretar una precipitación regional**. El scatter principal de la página 03 presenta valores absolutos de precipitación antecedente y producción provincial. No equivale al análisis de correlación ajustado dentro de provincia.

El análisis exploratorio separado relacionó la lluvia anual antecedente con el logaritmo de producción, descontando medias provinciales: `r = +0,655` para 48 provincia-cosechas según el informe de Codex. El calor primaveral mostró señal inestable, sensible a incluir/excluir la campaña 2025/26 provisional. No atribuir causalidad ni extrapolar la correlación a efectos individuales.

## 6. Calidad y validación

El proyecto utilizó scripts Python, pruebas automáticas y controles internos de integridad. Posteriormente se revisaron visualmente las cuatro páginas y sus interacciones en Power BI. Estas pruebas **no equivalen a validación científica independiente** ni reemplazan documentación del origen de datos.

## 7. Limitaciones esenciales

- 2025/26 y 2026 pueden estar sujetos a revisión o cobertura incompleta.
- Los costes `DINAMICO_PROXY` son simulaciones técnicas con supuestos de productividad de referencia, no contabilidad real de explotaciones.
- El valor unitario importado refleja comercio exterior y no precio al agricultor, coste de producción tunecino ni margen de la industria.
- Se comparan territorios y definiciones distintas: Andalucía (producción/costes) frente a España (importaciones desde Túnez).
- Los umbrales térmicos > o ≥ y los denominadores de los porcentajes deben mantenerse consistentes con el diccionario final.
