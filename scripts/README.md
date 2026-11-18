# Análisis regional publicable de OLIVAR 360°

Esta copia autónoma de `analisis_olivar.py` complementa la documentación del
repositorio. No incluye datos originales ni depende de carpetas de ejecuciones
anteriores. La licencia del código sigue pendiente según el README principal;
no se presupone autorización para redistribuir los datos de terceros.

## Entorno

Python **3.10 o superior**. Desde la raíz de este repositorio y en un entorno
virtual elegido por el usuario:

```console
python -m pip install -r scripts/requirements.txt
```

Se declaran `pandas>=2.1` (se utiliza `DataFrame.map`) y `openpyxl>=3.1.5`.
El motor de lectura Excel se fija explícitamente a `openpyxl`. Para habilitar
el gráfico, instalar el complemento opcional:

```console
python -m pip install -r scripts/requirements-graficos.txt
```

Estos manifiestos declaran dependencias, no un entorno bloqueado a versiones
exactas. El script no instala ni descarga nada. Matplotlib no se importa en
modo `--comprobar`; si no está instalado, la ejecución normal genera los CSV
y comunica la omisión del PNG.

## Entrada y validaciones

El usuario debe proporcionar un `.xlsx` autorizado con la hoja exacta
`Cruce con aceite`. `datos/entrada.xlsx` en los ejemplos es una ruta ilustrativa:
el repositorio no suministra ese archivo.

| Columna requerida | Condición |
| --- | --- |
| `Campaña` | Exactamente 2020/21, 2021/22, 2022/23, 2023/24, 2024/25 y 2025/26 |
| `Provincia` | Almería, Cádiz, Córdoba, Granada, Huelva, Jaén, Málaga y Sevilla en cada campaña |
| `Precipitación media mm` | Número finito, no nulo y no negativo |
| `Producción aceite t` | Número finito, no nulo y no negativo |

Se exigen 48 claves únicas provincia-campaña. Se rechazan archivos inexistentes,
hojas o columnas ausentes, tablas vacías, claves nulas o duplicadas, campañas
ausentes o adicionales y coberturas provinciales incompletas. No se imputan,
normalizan ni corrigen valores. Las columnas adicionales se descartan de la
copia en memoria y de las exportaciones; el Excel se abre solo para lectura.

## Uso

Las rutas relativas se interpretan desde el directorio de trabajo actual.
`--entrada` es obligatorio; `--salida` tiene por defecto `./resultados`.

```console
python -B scripts/analisis_olivar.py --entrada datos/entrada.xlsx --comprobar
python -B scripts/analisis_olivar.py --entrada datos/entrada.xlsx --salida resultados
```

`--comprobar` valida y calcula sin crear carpetas, CSV ni gráficos; no utiliza
el destino de `--salida`. La ejecución normal crea una subcarpeta única con
fecha UTC y UUID, sin sobrescribir resultados anteriores:

- `olivar_datos_preparados.csv`: solo las cuatro columnas analíticas.
- `resumen_campanas.csv`: producción total y precipitación media por campaña.
- `dispersion_lluvia_produccion.png`: únicamente si matplotlib está disponible.

Los CSV mantienen separador `;`, decimal `,` y codificación `utf-8-sig`.
Las rutas absolutas del equipo no se incluyen en los mensajes de resultado.
El código devuelve 0 al completar, 1 ante errores de lectura, validación o
exportación, y 2 ante argumentos incorrectos. Un fallo durante la exportación
puede dejar una carpeta parcial, que se identifica como tal en el mensaje.
Las salidas no se publican automáticamente: requieren una revisión independiente.

## Fórmulas y alcance

La función `calcular_resumen` conserva la implementación original:

1. **Producción regional:** suma de `Producción aceite t` de las ocho provincias.
2. **Precipitación regional descriptiva:** media aritmética simple de
   `Precipitación media mm` entre las ocho provincias, sin ponderaciones.
3. **Correlación:** Pearson entre las dos series regionales, ordenadas por
   campaña, con **seis observaciones**. Los cálculos no se redondean; solo la
   presentación en consola se redondea.

**Esta correlación no es el análisis ajustado r=+0,655 de
[la metodología](../docs/METODOLOGIA.md).** Aquel relaciona lluvia anual
antecedente y logaritmo de producción descontando medias provinciales sobre
48 provincia-cosechas. Este script no aplica logaritmos, ajustes provinciales
ni nuevas ventanas climáticas y tampoco reproduce el scatter provincial de
48 observaciones del dashboard. Las diferencias entre esos resultados no
deben interpretarse como un fallo de cálculo.

La correlación es exploratoria, no demuestra causalidad y conserva las cautelas
sobre clima y campaña 2025/26 provisional. El script no analiza precios,
estados de precios ni observaciones de Cádiz: esas columnas permanecen intactas
en la fuente, pero no se imprimen ni se exportan.

## Pruebas aisladas

```console
python -B -m unittest discover -s scripts/tests -v
```

Las pruebas usan `unittest` de la biblioteca estándar. Generan Excel sintéticos
en directorios temporales dentro de `scripts/tests/`, dirigen allí también la
caché de matplotlib y eliminan esos temporales al terminar. No buscan ni leen
los datos reales del proyecto. `-B` evita generar archivos de bytecode.
La prueba PNG se omite si no está instalado el complemento gráfico.

Se comprueban validación, CLI, importación sin efectos, cálculo frente a un
oráculo independiente, ausencia de escrituras en `--comprobar`, exportaciones
acotadas, conservación del archivo de entrada y ejecuciones sin sobrescritura.

## Diferencias respecto al script de trabajo

- Entrada configurable y salida configurable, sin rutas locales fijadas.
- Se exige el periodo completo; se conserva la validación provincial.
- Lectura explícita con openpyxl y mensajes sin rutas del equipo.
- Se requieren y exportan solo las cuatro columnas usadas en las fórmulas.
- Se retiran la impresión de texto libre y los diagnósticos de precios de Cádiz.
- Se documenta la diferencia entre correlación regional y análisis ajustado.
- Se mantienen las fórmulas, el gráfico, los formatos CSV y las carpetas únicas.
