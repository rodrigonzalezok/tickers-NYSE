-- Métricas para practicar sobre rrhh_attrition y estimaciones_agricolas.
-- Cada bloque corresponde a un punto de README.md. Los que en el README
-- tienen ✏️ (para completar) aparecen aquí ya resueltos, como referencia
-- del mentor -- no se los muestres a tu mentee antes de que lo intente.

USE practica_mentee;

-- ============================= RRHH =============================

-- 1. Sueldo promedio por departamento
SELECT department, ROUND(AVG(monthly_income)) AS sueldo_promedio, COUNT(*) AS empleados
FROM rrhh_attrition
GROUP BY department;

-- 2. Tasa de rotación por puesto
SELECT job_role, ROUND(100 * SUM(attrition = 'Yes') / COUNT(*), 1) AS tasa_rotacion
FROM rrhh_attrition
GROUP BY job_role
ORDER BY tasa_rotacion DESC;

-- 3. Rotación segun horas extra
SELECT over_time, ROUND(100 * SUM(attrition = 'Yes') / COUNT(*), 1) AS tasa_rotacion
FROM rrhh_attrition
GROUP BY over_time;

-- 4. Antiguedad promedio: se van vs. se quedan
SELECT attrition, ROUND(AVG(years_at_company), 1) AS antiguedad_promedio
FROM rrhh_attrition
GROUP BY attrition;

-- 5. Satisfaccion laboral segun rotacion
SELECT attrition, ROUND(AVG(job_satisfaction), 2) AS satisfaccion_promedio
FROM rrhh_attrition
GROUP BY attrition;

-- 6. Top 5 combinaciones puesto + departamento con mas gente
SELECT department, job_role, COUNT(*) AS empleados
FROM rrhh_attrition
GROUP BY department, job_role
ORDER BY empleados DESC
LIMIT 5;

-- 7. Rotacion por tramo de edad
SELECT
  CASE
    WHEN age < 25 THEN '<25'
    WHEN age < 35 THEN '25-34'
    WHEN age < 45 THEN '35-44'
    ELSE '45+'
  END AS tramo_edad,
  COUNT(*) AS empleados,
  ROUND(100 * SUM(attrition = 'Yes') / COUNT(*), 1) AS tasa_rotacion
FROM rrhh_attrition
GROUP BY tramo_edad
ORDER BY tramo_edad;

-- ============================= AGRO ==============================

-- 8. Rendimiento promedio por cultivo, un año dado
SELECT cultivo, ROUND(AVG(rendimiento_kgxha)) AS rendimiento_promedio
FROM estimaciones_agricolas
WHERE anio = 2023
GROUP BY cultivo
ORDER BY rendimiento_promedio DESC
LIMIT 5;

-- 9. Superficie sembrada por cultivo y provincia, ultimo año
SELECT provincia, cultivo, SUM(superficie_sembrada_ha) AS superficie_total
FROM estimaciones_agricolas
WHERE anio = (SELECT MAX(anio) FROM estimaciones_agricolas)
GROUP BY provincia, cultivo
ORDER BY superficie_total DESC
LIMIT 10;

-- 10. Evolucion del rendimiento de un cultivo a traves de los años
SELECT anio, ROUND(AVG(rendimiento_kgxha)) AS rendimiento_promedio
FROM estimaciones_agricolas
WHERE cultivo = 'soja total'
GROUP BY anio
ORDER BY anio;

-- 11. Ranking de provincias por superficie sembrada total, ultimo año
SELECT provincia, SUM(superficie_sembrada_ha) AS superficie_total
FROM estimaciones_agricolas
WHERE anio = (SELECT MAX(anio) FROM estimaciones_agricolas)
GROUP BY provincia
ORDER BY superficie_total DESC;

-- 12. Eficiencia cosechado/sembrado por cultivo (menor a mayor = mas perdida)
SELECT cultivo, ROUND(100 * SUM(superficie_cosechada_ha) / SUM(superficie_sembrada_ha), 1) AS pct_cosechado
FROM estimaciones_agricolas
GROUP BY cultivo
ORDER BY pct_cosechado ASC
LIMIT 5;

-- 13. Produccion total por decada, para 3 cultivos clave
SELECT FLOOR(anio / 10) * 10 AS decada, cultivo, SUM(produccion_tm) AS produccion_total
FROM estimaciones_agricolas
WHERE cultivo IN ('soja total', 'maíz', 'trigo')
GROUP BY decada, cultivo
ORDER BY cultivo, decada;
