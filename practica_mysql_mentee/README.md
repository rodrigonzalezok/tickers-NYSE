# Práctica en MySQL Workbench: RRHH + Agro

Dos bases de datos reales para que tu mentee practique SQL, ya convertidas en scripts `.sql` probados
contra MySQL/MariaDB. Todas las queries de este documento las corrí yo antes de escribirlas.

## Archivos

| Archivo | Contenido |
|---|---|
| `01_rrhh.sql` | Tabla `rrhh_attrition`, 1.470 empleados, 35 columnas (dataset IBM HR, sin nulos ni duplicados) |
| `02_agro.sql` | Tabla `estimaciones_agricolas`, 160.499 filas: cultivo × año × provincia/departamento, 1969–2024 |
| `metricas_para_practicar.sql` | Las consultas de este documento, listas para copiar y pegar |

## Cómo importar en Workbench

1. Abrí Workbench y conectate a tu servidor local.
2. Creá una base: `CREATE DATABASE practica_mentee;` y hacé doble clic para que quede como default schema.
3. **File → Open SQL Script...** → elegís `01_rrhh.sql` → click en el rayo (⚡ Execute) para correrlo entero.
4. Repetís con `02_agro.sql`. Tarda unos segundos: son 160 mil filas en bloques de 1.000.
5. Verificación rápida:
   ```sql
   SELECT COUNT(*) FROM rrhh_attrition;             -- 1470
   SELECT COUNT(*) FROM estimaciones_agricolas;     -- 160499
   ```

Los dos scripts empiezan con `DROP TABLE IF EXISTS`, así que se pueden correr de nuevo sin problema si algo sale mal a mitad de camino.

## Las tablas

**`rrhh_attrition`** — un empleado por fila. Columnas clave: `department`, `job_role`, `attrition` ('Yes'/'No'),
`monthly_income`, `over_time`, `years_at_company`, `age`, `gender`, escalas 1–4 como `job_satisfaction` y `work_life_balance`.

**`estimaciones_agricolas`** — una fila por cultivo/año/departamento. Columnas clave: `cultivo`, `anio`, `campania`,
`provincia`, `departamento`, `superficie_sembrada_ha`, `superficie_cosechada_ha`, `produccion_tm`, `rendimiento_kgxha`.
Ojo: hay categorías compuestas como `"soja total"`, `"soja 1ra"` y `"soja 2da"` — son cosas distintas, no las sumes sin pensarlo.

---

## Métricas para RRHH

Fáciles → van directo. Con ✏️ hay una pista, no la query completa — que la termine él.

**1. Sueldo promedio por departamento**
```sql
SELECT department, ROUND(AVG(monthly_income)) AS sueldo_promedio, COUNT(*) AS empleados
FROM rrhh_attrition
GROUP BY department;
```
*(Sale: RRHH 6.655 / I+D 6.281 / Ventas 6.959 — Ventas es el que más paga en promedio pero también el más chico)*

**2. ✏️ Tasa de rotación por puesto**
Adaptá la idea de "promedio" a "porcentaje de Attrition = 'Yes'". Pista: `SUM(attrition = 'Yes')` cuenta los `Yes`
porque en SQL un `TRUE` vale 1.
```sql
SELECT job_role, ROUND(100 * SUM(attrition = 'Yes') / COUNT(*), 1) AS tasa_rotacion
FROM rrhh_attrition
GROUP BY job_role
ORDER BY tasa_rotacion DESC;
```
*(Sale: Sales Representative 39,8% — muy por encima del resto)*

**3. ✏️ ¿El overtime se relaciona con la rotación?**
Agrupá por `over_time` en vez de por puesto.
*(Sale: con horas extra 30,5% se va, sin horas extra 10,4% — una diferencia enorme)*

**4. Antigüedad promedio de quienes se van vs. quienes se quedan**
```sql
SELECT attrition, ROUND(AVG(years_at_company), 1) AS antiguedad_promedio
FROM rrhh_attrition
GROUP BY attrition;
```

**5. ✏️ Satisfacción laboral por nivel de rotación**
Mismo patrón que el punto 4, pero con `job_satisfaction` (escala 1 a 4). ¿Se ve la diferencia que esperarías?

**6. Top 5 combinaciones puesto + departamento con más gente**
```sql
SELECT department, job_role, COUNT(*) AS empleados
FROM rrhh_attrition
GROUP BY department, job_role
ORDER BY empleados DESC
LIMIT 5;
```

**7. ✏️ Tramos de edad**
Usá `CASE WHEN` para armar tramos (`<25`, `25-34`, `35-44`, `45+`) y calculá la tasa de rotación de cada tramo.
```sql
SELECT
  CASE
    WHEN age < 25 THEN '<25'
    WHEN age < 35 THEN '25-34'
    -- completá los tramos que faltan
  END AS tramo_edad,
  COUNT(*) AS empleados
FROM rrhh_attrition
GROUP BY tramo_edad;
```

---

## Métricas para Agro

**8. Promedio de rendimiento por cultivo en un año**
```sql
SELECT cultivo, ROUND(AVG(rendimiento_kgxha)) AS rendimiento_promedio
FROM estimaciones_agricolas
WHERE anio = 2023
GROUP BY cultivo
ORDER BY rendimiento_promedio DESC
LIMIT 5;
```
*(Sale: té 10.559 kg/ha, arroz 6.561, maíz 5.413... el té rinde muchísimo más por hectárea, aunque se siembra en mucha menos superficie)*

**9. ✏️ Superficie sembrada por cultivo y provincia, en el último año**
Adaptá la query 8: agrupá por `provincia` y `cultivo` en vez de solo por `cultivo`, y sumá `superficie_sembrada_ha`
en lugar de promediar el rendimiento.
*(Pista de resultado: Buenos Aires y Córdoba dominan "soja total" con más de 4 millones de hectáreas cada una)*

**10. Evolución del rendimiento de un cultivo a través de los años**
```sql
SELECT anio, ROUND(AVG(rendimiento_kgxha)) AS rendimiento_promedio
FROM estimaciones_agricolas
WHERE cultivo = 'soja total'
GROUP BY anio
ORDER BY anio;
```
Probalo con distintos cultivos (`SELECT DISTINCT cultivo FROM estimaciones_agricolas;` para ver los nombres exactos —
la soja, por ejemplo, no existe como `'soja'` sola: está `'soja 1ra'`, `'soja 2da'` y `'soja total'`).

**11. ✏️ Ranking de provincias por superficie sembrada total**
Sumá `superficie_sembrada_ha` de **todos** los cultivos, agrupando solo por `provincia`, para el año más reciente.
Pista: `WHERE anio = (SELECT MAX(anio) FROM estimaciones_agricolas)` funciona sin necesidad de saber qué año es.
*(Sale: Buenos Aires casi 20 millones de hectáreas, Córdoba 13,6 millones, Santa Fe 9,3 millones)*

**12. ✏️ Eficiencia: cosechado vs. sembrado**
Calculá, por cultivo, qué porcentaje de la superficie sembrada efectivamente se cosechó:
`100 * SUM(superficie_cosechada_ha) / SUM(superficie_sembrada_ha)`. ¿Qué cultivo tiene la brecha más grande entre
lo que se siembra y lo que se cosecha? Pensá qué factor real (clima, plagas) podría explicarlo.

**13. Décadas: ¿la producción total viene creciendo?**
```sql
SELECT FLOOR(anio / 10) * 10 AS decada, cultivo, SUM(produccion_tm) AS produccion_total
FROM estimaciones_agricolas
WHERE cultivo IN ('soja total', 'maíz', 'trigo')
GROUP BY decada, cultivo
ORDER BY cultivo, decada;
```

---

## Para ir más allá (si le sobra tiempo)

- **`JOIN` casero:** creá una tabla chica `provincias_region (provincia, region)` a mano (Pampeana, NOA, NEA, Patagonia)
  e insertale unas filas con `INSERT`. Después hacé `JOIN` con `estimaciones_agricolas` para agrupar por región.
- **Vista:** convertí la query 8 en `CREATE VIEW rendimiento_por_cultivo_2023 AS SELECT ...` para no reescribirla.
- **Subconsulta:** encontrá el cultivo con el rendimiento máximo histórico en una sola query (sin mirar el resultado a ojo).

## Nota sobre los datos

`rrhh_attrition` viene de Kaggle (IBM HR Employee Attrition) y ya está limpio: sin nulos, sin duplicados.
`estimaciones_agricolas` viene de datos abiertos de la Secretaría de Agricultura, así que tiene sus propias particularidades
reales: categorías como "X total" que ya son la suma de subcategorías, algunos ceros que representan falta de dato más que
cosecha nula, y nombres de cultivo con tilde que conviene mirar con `SELECT DISTINCT cultivo` antes de filtrar.
Si en algún momento tu mentee vuelve a su idea original (demanda de trabajadores rurales en cosecha), esta tabla es
justo la fuente de superficie/cosecha que necesitaba.
