// fact_agro_detalle: solo las subcategorías (soja 1ra/2da, poroto por tipo, trigo candeal).
// Se usa en un único visual de detalle; nunca se suma junto con fact_agro.
let
    Origen = stg_agro,
    Desagregados = List.Buffer(Table.SelectRows(dim_cultivo, each [es_desagregado] = true)[cultivo]),
    SoloDetalle = Table.SelectRows(Origen, each List.Contains(Desagregados, [cultivo])),
    Final = Table.SelectColumns(SoloDetalle, {
        "cultivo", "campania", "departamento_id",
        "superficie_sembrada_ha", "superficie_cosechada_ha", "produccion_tm",
        // Las 11 filas con cosechado > sembrado del dataset están todas acá (soja 1ra/2da)
        "alerta_cosecha_mayor_siembra"
    })
in
    Final
