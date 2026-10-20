// stg_agro: consulta de STAGING. No se carga al modelo:
// clic derecho sobre la consulta > desmarcar "Habilitar carga".
// Todas las tablas de agro (hechos y dimensiones) parten de acá.
let
    Origen = MySQL.Database(ServidorMySQL, BaseMySQL, [ReturnSingleDatabase = true]),
    // Si este paso da error, borralo y elegí la tabla desde el Navegador: Power BI escribe la línea solo
    Tabla = Origen{[Schema = BaseMySQL, Item = "estimaciones_agricolas"]}[Data],
    QuitarId = Table.RemoveColumns(Tabla, {"id"}),
    Tipos = Table.TransformColumnTypes(QuitarId, {
        {"cultivo", type text}, {"anio", Int64.Type}, {"campania", type text},
        {"provincia", type text}, {"provincia_id", Int64.Type},
        {"departamento", type text}, {"departamento_id", Int64.Type},
        {"superficie_sembrada_ha", Int64.Type}, {"superficie_cosechada_ha", Int64.Type},
        {"produccion_tm", Int64.Type}, {"rendimiento_kgxha", Int64.Type}
    }),
    // 8 filas (1979-1980) no tienen provincia ni departamento: las dejamos como "Sin dato" (id 0)
    SinGeoTexto = Table.ReplaceValue(Tipos, null, "Sin dato", Replacer.ReplaceValue, {"provincia", "departamento"}),
    SinGeoId = Table.ReplaceValue(SinGeoTexto, null, 0, Replacer.ReplaceValue, {"provincia_id", "departamento_id"}),
    // 'anio' no significa lo mismo para todos los cultivos (en té y yerba mate es el 2do año de la campaña).
    // Usamos la campaña como eje de tiempo y su primer año como número.
    AnioInicio = Table.AddColumn(SinGeoId, "anio_inicio", each Number.FromText(Text.Start([campania], 4)), Int64.Type),
    Alerta = Table.AddColumn(AnioInicio, "alerta_cosecha_mayor_siembra", each [superficie_cosechada_ha] > [superficie_sembrada_ha], type logical)
in
    Alerta
