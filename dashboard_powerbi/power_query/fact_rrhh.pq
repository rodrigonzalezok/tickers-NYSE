// fact_rrhh: un registro por empleado, con nombres y valores en español,
// escalas 1-4 con etiqueta (y su número para ordenar) y tramos de edad y antigüedad.
let
    Origen = stg_rrhh,

    // --- Clave del puesto -------------------------------------------------------
    UnirPuesto = Table.NestedJoin(Origen, {"department", "job_role"}, dim_puesto, {"area_original", "puesto_original"}, "p", JoinKind.LeftOuter),
    PuestoId = Table.ExpandTableColumn(UnirPuesto, "p", {"puesto_id"}),

    // --- Traducciones (un registro = un diccionario) ------------------------------
    Traducir = (tabla as table, columna as text, diccionario as record) as table =>
        Table.TransformColumns(tabla, {{columna, each Record.FieldOrDefault(diccionario, _, _), type text}}),
    T1 = Traducir(PuestoId, "gender", [Female = "Mujer", Male = "Hombre"]),
    T2 = Traducir(T1, "marital_status", [Single = "Soltero/a", Married = "Casado/a", Divorced = "Divorciado/a"]),
    T3 = Traducir(T2, "business_travel", [#"Non-Travel" = "No viaja", Travel_Rarely = "Viaja poco", Travel_Frequently = "Viaja seguido"]),
    T4 = Traducir(T3, "education_field", [
        #"Life Sciences" = "Ciencias de la vida", Medical = "Medicina", Marketing = "Marketing",
        #"Technical Degree" = "Técnico", #"Human Resources" = "Recursos Humanos", Other = "Otro"]),
    T5 = Traducir(T4, "over_time", [Yes = "Sí", No = "No"]),

    // --- Escalas: etiqueta en texto + el número original para "Ordenar por columna" ---
    Escala4 = {"Baja", "Media", "Alta", "Muy alta"},
    EscalaBalance = {"Mala", "Buena", "Muy buena", "Excelente"},
    EscalaEducacion = {"Secundario", "Terciario", "Universitario", "Maestría", "Doctorado"},
    E1 = Table.AddColumn(T5, "nivel_educativo", each EscalaEducacion{[education] - 1}, type text),
    E2 = Table.AddColumn(E1, "satisfaccion_laboral", each Escala4{[job_satisfaction] - 1}, type text),
    E3 = Table.AddColumn(E2, "satisfaccion_ambiente", each Escala4{[environment_satisfaction] - 1}, type text),
    E4 = Table.AddColumn(E3, "involucramiento", each Escala4{[job_involvement] - 1}, type text),
    E5 = Table.AddColumn(E4, "equilibrio_vida_trabajo", each EscalaBalance{[work_life_balance] - 1}, type text),

    // --- Tramos (mismos cortes que en la clase de limpieza) -------------------------
    TramoEdad = Table.AddColumn(E5, "tramo_edad", each
        if [age] <= 25 then "18-25" else if [age] <= 35 then "26-35" else if [age] <= 45 then "36-45"
        else if [age] <= 55 then "46-55" else "56+", type text),
    TramoEdadOrden = Table.AddColumn(TramoEdad, "tramo_edad_orden", each
        if [age] <= 25 then 1 else if [age] <= 35 then 2 else if [age] <= 45 then 3
        else if [age] <= 55 then 4 else 5, Int64.Type),
    TramoAntig = Table.AddColumn(TramoEdadOrden, "tramo_antiguedad", each
        if [years_at_company] = 0 then "<1" else if [years_at_company] <= 2 then "1-2"
        else if [years_at_company] <= 5 then "3-5" else if [years_at_company] <= 10 then "6-10" else "+10", type text),
    TramoAntigOrden = Table.AddColumn(TramoAntig, "tramo_antiguedad_orden", each
        if [years_at_company] = 0 then 1 else if [years_at_company] <= 2 then 2
        else if [years_at_company] <= 5 then 3 else if [years_at_company] <= 10 then 4 else 5, Int64.Type),

    // --- Variable objetivo: texto para leer, número para sumar -----------------------
    Estado = Table.AddColumn(TramoAntigOrden, "estado", each if [attrition] = "Yes" then "Se fue" else "Sigue", type text),
    Baja = Table.AddColumn(Estado, "baja", each if [attrition] = "Yes" then 1 else 0, Int64.Type),

    // --- Nombres finales en español y orden de columnas ------------------------------
    Renombrar = Table.RenameColumns(Baja, {
        {"employee_number", "empleado_id"}, {"age", "edad"}, {"gender", "genero"},
        {"marital_status", "estado_civil"}, {"education", "nivel_educativo_orden"},
        {"education_field", "campo_estudio"}, {"business_travel", "viajes"},
        {"distance_from_home", "distancia_casa"}, {"job_level", "nivel_puesto"},
        {"monthly_income", "sueldo_mensual"}, {"percent_salary_hike", "aumento_pct"},
        {"over_time", "horas_extra"},
        {"job_satisfaction", "satisfaccion_laboral_orden"},
        {"environment_satisfaction", "satisfaccion_ambiente_orden"},
        {"job_involvement", "involucramiento_orden"},
        {"work_life_balance", "equilibrio_vida_trabajo_orden"},
        {"total_working_years", "anios_experiencia"}, {"years_at_company", "anios_en_empresa"},
        {"years_since_last_promotion", "anios_sin_ascenso"},
        {"num_companies_worked", "empresas_previas"},
        {"training_times_last_year", "capacitaciones_ultimo_anio"}
    }),
    Final = Table.SelectColumns(Renombrar, {
        "empleado_id", "puesto_id", "edad", "tramo_edad", "tramo_edad_orden", "genero", "estado_civil",
        "nivel_educativo", "nivel_educativo_orden", "campo_estudio", "viajes", "distancia_casa",
        "nivel_puesto", "sueldo_mensual", "aumento_pct", "horas_extra",
        "satisfaccion_laboral", "satisfaccion_laboral_orden",
        "satisfaccion_ambiente", "satisfaccion_ambiente_orden",
        "involucramiento", "involucramiento_orden",
        "equilibrio_vida_trabajo", "equilibrio_vida_trabajo_orden",
        "anios_experiencia", "anios_en_empresa", "tramo_antiguedad", "tramo_antiguedad_orden",
        "anios_sin_ascenso", "empresas_previas", "capacitaciones_ultimo_anio", "estado", "baja"
    })
in
    Final
