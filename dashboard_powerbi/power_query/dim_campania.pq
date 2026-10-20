// dim_campania: eje de tiempo del lado agro. Una fila por campaña ("2023/2024").
// No hay fechas reales, así que no usamos una tabla de calendario.
let
    Origen = stg_agro,
    Unicas = Table.Distinct(Table.SelectColumns(Origen, {"campania", "anio_inicio"})),
    Decada = Table.AddColumn(Unicas, "decada", each Text.From(Number.IntegerDivide([anio_inicio], 10) * 10) & "s", type text),
    Final = Table.Sort(Decada, {{"anio_inicio", Order.Ascending}})
in
    Final
