# Guía de clase: "Así se armó el dashboard"

**Para vos, el mentor.** Una clase dinámica de 60 minutos para explicarle a tu mentee cómo se construyó el
dashboard de RRHH y Agro: qué se decidió, por qué, y dónde están las trampas.
No es una clase de "mirá lo que hice": en cada bloque él predice, prueba o corrige algo antes de que le muestres
la respuesta.

**Material:**
- La vista previa (`vista_previa_dashboard.html`, o el link del artifact) abierta en una pestaña.
- El `.pbix` armado con `PASO_A_PASO_POWERBI.md`, o Power BI Desktop con el Excel `datos/modelo_rrhh_agro.xlsx`.
- `dax/valores_esperados.md` a mano, para los números.

---

## Antes de la clase (15 min, una sola vez)

1. Armá el .pbix siguiendo `PASO_A_PASO_POWERBI.md` (usá la opción B, Excel, si no querés depender de MySQL).
2. Guardá **dos copias**: `dashboard_completo.pbix` y `dashboard_para_practicar.pbix`.
   En la segunda borrá tres cosas: la medida `Rendimiento (kg/ha)`, el visual "Rotación por puesto" y las
   relaciones de `fact_agro_detalle`. Son los tres ejercicios de la clase.
3. Tené a mano estos números, son los que van a aparecer en la conversación:

| Dato | Valor |
|---|---|
| Rotación de la empresa | 16,1% (237 de 1.470) |
| Rotación con / sin horas extra | 30,5% / 10,4% → 2,9 veces |
| Puesto con más rotación | Representante de ventas, 39,8% |
| Rotación con menos de 1 año / más de 10 años | 36% / 8% |
| Producción 2024/25 | 141,3 millones de t |
| Caída por la sequía 2022/23 | −33% |
| Rinde ponderado vs promedio simple, 2024/25 | 3.674 vs 2.840 kg/ha |

---

## Estructura (60 min)

| Min | Bloque | Dinámica |
|---|---|---|
| 0–5 | 1. El final primero | Le mostrás el dashboard terminado y le preguntás qué ve |
| 5–15 | 2. La decisión que vino antes de todo | Discusión: ¿por qué dos páginas y no una? |
| 15–30 | 3. Power Query: las 4 trampas de los datos | Él predice, vos mostrás el paso que lo resuelve |
| 30–40 | 4. El modelo estrella | Ejercicio: reconectar las relaciones que borraste |
| 40–52 | 5. DAX: la medida que miente | Ejercicio: escribir el rinde y compararlo con el promedio simple |
| 52–58 | 6. Diseño: por qué se ve así | Él arma el visual de puestos con color condicional |
| 58–60 | 7. Cierre y tarea | Tres preguntas + la tarea |

---

## Bloque 1 · El final primero (0–5 min)

Abrí la vista previa en la página RRHH. **No expliques nada todavía.** Preguntale:

> "Tenés 30 segundos. Si fueras gerente de RRHH de esta empresa, ¿qué es lo primero que harías mañana?"

Lo que debería ver (si no lo ve, es una pista de que el diseño falla, y vale discutirlo):
- Las horas extra casi triplican la rotación.
- Representante de ventas y técnico de laboratorio están muy por encima del promedio.
- El primer año es el más crítico (36% se va).

**Mensaje del bloque:** un dashboard se juzga por la decisión que habilita, no por cuántos gráficos tiene.
Todo lo que viene después explica cómo se llegó a que esos tres mensajes se lean en 30 segundos.

---

## Bloque 2 · La decisión que vino antes de todo (5–15 min)

Pasá a la página "Notas y supuestos". Preguntale:

> "En tu proyecto querías cruzar rotación con demanda de mano de obra en cosecha. ¿Por qué este dashboard tiene
> dos páginas separadas y no una sola que las cruce?"

Dejalo pensar. La respuesta: **no hay ninguna columna en común**. RRHH es una empresa ficticia de EE.UU. sin
ubicación ni fechas; agro son departamentos argentinos por campaña. Cualquier `JOIN` sería inventado.

Llevalo a su proyecto con dos preguntas:
1. "Si tuvieras que unirlas, ¿qué tabla nueva necesitarías y de dónde sacarías los datos?"
   (Ej.: trabajadores temporarios por hectárea según cultivo, de RENATRE o de un supuesto escrito.)
2. "¿Dónde pondrías ese supuesto para que nadie lo tome como dato real?" (En una página de notas como esta.)

**Mensaje del bloque:** separar es una decisión válida. Lo que no es válido es cruzar sin decirlo.

---

## Bloque 3 · Power Query: las 4 trampas de los datos (15–30 min)

Abrí el Editor de Power Query del .pbix completo. Para cada trampa: primero le das la pista,
**él adivina el problema**, y recién ahí le mostrás el paso que lo resuelve (panel "Pasos aplicados").

### Trampa 1: la soja se cuenta dos veces

- **Pista:** "En la tabla original hay tres cultivos: soja total, soja 1ra y soja 2da. ¿Qué pasa si sumo todo?"
- **Problema:** soja total ya es 1ra + 2da (desde 2000). Lo mismo con poroto (por tipo) y trigo candeal.
  Sumar todo infla la superficie de soja casi al doble.
- **Solución:** `dim_cultivo` marca `es_desagregado`, y `fact_agro` excluye esas filas. Van a una tabla aparte,
  `fact_agro_detalle`, que solo usa el visual "Soja de primera y de segunda".
- **Por qué en Power Query y no en DAX:** si se resuelve en la preparación, *cualquier* SUM que escriba después
  es correcta. Si se resuelve en una fórmula, hay que acordarse en cada fórmula.

### Trampa 2: el "año" no significa lo mismo para todos

- **Pista:** "Para el té, la campaña 1969/1970 tiene anio = 1970. Para el maíz, la campaña 1970/1971 tiene anio = 1970.
  ¿Qué pasa si grafico por año?"
- **Problema:** se mezclan campañas distintas en el mismo punto del eje.
- **Solución:** el eje de tiempo es `campania`, con su primer año (`anio_inicio`) para ordenar y graficar.
- **Mensaje:** antes de usar una columna, verificá que signifique lo mismo en todas las filas.

### Trampa 3: producción sin superficie

- **Pista:** "Naranja, mandarina, limón, pomelo y banana, entre 1969 y 1975: tienen toneladas pero 0 hectáreas cosechadas.
  ¿Qué le pasa a un rendimiento calculado como toneladas / hectáreas?"
- **Problema:** el numerador suma toneladas que no tienen hectáreas en el denominador: el rinde sale inflado.
- **Solución:** la medida de rendimiento solo usa la producción de filas con superficie cosechada > 0 (lo ven en el bloque 5).

### Trampa 4: tablas en inglés con códigos

- Mostrale `fact_rrhh` antes y después: `Attrition = Yes` pasó a `estado = "Se fue"` y `baja = 1`;
  `JobSatisfaction = 1` pasó a `satisfaccion_laboral = "Baja"` con su columna `_orden` para que el eje no quede
  alfabético ("Alta, Baja, Media, Muy alta").
- **Pregunta:** "¿Por qué guardamos `baja` como número 1/0 además del texto?" (Porque sumar unos es contar
  bajas, y promediar unos y ceros es la tasa de rotación.)

**Cierre del bloque:** abrí la página de notas y mostrale que las cuatro decisiones están escritas ahí.
Es la misma bitácora de decisiones de la clase de limpieza en pandas, pero en Power BI.

---

## Bloque 4 · El modelo estrella (30–40 min)

**Ejercicio (en `dashboard_para_practicar.pbix`):** abrí la vista de Modelo. Las relaciones de
`fact_agro_detalle` no están. Pedile que:

1. Las cree él (arrastrando columnas): `cultivo`, `campania`, `departamento_id` hacia sus dimensiones.
2. Explique por qué la flecha va desde la dimensión hacia el hecho y no al revés.
3. Diga qué pasaría con el visual "Soja de primera y de segunda" si no existiera la relación con `dim_campania`.
   (El segmentador de campaña no lo filtraría: mostraría la suma de todas las campañas.)

Después mostrale el diagrama completo y señalá las dos "islas": RRHH y agro no están unidas. Volvé al bloque 2:
esa ausencia de línea es la decisión de no inventar un cruce.

**Pregunta extra:** "¿Por qué `dim_geografia` usa `departamento_id` y no el nombre del departamento?"
(Hay nombres repetidos entre provincias: "San Martín", "Belgrano", "General Roca"...)

---

## Bloque 5 · DAX: la medida que miente (40–52 min)

**Ejercicio (en `dashboard_para_practicar.pbix`):** la medida `Rendimiento (kg/ha)` no está.

1. Pedile que la escriba él, como le parezca. Lo más probable es que escriba
   `AVERAGE(fact_agro[rendimiento_fila_kgxha])`. Que la ponga en una tarjeta con la campaña 2024/2025:
   va a dar **2.840**.
2. Mostrale `Rendimiento (kg/ha)` del .pbix completo: **3.674**. Preguntale: "¿Cuál está bien y por qué?"
3. La explicación, con un ejemplo de pizarrón:
   - Lote A: 10 ha, rinde 1.000 kg/ha (10 t).
   - Lote B: 1.000 ha, rinde 4.000 kg/ha (4.000 t).
   - Promedio simple: (1.000 + 4.000) / 2 = **2.500 kg/ha**.
   - Ponderado: 4.010 t / 1.010 ha = **3.970 kg/ha**. Este es el real: casi todo el campo rinde 4.000.
4. Que la reescriba como `DIVIDE(SUM(produccion) * 1000, SUM(superficie_cosechada))` y compare.
   Después mostrale la versión final, con el `CALCULATE(..., superficie_cosechada_ha > 0)` de la trampa 3.

**Mensaje del bloque:** nunca se promedia una tasa. Se suman numerador y denominador por separado y se divide al final.
Pasa lo mismo con la rotación: por eso `Tasa de Rotación` es `DIVIDE([Bajas], [Empleados])` y no un promedio
de tasas por área.

**Si sobra tiempo:** mostrale `Producción Campaña Anterior`. Sin tabla de calendario no existe
`SAMEPERIODLASTYEAR`, así que se mueve el filtro a mano con `REMOVEFILTERS` + `anio_inicio - 1`.
Que pruebe el segmentador en 2022/2023 y vea la caída de −33% de la sequía.

---

## Bloque 6 · Diseño: por qué se ve así (52–58 min)

**Ejercicio:** en `dashboard_para_practicar.pbix` falta el visual "Rotación por puesto". Que lo arme
siguiendo la etapa 5 del paso a paso, punto 4: barras horizontales, ordenadas, color por `Color Rotación`
y línea constante con `Tasa de Rotación (empresa)`.

Mientras lo arma, preguntale por cada decisión de diseño:

| Decisión | Pregunta para él | Por qué |
|---|---|---|
| Solo naranja y gris, no un color por puesto | "¿Qué te dice el color acá?" | El color marca *una* cosa: estar por encima del promedio. Nueve colores no dirían nada. |
| Horas extra en números grandes, sin gráfico | "¿Para qué un gráfico de dos barras?" | Cuando el mensaje es un número, el número es el gráfico. |
| Línea en vez de barras para producción | "¿Por qué no columnas?" | Es evolución en el tiempo: la línea muestra la tendencia y la caída de 2022. |
| Ninguna torta | "¿Con 41 cultivos, cómo se vería una torta?" | Ilegible. Barras ordenadas comparan mejor. |
| Escala de un solo color en el mapa de calor | "¿Por qué no rojo-amarillo-verde?" | Más oscuro = más rotación se entiende solo, y lo leen también los daltónicos. |
| Página de notas | "¿Quién la va a leer?" | Quien dude de un número. Es lo que hace confiable al resto. |

El tema (`tema/tema_rrhh_agro.json`) define la paleta una sola vez para todo el informe, y fue validada
para daltonismo. Por eso los colores no se cambian a mano visual por visual.

---

## Bloque 7 · Cierre y tarea (58–60 min)

**Tres preguntas para que responda en voz alta:**
1. De las cuatro trampas de los datos, ¿cuál te hubiera pasado inadvertida?
2. Si tuvieras que agregar una página que cruce rotación y cosecha para tu proyecto, ¿qué tabla nueva harías
   y qué supuesto escribirías en la página de notas?
3. ¿Qué medida de este dashboard le mostrarías primero a un productor agropecuario, y por qué?

**Tarea para la próxima:**
1. Agregar al dashboard un segmentador de `viajes` en la página RRHH y contar qué cambia
   (la rotación de quienes viajan seguido es 24,9% vs 8,0% de quienes no viajan).
2. Escribir una medida nueva, `Bajas en el primer año`, y ponerla en una tarjeta. Valor esperado: 16
   (16 de los 44 empleados con menos de un año se fueron).
3. Proponer por escrito la tabla puente para su proyecto: columnas, fuente y supuesto.

---

## Si algo sale mal en vivo

| Síntoma | Causa probable | Arreglo |
|---|---|---|
| `dim_cultivo` tiene "Sin clasificar" | Las tildes se rompieron al importar en MySQL | Reimportar `02_agro.sql` con conexión en utf8mb4, o usar el Excel |
| Los ejes salen "+10, 1-2, 3-5, 6-10, <1" | Falta "Ordenar por columna" | Etapa 2 del paso a paso |
| La línea de producción muestra un solo punto | El segmentador de campaña la filtra | Editar interacciones → Ninguno |
| El mapa no aparece | Mapas deshabilitados en Opciones → Seguridad | Activarlos o usar el treemap |
| Una tarjeta da distinto que la guía | Relación faltante o medida mal copiada | Comparar con `dax/valores_esperados.md` |
