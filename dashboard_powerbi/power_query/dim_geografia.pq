// dim_geografia: un registro por departamento (clave departamento_id), con su provincia y región.
// Los nombres de departamento se repiten entre provincias ("San Martín", "Belgrano"...): por eso la clave es el id.
let
    Origen = stg_agro,
    Columnas = Table.SelectColumns(Origen, {"departamento_id", "departamento", "provincia_id", "provincia"}),
    Unicos = Table.Distinct(Columnas, {"departamento_id"}),
    Regiones = #table(
        type table [provincia = text, region = text],
        {
            {"Buenos Aires", "Pampeana"},
            {"Córdoba", "Pampeana"},
            {"Santa Fe", "Pampeana"},
            {"Entre Ríos", "Pampeana"},
            {"La Pampa", "Pampeana"},
            {"Jujuy", "NOA"},
            {"Salta", "NOA"},
            {"Tucumán", "NOA"},
            {"Catamarca", "NOA"},
            {"Santiago del Estero", "NOA"},
            {"La Rioja", "NOA"},
            {"Chaco", "NEA"},
            {"Corrientes", "NEA"},
            {"Formosa", "NEA"},
            {"Misiones", "NEA"},
            {"Mendoza", "Cuyo"},
            {"San Juan", "Cuyo"},
            {"San Luis", "Cuyo"},
            {"Neuquén", "Patagonia"},
            {"Río Negro", "Patagonia"},
            {"Chubut", "Patagonia"},
            {"Santa Cruz", "Patagonia"},
            {"Tierra del Fuego", "Patagonia"}
        }
    ),
    Unir = Table.NestedJoin(Unicos, {"provincia"}, Regiones, {"provincia"}, "reg", JoinKind.LeftOuter),
    Expandir = Table.ExpandTableColumn(Unir, "reg", {"region"}),
    SinRegion = Table.ReplaceValue(Expandir, null, "Sin dato", Replacer.ReplaceValue, {"region"}),
    Etiqueta = Table.AddColumn(SinRegion, "departamento_etiqueta", each [departamento] & " (" & [provincia] & ")", type text),
    // Para el mapa: con ", Argentina" Bing no confunde "Córdoba" o "Santa Cruz" con lugares de otros países
    ParaMapa = Table.AddColumn(Etiqueta, "provincia_mapa", each if [provincia] = "Sin dato" then null else [provincia] & ", Argentina", type text),
    Final = Table.Sort(ParaMapa, {{"departamento_id", Order.Ascending}})
in
    Final
