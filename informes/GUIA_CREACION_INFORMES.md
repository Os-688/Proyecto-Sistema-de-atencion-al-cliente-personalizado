# Guia Base de Creacion de Informes

## Objetivo
Estandarizar como se crean, nombran y guardan informes para que cualquier agente
o colaborador mantenga el mismo formato.

## Estructura de carpetas
- `informes/analisis`: investigacion tecnica, causa raiz, disenos.
- `informes/resumenes`: cierres ejecutivos, consolidaciones, reportes finales.
- `informes/ejecuciones`: logs y salidas crudas de pruebas.
- `informes/revalidacion`: resultados de reruns y comparativas antes/despues.

## Convencion de nombres
Patron:

`AAAA-MM-DD_HHMM_tipo_modulo_estado_vNN.ext`

Campos:
- `AAAA-MM-DD_HHMM`: fecha y hora de generacion.
- `tipo`: `analisis`, `resumen`, `ejecucion`, `revalidacion`.
- `modulo`: alcance (ej. `suite8`, `p1`, `chat_service`).
- `estado`: `draft`, `final`, `error`, `pass`.
- `vNN`: version incremental (`v01`, `v02`, ...).

## Reglas operativas
1. No sobrescribir archivos: crear nueva version.
2. Mantener nombres en minusculas y con guion bajo.
3. Guardar logs en `ejecuciones`, no en raiz.
4. Si un informe mezcla hallazgos y cierre, guardar en `resumenes`.
5. Si se reejecuta una suite, guardar salida y JSON en `revalidacion`.
6. En la seccion de validacion, documentar comando con entorno local `.venv` activo o con interprete explicito de `.venv` para evitar ambiguedad de entorno global.

## Politica de Retencion y Archivo

1. Conservar siempre:
- `analisis/` y `resumenes/` finales (valor historico).

2. Conservar en ventana activa (recomendado 90 dias):
- `ejecuciones/` y `revalidacion/` de trabajo operativo.

3. Archivado trimestral sugerido:
- Mover evidencias antiguas a subcarpeta por periodo (ej. `revalidacion/2026Q1/`).

4. No borrar evidencia sin reemplazo:
- Si se elimina un artefacto, debe existir consolidado equivalente en `resumenes/`.

## Plantilla minima para reportes .md
Usar estas secciones:

1. Contexto
2. Problema
3. Causa raiz (si aplica)
4. Cambios aplicados
5. Validacion
6. Impacto
7. Riesgos
8. Proximos pasos

## Checklist previo a guardar
- [ ] Nombre cumple patron.
- [ ] Carpeta correcta segun tipo.
- [ ] Fecha y version actualizadas.
- [ ] Referencias de archivos verificadas.
- [ ] Seccion de validacion completada.
