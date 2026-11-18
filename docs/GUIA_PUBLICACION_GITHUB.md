# Guía paso a paso para publicar OLIVAR 360° en GitHub

## Método recomendado: repositorio nuevo y limpio (Windows + VS Code)

1. Crear un repositorio público nuevo en github.com llamado `OLIVAR-360`, **sin marcar** «Add a README» ni `.gitignore` (ya existen en esta carpeta).
2. Descomprimir el paquete `OLIVAR_360_GITHUB.zip` en una carpeta de trabajo aparte. No mezclarlo todavía con el directorio completo de datos y scripts.
3. Abrir esa carpeta en VS Code: **Archivo → Abrir carpeta**.
4. Incorporar cuatro capturas propias en `imagenes/` con nombres `01_panorama.png`, `02_costes.png`, `03_clima.png`, `04_competitividad.png` (recortar las interfaces y rutas locales).
5. Revisar README, metodología, derechos y datos sensibles. El archivo `.gitignore` excluye por defecto fuentes grandes y potencialmente no autorizadas.
6. En **Terminal → Nuevo terminal**, ejecutar `git status`; si aparece «not a git repository», ejecutar `git init` y `git branch -M main`.
7. Ejecutar `git add README.md .gitignore docs/ imagenes/` (solo archivos de este paquete revisado), después `git status` y comprobar qué se publicará.
8. Ejecutar `git commit -m "Documenta proyecto OLIVAR 360"`.
9. En GitHub, copiar la URL HTTPS de tu repositorio; ejecutar `git remote add origin https://github.com/TU_USUARIO/OLIVAR-360.git` sustituyendo el usuario; si ya existe `origin`, usar `git remote -v` y resolver antes de añadir otro.
10. Ejecutar `git push -u origin main`; completar el inicio de sesión solicitado por Git/GitHub.
11. Abrir la página del repositorio y confirmar que README, docs e imágenes aparecen correctamente.

> Si `git status` revela que estás dentro de otro repositorio o si el repositorio remoto ya contiene commits, **no sobreescribas nada**; revisa `git remote -v`, `git branch` y el historial antes de hacer push. Evita `--force`.

## Qué se publica y qué no

**Sí:** README, metodología, diccionario, resultados con caveats y capturas propias. Opcionalmente scripts propios revisados y un PBIX autorizado/comprobado.

**No automáticamente:** base completa de XML RAIF, libros originales de terceros, copias `.bak`, tokens, perfiles personales, cachés, archivos privados, PBIX no revisado.

## Tamaño PBIX

GitHub bloquea ficheros individuales mayores de 100 MiB en Git normal; para binarios grandes existe Git LFS. Antes de subir un `.pbix`, revisa tamaño, datos embebidos, permisos y conveniencia de publicar una versión de demostración.

## Alternativa solo web

En la página del repositorio: **Add file → Upload files**, arrastrar archivos y confirmar «Commit changes». Para conservar carpetas, subir contenido de la estructura `docs/` e `imagenes/` y verificar rutas; la ruta por VS Code/Git suele ser más clara para múltiples archivos.

## Comprobación final

- [ ] URL pública abre el README correctamente
- [ ] Las cuatro capturas se ven
- [ ] No hay datos con derechos dudosos ni secretos
- [ ] La advertencia sobre causalidad y provisionalidad es visible
- [ ] Enlaces de documentación funcionan
