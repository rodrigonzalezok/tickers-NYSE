# Guía para acompañar el dashboard de Power BI

> **Ya está hecho:** el dashboard completo que propone esta guía está en `dashboard_powerbi/`
> (modelo, consultas, medidas, tema, vista previa y guía de clase).

Para el mentor. Ideas operativas, analíticas y de diseño para ayudar a tu mentee a llevar
`rrhh_attrition` y `estimaciones_agricolas` (las tablas de `practica_mysql_mentee/`) a un dashboard
en Power Query + Power BI, sin resolvérselo.

## 0. Antes de todo: la decisión pendiente

En la revisión de sus "Definiciones del Proyecto" quedó una pregunta sin cerrar: las dos tablas
reales (RRHH de una empresa de EE.UU., agro de Argentina) **no tienen ninguna clave en común**.
No hay forma honesta de cruzarlas con un `JOIN`.

Esto no bloquea el dashboard, pero sí decide su forma. Dos caminos, cualquiera es válido:

- **A) Dos dashboards separados** (dos archivos o dos secciones del mismo .pbix, sin relación entre sí):
  uno de rotación de personal, otro de producción agrícola. Es el camino más honesto y el que recomendaría
  si no resolvió el punto anterior.
- **B) Un dashboard integrado**, pero solo si construye él mismo (en Power Query, con una tabla nueva)
  el puente que decidió en la clase anterior: una tabla sintética de "demanda de personal por campaña"
  con un supuesto explícito y documentado (ej. "se asume 1 trabajador temporario cada 15 hectáreas de
  cultivos de cosecha manual"). Si elige este camino, el supuesto tiene que estar escrito en una página
  del dashboard, no escondido en una fórmula.

Preguntale cuál de los dos eligió antes de que empiece a modelar. Si no lo sabe todavía, empezá por A:
siempre se puede integrar después.

## 1. Power Query: preparación de datos (operativo)

**Conexión:** Obtener datos → Base de datos → MySQL (necesita el conector ODBC de MySQL instalado;
si Workbench ya le anda, el conector suele estar). Alternativa sin servidor: Obtener datos → Texto/CSV,
exportando cada tabla desde Workbench con `SELECT * INTO OUTFILE` o simplemente un `SELECT *` y "Export
Resultset".

**Qué hacer en el Editor de Poder Query, por tabla** (esto ya lo practicó en la clase de limpieza —
es el mismo método, con otra herramienta):

- Verificar tipos de dato por columna (`Cambiar tipo`): que `anio` sea entero y no texto, que los
  flags como `attrition` quedaren como texto corto, no como "Any".
- Columnas que no aportan: en `rrhh_attrition` sobran `employee_count`, `over18`, `standard_hours`
  (son constantes) → `Quitar columnas`.
- Columnas calculadas **en Power Query, no en DAX**, cuando sirven para filtrar (Power Query es mejor
  para transformación de filas; DAX para agregación):
  - `estimaciones_agricolas`: una columna `decada` (`Number.RoundDown([anio]/10)*10`) y una columna
    `tipo_campania` derivada de `cultivo` (separar "soja total" de "soja 1ra"/"soja 2da" con
    `Text.Contains`) — la trampa que ya detectamos en la guía de métricas SQL reaparece acá.
  - `rrhh_attrition`: tramos de edad y de antigüedad con `Table.AddColumn` + `if...then...else`
    (el mismo criterio del notebook de limpieza, ahora en M en vez de en pandas).
- **Perfilado de columna** (pestaña Vista → Estadísticas de columna / Distribución de columna): es el
  reemplazo directo de `.isna().sum()` y `.value_counts()` que usó en la clase de limpieza. Pedile que
  lo corra sobre las dos tablas **antes** de tocar nada, igual que en esa clase.
- **Deshabilitar la carga** de cualquier tabla intermedia que solo use como paso (ej. una tabla de
  cultivos únicos para armar una dimensión) — así no infla el modelo.

## 2. Modelo de datos: pensar en esquema estrella (operativo + analítico)

Un error común al venir de SQL/pandas es llevar una sola tabla ancha a Power BI. Power BI rinde mejor
y es más fácil de mantener con **tablas de hechos chicas + tablas de dimensión**:

- `estimaciones_agricolas` → separar en una dimensión `dim_cultivo` (cultivo, categoría: cereal /
  oleaginosa / legumbre / industrial — esta categorización la arma él, no existe en la fuente) y una
  `dim_geografia` (provincia, departamento, región — Buenos Aires/Córdoba/Santa Fe = Pampeana, etc.,
  mismo agrupamiento de región que ya aparecía en sus Definiciones). La tabla de hechos queda con las
  métricas numéricas y las claves a esas dimensiones.
- `rrhh_attrition` → separar `dim_puesto` (`department`, `job_role`) de la tabla de hechos con las
  métricas numéricas por empleado.
- Como ninguna de las dos tiene una columna de fecha real (agro tiene `anio`, un número; RRHH no tiene
  fecha de ingreso/egreso), **no hace falta una tabla de calendario completa**. Alcanza con una tabla
  chica `dim_anio` para el eje temporal del lado agro. Dejá que descubra esto solo tratando de usar
  la jerarquía de fecha automática de Power BI y viendo que no aplica — es una buena lección sobre
  cuándo una tabla de calendario sirve y cuándo no.
- Marcá (o pedile que marque) las relaciones como 1 a muchos desde la dimensión hacia el hecho, con
  dirección de filtro única, salvo que tenga una razón concreta para cruzada.

## 3. Medidas DAX: dale la idea, no la fórmula completa

Para cada una, dale el nombre y qué debería devolver; que la escriba él.

**RRHH**
- `Tasa de Rotación` = empleados con `attrition = "Yes"` sobre el total, como `%`. Pista: `DIVIDE`,
  no `/` (evita el error de división por cero que ya vimos en SQL).
- `Sueldo Promedio` = promedio de `monthly_income`, con una variante por `department` para comparar.
- `Rotación con Horas Extra` = la misma tasa de rotación, pero como medida que reacciona al filtro de
  `over_time` puesto desde un slicer (no hace falta nada especial en DAX: el filtro de contexto lo hace
  solo — es un buen momento para que entienda qué es el "contexto de filtro").

**Agro**
- `Superficie Total` y `Producción Total` = `SUM` directo.
- `Rendimiento Promedio Ponderado` = cuidado acá: promediar `rendimiento_kgxha` fila a fila pondera
  igual a una parcela de 3 hectáreas que a una de 300.000. La métrica correcta es
  `DIVIDE(SUM(produccion_tm), SUM(superficie_cosechada_ha))`. Es un lindo error para que cometa primero
  y corrija después viendo que los números no cierran contra lo que sabe del sector.
- `% Cosechado sobre Sembrado` = la métrica 12 de la guía SQL, ahora en DAX.
- `Variación Interanual` = usando `dim_anio`, con `CALCULATE` moviendo el filtro de año (sin tabla de
  calendario completa no hay `SAMEPERIODLASTYEAR`, así que toca resolverlo con una columna de año
  anterior o con `OFFSET`/`INDEX` — buen desafío para alguien que ya vio funciones de ventana en SQL).

## 4. Ideas analíticas: qué contar en cada página

**Página RRHH — foto actual, no evolución** (no hay fechas, así que el dashboard cuenta un estado,
no una tendencia; decile esto explícitamente para que no prometa un gráfico de línea temporal que la
fuente no permite):
- Fila de KPIs arriba: headcount total, tasa de rotación global, sueldo promedio, % con horas extra.
- Barras: tasa de rotación por `job_role` y por `department` (ya sabemos que Sales Representative
  destaca con ~40%).
- Comparación horas extra sí/no — la diferencia es grande (30,5% vs 10,4%) y es un buen foco visual.
- Histograma o distribución de `years_at_company` partido por `attrition`.
- Una matriz o mapa de calor de `job_satisfaction` × `department`.
- Una tabla de detalle al final, para quien quiera bajar al dato fila por fila (con los slicers
  aplicados arriba).

**Página Agro — evolución y territorio**:
- KPIs: superficie sembrada total, producción total, rendimiento promedio ponderado, del año o
  rango de años filtrado.
- Línea temporal: evolución del rendimiento de un cultivo (el slicer de `cultivo` decide cuál) a
  través de los años — mismo patrón que la query SQL 10.
- Mapa: Power BI tiene "Mapa de formas" (Shape Map) con geoJSON de provincias argentinas, o un mapa
  de burbujas si consigue latitud/longitud de cabeceras departamentales. Si no encuentra un geoJSON
  de provincias argentinas, un treemap por provincia es una alternativa honesta y más simple.
- Treemap o barras: superficie sembrada por provincia y cultivo (la pregunta de la métrica 9).
- Tabla de ranking de cultivos por "% cosechado sobre sembrado" (la 12), ordenada de menor a mayor,
  para resaltar los cultivos con más pérdida relativa entre siembra y cosecha.
- Slicers compartidos arriba de la página: `anio` (o rango), `provincia`, `cultivo`.

**Si integra las dos (camino B del punto 0):** una tercera página que cruce la brecha de personal
estimada (de su tabla sintética) con la tasa de rotación por región — ahí sí tiene sentido un
scatter/cuadrante (ejes: tasa de rotación vs. brecha de personal) para la clasificación de riesgo que
le faltaba en las Definiciones.

## 5. Diseño del dashboard

- **Paleta con intención, no la de Power BI por defecto.** Dos mundos, dos paletas: para RRHH, algo
  neutro corporativo (grises + un acento azul o verde petróleo para alertas de rotación alta); para
  agro, tonos tierra/verde que evoquen el sector, con un acento cálido (ocre/naranja) reservado para
  alertas de déficit o baja eficiencia. Que no use el rojo/verde semáforo salvo para eso exactamente:
  alerta/ok — si lo usa también como color decorativo, pierde significado.
- **Jerarquía: KPIs arriba, detalle abajo.** Tarjetas grandes con el número más importante de la página
  arriba de todo, seguidas por los gráficos que lo explican, y la tabla de detalle al final. Nunca
  arrancar la página con una tabla.
- **Un tema consistente**, no el default de cada gráfico. Power BI permite definir un archivo de tema
  (JSON) con la paleta, fuente y estilo de tarjetas una sola vez, aplicado a todo el reporte — mejor que
  ir coloreando gráfico por gráfico.
- **Slicers arriba o a la izquierda, siempre visibles**, sincronizados entre las páginas que compartan
  dimensión (ej. `provincia` entre las páginas de agro).
- **Evitar el gráfico de torta** salvo con 2-3 categorías. Para `job_role` (9 categorías) o `cultivo`
  (41 categorías), barras horizontales ordenadas o treemap leen mucho mejor.
- **Tooltips con contexto**, no solo el valor: que al pasar el mouse sobre una barra de rotación por
  puesto, el tooltip muestre también el headcount de ese puesto (un 100% de rotación sobre 2 personas
  no es lo mismo que sobre 200).
- **Una página de notas/supuestos.** Dado el punto 0, conviene una página chica (o un ícono de info)
  que diga de dónde sale cada tabla y qué supuestos tiene — mismo espíritu que la bitácora de
  decisiones de la clase de limpieza, pero visible para quien mire el dashboard.

## 6. Buenas prácticas operativas

- **Modo Importación, no DirectQuery.** 160 mil filas de agro entran cómodas en memoria; DirectQuery
  contra MySQL solo complica la clase sin necesidad.
- **Actualizar con intención.** Mientras practica, actualización manual (botón Actualizar) alcanza.
  Si más adelante lo publica en el servicio de Power BI, recién ahí entra en juego un gateway y una
  actualización programada — no hace falta para el TP.
- **Nombrar todo en español y consistente**: medidas, columnas calculadas y tablas con el mismo criterio
  de nombres que ya usó en SQL (snake_case para columnas de origen, "Nombre Propio" para medidas DAX
  es la convención más común en Power BI — dejá que elija una y la mantenga).
- **Organizar las medidas en una tabla separada** ("_Medidas" o similar, sin datos, solo como carpeta)
  en vez de dejarlas sueltas dentro de las tablas de hechos — se vuelve inmantenible rápido si no.
- **Documentar cada decisión de transformación** en los nombres de los pasos de Power Query (click
  derecho → Cambiar nombre en cada paso del panel de Pasos aplicados) — es la versión Power Query de la
  bitácora que armó en pandas.

## 7. Cómo acompañarlo en la práctica

1. Que primero decida el punto 0 (dashboards separados o integrados) y te lo cuente, antes de abrir
   Power BI.
2. Que haga el perfilado de columnas en Power Query **sin que vos mires el resultado antes que él** —
   es el mismo ejercicio de diagnóstico de la clase de limpieza, ahora con otra herramienta; si ya lo
   hizo una vez en pandas, debería reconocer los mismos problemas más rápido.
3. Que arme el modelo de estrella con las dimensiones mínimas (puesto, geografía, cultivo, año) antes
   de escribir la primera medida — si empieza por los gráficos, va a terminar con medidas calculadas
   sobre una tabla plana y lo va a tener que rehacer.
4. Dale una sola medida como ejemplo completo (la de `Tasa de Rotación`, con `DIVIDE`) y que el resto
   las escriba él siguiendo el mismo patrón.
5. Para el diseño, mostrale un dashboard ajeno bien hecho (cualquiera de la galería pública de Power BI)
   y pedile que identifique la jerarquía KPI → gráfico → detalle antes de copiar el estilo — que lo
   razone, no que lo imite a ciegas.
