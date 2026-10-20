// fact_agro: hechos de producción SIN las subcategorías que ya están dentro de un total.
// Así cualquier SUM es correcta y nunca se cuenta doble la soja (o el poroto, o el trigo).
let
    Origen = stg_agro,
    Desagregados = List.Buffer(Table.SelectRows(dim_cultivo, each [es_desagregado] = true)[cultivo]),
    SoloTotales = Table.SelectRows(Origen, each not List.Contains(Desagregados, [cultivo])),
    Columnas = Table.SelectColumns(SoloTotales, {
        "cultivo", "campania", "departamento_id",
        "superficie_sembrada_ha", "superficie_cosechada_ha", "produccion_tm", "rendimiento_kgxha"
    }),
    // Se conserva solo para mostrar en clase por qué NO se promedia un rendimiento
    Renombrar = Table.RenameColumns(Columnas, {{"rendimiento_kgxha", "rendimiento_fila_kgxha"}})
in
    Renombrar
