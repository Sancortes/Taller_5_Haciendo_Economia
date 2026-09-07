"""
Taller 5 - Consultoria Clima
PARTE 1.2 - Variacion de la temperatura en el tiempo

Rol principal sugerido: Analista cuantitativo (tablas, cuantiles, varianzas)
                         + Especialista en visualizacion (histogramas)

============================================================
COMO EJECUTAR ESTE SCRIPT EN SPYDER (Anaconda)
============================================================
1. Abre este archivo en Spyder (File > Open).
2. Estructura de carpetas esperada (ajusta si la tuya es distinta):

       TuRepositorio/
       |-- RawData/
       |     |-- NH_Ts_dSST.csv
       |-- Scripts/   (o Code/)   <- aqui va este .py
       |-- Output/    (o Figures/)

   La ruta a RawData/ se calcula automaticamente a partir de la ubicacion
   de este script (BASE_DIR), asi que no depende del working directory
   configurado en Spyder.
3. Ejecutar con el boton verde "Run file" (o F5).
4. Las graficas apareceran en el panel "Plots" de Spyder y tambien se
   guardaran como .png en la misma carpeta del script. Las tablas se
   guardan como .csv en esa misma carpeta.

Requisitos (si falta algun paquete, instalar desde Anaconda Prompt):
    conda install pandas matplotlib numpy
"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parent
RUTA_DATOS = BASE_DIR.parent / "RawData" / "NH_Ts_dSST.csv"
# Si tu estructura de carpetas es distinta, reemplaza por la ruta completa:
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
        "  2) La carpeta 'RawData' este al mismo nivel que 'Scripts'.\n"
        "  3) El archivo CSV se llame exactamente 'NH_Ts_dSST.csv'.\n"
    )

df = pd.read_csv(RUTA_DATOS, skiprows=1, na_values="***")

# --- BLINDAJE: forzar que todas las columnas (menos "Year") sean numericas ---
# Algunos archivos descargados desde una pagina web traen el signo menos
# como el caracter unicode "\u2212" en vez del guion normal "-", lo que
# hace que pandas lea la columna como texto en vez de numero. Esto arregla
# eso sin importar de donde salio el archivo:
df = df.replace({"\u2212": "-"}, regex=True)
for col in df.columns:
    if col != "Year":
        df[col] = pd.to_numeric(df[col], errors="coerce")

# Usaremos las anomalias MENSUALES (todas las observaciones mes a mes),
# que es el enfoque del articulo del NYT (miles de observaciones,
# no solo el promedio anual). Convertimos el bloque Jan..Dec a formato
# "largo" (una fila por mes-año).
meses = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
         "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

df_largo = df.melt(id_vars=["Year"], value_vars=meses,
                    var_name="Mes", value_name="Anomalia")
df_largo = df_largo.dropna(subset=["Anomalia"])


def periodo(df_in, ini, fin):
    return df_in[(df_in["Year"] >= ini) & (df_in["Year"] <= fin)]["Anomalia"]


p1951_1980 = periodo(df_largo, 1951, 1980)
p1981_2010 = periodo(df_largo, 1981, 2010)
p1921_1950 = periodo(df_largo, 1921, 1950)

# -----------------------------------------------------------------------
# PREGUNTA 1.2.1: Tablas de frecuencia (similares a Figura 1.6)
# -----------------------------------------------------------------------
# Se agrupan las anomalias en intervalos (bins) de 0.5 °C, al estilo del
# articulo del NYT ("mucho mas frio", "mas frio", "normal", "mas caliente",
# "mucho mas caliente"). Ajusten los bins si su docente pide otro esquema.

bins = [-3, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 3]
etiquetas = ["< -1.5", "-1.5 a -1", "-1 a -0.5", "-0.5 a 0",
             "0 a 0.5", "0.5 a 1", "1 a 1.5", "> 1.5"]


def tabla_frecuencias(serie, etiqueta_periodo):
    cortes = pd.cut(serie, bins=bins, labels=etiquetas, right=False)
    tabla = cortes.value_counts().sort_index().rename("Frecuencia").to_frame()
    tabla["Porcentaje (%)"] = (tabla["Frecuencia"] / tabla["Frecuencia"].sum() * 100).round(1)
    print(f"\nTabla de frecuencias {etiqueta_periodo}")
    print(tabla)
    return tabla


tabla_1951_1980 = tabla_frecuencias(p1951_1980, "1951-1980")
tabla_1981_2010 = tabla_frecuencias(p1981_2010, "1981-2010")

tabla_1951_1980.to_csv(BASE_DIR / "tabla_frecuencias_1951_1980.csv")
tabla_1981_2010.to_csv(BASE_DIR / "tabla_frecuencias_1981_2010.csv")


# -----------------------------------------------------------------------
# PREGUNTA 1.2.2: Histogramas comparando ambos periodos
# -----------------------------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=True)

axes[0].hist(p1951_1980, bins=15, color="steelblue", edgecolor="black")
axes[0].axvline(0, color="black", linewidth=1)
axes[0].set_title("Distribucion de anomalias\n1951-1980")
axes[0].set_xlabel("Anomalia de temperatura (°C)")
axes[0].set_ylabel("Frecuencia (numero de meses)")

axes[1].hist(p1981_2010, bins=15, color="indianred", edgecolor="black")
axes[1].axvline(0, color="black", linewidth=1)
axes[1].set_title("Distribucion de anomalias\n1981-2010")
axes[1].set_xlabel("Anomalia de temperatura (°C)")

fig.suptitle("Comparacion de la distribucion de anomalias de temperatura\n"
             "Hemisferio norte, datos mensuales")
fig.tight_layout()
fig.savefig(BASE_DIR / "fig_1_2_2_histogramas.png", dpi=150)
plt.show()

# Version superpuesta (opcional, ayuda a comparar directamente)
fig, ax = plt.subplots(figsize=(9, 5))
ax.hist(p1951_1980, bins=15, alpha=0.6, label="1951-1980", color="steelblue")
ax.hist(p1981_2010, bins=15, alpha=0.6, label="1981-2010", color="indianred")
ax.axvline(0, color="black", linewidth=1)
ax.set_title("Distribucion de anomalias de temperatura: 1951-1980 vs 1981-2010")
ax.set_xlabel("Anomalia de temperatura (°C)")
ax.set_ylabel("Frecuencia (numero de meses)")
ax.legend()
fig.tight_layout()
fig.savefig(BASE_DIR / "fig_1_2_2_histogramas_superpuestos.png", dpi=150)
plt.show()


# -----------------------------------------------------------------------
# PREGUNTA 1.2.3: Deciles 3 y 7 del periodo 1951-1980
# -----------------------------------------------------------------------
decil_3 = np.quantile(p1951_1980, 0.3)
decil_7 = np.quantile(p1951_1980, 0.7)

print(f"\nDecil 3 (1951-1980): {decil_3:.3f} °C  -> umbral 'frio'")
print(f"Decil 7 (1951-1980): {decil_7:.3f} °C  -> umbral 'caliente'")


# -----------------------------------------------------------------------
# PREGUNTA 1.2.4: % de meses "calientes" en 1981-2010 usando esos umbrales
# -----------------------------------------------------------------------
n_total_81_10 = len(p1981_2010)
n_calientes_81_10 = (p1981_2010 > decil_7).sum()
pct_calientes_81_10 = n_calientes_81_10 / n_total_81_10 * 100

# Para comparar: en 1951-1980, por definicion, el 30% deberia ser "caliente"
n_calientes_51_80 = (p1951_1980 > decil_7).sum()
pct_calientes_51_80 = n_calientes_51_80 / len(p1951_1980) * 100

print(f"\nMeses 'calientes' (> decil 7 de 1951-1980) en 1981-2010: "
      f"{n_calientes_81_10} de {n_total_81_10} ({pct_calientes_81_10:.1f}%)")
print(f"(Referencia: en 1951-1980 esto era, por construccion, ~"
      f"{pct_calientes_51_80:.1f}%)")


# -----------------------------------------------------------------------
# PREGUNTA 1.2.5: Media y varianza estacional en tres periodos
# -----------------------------------------------------------------------
estaciones = ["DJF", "MAM", "JJA", "SON"]
periodos_def = {
    "1921-1950": (1921, 1950),
    "1951-1980": (1951, 1980),
    "1981-2010": (1981, 2010),
}

resultados = []
for nombre_periodo, (ini, fin) in periodos_def.items():
    sub = df[(df["Year"] >= ini) & (df["Year"] <= fin)]
    for est in estaciones:
        resultados.append({
            "Periodo": nombre_periodo,
            "Estacion": est,
            "Media": sub[est].mean(),
            "Varianza": sub[est].var(),
        })

tabla_estacional = pd.DataFrame(resultados)
tabla_pivote_media = tabla_estacional.pivot(index="Estacion", columns="Periodo", values="Media")
tabla_pivote_var = tabla_estacional.pivot(index="Estacion", columns="Periodo", values="Varianza")

print("\nMedia estacional por periodo:")
print(tabla_pivote_media.round(3))
print("\nVarianza estacional por periodo:")
print(tabla_pivote_var.round(4))

tabla_estacional.to_csv(BASE_DIR / "tabla_media_varianza_estacional.csv", index=False)

print("\nListo. Archivos generados:")
print(" - tabla_frecuencias_1951_1980.csv / tabla_frecuencias_1981_2010.csv (Pregunta 1.2.1)")
print(" - fig_1_2_2_histogramas.png y fig_1_2_2_histogramas_superpuestos.png (Pregunta 1.2.2)")
print(" - tabla_media_varianza_estacional.csv (Pregunta 1.2.5)")
