"""
Implementacion de referencia del modelo del dashboard (en pandas).

Hace exactamente las mismas transformaciones que las consultas de Power Query
de la carpeta power_query/, para poder:
  1. generar datos/modelo_rrhh_agro.xlsx (las tablas finales, listas para cargar
     en Power BI si la conexion a MySQL falla), y
  2. calcular los valores que tienen que dar las medidas DAX (dax/valores_esperados.md).

Uso:
    python generar_modelo.py <csv_agro> <csv_rrhh> <carpeta_salida>
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

CSV_AGRO, CSV_RRHH, SALIDA = sys.argv[1], sys.argv[2], Path(sys.argv[3])
(SALIDA / "datos").mkdir(parents=True, exist_ok=True)
(SALIDA / "dax").mkdir(parents=True, exist_ok=True)

# =============================================================================
# AGRO
# =============================================================================
agro = pd.read_csv(CSV_AGRO, dtype={"provincia_id": "Int64", "departamento_id": "Int64"})

# Filas sin geografia (8, todas de 1979-1980 y casi sin produccion): se conservan
# con clave 0 = "Sin dato" para no perder superficie sembrada.
agro["departamento_id"] = agro["departamento_id"].fillna(0).astype(int)
agro["provincia_id"] = agro["provincia_id"].fillna(0).astype(int)
agro[["provincia", "departamento"]] = agro[["provincia", "departamento"]].fillna("Sin dato")

# La columna 'anio' no significa lo mismo para todos los cultivos: en te y yerba
# mate es el SEGUNDO año de la campaña. Usamos la campaña como eje de tiempo.
agro["anio_inicio"] = agro["campania"].str[:4].astype(int)

# Clasificacion de cultivos (la arma el analista, no viene en la fuente)
CULTIVOS = {
    # cultivo:            (nombre,              grupo,      categoria,     es_desagregado)
    "ajo":               ("Ajo",               "Ajo",       "Hortalizas",   False),
    "algodón":           ("Algodón",           "Algodón",   "Industriales", False),
    "alpiste":           ("Alpiste",           "Alpiste",   "Cereales",     False),
    "arroz":             ("Arroz",             "Arroz",     "Cereales",     False),
    "arveja":            ("Arveja",            "Arveja",    "Legumbres",    False),
    "avena":             ("Avena",             "Avena",     "Cereales",     False),
    "banana":            ("Banana",            "Banana",    "Frutales",     False),
    "caña de azúcar":    ("Caña de azúcar",    "Caña de azúcar", "Industriales", False),
    "cebada cervecera":  ("Cebada cervecera",  "Cebada",    "Cereales",     False),
    "cebada forrajera":  ("Cebada forrajera",  "Cebada",    "Cereales",     False),
    "cebada total":      ("Cebada total",      "Cebada",    "Cereales",     False),
    "cebolla total":     ("Cebolla",           "Cebolla",   "Hortalizas",   False),
    "centeno":           ("Centeno",           "Centeno",   "Cereales",     False),
    "colza":             ("Colza",             "Colza",     "Oleaginosas",  False),
    "cártamo":           ("Cártamo",           "Cártamo",   "Oleaginosas",  False),
    "garbanzo":          ("Garbanzo",          "Garbanzo",  "Legumbres",    False),
    "girasol":           ("Girasol",           "Girasol",   "Oleaginosas",  False),
    "jojoba":            ("Jojoba",            "Jojoba",    "Oleaginosas",  False),
    "lenteja":           ("Lenteja",           "Lenteja",   "Legumbres",    False),
    "limón":             ("Limón",             "Limón",     "Frutales",     False),
    "lino":              ("Lino",              "Lino",      "Oleaginosas",  False),
    "mandarina":         ("Mandarina",         "Mandarina", "Frutales",     False),
    "maní":              ("Maní",              "Maní",      "Oleaginosas",  False),
    "maíz":              ("Maíz",              "Maíz",      "Cereales",     False),
    "mijo":              ("Mijo",              "Mijo",      "Cereales",     False),
    "naranja":           ("Naranja",           "Naranja",   "Frutales",     False),
    "papa total":        ("Papa",              "Papa",      "Hortalizas",   False),
    "pomelo":            ("Pomelo",            "Pomelo",    "Frutales",     False),
    "poroto alubia":     ("Poroto alubia",     "Poroto",    "Legumbres",    True),
    "poroto negro":      ("Poroto negro",      "Poroto",    "Legumbres",    True),
    "poroto otros":      ("Poroto otros",      "Poroto",    "Legumbres",    True),
    "poroto total":      ("Poroto total",      "Poroto",    "Legumbres",    False),
    "soja 1ra":          ("Soja de primera",   "Soja",      "Oleaginosas",  True),
    "soja 2da":          ("Soja de segunda",   "Soja",      "Oleaginosas",  True),
    "soja total":        ("Soja total",        "Soja",      "Oleaginosas",  False),
    "sorgo":             ("Sorgo",             "Sorgo",     "Cereales",     False),
    "trigo candeal":     ("Trigo candeal",     "Trigo",     "Cereales",     True),
    "trigo total":       ("Trigo total",       "Trigo",     "Cereales",     False),
    "tung":              ("Tung",              "Tung",      "Oleaginosas",  False),
    "té":                ("Té",                "Té",        "Industriales", False),
    "yerba mate":        ("Yerba mate",        "Yerba mate", "Industriales", False),
}
dim_cultivo = pd.DataFrame(
    [(k, *v) for k, v in CULTIVOS.items()],
    columns=["cultivo", "cultivo_nombre", "cultivo_grupo", "categoria", "es_desagregado"],
)
faltan = set(agro["cultivo"]) - set(dim_cultivo["cultivo"])
assert not faltan, f"Cultivos sin clasificar: {faltan}"

REGIONES = {
    "Buenos Aires": "Pampeana", "Córdoba": "Pampeana", "Santa Fe": "Pampeana",
    "Entre Ríos": "Pampeana", "La Pampa": "Pampeana",
    "Jujuy": "NOA", "Salta": "NOA", "Tucumán": "NOA", "Catamarca": "NOA",
    "Santiago del Estero": "NOA", "La Rioja": "NOA",
    "Chaco": "NEA", "Corrientes": "NEA", "Formosa": "NEA", "Misiones": "NEA",
    "Mendoza": "Cuyo", "San Juan": "Cuyo", "San Luis": "Cuyo",
    "Neuquén": "Patagonia", "Río Negro": "Patagonia", "Chubut": "Patagonia",
    "Santa Cruz": "Patagonia", "Tierra del Fuego": "Patagonia",
    "Sin dato": "Sin dato",
}
dim_geografia = (
    agro[["departamento_id", "departamento", "provincia_id", "provincia"]]
    .drop_duplicates()
    .sort_values("departamento_id")
    .reset_index(drop=True)
)
assert dim_geografia["departamento_id"].is_unique
dim_geografia["region"] = dim_geografia["provincia"].map(REGIONES)
assert dim_geografia["region"].notna().all()
dim_geografia["departamento_etiqueta"] = dim_geografia["departamento"] + " (" + dim_geografia["provincia"] + ")"
# Para el mapa: Power BI geocodifica mejor con el pais explicito
dim_geografia["provincia_mapa"] = np.where(
    dim_geografia["provincia"] == "Sin dato", None, dim_geografia["provincia"] + ", Argentina"
)

campanias = sorted(agro["campania"].unique())
dim_campania = pd.DataFrame({"campania": campanias})
dim_campania["anio_inicio"] = dim_campania["campania"].str[:4].astype(int)
dim_campania["decada"] = (dim_campania["anio_inicio"] // 10 * 10).astype(str) + "s"

COLS_HECHO = ["cultivo", "campania", "departamento_id",
              "superficie_sembrada_ha", "superficie_cosechada_ha", "produccion_tm",
              "rendimiento_kgxha"]
agro["alerta_cosecha_mayor_siembra"] = agro["superficie_cosechada_ha"] > agro["superficie_sembrada_ha"]
desagregados = set(dim_cultivo.loc[dim_cultivo["es_desagregado"], "cultivo"])
fact_agro = agro.loc[~agro["cultivo"].isin(desagregados), COLS_HECHO]
fact_agro = fact_agro.rename(columns={"rendimiento_kgxha": "rendimiento_fila_kgxha"}).reset_index(drop=True)
# Las 11 filas con cosechado > sembrado son todas de soja 1ra/2da: la alerta vive en el detalle
fact_agro_detalle = agro.loc[agro["cultivo"].isin(desagregados), COLS_HECHO[:-1] + ["alerta_cosecha_mayor_siembra"]].reset_index(drop=True)

# =============================================================================
# RRHH
# =============================================================================
hr = pd.read_csv(CSV_RRHH, sep=";", encoding="utf-8-sig")

DEPTO = {"Human Resources": "Recursos Humanos", "Research & Development": "Investigación y Desarrollo",
         "Sales": "Ventas"}
PUESTO = {
    "Healthcare Representative": "Representante de salud", "Human Resources": "Analista de RRHH",
    "Laboratory Technician": "Técnico de laboratorio", "Manager": "Gerente",
    "Manufacturing Director": "Director de manufactura", "Research Director": "Director de investigación",
    "Research Scientist": "Científico investigador", "Sales Executive": "Ejecutivo de ventas",
    "Sales Representative": "Representante de ventas",
}
VIAJES = {"Non-Travel": "No viaja", "Travel_Rarely": "Viaja poco", "Travel_Frequently": "Viaja seguido"}
GENERO = {"Female": "Mujer", "Male": "Hombre"}
CIVIL = {"Single": "Soltero/a", "Married": "Casado/a", "Divorced": "Divorciado/a"}
CAMPO = {"Life Sciences": "Ciencias de la vida", "Medical": "Medicina", "Marketing": "Marketing",
         "Technical Degree": "Técnico", "Human Resources": "Recursos Humanos", "Other": "Otro"}
SI_NO = {"Yes": "Sí", "No": "No"}
ESC_4 = {1: "Baja", 2: "Media", 3: "Alta", 4: "Muy alta"}
ESC_BAL = {1: "Mala", 2: "Buena", 3: "Muy buena", 4: "Excelente"}
ESC_EDU = {1: "Secundario", 2: "Terciario", 3: "Universitario", 4: "Maestría", 5: "Doctorado"}

dim_puesto = (
    hr[["Department", "JobRole"]].drop_duplicates()
    .sort_values(["Department", "JobRole"]).reset_index(drop=True)
)
dim_puesto.insert(0, "puesto_id", range(1, len(dim_puesto) + 1))
fact = hr.merge(dim_puesto, on=["Department", "JobRole"])
dim_puesto["area"] = dim_puesto["Department"].map(DEPTO)
dim_puesto["puesto"] = dim_puesto["JobRole"].map(PUESTO)
# Los nombres originales quedan (ocultos en el informe) porque fact_rrhh se une por ellos
dim_puesto = dim_puesto.rename(columns={"Department": "area_original", "JobRole": "puesto_original"})
dim_puesto = dim_puesto[["puesto_id", "area", "puesto", "area_original", "puesto_original"]]


def tramo(serie, cortes, etiquetas):
    return pd.cut(serie, bins=cortes, labels=etiquetas).astype(str)


fact_rrhh = pd.DataFrame({
    "empleado_id": fact["EmployeeNumber"],
    "puesto_id": fact["puesto_id"],
    "edad": fact["Age"],
    "tramo_edad": tramo(fact["Age"], [17, 25, 35, 45, 55, 100], ["18-25", "26-35", "36-45", "46-55", "56+"]),
    "tramo_edad_orden": tramo(fact["Age"], [17, 25, 35, 45, 55, 100], ["1", "2", "3", "4", "5"]).astype(int),
    "genero": fact["Gender"].map(GENERO),
    "estado_civil": fact["MaritalStatus"].map(CIVIL),
    "nivel_educativo": fact["Education"].map(ESC_EDU),
    "nivel_educativo_orden": fact["Education"],
    "campo_estudio": fact["EducationField"].map(CAMPO),
    "viajes": fact["BusinessTravel"].map(VIAJES),
    "distancia_casa": fact["DistanceFromHome"],
    "nivel_puesto": fact["JobLevel"],
    "sueldo_mensual": fact["MonthlyIncome"],
    "aumento_pct": fact["PercentSalaryHike"],
    "horas_extra": fact["OverTime"].map(SI_NO),
    "satisfaccion_laboral": fact["JobSatisfaction"].map(ESC_4),
    "satisfaccion_laboral_orden": fact["JobSatisfaction"],
    "satisfaccion_ambiente": fact["EnvironmentSatisfaction"].map(ESC_4),
    "satisfaccion_ambiente_orden": fact["EnvironmentSatisfaction"],
    "involucramiento": fact["JobInvolvement"].map(ESC_4),
    "involucramiento_orden": fact["JobInvolvement"],
    "equilibrio_vida_trabajo": fact["WorkLifeBalance"].map(ESC_BAL),
    "equilibrio_vida_trabajo_orden": fact["WorkLifeBalance"],
    "anios_experiencia": fact["TotalWorkingYears"],
    "anios_en_empresa": fact["YearsAtCompany"],
    "tramo_antiguedad": tramo(fact["YearsAtCompany"], [-1, 0, 2, 5, 10, 100], ["<1", "1-2", "3-5", "6-10", "+10"]),
    "tramo_antiguedad_orden": tramo(fact["YearsAtCompany"], [-1, 0, 2, 5, 10, 100], ["1", "2", "3", "4", "5"]).astype(int),
    "anios_sin_ascenso": fact["YearsSinceLastPromotion"],
    "empresas_previas": fact["NumCompaniesWorked"],
    "capacitaciones_ultimo_anio": fact["TrainingTimesLastYear"],
    "estado": np.where(fact["Attrition"] == "Yes", "Se fue", "Sigue"),
    "baja": (fact["Attrition"] == "Yes").astype(int),
}).sort_values("empleado_id").reset_index(drop=True)
assert fact_rrhh.notna().all().all()

# =============================================================================
# Salida: Excel con todas las tablas
# =============================================================================
tablas = {
    "fact_agro": fact_agro, "fact_agro_detalle": fact_agro_detalle,
    "dim_cultivo": dim_cultivo, "dim_geografia": dim_geografia, "dim_campania": dim_campania,
    "fact_rrhh": fact_rrhh, "dim_puesto": dim_puesto,
}
with pd.ExcelWriter(SALIDA / "datos" / "modelo_rrhh_agro.xlsx", engine="openpyxl") as xl:
    for nombre, t in tablas.items():
        t.to_excel(xl, sheet_name=nombre, index=False)

# =============================================================================
# Valores esperados de las medidas (para validar el .pbix)
# =============================================================================
def tasa(df):
    return df["baja"].sum() / len(df)


def rinde(df):
    con_sup = df[df["superficie_cosechada_ha"] > 0]
    return con_sup["produccion_tm"].sum() * 1000 / df["superficie_cosechada_ha"].sum()


f = fact_agro.merge(dim_campania, on="campania").merge(dim_cultivo, on="cultivo").merge(dim_geografia, on="departamento_id")
r = fact_rrhh.merge(dim_puesto, on="puesto_id")
ult = "2024/2025"
u = f[f["campania"] == ult]
ant = f[f["campania"] == "2023/2024"]
seca = f[f["campania"] == "2022/2023"]
pre_seca = f[f["campania"] == "2021/2022"]

esperado = {
    "rrhh": {
        "empleados": len(r),
        "bajas": int(r["baja"].sum()),
        "tasa_rotacion": tasa(r),
        "sueldo_promedio": r["sueldo_mensual"].mean(),
        "pct_horas_extra": (r["horas_extra"] == "Sí").mean(),
        "rot_con_he": tasa(r[r["horas_extra"] == "Sí"]),
        "rot_sin_he": tasa(r[r["horas_extra"] == "No"]),
        "antig_promedio": r["anios_en_empresa"].mean(),
        "por_puesto": r.groupby("puesto").apply(lambda g: (len(g), tasa(g)), include_groups=False).to_dict(),
        "por_area": r.groupby("area").apply(lambda g: (len(g), tasa(g), g["sueldo_mensual"].mean()), include_groups=False).to_dict(),
        "por_tramo_edad": r.groupby("tramo_edad").apply(lambda g: (len(g), tasa(g)), include_groups=False).to_dict(),
        "por_antiguedad": r.groupby(["tramo_antiguedad_orden", "tramo_antiguedad"]).apply(lambda g: (len(g), tasa(g)), include_groups=False).to_dict(),
        "por_satisf": r.groupby(["satisfaccion_laboral_orden", "satisfaccion_laboral"]).apply(lambda g: (len(g), tasa(g)), include_groups=False).to_dict(),
        "por_viajes": r.groupby("viajes").apply(lambda g: (len(g), tasa(g)), include_groups=False).to_dict(),
        "heat_area_satisf": r.groupby(["area", "satisfaccion_laboral_orden"]).apply(tasa, include_groups=False).to_dict(),
    },
    "agro": {
        "ultima_campania": ult,
        "sup_sembrada": int(u["superficie_sembrada_ha"].sum()),
        "sup_cosechada": int(u["superficie_cosechada_ha"].sum()),
        "produccion": int(u["produccion_tm"].sum()),
        "rinde": rinde(u),
        "rinde_simple_incorrecto": u["rendimiento_fila_kgxha"].mean(),
        "pct_cosechado": u["superficie_cosechada_ha"].sum() / u["superficie_sembrada_ha"].sum(),
        "prod_anterior": int(ant["produccion_tm"].sum()),
        "var_interanual": u["produccion_tm"].sum() / ant["produccion_tm"].sum() - 1,
        "prod_seca": int(seca["produccion_tm"].sum()),
        "var_seca": seca["produccion_tm"].sum() / pre_seca["produccion_tm"].sum() - 1,
        "serie_produccion": f.groupby("anio_inicio")["produccion_tm"].sum().to_dict(),
        "serie_sup": f.groupby("anio_inicio")["superficie_sembrada_ha"].sum().to_dict(),
        "serie_grupo": f[f["cultivo_grupo"].isin(["Soja", "Maíz", "Trigo", "Girasol"])]
            .groupby(["cultivo_grupo", "anio_inicio"])["produccion_tm"].sum().to_dict(),
        "rinde_soja_serie": f[f["cultivo"] == "soja total"].groupby("anio_inicio").apply(rinde, include_groups=False).to_dict(),
        "rinde_maiz_serie": f[f["cultivo"] == "maíz"].groupby("anio_inicio").apply(rinde, include_groups=False).to_dict(),
        "prov_ult": u.groupby("provincia")["superficie_sembrada_ha"].sum().sort_values(ascending=False).to_dict(),
        "region_ult": u.groupby("region")["superficie_sembrada_ha"].sum().sort_values(ascending=False).to_dict(),
        "categoria_ult": u.groupby("categoria")["superficie_sembrada_ha"].sum().sort_values(ascending=False).to_dict(),
        "grupo_ult": u.groupby("cultivo_grupo")[["superficie_sembrada_ha", "produccion_tm"]].sum()
            .sort_values("superficie_sembrada_ha", ascending=False).head(8).to_dict("index"),
        "pct_cosechado_cultivo": f.groupby("cultivo_nombre").apply(
            lambda g: g["superficie_cosechada_ha"].sum() / g["superficie_sembrada_ha"].sum(), include_groups=False
        ).sort_values().to_dict(),
        "soja_1ra_2da_ult": fact_agro_detalle[(fact_agro_detalle["campania"] == ult) & fact_agro_detalle["cultivo"].str.startswith("soja")]
            .groupby("cultivo")["superficie_sembrada_ha"].sum().to_dict(),
        "alertas": int(fact_agro_detalle["alerta_cosecha_mayor_siembra"].sum()),
    },
    "filas": {k: len(v) for k, v in tablas.items()},
}


def a_json(o):
    if isinstance(o, dict):
        return {(" | ".join(map(str, k)) if isinstance(k, tuple) else str(k)): a_json(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [a_json(x) for x in o]
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating, float)):
        return round(float(o), 6)
    return o


(SALIDA / "datos" / "valores_esperados.json").write_text(json.dumps(a_json(esperado), ensure_ascii=False, indent=1))
print(json.dumps(esperado["filas"]))
