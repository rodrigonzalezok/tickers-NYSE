"""
Genera una version "sucia" del dataset IBM HR Employee Attrition.

Por que: el CSV de IBM es sintetico y viene casi perfecto (sin nulos ni
duplicados). Un export real de un sistema de RRHH nunca llega asi, asi que
para practicar limpieza le metemos a proposito los problemas tipicos que
aparecen en la vida real: duplicados, nulos, texto inconsistente, montos
guardados como texto y edades imposibles.

Uso:
    python ensuciar_datos.py ruta/al/archivo_original.csv
    -> genera HR_sucio.csv en la carpeta actual

La semilla es fija: siempre se generan los mismos problemas, asi mentor y
mentee ven exactamente los mismos numeros.
"""
import sys

import numpy as np
import pandas as pd

SEMILLA = 42
ORIGEN = sys.argv[1] if len(sys.argv) > 1 else "WA_Fn-UseC_-HR-Employee-Attrition.csv"
DESTINO = "HR_sucio.csv"

rng = np.random.default_rng(SEMILLA)
df = pd.read_csv(ORIGEN, encoding="utf-8-sig")
df.columns = df.columns.str.strip()
n = len(df)


def filas(frac):
    """Devuelve un indice aleatorio con el `frac` de las filas."""
    return rng.choice(df.index, size=int(n * frac), replace=False)


# 1) Texto inconsistente: mayusculas, espacios y abreviaturas
dept_variantes = {
    "Sales": ["sales", "Sales ", "SALES"],
    "Research & Development": ["R&D", "research & development", " Research & Development"],
    "Human Resources": ["HR", "human resources"],
}
for idx in filas(0.10):
    original = df.at[idx, "Department"]
    df.at[idx, "Department"] = rng.choice(dept_variantes[original])

genero_variantes = {"Male": ["M", "male", "MALE"], "Female": ["F", "female", "Fem"]}
for idx in filas(0.06):
    df.at[idx, "Gender"] = rng.choice(genero_variantes[df.at[idx, "Gender"]])

si_no = {"Yes": ["Y", "yes", "Si"], "No": ["N", "no", "NO"]}
for col in ["Attrition", "OverTime"]:
    for idx in filas(0.04):
        df.at[idx, col] = rng.choice(si_no[df.at[idx, col]])

# 2) Montos cargados como texto ("$5,993") -> la columna deja de ser numerica
df["MonthlyIncome"] = df["MonthlyIncome"].astype(object)
for idx in filas(0.05):
    df.at[idx, "MonthlyIncome"] = f"${int(df.at[idx, 'MonthlyIncome']):,}"

# 3) Valores imposibles (errores de tipeo)
for idx, edad in zip(filas(0.003), [150, 4, 999, -1]):
    df.at[idx, "Age"] = edad

# 4) Nulos
df.loc[filas(0.03), "MonthlyIncome"] = np.nan
df.loc[filas(0.02), "DistanceFromHome"] = np.nan
df.loc[filas(0.01), "Department"] = np.nan

# 5) Duplicados exactos (el mismo registro exportado dos veces)
duplicados = df.loc[filas(0.02)]
df = pd.concat([df, duplicados], ignore_index=True)

# Mezclamos para que los duplicados no queden todos al final
df = df.sample(frac=1, random_state=SEMILLA).reset_index(drop=True)
df.to_csv(DESTINO, index=False)
print(f"{DESTINO}: {len(df)} filas ({len(duplicados)} duplicadas agregadas)")
