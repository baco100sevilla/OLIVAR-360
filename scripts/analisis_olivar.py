"""Análisis regional exploratorio; --comprobar valida sin exportar archivos.

Pearson sobre seis campañas regionales, distinto del análisis ajustado r=+0,655.
"""
import argparse
from collections.abc import Sequence
from datetime import datetime, timezone
from importlib.util import find_spec
from math import isfinite
from pathlib import Path
import sys
from uuid import uuid4
from xml.etree.ElementTree import ParseError
from zipfile import BadZipFile

import pandas as pd

HOJA = 'Cruce con aceite'
CAMPANAS = frozenset(f'{anio}/{str(anio + 1)[-2:]}' for anio in range(2020, 2026))
PROVINCIAS = frozenset({'Almería', 'Cádiz', 'Córdoba', 'Granada', 'Huelva',
                        'Jaén', 'Málaga', 'Sevilla'})
COLUMNAS = ('Campaña', 'Provincia', 'Precipitación media mm', 'Producción aceite t')


def cargar_datos(archivo: str | Path) -> pd.DataFrame:
    """Leer las cuatro columnas analíticas y exigir las 48 claves previstas."""
    archivo = Path(archivo)
    if not archivo.is_file():
        raise FileNotFoundError('No se encuentra un archivo válido en --entrada.')
    if archivo.suffix.lower() != '.xlsx':
        raise ValueError('La entrada debe ser un archivo .xlsx.')
    with pd.ExcelFile(archivo, engine='openpyxl') as excel:
        if HOJA not in excel.sheet_names:
            raise ValueError(f'Falta la hoja requerida: {HOJA}.')
        df = pd.read_excel(excel, sheet_name=HOJA)
    faltantes = sorted(set(COLUMNAS) - set(df.columns))
    if faltantes:
        raise ValueError(f'Faltan columnas requeridas: {faltantes}')
    df = df.loc[:, list(COLUMNAS)].copy()
    if df.empty:
        raise ValueError('La hoja no contiene registros.')
    if df[['Campaña', 'Provincia']].isna().any().any():
        raise ValueError('Hay campañas o provincias vacías.')
    if df.duplicated(['Campaña', 'Provincia']).any():
        raise ValueError('Hay claves Campaña + Provincia duplicadas.')
    presentes = set(df['Campaña'])
    if presentes != CAMPANAS:
        raise ValueError(
            'Cobertura de campañas inválida: '
            f'faltan {sorted(CAMPANAS - presentes)}; '
            f'no reconocidas {sorted(presentes - CAMPANAS, key=str)}.')
    for columna in ('Producción aceite t', 'Precipitación media mm'):
        if not pd.api.types.is_numeric_dtype(df[columna]) or df[columna].isna().any():
            raise ValueError(f'{columna} debe ser numérica y no contener nulos.')
        if not df[columna].map(isfinite).all() or (df[columna] < 0).any():
            raise ValueError(f'{columna} debe contener valores finitos y no negativos.')
    for campana, grupo in df.groupby('Campaña'):
        presentes = set(grupo['Provincia'])
        if presentes != PROVINCIAS:
            raise ValueError(
                f'Cobertura provincial inválida en {campana}: '
                f'faltan {sorted(PROVINCIAS - presentes)}; '
                f'no reconocidas {sorted(presentes - PROVINCIAS, key=str)}.')
    return df


def calcular_resumen(df: pd.DataFrame) -> tuple[pd.DataFrame, float]:
    """Agregar datos validados; rechazar una correlación no calculable."""
    # Método original: producción total y media provincial simple de precipitación.
    resumen = df.groupby('Campaña').agg(
        Produccion_t=('Producción aceite t', 'sum'),
        Precipitacion_mm=('Precipitación media mm', 'mean')).sort_index()
    if (len(resumen) < 2 or resumen.nunique().lt(2).any()
            or not resumen.map(isfinite).all().all()):
        raise ValueError('Correlación no calculable: se requieren al menos dos '
                         'campañas, valores finitos y variabilidad en ambas series.')
    correlacion = float(resumen.Precipitacion_mm.corr(resumen.Produccion_t))
    if not isfinite(correlacion):
        raise ValueError('Correlación no calculable: resultado no finito.')
    return resumen, correlacion


def crear_grafico(resumen: pd.DataFrame, destino: str | Path) -> None:
    import matplotlib
    matplotlib.use('Agg')
    from matplotlib import pyplot as plt
    fig, ax = plt.subplots(figsize=(10, 6))
    try:
        ax.scatter(resumen.Precipitacion_mm, resumen.Produccion_t, s=100)
        for campana, fila in resumen.iterrows():
            ax.annotate(campana, (fila.Precipitacion_mm, fila.Produccion_t),
                        xytext=(5, 5), textcoords='offset points')
        ax.set(title='Precipitaciones y producción de aceite en Andalucía',
               xlabel='Precipitación media provincial (mm)',
               ylabel='Producción de aceite (toneladas)')
        ax.grid(alpha=0.3)
        fig.tight_layout()
        with Path(destino).open('xb') as fichero:
            fig.savefig(fichero, format='png', dpi=300)
    finally:
        plt.close(fig)


def exportar_resultados(df: pd.DataFrame, resumen: pd.DataFrame,
                        directorio: str | Path, con_grafico: bool) -> Path:
    """Crear una ejecución independiente, sin exportar columnas adicionales."""
    nombre = datetime.now(timezone.utc).strftime('ejecucion_%Y%m%dT%H%M%S_%fZ_') + uuid4().hex
    salida = Path(directorio) / nombre
    salida.mkdir(parents=True, exist_ok=False)
    df.loc[:, list(COLUMNAS)].to_csv(
        salida / 'olivar_datos_preparados.csv', index=False, sep=';',
        encoding='utf-8-sig', decimal=',', mode='x')
    resumen.to_csv(salida / 'resumen_campanas.csv', sep=';',
                   encoding='utf-8-sig', decimal=',', mode='x')
    if con_grafico:
        crear_grafico(resumen, salida / 'dispersion_lluvia_produccion.png')
    return salida


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--entrada', required=True, type=Path,
                        help='Excel .xlsx con la hoja Cruce con aceite.')
    parser.add_argument('--salida', type=Path, default=Path('resultados'),
                        help='Directorio de resultados (por defecto: ./resultados).')
    parser.add_argument('--comprobar', action='store_true',
                        help='Validar y calcular en memoria sin crear archivos ni gráficos.')
    args = parser.parse_args(argv)
    try:
        df = cargar_datos(args.entrada)
        resumen, correlacion = calcular_resumen(df)
        if not args.comprobar and args.salida.exists() and not args.salida.is_dir():
            raise ValueError('--salida debe ser un directorio, no un archivo.')
    except FileNotFoundError:
        print('ERROR: no se encuentra el archivo de entrada; revise --entrada.', file=sys.stderr)
        return 1
    except ImportError:
        print('ERROR: falta una dependencia de lectura; consulte scripts/requirements.txt.',
              file=sys.stderr)
        return 1
    except (OSError, BadZipFile, ParseError):
        print('ERROR: no se pudo leer el Excel; compruebe formato, integridad y permisos.',
              file=sys.stderr)
        return 1
    except ValueError as error:
        print(f'ERROR: {error}', file=sys.stderr)
        return 1
    print(f'Fuente: {args.entrada.name}\nHoja: {HOJA}\nDimensiones analíticas: {df.shape}')
    print(f"Provincias: {df['Provincia'].nunique()}; campañas: {df['Campaña'].nunique()}")
    print('Cobertura validada: 2020/21–2025/26, ocho provincias por campaña.')
    print('\nResumen por campaña:\n', resumen.round(2))
    print(f'\nCorrelación regional de Pearson: {correlacion:.9f}')
    print('Análisis exploratorio de seis campañas: producción regional total y '
          'media simple provincial de precipitación. No demuestra causalidad; '
          '2025/26 se considera provisional.')
    print('Esta correlación regional no equivale al análisis ajustado dentro de '
          'provincia sobre logaritmo de producción (r=+0,655) de la documentación.')
    if args.comprobar:
        print('Comprobación completada: no se han creado ni exportado archivos.')
        return 0
    disponible = find_spec('matplotlib') is not None
    try:
        salida = exportar_resultados(df, resumen, args.salida, disponible)
    except (OSError, ValueError, ImportError, RuntimeError):
        print('ERROR de exportación: revise permisos, espacio y dependencias. '
              'Puede existir una ejecución parcial dentro de --salida.', file=sys.stderr)
        return 1
    print(f'Resultados guardados en --salida, subcarpeta: {salida.name}')
    if not disponible:
        print('Ambos CSV disponibles; PNG omitido por falta de matplotlib. '
              'Dependencia opcional: scripts/requirements-graficos.txt.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
