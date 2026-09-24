# Clase guiada (40 min): limpieza y estructura de datos de RRHH

Guía para el mentor. Dataset: [IBM HR Employee Attrition](https://www.kaggle.com/datasets/nibeditasahu/ibm-hr-employee-attrition-analysis) (Kaggle).

## Archivos

| Archivo | Para quién | Qué es |
|---|---|---|
| `clase_alumno.ipynb` | Mentee | Notebook con explicaciones y 8 ejercicios ✏️ **sin resolver** |
| `solucion_mentor.ipynb` | Mentor | El mismo notebook resuelto y ejecutado (no compartir antes de la clase) |
| `ensuciar_datos.py` | Los dos | Genera `HR_sucio.csv` a partir del CSV original |

## Por qué "ensuciamos" los datos

El CSV de IBM es sintético y viene casi perfecto: no tiene nulos ni duplicados. Si se limpia tal cual, la clase dura 5 minutos
y no se aprende nada. `ensuciar_datos.py` le agrega los problemas típicos de un export real de un sistema de RRHH
(semilla fija, así mentor y mentee ven los mismos números):

- 29 filas duplicadas
- `Department`, `Gender`, `Attrition` y `OverTime` escritos de varias formas (`R&D`, `sales `, `M`, `Fem`, `Si`, `N`…)
- `MonthlyIncome` guardado como texto en algunas filas (`"$5,993"`)
- 4 edades imposibles (-1, 4, 150, 999)
- Nulos en `MonthlyIncome`, `DistanceFromHome` y `Department`

Contale esto al mentee de entrada: es honesto, y también es una lección en sí misma ("los datasets de Kaggle no se parecen a los de una empresa").

## Preparación (antes de la clase, 10 min)

1. Que el mentee descargue el CSV de Kaggle (que lo haga él es parte del ejercicio).
2. `pip install pandas numpy jupyter`
3. `python ensuciar_datos.py WA_Fn-UseC_-HR-Employee-Attrition.csv` → genera `HR_sucio.csv` (el nombre del CSV puede variar según la versión de Kaggle).
4. Correr la primera celda del notebook para confirmar que carga.

## Agenda

| Min | Bloque | Vos hacés | Él hace |
|---|---|---|---|
| 0–5 | Contexto | Presentás la pregunta de negocio y las 3 reglas (no pisar el original, diagnosticar antes de limpiar, dejar escrita cada decisión) | Escucha y cuenta qué espera encontrar |
| 5–10 | Cargar y mirar | Mostrás `read_csv`, `head`, `info` | Detecta que `MonthlyIncome` es texto |
| 10–17 | Diagnosticar | Mostrás el conteo de nulos | Ej. 1 (duplicados y columnas constantes) y Ej. 2 (inconsistencias de texto). Completan juntos la lista de problemas |
| 17–30 | Limpiar | Mostrás duplicados, `Department`, conversión del sueldo e imputación por `JobLevel` | Ej. 3 a 6: columnas constantes, `Gender`/booleanos, edades, nulos |
| 30–35 | Estructurar | Mostrás escalas 1–4 → etiquetas ordenadas | Ej. 7: tramos y **una variable inventada por él desde RRHH** |
| 35–40 | Validar y cierre | Mostrás `chequear()` y la bitácora | Ej. 8: dos chequeos propios. Preguntas de cierre |

**Si se atrasan:** el Ej. 7 c) y el Ej. 8 pueden quedar de tarea. No saltees el bloque 5: validar es lo que más se transfiere a un trabajo real.

## Cómo ayudar sin hacerle la tarea

- **Primero pregunta, después pista, recién después código.** Cada ejercicio tiene una pista en el comentario; si se traba más de 2 minutos, dale la siguiente pista verbal, no la solución.
- **Las decisiones son de él.** Rango de edad válido, cortes de los tramos, qué hacer con los "Manager" sin departamento: no hay una respuesta única. Pedile que la justifique, no que adivine la tuya.
- **Aprovechá su perfil de RRHH.** Él sabe más que el dataset sobre por qué se va la gente. El Ej. 7 c) y la pregunta de cierre "¿qué columna falta?" están pensadas para que ese conocimiento aparezca.
- **La clase enseña el método, no resuelve su proyecto.** El análisis de rotación (EDA, modelo) queda enteramente para él.

## Preguntas para disparar discusión

- ¿Borramos la fila con edad 999 o solo el dato? (se pierde el resto de la información de esa persona)
- ¿Por qué imputar el sueldo con la mediana **del nivel** y no la general? (un gerente no gana lo mismo que un analista)
- ¿Por qué dejamos una columna `sueldo_imputado`? (transparencia: después se puede ver si los imputados distorsionan algo)
- `DailyRate`, `HourlyRate` y `MonthlyRate` casi no se correlacionan con `MonthlyIncome`. ¿Qué son? Si no se puede explicar una columna, no se usa sin preguntar.
- Ética: `Gender`, `Age` y `MaritalStatus` sirven para **detectar** inequidades; usarlos para **decidir** sobre personas es otra cosa.

## Tarea para la próxima (la hace él)

1. Subir `HR_limpio.csv` a MySQL (`sqlalchemy.create_engine` + `df.to_sql`), como le recomendó el docente, y repetir dos chequeos en SQL.
2. Análisis exploratorio: tasa de rotación por `Department`, `OverTime`, `tramo_edad` y `JobSatisfaction_txt`.
3. Traer 3 hallazgos y 1 pregunta que no haya podido responder.

## Puente con su idea original (agro)

Su primera propuesta (demanda de trabajadores temporarios en cosecha, con datos de la Secretaría de Agricultura y RENATRE) tiene los mismos problemas, pero más fuertes:
nombres de departamentos/provincias escritos distinto entre fuentes, campañas como texto (`"2022/23"`), nulos por departamentos sin dato y la necesidad de **unir** varias fuentes.
Lo de hoy (normalizar texto, convertir tipos, imputar con criterio, validar) es exactamente lo que va a necesitar si vuelve a ese proyecto.
