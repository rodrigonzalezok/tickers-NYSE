// dim_puesto: un registro por combinación área + puesto, traducida al español.
// area_original y puesto_original quedan para unir con fact_rrhh: ocultalas en la vista de informe.
let
    Areas = [
        #"Human Resources" = "Recursos Humanos",
        #"Research & Development" = "Investigación y Desarrollo",
        Sales = "Ventas"
    ],
    Puestos = [
        #"Healthcare Representative" = "Representante de salud",
        #"Human Resources" = "Analista de RRHH",
        #"Laboratory Technician" = "Técnico de laboratorio",
        Manager = "Gerente",
        #"Manufacturing Director" = "Director de manufactura",
        #"Research Director" = "Director de investigación",
        #"Research Scientist" = "Científico investigador",
        #"Sales Executive" = "Ejecutivo de ventas",
        #"Sales Representative" = "Representante de ventas"
    ],
    Combinaciones = Table.Distinct(Table.SelectColumns(stg_rrhh, {"department", "job_role"})),
    Ordenar = Table.Sort(Combinaciones, {{"department", Order.Ascending}, {"job_role", Order.Ascending}}),
    Id = Table.AddIndexColumn(Ordenar, "puesto_id", 1, 1, Int64.Type),
    Area = Table.AddColumn(Id, "area", each Record.FieldOrDefault(Areas, [department], [department]), type text),
    Puesto = Table.AddColumn(Area, "puesto", each Record.FieldOrDefault(Puestos, [job_role], [job_role]), type text),
    Renombrar = Table.RenameColumns(Puesto, {{"department", "area_original"}, {"job_role", "puesto_original"}}),
    Final = Table.ReorderColumns(Renombrar, {"puesto_id", "area", "puesto", "area_original", "puesto_original"})
in
    Final
