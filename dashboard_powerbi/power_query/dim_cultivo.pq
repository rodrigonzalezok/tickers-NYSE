// dim_cultivo: clasificación de cultivos (la arma el analista; no viene en la fuente).
// es_desagregado = true marca las subcategorías que YA están sumadas en un "total"
// (soja 1ra/2da en soja total, poroto alubia/negro/otros en poroto total, trigo candeal en trigo total).
let
    Clasificacion = #table(
        type table [cultivo = text, cultivo_nombre = text, cultivo_grupo = text, categoria = text, es_desagregado = logical],
        {
            {"ajo", "Ajo", "Ajo", "Hortalizas", false},
            {"algodón", "Algodón", "Algodón", "Industriales", false},
            {"alpiste", "Alpiste", "Alpiste", "Cereales", false},
            {"arroz", "Arroz", "Arroz", "Cereales", false},
            {"arveja", "Arveja", "Arveja", "Legumbres", false},
            {"avena", "Avena", "Avena", "Cereales", false},
            {"banana", "Banana", "Banana", "Frutales", false},
            {"caña de azúcar", "Caña de azúcar", "Caña de azúcar", "Industriales", false},
            {"cebada cervecera", "Cebada cervecera", "Cebada", "Cereales", false},
            {"cebada forrajera", "Cebada forrajera", "Cebada", "Cereales", false},
            {"cebada total", "Cebada total", "Cebada", "Cereales", false},
            {"cebolla total", "Cebolla", "Cebolla", "Hortalizas", false},
            {"centeno", "Centeno", "Centeno", "Cereales", false},
            {"colza", "Colza", "Colza", "Oleaginosas", false},
            {"cártamo", "Cártamo", "Cártamo", "Oleaginosas", false},
            {"garbanzo", "Garbanzo", "Garbanzo", "Legumbres", false},
            {"girasol", "Girasol", "Girasol", "Oleaginosas", false},
            {"jojoba", "Jojoba", "Jojoba", "Oleaginosas", false},
            {"lenteja", "Lenteja", "Lenteja", "Legumbres", false},
            {"limón", "Limón", "Limón", "Frutales", false},
            {"lino", "Lino", "Lino", "Oleaginosas", false},
            {"mandarina", "Mandarina", "Mandarina", "Frutales", false},
            {"maní", "Maní", "Maní", "Oleaginosas", false},
            {"maíz", "Maíz", "Maíz", "Cereales", false},
            {"mijo", "Mijo", "Mijo", "Cereales", false},
            {"naranja", "Naranja", "Naranja", "Frutales", false},
            {"papa total", "Papa", "Papa", "Hortalizas", false},
            {"pomelo", "Pomelo", "Pomelo", "Frutales", false},
            {"poroto alubia", "Poroto alubia", "Poroto", "Legumbres", true},
            {"poroto negro", "Poroto negro", "Poroto", "Legumbres", true},
            {"poroto otros", "Poroto otros", "Poroto", "Legumbres", true},
            {"poroto total", "Poroto total", "Poroto", "Legumbres", false},
            {"soja 1ra", "Soja de primera", "Soja", "Oleaginosas", true},
            {"soja 2da", "Soja de segunda", "Soja", "Oleaginosas", true},
            {"soja total", "Soja total", "Soja", "Oleaginosas", false},
            {"sorgo", "Sorgo", "Sorgo", "Cereales", false},
            {"trigo candeal", "Trigo candeal", "Trigo", "Cereales", true},
            {"trigo total", "Trigo total", "Trigo", "Cereales", false},
            {"tung", "Tung", "Tung", "Oleaginosas", false},
            {"té", "Té", "Té", "Industriales", false},
            {"yerba mate", "Yerba mate", "Yerba mate", "Industriales", false}
        }
    ),
    // Partimos de los cultivos que REALMENTE están en los datos: si aparece uno nuevo, no se pierde
    CultivosEnDatos = Table.Distinct(Table.SelectColumns(stg_agro, {"cultivo"})),
    Unir = Table.NestedJoin(CultivosEnDatos, {"cultivo"}, Clasificacion, {"cultivo"}, "clasif", JoinKind.LeftOuter),
    Expandir = Table.ExpandTableColumn(Unir, "clasif", {"cultivo_nombre", "cultivo_grupo", "categoria", "es_desagregado"}),
    // Si algo queda "Sin clasificar", casi siempre es un problema de tildes (codificación) al importar en MySQL
    Nombre = Table.AddColumn(Expandir, "nombre", each if [cultivo_nombre] = null then [cultivo] else [cultivo_nombre], type text),
    QuitarNombreViejo = Table.RemoveColumns(Nombre, {"cultivo_nombre"}),
    RenombrarNombre = Table.RenameColumns(QuitarNombreViejo, {{"nombre", "cultivo_nombre"}}),
    SinClasificar = Table.ReplaceValue(RenombrarNombre, null, "Sin clasificar", Replacer.ReplaceValue, {"cultivo_grupo", "categoria"}),
    SinMarca = Table.ReplaceValue(SinClasificar, null, false, Replacer.ReplaceValue, {"es_desagregado"}),
    Tipos = Table.TransformColumnTypes(SinMarca, {{"cultivo", type text}, {"cultivo_grupo", type text}, {"categoria", type text}, {"es_desagregado", type logical}}),
    Ordenar = Table.ReorderColumns(Tipos, {"cultivo", "cultivo_nombre", "cultivo_grupo", "categoria", "es_desagregado"}),
    Final = Table.Sort(Ordenar, {{"cultivo", Order.Ascending}})
in
    Final
