# Valores esperados de las medidas

Si una medida da distinto en Power BI, hay un error en la consulta, en la relación o en la fórmula. Todos los valores se calcularon con `generar_modelo.py` y los de agro se verificaron además con SQL directo sobre MySQL.

## Filas por tabla (después de Cerrar y aplicar)

| Tabla | Filas |
|---|---|
| `fact_agro` | 147.272 |
| `fact_agro_detalle` | 13.227 |
| `dim_cultivo` | 41 |
| `dim_geografia` | 508 |
| `dim_campania` | 56 |
| `fact_rrhh` | 1.470 |
| `dim_puesto` | 11 |

## RRHH, sin filtros

| Medida | Valor |
|---|---|
| Empleados | 1.470 |
| Bajas | 237 |
| Tasa de Rotación | 16,1% |
| Sueldo Promedio | 6.503 |
| % Con Horas Extra | 28% |
| Rotación con Horas Extra | 30,5% |
| Rotación sin Horas Extra | 10,4% |
| Multiplicador Horas Extra | 2,9 |
| Antigüedad Promedio (años) | 7,0 |

### Tasa de Rotación por área

| Área | Empleados | Rotación | Sueldo promedio |
|---|---|---|---|
| Investigación y Desarrollo | 961 | 13,8% | 6.281 |
| Recursos Humanos | 63 | 19,0% | 6.655 |
| Ventas | 446 | 20,6% | 6.959 |

### Tasa de Rotación por puesto

| Puesto | Empleados | Rotación |
|---|---|---|
| Representante de ventas | 83 | 39,8% |
| Técnico de laboratorio | 259 | 23,9% |
| Analista de RRHH | 52 | 23,1% |
| Ejecutivo de ventas | 326 | 17,5% |
| Científico investigador | 292 | 16,1% |
| Director de manufactura | 145 | 6,9% |
| Representante de salud | 131 | 6,9% |
| Gerente | 102 | 4,9% |
| Director de investigación | 80 | 2,5% |

### Tasa de Rotación por tramo de edad

| Valor | Empleados | Rotación |
|---|---|---|
| 18-25 | 123 | 35,8% |
| 26-35 | 606 | 19,1% |
| 36-45 | 468 | 9,2% |
| 46-55 | 226 | 11,5% |
| 56+ | 47 | 17,0% |

### Tasa de Rotación por antigüedad

| Valor | Empleados | Rotación |
|---|---|---|
| <1 | 44 | 36,4% |
| 1-2 | 298 | 28,9% |
| 3-5 | 434 | 13,8% |
| 6-10 | 448 | 12,3% |
| +10 | 246 | 8,1% |

### Tasa de Rotación por satisfacción laboral

| Valor | Empleados | Rotación |
|---|---|---|
| Baja | 289 | 22,8% |
| Media | 280 | 16,4% |
| Alta | 442 | 16,5% |
| Muy alta | 459 | 11,3% |

### Tasa de Rotación por frecuencia de viajes

| Valor | Empleados | Rotación |
|---|---|---|
| No viaja | 150 | 8,0% |
| Viaja poco | 1.043 | 15,0% |
| Viaja seguido | 277 | 24,9% |

## Agro, con el segmentador en la campaña 2024/2025

| Medida | Valor |
|---|---|
| Superficie Sembrada (ha) | 43.806.874 |
| Superficie Cosechada (ha) | 38.464.199 |
| Producción (t) | 141.311.687 |
| Rendimiento (kg/ha) | 3.674 |
| Rendimiento promedio simple (NO USAR) | 2.840 |
| % Cosechado | 88% |
| Producción Campaña Anterior | 140.160.203 |
| Variación Interanual % | 0,8% |

Con el segmentador en **2022/2023** (la sequía): Producción (t) = 96.134.972 y Variación Interanual % = -33,0%.

### Superficie sembrada 2024/2025 por región

| Región | Hectáreas |
|---|---|
| Pampeana | 36.268.767 |
| NOA | 4.828.909 |
| NEA | 1.697.458 |
| Cuyo | 1.011.740 |

### Por grupo de cultivo, 2024/2025 (top 8)

| Grupo | Sembrada (ha) | Producción (t) |
|---|---|---|
| Soja | 17.994.965 | 51.107.839 |
| Maíz | 9.234.043 | 51.690.953 |
| Trigo | 6.550.169 | 18.510.280 |
| Girasol | 2.413.081 | 5.592.453 |
| Cebada | 1.690.458 | 4.823.506 |
| Avena | 1.432.632 | 556.060 |
| Sorgo | 1.005.799 | 2.853.150 |
| Centeno | 957.215 | 215.369 |

### Soja de primera y de segunda, 2024/2025 (medida de detalle)

| Cultivo | Sembrada (ha) |
|---|---|
| soja 1ra | 12.483.086 |
| soja 2da | 5.511.879 |

### % Cosechado, todas las campañas (los 6 más bajos)

| Cultivo | % Cosechado |
|---|---|
| Cebada forrajera | 13% |
| Centeno | 16% |
| Avena | 21% |
| Mijo | 57% |
| Mandarina | 78% |
| Jojoba | 78% |

Filas con alerta de cosechado mayor a sembrado (en `fact_agro_detalle`): 11.
