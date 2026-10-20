# Paso a paso: armar el dashboard en Power BI Desktop

Tiempo estimado: 60 a 90 minutos la primera vez. Requiere Power BI Desktop en Windows.
Los nombres de menú están en español (Power BI Desktop en español). Si lo tenés en inglés, el orden de los menús es el mismo.

Al final de cada etapa hay un **✅ Control**: compará con `dax/valores_esperados.md` antes de seguir.
Un error en la etapa 2 se arrastra a todo lo demás, y es mucho más fácil encontrarlo ahí.

---

## Etapa 1. Traer los datos (elegí UNA opción)

### Opción A: desde MySQL con las consultas de Power Query (la que enseña)

Requisito: tener importados `01_rrhh.sql` y `02_agro.sql` en la base `practica_mentee`, y el conector
**MySQL Connector/NET** instalado (Power BI lo pide la primera vez; se descarga gratis de la web de MySQL).

1. Abrí Power BI Desktop → **Transformar datos** (abre el Editor de Power Query).
2. Creá los dos parámetros: **Inicio → Administrar parámetros → Nuevo parámetro**.
   - `ServidorMySQL`, Tipo *Texto*, Valor actual `localhost`
   - `BaseMySQL`, Tipo *Texto*, Valor actual `practica_mentee`
3. Por cada archivo de la carpeta `power_query/`, **en este orden**:
   `stg_agro` → `dim_cultivo` → `dim_geografia` → `dim_campania` → `fact_agro` → `fact_agro_detalle` →
   `stg_rrhh` → `dim_puesto` → `fact_rrhh`
   1. **Inicio → Nueva fuente → Consulta en blanco**.
   2. **Inicio → Editor avanzado**, borrá lo que hay y pegá el contenido del archivo.
   3. Renombrá la consulta **exactamente** como el archivo, sin `.pq` (panel derecho → Propiedades → Nombre).
      Las consultas se llaman entre sí por nombre: `fact_agro` no anda si `dim_cultivo` se llama "Consulta1".
4. Clic derecho sobre `stg_agro` → desmarcá **Habilitar carga**. Lo mismo con `stg_rrhh`.
   (Quedan en cursiva: se usan, pero no se cargan al modelo.)
5. La primera vez Power BI pide credenciales de MySQL: **Base de datos**, tu usuario y contraseña.
6. **Inicio → Cerrar y aplicar**. Tarda unos segundos (son 160 mil filas).

Si el paso `Tabla` de `stg_agro` o `stg_rrhh` da error: borrá ese paso y el siguiente se va a quejar;
en su lugar hacé **Nueva fuente → MySQL**, elegí la tabla en el Navegador y copiá la línea que genera Power BI.

### Opción B: desde Excel (la rápida, si MySQL da problemas)

1. **Obtener datos → Libro de Excel** → `datos/modelo_rrhh_agro.xlsx`.
2. Marcá las 7 hojas → **Transformar datos**.
3. En cada tabla revisá el ícono de tipo de cada columna: los `_id` y `anio_inicio` deben ser **número entero**,
   `es_desagregado` y `alerta_cosecha_mayor_siembra` **Verdadero/Falso**.
4. **Cerrar y aplicar**.

Las tablas son idénticas a las de la opción A: el Excel lo generó `generar_modelo.py`, que hace las mismas
transformaciones en Python.

**✅ Control 1**: en la vista de **Datos** (ícono de tabla a la izquierda), la cantidad de filas de cada tabla
(abajo a la izquierda) coincide con la tabla "Filas por tabla".

---

## Etapa 2. El modelo (vista de Modelo, el ícono de tres cuadritos)

### Relaciones

Power BI puede haber creado algunas solo. Borrá cualquiera que no esté en esta lista y creá las que falten
arrastrando la columna de la tabla de hechos sobre la de la dimensión:

| Desde (muchos) | Hacia (uno) |
|---|---|
| `fact_agro[cultivo]` | `dim_cultivo[cultivo]` |
| `fact_agro[campania]` | `dim_campania[campania]` |
| `fact_agro[departamento_id]` | `dim_geografia[departamento_id]` |
| `fact_agro_detalle[cultivo]` | `dim_cultivo[cultivo]` |
| `fact_agro_detalle[campania]` | `dim_campania[campania]` |
| `fact_agro_detalle[departamento_id]` | `dim_geografia[departamento_id]` |
| `fact_rrhh[puesto_id]` | `dim_puesto[puesto_id]` |

Todas: cardinalidad **Varios a uno (*:1)**, dirección de filtro **Única**.
Las tablas de RRHH y las de agro quedan como dos islas sin relación entre sí, y está bien: no hay ninguna clave
en común (ver la página de notas del dashboard).

### Ordenar por columna

Vista de **Datos** → seleccioná la columna → **Herramientas de columnas → Ordenar por columna**:

| Columna | Ordenar por |
|---|---|
| `fact_rrhh[tramo_edad]` | `tramo_edad_orden` |
| `fact_rrhh[tramo_antiguedad]` | `tramo_antiguedad_orden` |
| `fact_rrhh[satisfaccion_laboral]` | `satisfaccion_laboral_orden` |
| `fact_rrhh[satisfaccion_ambiente]` | `satisfaccion_ambiente_orden` |
| `fact_rrhh[involucramiento]` | `involucramiento_orden` |
| `fact_rrhh[equilibrio_vida_trabajo]` | `equilibrio_vida_trabajo_orden` |
| `fact_rrhh[nivel_educativo]` | `nivel_educativo_orden` |
| `dim_campania[campania]` | `anio_inicio` |

Sin esto, los ejes salen en orden alfabético ("+10" antes que "<1", "Alta" antes que "Baja").

### Categoría de datos y resumen

- `dim_geografia[provincia_mapa]` → **Herramientas de columnas → Categoría de datos → Lugar**.
- `dim_campania[anio_inicio]`, todos los `_id` y todos los `_orden` → **Resumen → No resumir**.

### Ocultar lo técnico

Clic derecho → **Ocultar en la vista de informe**: todas las columnas `_id`, todas las `_orden`,
`dim_puesto[area_original]`, `dim_puesto[puesto_original]`, `fact_rrhh[baja]`,
`fact_agro[rendimiento_fila_kgxha]`. Lo que queda visible es lo que tiene sentido arrastrar a un gráfico.

**✅ Control 2**: el diagrama muestra dos estrellas: `fact_agro` y `fact_agro_detalle` en el centro con las tres
dimensiones de agro alrededor, y `fact_rrhh` con `dim_puesto`.

---

## Etapa 3. Las medidas

1. **Inicio → Escribir datos** → nombre de la tabla `_Medidas` → **Cargar** (la columna vacía no importa).
2. Seleccioná `_Medidas` en el panel Datos → **Nueva medida**, y pegá cada medida de `dax/medidas.dax`
   (desde el nombre hasta el final de la fórmula, sin los comentarios).
3. Con la medida seleccionada, poné el formato que figura entre corchetes en el comentario
   (**Herramientas de medidas → Formato**).
4. Ordenalas en carpetas: vista de **Modelo** → seleccioná varias medidas → Propiedades →
   **Carpeta para mostrar**: `RRHH` o `Agro`.
5. Cuando `_Medidas` tenga al menos una medida, borrá su columna `Columna1`: la tabla pasa al tope de la lista
   con un ícono de calculadora.

**✅ Control 3**: poné una **Tarjeta** con cada medida de RRHH y compará con "RRHH, sin filtros".
Para agro, agregá un segmentador de `dim_campania[campania]`, elegí 2024/2025 y compará.
Después borrá esas tarjetas de prueba.

---

## Etapa 4. El tema

**Vista → Temas → Examinar temas** → `tema/tema_rrhh_agro.json`.
Esto define la paleta (validada para daltonismo), el fondo, los bordes y las fuentes de todo el informe.

---

## Etapa 5. Página "RRHH · Rotación"

Renombrá la página 1 (doble clic en la pestaña de abajo). Lienzo de 1280 × 720 (por defecto).

Distribución, de arriba hacia abajo:

```
┌───────────────────────────────────────────────────────────────────────┐
│ Título  ·  subtítulo                 [Área ▾] [Género ▾] [Edad ▾]    │
├──────────────┬──────────────┬──────────────┬──────────────────────────┤
│  Empleados   │  Rotación    │ Sueldo prom. │  % con horas extra       │
├──────────────┴──────────────┼──────────────┴──────────────────────────┤
│ Rotación por puesto         │  Horas extra: 30,5% vs 10,4% (2,9×)     │
│ (barras horizontales)       ├──────────────────────┬──────────────────┤
│                             │ Por antigüedad       │ Por tramo edad   │
├─────────────────────────────┴──────────────────────┴──────────────────┤
│ Mapa de calor: área × satisfacción laboral   │  Tabla de detalle      │
└───────────────────────────────────────────────────────────────────────┘
```

1. **Título**: cuadro de texto "Rotación de personal". Debajo, más chico y en gris:
   "Foto de 1.470 empleados (dataset IBM HR). No hay fechas: muestra un estado, no una evolución."
2. **Segmentadores** (estilo Lista desplegable): `dim_puesto[area]`, `fact_rrhh[genero]`, `fact_rrhh[tramo_edad]`.
3. **Cuatro tarjetas**: `Empleados`, `Tasa de Rotación`, `Sueldo Promedio`, `% Con Horas Extra`.
   Título de cada tarjeta en lenguaje natural ("Rotación", no "Tasa de Rotación").
4. **Rotación por puesto**: *Gráfico de barras agrupadas*.
   - Eje Y: `dim_puesto[puesto]` · Eje X: `Tasa de Rotación` · Información sobre herramientas: `Empleados`, `Diferencia vs Empresa (pp)`.
   - Ordenar (los tres puntos del visual) por `Tasa de Rotación`, descendente.
   - Formato → Barras → Color → **fx** → Estilo *Valor de campo* → `Color Rotación`.
     Naranja = por encima del promedio de la empresa; gris = por debajo.
   - Panel **Análisis** (lupa) → **Línea X constante** → valor **fx** → `Tasa de Rotación (empresa)`,
     etiqueta de datos activada: "Promedio empresa".
   - Etiquetas de datos activadas, formato 0,0%.
   - Subtítulo del visual: "Naranja: por encima del promedio de la empresa".
5. **Horas extra**: dos *Tarjetas* lado a lado, `Rotación con Horas Extra` y `Rotación sin Horas Extra`,
   y una tercera más chica con `Multiplicador Horas Extra` titulada "veces más rotación con horas extra".
   Es el hallazgo más fuerte del dataset: merece números grandes, no un gráfico.
6. **Rotación por antigüedad**: *Gráfico de columnas*. Eje X `fact_rrhh[tramo_antiguedad]`, Eje Y `Tasa de Rotación`,
   color único (azul del tema), etiquetas de datos activadas. Título: "Rotación según años en la empresa".
7. **Rotación por tramo de edad**: igual que el anterior con `fact_rrhh[tramo_edad]`.
8. **Mapa de calor**: *Matriz*. Filas `dim_puesto[area]`, Columnas `fact_rrhh[satisfaccion_laboral]`,
   Valores `Tasa de Rotación`.
   - Formato → Elementos de celda → **Color de fondo** activado → fx → *Escala de colores*,
     mínimo `#CDE2FB`, máximo `#5598E7` (una sola tonalidad, de claro a oscuro: el texto negro se lee en las dos).
   - Desactivá los subtotales de filas y columnas.
9. **Tabla de detalle**: *Tabla* con `dim_puesto[puesto]`, `Empleados`, `Bajas`, `Tasa de Rotación`,
   `Sueldo Promedio`, `Antigüedad Promedio (años)`, ordenada por `Tasa de Rotación`.

**✅ Control 5**: elegí Área = Ventas en el segmentador. Rotación debe dar 20,6%, y en la barra de puestos
"Representante de ventas" tiene que seguir en naranja con 39,8%.

---

## Etapa 6. Página "Agro · Producción"

Página nueva. Mismo esquema: título, segmentadores, KPIs, evolución, territorio, detalle.

```
┌───────────────────────────────────────────────────────────────────────┐
│ Título · subtítulo          [Campaña ▾] [Región ▾] [Categoría ▾]     │
├──────────────┬──────────────┬──────────────┬──────────────────────────┤
│ Sembrada (ha)│Producción (t)│ Rinde (kg/ha)│ Variación interanual     │
├──────────────┴──────────────┴──────────────┴──────────────────────────┤
│ Producción total por campaña, 1969–2024 (línea)                       │
├─────────────────────────────┬─────────────────────────────────────────┤
│ Mapa por provincia          │ Superficie por grupo de cultivo (top 8) │
├─────────────────────────────┼──────────────────────┬──────────────────┤
│ Rinde: soja, maíz, trigo,   │ % cosechado (más     │ Soja de 1ra      │
│ girasol (líneas)            │ bajos)               │ y de 2da         │
└─────────────────────────────┴──────────────────────┴──────────────────┘
```

1. **Título** "Producción agrícola argentina". Subtítulo: "Estimaciones agrícolas por departamento,
   campañas 1969/70 a 2024/25. Fuente: Secretaría de Agricultura."
2. **Segmentadores**: `dim_campania[campania]` (Lista desplegable, **Selección única** activada, elegí 2024/2025),
   `dim_geografia[region]`, `dim_cultivo[categoria]`.
3. **Cuatro tarjetas**: `Superficie Sembrada (ha)`, `Producción (t)`, `Rendimiento (kg/ha)`, `Variación Interanual %`.
   - En la de variación: Formato → Valor → Color → fx → Reglas: si el valor es < 0 → `#D03B3B`; si ≥ 0 → `#006300`.
   - Para que se lea qué campaña muestran, agregá en el título de cada tarjeta **fx** → `Campaña Seleccionada`.
4. **Producción por campaña**: *Gráfico de líneas*. Eje X `dim_campania[anio_inicio]` (tipo **Continuo**),
   Eje Y `Producción (t)`. Una sola serie, sin leyenda.
   Agregá un cuadro de texto encima del pozo de 2022: "Sequía 2022/23: −33%".
5. **Mapa**: *Mapa coroplético*. Ubicación `dim_geografia[provincia_mapa]`, Información sobre herramientas
   `Superficie Sembrada (ha)` y `Participación en Superficie %`.
   Formato → Colores de relleno → fx → *Escala de colores* por `Superficie Sembrada (ha)`, de `#CDE2FB` a `#104281`.
   Si el mapa no aparece: Archivo → Opciones → Seguridad → marcá "Usar elementos visuales de Mapa y Mapa coroplético".
   Si en tu organización están bloqueados, reemplazalo por un *Gráfico de rectángulos* (treemap) de
   `dim_geografia[provincia]` con `Superficie Sembrada (ha)`.
6. **Superficie por grupo de cultivo**: *Gráfico de barras agrupadas*. Eje Y `dim_cultivo[cultivo_grupo]`,
   Eje X `Superficie Sembrada (ha)`. Panel de filtros del visual → `cultivo_grupo` → Tipo de filtro
   **N superior** → 8 → por `Superficie Sembrada (ha)`. Color único.
7. **Rinde de los cuatro grandes**: *Gráfico de líneas*. Eje X `dim_campania[anio_inicio]`, Eje Y `Rendimiento (kg/ha)`,
   Leyenda `dim_cultivo[cultivo_grupo]`, filtro del visual: cultivo_grupo = Soja, Maíz, Trigo, Girasol.
   Los colores salen del tema en orden fijo: no los cambies a mano.
8. **% Cosechado**: *Gráfico de barras agrupadas*. Eje Y `dim_cultivo[cultivo_nombre]`, Eje X `% Cosechado`,
   filtro N inferior 8 por `% Cosechado`, orden ascendente. Subtítulo:
   "Avena, centeno y cebada forrajera se siembran para pastoreo: no es pérdida."
9. **Soja de primera y de segunda**: *Gráfico de columnas*. Eje X `dim_cultivo[cultivo_nombre]`,
   Eje Y `Superficie Sembrada Detalle (ha)`, filtro del visual cultivo_nombre = Soja de primera, Soja de segunda.
   Subtítulo: "La de segunda se siembra después del trigo, en el mismo lote."

### Editar interacciones (clave en esta página)

Los gráficos de evolución (4 y 7) **no** tienen que filtrarse por campaña, o mostrarían un solo punto.
Seleccioná el segmentador de campaña → **Formato → Editar interacciones** → en los visuales 4 y 7 hacé clic
en el ícono de **Ninguno** (círculo tachado). Los segmentadores de región y categoría sí los siguen filtrando.

**✅ Control 6**: con 2024/2025, las tarjetas dan 43.806.874 ha, 141.311.687 t, 3.674 kg/ha y +0,8%.
Con 2022/2023, la variación da −33,0% y se pone roja.

---

## Etapa 7. Página "Notas y supuestos"

Una página con cuadros de texto (podés copiar el texto de la sección "Notas" de `GUIA_CLASE_MENTOR.md`):

- **Fuentes**: IBM HR Employee Attrition (Kaggle, dataset ficticio de una empresa de EE.UU.) y
  Estimaciones Agrícolas de la Secretaría de Agricultura (Argentina).
- **Las dos fuentes no se cruzan**: no comparten ninguna clave; por eso son dos páginas independientes.
- **Decisiones de preparación**: la lista de la sección 3 de la guía (doble conteo, campaña vs año,
  filas sin geografía, rendimiento ponderado, columnas descartadas).
- **Limitaciones**: RRHH es una foto sin fechas; la moneda del sueldo no está informada;
  la serie de cebada cambia de definición en 2016.

---

## Etapa 8. Terminaciones

- **Sincronizar segmentadores** (Vista → Sincronizar segmentadores) no hace falta: cada página tiene los suyos.
- **Vista móvil** (Vista → Diseño móvil): arrastrá las tarjetas y los dos gráficos principales de cada página.
- **Guardar** como `dashboard_rrhh_agro.pbix`.
- Si lo publica en el servicio de Power BI con la opción A, va a necesitar una puerta de enlace para actualizar
  desde MySQL local. Para el TP alcanza con el .pbix.
