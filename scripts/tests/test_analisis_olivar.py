"""Pruebas con datos sintéticos; todos los archivos se crean en temporales."""
import contextlib
import hashlib
import importlib.util
import io
import os
from pathlib import Path
import statistics
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import pandas as pd

SCRIPT = Path(__file__).resolve().parents[1] / 'analisis_olivar.py'
spec = importlib.util.spec_from_file_location('olivar_publicable', SCRIPT)
olivar = importlib.util.module_from_spec(spec)
spec.loader.exec_module(olivar)


def datos_sinteticos():
    """Seis campañas con ocho provincias; valores sin origen en datos reales."""
    lluvia = [310, 440, 290, 610, 500, 370]
    factores = [10, 20, 8, 28, 22, 12]
    return pd.DataFrame([
        {'Campaña':campana, 'Provincia':provincia,
         'Precipitación media mm':lluvia[i] + 2 * (j - 1),
         'Producción aceite t':factores[i] * j,
         'Observaciones':'TEXTO_SINTETICO_NO_EXPORTAR',
         'Columna adicional':'DATO_SINTETICO_NO_EXPORTAR'}
        for i, campana in enumerate(sorted(olivar.CAMPANAS))
        for j, provincia in enumerate(sorted(olivar.PROVINCIAS), start=1)
    ])


def huella(archivo):
    return hashlib.sha256(archivo.read_bytes()).hexdigest()


class PruebasOlivarPublicable(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.area = tempfile.TemporaryDirectory(
            prefix='.olivar_tests_', dir=Path(__file__).resolve().parent)
        cls.addClassCleanup(cls.area.cleanup)
        cls.entorno = patch.dict(os.environ, {
            'MPLCONFIGDIR':str(Path(cls.area.name) / 'matplotlib'),
            'TMP':cls.area.name, 'TEMP':cls.area.name, 'TMPDIR':cls.area.name,
            'PYTHONDONTWRITEBYTECODE':'1', 'PYTHONUTF8':'1',
        })
        cls.entorno.start()
        cls.addClassCleanup(cls.entorno.stop)

    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory(dir=self.area.name)
        self.addCleanup(self.temporal.cleanup)
        self.raiz = Path(self.temporal.name)
        self.entrada = self.raiz / 'entrada.xlsx'
        self.df = datos_sinteticos()
        self.escribir(self.df)

    def escribir(self, df, hoja=olivar.HOJA):
        df.to_excel(self.entrada, sheet_name=hoja, index=False, engine='openpyxl')

    def ejecutar(self, argumentos):
        salida, errores = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(salida), contextlib.redirect_stderr(errores):
            codigo = olivar.main(argumentos)
        return codigo, salida.getvalue(), errores.getvalue()

    def cli(self, *argumentos):
        return subprocess.run(
            [sys.executable, '-B', str(SCRIPT), *argumentos], cwd=self.raiz,
            capture_output=True, text=True, encoding='utf-8', timeout=30,
            check=False)

    def test_carga_columnas_analiticas_y_fuente_intacta(self):
        antes = huella(self.entrada)
        cargado = olivar.cargar_datos(self.entrada)
        pd.testing.assert_frame_equal(cargado, self.df.loc[:, list(olivar.COLUMNAS)])
        self.assertEqual(cargado.shape, (48, 4))
        self.assertEqual(huella(self.entrada), antes)

    def test_archivo_ausente_y_directorio(self):
        for ruta in (self.raiz / 'ausente.xlsx', self.raiz):
            with self.subTest(ruta=ruta.name), self.assertRaises(FileNotFoundError):
                olivar.cargar_datos(ruta)

    def test_hoja_columnas_y_tabla_vacia(self):
        casos = [
            (self.df, 'Otra', 'Falta la hoja'),
            (self.df.drop(columns=['Provincia']), olivar.HOJA, 'Faltan columnas'),
            (self.df.iloc[:0], olivar.HOJA, 'no contiene registros'),
        ]
        for datos, hoja, mensaje in casos:
            with self.subTest(mensaje=mensaje):
                self.escribir(datos, hoja)
                with self.assertRaisesRegex(ValueError, mensaje):
                    olivar.cargar_datos(self.entrada)

    def test_campanas_ausentes_adicionales_y_formato(self):
        casos = [
            self.df[self.df['Campaña'] != '2022/23'],
            pd.concat([self.df, self.df.iloc[:8].assign(Campaña='2026/27')]),
            self.df.assign(Campaña=self.df['Campaña'].replace({'2020/21':'2020-21'})),
        ]
        for datos in casos:
            with self.subTest(filas=len(datos)):
                self.escribir(datos)
                with self.assertRaisesRegex(ValueError, 'Cobertura de campañas'):
                    olivar.cargar_datos(self.entrada)

    def test_cobertura_provincial(self):
        casos = [self.df.iloc[1:],
                 self.df.assign(Provincia=self.df.Provincia.replace({'Cádiz':'Otra'}))]
        for datos in casos:
            with self.subTest(filas=len(datos)):
                self.escribir(datos)
                with self.assertRaisesRegex(ValueError, 'Cobertura provincial'):
                    olivar.cargar_datos(self.entrada)

    def test_claves_nulas_y_duplicadas(self):
        casos = [(pd.concat([self.df, self.df.iloc[:1]]), 'duplicadas'),
                 (self.df.assign(Provincia=None), 'vacías'),
                 (self.df.assign(Campaña=None), 'vacías')]
        for datos, mensaje in casos:
            with self.subTest(mensaje=mensaje):
                self.escribir(datos)
                with self.assertRaisesRegex(ValueError, mensaje):
                    olivar.cargar_datos(self.entrada)

    def test_medidas_nulas_no_numericas_negativas_e_infinitas(self):
        for columna in ('Producción aceite t', 'Precipitación media mm'):
            for valor in (None, 'texto', -1, float('inf'), float('-inf')):
                with self.subTest(columna=columna, valor=valor):
                    datos = self.df.astype({columna:object})
                    datos.loc[0, columna] = valor
                    self.escribir(datos)
                    with self.assertRaises(ValueError):
                        olivar.cargar_datos(self.entrada)

    def test_calculo_con_oraculo_independiente(self):
        cargado = olivar.cargar_datos(self.entrada)
        antes = cargado.copy(deep=True)
        resumen, correlacion = olivar.calcular_resumen(cargado)
        producciones = [360, 720, 288, 1008, 792, 432]
        precipitaciones = [317, 447, 297, 617, 507, 377]
        self.assertEqual(resumen.index.tolist(), sorted(olivar.CAMPANAS))
        self.assertEqual(resumen.Produccion_t.tolist(), producciones)
        self.assertEqual(resumen.Precipitacion_mm.tolist(), precipitaciones)
        self.assertAlmostEqual(
            correlacion, statistics.correlation(precipitaciones, producciones), places=14)
        pd.testing.assert_frame_equal(cargado, antes)

    def test_correlacion_indefinida(self):
        datos = olivar.cargar_datos(self.entrada)
        for caso in (datos.iloc[:0], datos.iloc[:8],
                     datos.assign(**{'Precipitación media mm':1}),
                     datos.assign(**{'Producción aceite t':1})):
            with self.subTest(filas=len(caso)), self.assertRaisesRegex(
                    ValueError, 'Correlación no calculable'):
                olivar.calcular_resumen(caso)

    def test_comprobar_no_exporta_ni_importa_graficos(self):
        antes = huella(self.entrada)
        destino = self.raiz / 'sin_crear'
        with patch.object(olivar, 'exportar_resultados') as exportar, \
                patch.object(olivar, 'find_spec') as buscar:
            codigo, salida, errores = self.ejecutar([
                '--entrada', str(self.entrada), '--salida', str(destino), '--comprobar'])
        self.assertEqual(codigo, 0, errores)
        exportar.assert_not_called()
        buscar.assert_not_called()
        self.assertFalse(destino.exists())
        self.assertEqual(huella(self.entrada), antes)
        self.assertNotIn(str(self.raiz), salida + errores)
        self.assertIn('r=+0,655', salida)
        self.assertNotIn('TEXTO_SINTETICO_NO_EXPORTAR', salida)

    def test_error_de_validacion_no_crea_salida(self):
        self.escribir(self.df.iloc[1:])
        destino = self.raiz / 'sin_crear'
        codigo, _, errores = self.ejecutar([
            '--entrada', str(self.entrada), '--salida', str(destino)])
        self.assertEqual(codigo, 1)
        self.assertIn('Cobertura provincial', errores)
        self.assertFalse(destino.exists())

    def test_salida_archivo_no_se_sobrescribe(self):
        destino = self.raiz / 'ocupado'
        destino.write_text('conservar', encoding='utf-8')
        codigo, _, errores = self.ejecutar([
            '--entrada', str(self.entrada), '--salida', str(destino)])
        self.assertEqual(codigo, 1)
        self.assertIn('--salida debe ser un directorio', errores)
        self.assertEqual(destino.read_text(encoding='utf-8'), 'conservar')

    def test_exportaciones_acotadas_repetibles_y_sin_sobrescritura(self):
        antes = huella(self.entrada)
        resumen, _ = olivar.calcular_resumen(self.df)
        destino = self.raiz / 'salidas'
        primera = olivar.exportar_resultados(self.df, resumen, destino, False)
        huellas = {p.name:huella(p) for p in primera.iterdir()}
        segunda = olivar.exportar_resultados(self.df, resumen, destino, False)
        self.assertNotEqual(primera, segunda)
        self.assertEqual({p.name:huella(p) for p in primera.iterdir()}, huellas)
        for carpeta in (primera, segunda):
            self.assertEqual({p.name for p in carpeta.iterdir()}, {
                'olivar_datos_preparados.csv', 'resumen_campanas.csv'})
            cargado = pd.read_csv(carpeta / 'olivar_datos_preparados.csv', sep=';', decimal=',')
            pd.testing.assert_frame_equal(cargado, self.df.loc[:, list(olivar.COLUMNAS)])
            regional = pd.read_csv(carpeta / 'resumen_campanas.csv', sep=';', decimal=',', index_col=0)
            pd.testing.assert_frame_equal(regional, resumen)
        self.assertEqual(huella(self.entrada), antes)

    def test_matplotlib_ausente_permite_exportar_csv(self):
        destino = self.raiz / 'csv'
        with patch.object(olivar, 'find_spec', return_value=None):
            codigo, salida, errores = self.ejecutar([
                '--entrada', str(self.entrada), '--salida', str(destino)])
        self.assertEqual(codigo, 0, errores)
        self.assertIn('PNG omitido', salida)
        self.assertNotIn(str(self.raiz), salida + errores)
        self.assertEqual(len(list(destino.rglob('*.csv'))), 2)
        self.assertEqual(len(list(destino.rglob('*.png'))), 0)

    @unittest.skipUnless(olivar.find_spec('matplotlib'), 'Complemento gráfico no instalado')
    def test_png_y_cierre_de_figuras(self):
        from matplotlib import image, pyplot as plt
        resumen, _ = olivar.calcular_resumen(self.df)
        destino = olivar.exportar_resultados(self.df, resumen, self.raiz / 'grafico', True)
        pixeles = image.imread(destino / 'dispersion_lluvia_produccion.png')
        self.assertEqual(pixeles.shape[:2], (1800, 3000))
        self.assertGreater(float(pixeles.max() - pixeles.min()), 0)
        self.assertEqual(plt.get_fignums(), [])

    def test_errores_de_lectura_y_dependencias(self):
        self.entrada.write_bytes(b'No es un libro Excel')
        codigo, _, errores = self.ejecutar(['--entrada', str(self.entrada), '--comprobar'])
        self.assertEqual(codigo, 1)
        self.assertIn('integridad', errores)
        with patch.object(olivar, 'cargar_datos', side_effect=ImportError):
            codigo, _, errores = self.ejecutar(['--entrada', str(self.entrada)])
        self.assertEqual(codigo, 1)
        self.assertIn('dependencia', errores)

    def test_cli_rutas_relativas_y_entrada_obligatoria(self):
        resultado = self.cli('--entrada', 'entrada.xlsx', '--salida', 'salidas', '--comprobar')
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertFalse((self.raiz / 'salidas').exists())
        self.assertNotIn(str(self.raiz), resultado.stdout + resultado.stderr)
        self.assertEqual(self.cli('--comprobar').returncode, 2)
        ausente = self.cli('--entrada', 'ausente.xlsx')
        self.assertEqual(ausente.returncode, 1)
        self.assertFalse((self.raiz / 'resultados').exists())

    def test_importacion_sin_efectos(self):
        antes = {p.name:huella(p) for p in self.raiz.iterdir()}
        resultado = subprocess.run([
            sys.executable, '-B', '-c',
            'import runpy, sys; runpy.run_path(sys.argv[1], run_name="solo_importacion")',
            str(SCRIPT)], cwd=self.raiz, capture_output=True, text=True,
            encoding='utf-8', timeout=30, check=False)
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertEqual(resultado.stdout, '')
        self.assertEqual({p.name:huella(p) for p in self.raiz.iterdir()}, antes)


if __name__ == '__main__':
    unittest.main()
