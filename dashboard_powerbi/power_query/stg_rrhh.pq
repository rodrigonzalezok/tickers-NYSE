// stg_rrhh: consulta de STAGING (desmarcar "Habilitar carga").
let
    Origen = MySQL.Database(ServidorMySQL, BaseMySQL, [ReturnSingleDatabase = true]),
    Tabla = Origen{[Schema = BaseMySQL, Item = "rrhh_attrition"]}[Data],
    // Fuera: columnas constantes (employee_count, over18, standard_hours) y las tres "rates"
    // que no se correlacionan con el sueldo y no sabemos qué miden (pregunta abierta de la clase de limpieza)
    Quitar = Table.RemoveColumns(Tabla, {"employee_count", "over18", "standard_hours", "daily_rate", "hourly_rate", "monthly_rate"})
in
    Quitar
