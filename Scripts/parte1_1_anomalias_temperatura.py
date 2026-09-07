"""
Taller 5 - Consultoria Clima
PARTE 1.1 - Analizando anomalias de temperatura

Rol principal sugerido: Analista cuantitativo + Especialista en visualizacion
(pero todo el equipo debe entender y poder correr este script)

============================================================
COMO EJECUTAR ESTE SCRIPT EN SPYDER (Anaconda)
============================================================
1. Abre Anaconda Navigator -> Spyder (o desde Anaconda Prompt: `spyder`).
2. Abre este archivo (.py) con Spyder: File > Open.
3. Estructura de carpetas esperada (ajusta si la tuya es distinta):

       TuRepositorio/
       |-- RawData/
       |     |-- NH_Ts_dSST.csv
       |-- Scripts/   (o Code/)   <- aqui va este .py
       |-- Output/    (o Figures/)

   El script ya calcula la ruta a RawData/ de forma automatica a partir
   de su propia ubicacion (ver BASE_DIR mas abajo), asi que NO importa
   cual sea el "directorio de trabajo" (working directory) configurado
   en Spyder.
4. Para ejecutar: boton verde "Run file" (o tecla F5).
5. Las graficas apareceran en el panel "Plots" de Spyder (arriba a la
   derecha) y ademas se guardaran como archivos .png en la carpeta
   Outputs/ del proyecto (se crea automaticamente si no existe).

Requisitos (si falta algun paquete, instalar desde Anaconda Prompt):
    conda install pandas matplotlib numpy
    (o) pip install pandas matplotlib numpy
"""

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# -----------------------------------------------------------------------
# 0. CARGA DE DATOS
# -----------------------------------------------------------------------
# BASE_DIR = carpeta donde esta guardado este script. A partir de ahi
# construimos la ruta a RawData/, sin importar el working directory de Spyder.
BASE_DIR = Path(__file__).resolve().parent
RUTA_DATOS = BASE_DIR.parent / "RawData" / "NH_Ts_dSST.csv"

# Carpeta donde se guardan las graficas y tablas generadas (hermana de
# Scripts y RawData). Se crea automaticamente si no existe.
OUTPUT_DIR = BASE_DIR.parent / "Outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

# Si tu estructura de carpetas es distinta, comenta la linea anterior y
# escribe la ruta completa a mano, por ejemplo (Windows):
# RUTA_DATOS = r"C:\Users\TuUsuario\TuRepositorio\RawData\NH_Ts_dSST.csv"

# --- DIAGNOSTICO: muestra exactamente donde esta buscando el archivo ---
print(f"Carpeta del script (BASE_DIR): {BASE_DIR}")
print(f"Buscando el archivo de datos en: {RUTA_DATOS}")
if not RUTA_DATOS.exists():
    raise FileNotFoundError(
        f"\n\nNo se encontro el archivo en:\n  {RUTA_DATOS}\n\n"
        "Revisa que:\n"
        "  1) Este script (.py) este guardado dentro de la carpeta 'Scripts' "
        "de tu proyecto (no en otra ubicacion, ej. C:\\Users\\TuUsuario\\).\n"
        "  2) La carpeta 'RawData' este al mismo nivel que 'Scripts' "
        "(es decir, ambas dentro de la misma carpeta del proyecto).\n"
        "  3) El archivo CSV se llame exactamente 'NH_Ts_dSST.csv' "
        "(revisa mayusculas y que no termine en '.csv.txt').\n"
    )

# La primera fila del CSV original de GISS-NASA es un titulo, no datos.
# Los valores faltantes se marcan con '***'.
df = pd.read_csv(RUTA_DATOS, skiprows=1, na_values="***")

# --- BLINDAJE: forzar que todas las columnas (menos "Year") sean numericas ---
# Algunos archivos descargados desde una pagina web (en vez del CSV crudo)
# traen el signo menos como el caracter unicode "\u2212" en lugar del guion
# normal "-". Eso hace que pandas NO pueda leer los numeros negativos y
# convierta toda la columna a texto, lo que despues arruina la grafica
# (aparecen cientos de marcas de texto amontonadas en el eje Y).
# Estas dos lineas arreglan eso sin importar de donde salio el archivo:
df = df.replace({"\u2212": "-"}, regex=True)          # normaliza el signo menos
for col in df.columns:
    if col != "Year":
        df[col] = pd.to_numeric(df[col], errors="coerce")

print("\nTipos de datos despues del blindaje (todas deben ser float64, "
      "menos Year que es int64):")
print(df.dtypes)

# El ultimo anio suele venir incompleto (meses futuros = NaN). Lo dejamos,
# pandas y matplotlib ignoran los NaN automaticamente en las lineas.

print("Datos cargados:", df.shape[0], "anios, desde", df["Year"].min(),
      "hasta", df["Year"].max())
print(df.head())


# -----------------------------------------------------------------------
# PREGUNTA 1.1.2 (i): Un mes especifico, serie de tiempo 1880-actualidad
# -----------------------------------------------------------------------
MES = "Jan"  # <-- cambien el mes elegido por el equipo (Jan, Feb, ..., Dec)

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(df["Year"], df[MES], color="tab:red", linewidth=1.2)
ax.axhline(0, color="black", linewidth=1)
ax.text(df["Year"].min(), 0.03, "promedio de 1951 a 1980",
        fontsize=9, va="bottom")

ax.set_title(f"Anomalia de temperatura en el hemisferio norte - Mes: {MES}\n"
             f"({df['Year'].min()}-{df['Year'].max()})")
ax.set_xlabel("Año")
ax.set_ylabel("Anomalia de temperatura (°C)")
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(OUTPUT_DIR / "fig_1_1_2i_mes.png", dpi=150)
plt.show()


# -----------------------------------------------------------------------
# PREGUNTA 1.1.2 (ii): Promedios estacionales (DJF, MAM, JJA, SON)
# -----------------------------------------------------------------------
estaciones = ["DJF", "MAM", "JJA", "SON"]
nombres_es = {
    "DJF": "DJF (Dic-Ene-Feb, invierno boreal)",
    "MAM": "MAM (Mar-Abr-May, primavera boreal)",
    "JJA": "JJA (Jun-Jul-Ago, verano boreal)",
    "SON": "SON (Sep-Oct-Nov, otoño boreal)",
}

fig, ax = plt.subplots(figsize=(10, 5))
for est in estaciones:
    ax.plot(df["Year"], df[est], label=nombres_es[est], linewidth=1.1)

ax.axhline(0, color="black", linewidth=1)
ax.text(df["Year"].min(), 0.03, "promedio de 1951 a 1980",
        fontsize=9, va="bottom")

ax.set_title("Anomalia de temperatura por estacion del año\n"
             f"Hemisferio norte ({df['Year'].min()}-{df['Year'].max()})")
ax.set_xlabel("Año")
ax.set_ylabel("Anomalia de temperatura (°C)")
ax.legend(loc="upper left", fontsize=8)
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(OUTPUT_DIR / "fig_1_1_2ii_estaciones.png", dpi=150)
plt.show()


# -----------------------------------------------------------------------
# PREGUNTA 1.1.3 (iii): Promedio anual (columna J-D)
# -----------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(df["Year"], df["J-D"], color="tab:blue", linewidth=1.4)
ax.axhline(0, color="black", linewidth=1)
ax.text(df["Year"].min(), 0.03, "promedio de 1951 a 1980",
        fontsize=9, va="bottom")

ax.set_title("Anomalia de temperatura promedio anual\n"
             f"Hemisferio norte ({df['Year'].min()}-{df['Year'].max()})")
ax.set_xlabel("Año")
ax.set_ylabel("Anomalia de temperatura (°C)")
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(OUTPUT_DIR / "fig_1_1_3iii_anual.png", dpi=150)
plt.show()

print("\nListo. Se generaron 3 figuras en la carpeta Outputs/:")
print(" - fig_1_1_2i_mes.png       (Pregunta 1.1.2 (i): un mes)")
print(" - fig_1_1_2ii_estaciones.png (Pregunta 1.1.2 (ii): estaciones)")
print(" - fig_1_1_3iii_anual.png   (Pregunta 1.1.3 (iii): anual)")
