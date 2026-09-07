"""
Taller 5 - Consultoria Clima
PARTE 1.3 - CO2 y su relacion con la temperatura

Rol principal sugerido: Especialista en datos (descarga/organiza CO2)
                         + Analista cuantitativo (correlacion de Pearson)
                         + Especialista en visualizacion (graficos)

IMPORTANTE (Especialista en datos y reproducibilidad):
    Este script asume que ya descargaron el archivo de CO2 de Mauna Loa
    desde el enlace del taller (https://tinyco.re/3763425) y lo guardaron
    en RawData/ con un nombre descriptivo, por ejemplo: co2_mm_mlo.csv

    El archivo de Doing Economics normalmente trae columnas del estilo:
        Year, Month, Date (decimal), Average, Interpolated, Trend, ...
    Los nombres exactos pueden variar levemente segun la version que
    descarguen. Revisen las primeras filas del archivo (abrelo en Excel
    o en el explorador de variables de Spyder) y ajusten COL_YEAR,
    COL_MONTH, COL_INTERPOLATED y COL_TREND abajo si es necesario.

============================================================
COMO EJECUTAR ESTE SCRIPT EN SPYDER (Anaconda)
============================================================
1. Abre este archivo en Spyder (File > Open).
2. Estructura de carpetas esperada (ajusta si la tuya es distinta):

       TuRepositorio/
       |-- RawData/
       |     |-- NH_Ts_dSST.csv
       |     |-- co2_mm_mlo.csv      <- lo descargas tu del enlace del taller
       |-- Scripts/   (o Code/)      <- aqui va este .py
       |-- Output/    (o Figures/)

   Las rutas a RawData/ se calculan automaticamente a partir de la
   ubicacion de este script (BASE_DIR), sin depender del working
   directory configurado en Spyder.
3. Ejecutar con el boton verde "Run file" (o F5).
4. Las graficas apareceran en el panel "Plots" de Spyder y tambien se
   guardaran como .png en la carpeta Outputs/ del proyecto (se crea
   automaticamente si no existe).

Requisitos (si falta algun paquete, instalar desde Anaconda Prompt):
    conda install pandas matplotlib numpy scipy
"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import pearsonr

BASE_DIR = Path(__file__).resolve().parent

# Carpeta donde se guardan las graficas generadas (hermana de Scripts y
# RawData). Se crea automaticamente si no existe.
OUTPUT_DIR = BASE_DIR.parent / "Outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

# -----------------------------------------------------------------------
# 0. CARGA DE DATOS DE CO2 (Mauna Loa)
# -----------------------------------------------------------------------
RUTA_CO2 = BASE_DIR.parent / "RawData" / "doing-economics-datafile-working-in-excel-project-1.csv"
# Si tu archivo se llama distinto o tu estructura de carpetas es otra,
# reemplaza por la ruta completa:
# RUTA_CO2 = r"C:\Users\TuUsuario\TuRepositorio\RawData\NombreDeTuArchivo.csv"

# --- DIAGNOSTICO: muestra exactamente donde esta buscando el archivo ---
print(f"Carpeta del script (BASE_DIR): {BASE_DIR}")
print(f"Buscando el archivo de CO2 en: {RUTA_CO2}")
if not RUTA_CO2.exists():
    raise FileNotFoundError(
        f"\n\nNo se encontro el archivo en:\n  {RUTA_CO2}\n\n"
        "Revisa que:\n"
        "  1) Este script (.py) este guardado dentro de la carpeta 'Scripts' "
        "de tu proyecto.\n"
        "  2) Ya hayas descargado el archivo de CO2 de Mauna Loa "
        "(enlace del taller) y lo hayas guardado en 'RawData'.\n"
        "  3) El nombre del archivo coincida con RUTA_CO2 (ajusta el nombre "
        "arriba si tu archivo se llama distinto).\n"
    )

# Ajusten estos nombres despues de inspeccionar su archivo real.
COL_YEAR = "Year"
COL_MONTH = "Month"
COL_INTERPOLATED = "Interpolated"
COL_TREND = "Trend"

# --- BLINDAJE: detecta automaticamente el separador y el formato decimal ---
# Cuando Excel guarda un CSV con la configuracion regional en español/
# Latinoamerica, usa punto y coma (;) para separar columnas (en vez de
# coma) y coma para los decimales (en vez de punto), por ejemplo "315,71"
# en vez de "315.71". Si no se detecta esto, pandas lee TODO el archivo
# como una sola columna de texto. Este bloque detecta el separador
# correcto automaticamente, sin que tengas que configurar nada a mano.
with open(RUTA_CO2, "r", encoding="utf-8-sig") as f:
    primera_linea = f.readline()

if primera_linea.count(";") > primera_linea.count(","):
    separador, decimal = ";", ","
else:
    separador, decimal = ",", "."

print(f"Separador detectado: '{separador}'  |  Separador decimal detectado: '{decimal}'")

co2 = pd.read_csv(RUTA_CO2, sep=separador, decimal=decimal, encoding="utf-8-sig")
co2.columns = [c.strip() for c in co2.columns]  # limpia espacios en nombres

# --- DIAGNOSTICO: muestra los nombres de columna que realmente trae el archivo ---
print("\nColumnas encontradas en el archivo de CO2:")
print(co2.columns.tolist())

# --- VALIDACION: confirma que las columnas esperadas existan antes de seguir ---
columnas_esperadas = {COL_YEAR, COL_MONTH, COL_INTERPOLATED, COL_TREND}
columnas_faltantes = columnas_esperadas - set(co2.columns)
if columnas_faltantes:
    raise KeyError(
        f"\n\nNo se encontraron estas columnas en el archivo: {columnas_faltantes}\n\n"
        f"Las columnas que SI tiene tu archivo son:\n  {co2.columns.tolist()}\n\n"
        "Solucion: sube unas lineas y ajusta las variables COL_YEAR, COL_MONTH, "
        "COL_INTERPOLATED y COL_TREND para que coincidan EXACTAMENTE (mayusculas, "
        "espacios, tildes) con los nombres reales que se imprimieron arriba.\n"
    )

# --- BLINDAJE: normaliza el signo menos y fuerza columnas numericas ---
# (mismo problema que puede pasar con el archivo de temperatura: si el
# CSV viene de copiar una tabla web, el signo menos puede venir como el
# caracter unicode "\u2212" y arruinar las graficas).
co2 = co2.replace({"\u2212": "-"}, regex=True)
for col in co2.columns:
    if col not in (COL_YEAR, COL_MONTH):
        co2[col] = pd.to_numeric(co2[col], errors="coerce")

# Muchos archivos de Mauna Loa usan -99.99 como codigo de dato faltante
co2 = co2.replace(-99.99, np.nan)

# Construimos una fecha (dia 1 de cada mes) para graficar en el tiempo
co2["Fecha"] = pd.to_datetime(dict(year=co2[COL_YEAR], month=co2[COL_MONTH], day=1))

# Nos quedamos desde enero de 1960, como pide el enunciado
co2 = co2[co2["Fecha"] >= "1960-01-01"].reset_index(drop=True)

print("Datos de CO2 cargados:", co2.shape[0], "meses, desde",
      co2["Fecha"].min().date(), "hasta", co2["Fecha"].max().date())
print(co2[[COL_YEAR, COL_MONTH, COL_INTERPOLATED, COL_TREND]].head())


# -----------------------------------------------------------------------
# PREGUNTA 1.3.3: Linea de tiempo de CO2 (interpolated y trend)
# -----------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(co2["Fecha"], co2[COL_INTERPOLATED], label="Interpolated (valores mensuales)",
        color="tab:green", linewidth=1)
ax.plot(co2["Fecha"], co2[COL_TREND], label="Trend (tendencia, sin ciclo estacional)",
        color="tab:orange", linewidth=1.5)

ax.set_title("Concentracion de CO2 en la atmosfera - Observatorio de Mauna Loa\n"
             f"({co2['Fecha'].min().year}-{co2['Fecha'].max().year})")
ax.set_xlabel("Año")
ax.set_ylabel("CO2 (ppm - partes por millon)")
ax.legend()
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(OUTPUT_DIR / "fig_1_3_3_co2_tiempo.png", dpi=150)
plt.show()


# -----------------------------------------------------------------------
# PREGUNTA 1.3.4: CO2 (trend) vs anomalia de temperatura, dispersion + Pearson
# -----------------------------------------------------------------------
# Se elige un mes especifico de la Parte 1.1 (debe ser el MISMO mes que
# usaron en la pregunta 1.1.2(i) para que la comparacion sea consistente).
MES_ELEGIDO = "Jan"       # <-- mismo mes que en parte1_1
MES_NUM = 1               # 1=Jan, 2=Feb, ..., 12=Dec

RUTA_TEMP = BASE_DIR.parent / "RawData" / "NH_Ts_dSST.csv"
temp = pd.read_csv(RUTA_TEMP, skiprows=1, na_values="***")
temp_mes = temp[["Year", MES_ELEGIDO]].rename(columns={MES_ELEGIDO: "Anomalia"})

co2_mes = co2[co2[COL_MONTH] == MES_NUM][[COL_YEAR, COL_TREND]].rename(
    columns={COL_YEAR: "Year", COL_TREND: "CO2_trend"})

datos_unidos = pd.merge(temp_mes, co2_mes, on="Year", how="inner").dropna()

fig, ax = plt.subplots(figsize=(7, 6))
ax.scatter(datos_unidos["Anomalia"], datos_unidos["CO2_trend"],
           color="tab:purple", alpha=0.7, edgecolor="black")
ax.set_title(f"CO2 (tendencia) vs anomalia de temperatura - Mes: {MES_ELEGIDO}")
ax.set_xlabel("Anomalia de temperatura (°C)")
ax.set_ylabel("CO2 (ppm, tendencia)")
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(OUTPUT_DIR / "fig_1_3_4_dispersion_co2_temp.png", dpi=150)
plt.show()

r, p_valor = pearsonr(datos_unidos["Anomalia"], datos_unidos["CO2_trend"])
print(f"\nCoeficiente de correlacion de Pearson (mes={MES_ELEGIDO}): r = {r:.3f}"
      f" (p-valor = {p_valor:.2e})")
print(f"Numero de observaciones usadas: {len(datos_unidos)}")

print("\nListo. Archivos generados en la carpeta Outputs/:")
print(" - fig_1_3_3_co2_tiempo.png       (Pregunta 1.3.3)")
print(" - fig_1_3_4_dispersion_co2_temp.png (Pregunta 1.3.4)")
