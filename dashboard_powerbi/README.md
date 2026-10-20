# Dashboard RRHH y Agro (Power Query + Power BI)

El dashboard terminado que proponía `guia_powerbi_dashboard/`: modelo, consultas, medidas, tema,
vista previa y la guía para explicarlo en clase.

## Qué hay y para qué sirve

| Archivo | Para qué |
|---|---|
| `GUIA_CLASE_MENTOR.md` | **Empezá por acá.** Clase dinámica de 60 min para explicarle al mentee cómo se hizo |
| `PASO_A_PASO_POWERBI.md` | Construcción del .pbix clic a clic, con controles de números en cada etapa |
| `vista_previa_dashboard.html` | Cómo tiene que quedar: las 3 páginas con los datos reales (se abre en cualquier navegador) |
| `datos/modelo_rrhh_agro.xlsx` | Las 7 tablas del modelo estrella, ya preparadas (atajo si MySQL falla) |
| `power_query/*.pq` | Las consultas M que hacen la preparación desde MySQL (el camino que enseña Power Query) |
| `dax/medidas.dax` | Las 23 medidas, con el formato de cada una |
| `dax/valores_esperados.md` | Lo que tiene que dar cada medida, para validar el .pbix |
| `tema/tema_rrhh_agro.json` | Tema de Power BI: paleta validada para daltonismo, fondos, bordes y fuentes |
| `generar_modelo.py` | Implementación de referencia en Python de las mismas transformaciones |

## El modelo

Dos esquemas estrella independientes (no hay ninguna clave en común entre RRHH y agro):

- **Agro:** `fact_agro` (147.272 filas) y `fact_agro_detalle` (13.227) con `dim_cultivo`, `dim_geografia`, `dim_campania`.
- **RRHH:** `fact_rrhh` (1.470 filas) con `dim_puesto`.

## Qué no incluye

- **El archivo .pbix.** Es un binario que solo genera Power BI Desktop (Windows). Se arma en 60 a 90 minutos con
  `PASO_A_PASO_POWERBI.md`; todo lo que hay que pegar o importar ya está en esta carpeta.
- **Pruebas dentro de Power BI.** Las consultas M y las medidas DAX no se pudieron ejecutar acá. Las mismas
  transformaciones sí se ejecutaron en Python (`generar_modelo.py`) y los totales de agro se verificaron con SQL
  directo sobre MySQL: si una medida da distinto que `dax/valores_esperados.md`, el error está en el .pbix.

## Regenerar el Excel y los valores esperados

```
python generar_modelo.py estimaciones-agricolas-2026-03.csv IBM_HR_Employee_Attrition_Data.csv .
```

Requiere `pandas` y `openpyxl`.
