# ================================================================
# ACTIVIDAD INDIVIDUAL
# Análisis de nivel de ríos y quebradas - CORNARE / MARCO
# ================================================================

import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ================================================================
# 1. PARÁMETROS DE TU CONSULTA
# ================================================================

# Cada estudiante debe cambiar estos valores
NOMBRE_ESTUDIANTE = "Juan Jose Patiño Amariles"

CODIGO_ESTACION = "42"

FECHA_DESDE = "2026-08-23"
FECHA_HASTA = "2026-08-30"

CALIDAD = 1
# 1 = datos validados
# 0 = todos los datos disponibles


# ================================================================
# CONFIGURACIÓN DE LA API
# ================================================================

API_BASE_URL = "https://marco.cornare.gov.co/api/v1/estaciones"

LLAVE_FECHA = "level_date"
LLAVE_VALOR = "level"


# Coordenadas por defecto
LAT_DEFECTO = 6.2766
LON_DEFECTO = -75.5901

CANDIDATOS_LAT = ["lat", "latitude", "latitud"]
CANDIDATOS_LON = ["lng", "lon", "longitude", "longitud"]


# ================================================================
# 2. CONSULTAR LA API REAL Y TRAER TODAS LAS PÁGINAS
# ================================================================

def obtener_serie_nivel(codigo_estacion, desde, hasta, calidad=1, timeout=30):

    url = f"{API_BASE_URL}/{codigo_estacion}/nivel"

    params = {
        "desde": desde,
        "hasta": hasta,
        "calidad": calidad
    }

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json, text/plain, */*"
    }

    try:
        respuesta = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=timeout,
            verify=False
        )

        if respuesta.status_code == 200:
            return respuesta.json(), None

        return None, f"HTTP {respuesta.status_code}"

    except requests.exceptions.RequestException as e:
        return None, f"Error de red: {e}"


def obtener_todas_las_paginas(datos_json, timeout=30):

    registros = list(datos_json.get("values", []))

    siguiente_url = datos_json.get("next")

    while siguiente_url:

        try:
            respuesta = requests.get(
                siguiente_url,
                timeout=timeout,
                verify=False
            )

        except requests.exceptions.RequestException:
            break

        if respuesta.status_code != 200:
            break

        pagina = respuesta.json()

        registros.extend(
            pagina.get("values", [])
        )

        siguiente_url = pagina.get("next")

    return registros


# Ejecutar consulta
datos_crudos, error = obtener_serie_nivel(
    CODIGO_ESTACION,
    FECHA_DESDE,
    FECHA_HASTA,
    CALIDAD
)


if error:

    print("❌ Error al consultar la API:")
    print(error)

else:

    registros = obtener_todas_las_paginas(datos_crudos)

    print("Consulta realizada correctamente.")
    print("Cantidad de registros obtenidos:", len(registros))


# ================================================================
# 3. CONSTRUIR EL DATAFRAME DE SERIE DE TIEMPO
# ================================================================

if not error and registros:

    df = pd.DataFrame(registros)

    # Cambiar nombres de columnas
    df = df.rename(
        columns={
            LLAVE_FECHA: "fecha",
            LLAVE_VALOR: "nivel"
        }
    )

    print("Columnas disponibles:")
    print(df.columns.tolist())

    print("\nPrimeros registros:")
    display(df.head())


# ================================================================
# 4. TIPOS DE DATOS Y ORDEN TEMPORAL
# ================================================================

if not error and registros:

    # Convertir fecha a datetime
    df["fecha"] = pd.to_datetime(
        df["fecha"],
        errors="coerce"
    )

    # Convertir nivel a número
    df["nivel"] = pd.to_numeric(
        df["nivel"],
        errors="coerce"
    )

    # Eliminar registros que no tengan fecha o nivel
    df = df.dropna(
        subset=["fecha", "nivel"]
    )

    # Ordenar cronológicamente
    df = df.sort_values(
        "fecha"
    ).reset_index(drop=True)

    print("Tipos de datos:")

    print(df.dtypes)

    print("\nRango temporal:")

    print("Desde:", df["fecha"].min())
    print("Hasta:", df["fecha"].max())

    print("\nCantidad de registros:", len(df))

    print("\nDataFrame ordenado:")
    display(df.head(10))


# ================================================================
# 5. MISSING VALUES REALES
#    MÉTODO CORRECTO: REINDEXAR A FRECUENCIA REGULAR
# ================================================================

if not error and registros and len(df) > 1:

    # ------------------------------------------------------------
    # Detectar la frecuencia típica de medición
    # ------------------------------------------------------------

    diferencias = (
        df["fecha"]
        .sort_values()
        .diff()
        .dropna()
    )

    frecuencia_tipica = diferencias.mode()

    if len(frecuencia_tipica) > 0:

        frecuencia = frecuencia_tipica.iloc[0]

        print("Frecuencia típica detectada:")
        print(frecuencia)

    else:

        frecuencia = None

        print("No fue posible determinar la frecuencia.")


    # ------------------------------------------------------------
    # Reindexar a frecuencia regular
    # ------------------------------------------------------------

    if frecuencia is not None:

        # Convertimos la frecuencia a una frecuencia de pandas
        frecuencia_str = pd.tseries.frequencies.to_offset(
            frecuencia
        )

        indice_completo = pd.date_range(
            start=df["fecha"].min(),
            end=df["fecha"].max(),
            freq=frecuencia_str
        )

        df_missing = (
            df.set_index("fecha")
            .reindex(indice_completo)
        )

        df_missing.index.name = "fecha"

        # --------------------------------------------------------
        # Identificar missing values reales
        # --------------------------------------------------------

        cantidad_missing = df_missing["nivel"].isna().sum()

        total_esperado = len(df_missing)

        print("\n========== MISSING VALUES ==========")

        print("Registros esperados:", total_esperado)
        print("Registros originales:", len(df))
        print("Missing values reales:", cantidad_missing)

        porcentaje_missing = (
            cantidad_missing / total_esperado
        ) * 100

        print(
            f"Porcentaje de missing: "
            f"{porcentaje_missing:.2f}%"
        )

        print("\nPrimeros registros con estructura regular:")

        display(df_missing.head(20))

    else:

        df_missing = df.set_index("fecha").copy()

else:

    print("No hay suficientes datos para analizar missing values.")


# ================================================================
# 6. OUTLIERS CON IQR + LÍMITES FÍSICOS
# ================================================================

if not error and registros:

    # Trabajamos únicamente con valores existentes
    serie_nivel = df["nivel"].dropna()

    # ------------------------------------------------------------
    # Método IQR
    # ------------------------------------------------------------

    Q1 = serie_nivel.quantile(0.25)

    Q3 = serie_nivel.quantile(0.75)

    IQR = Q3 - Q1

    limite_inferior_iqr = Q1 - 1.5 * IQR

    limite_superior_iqr = Q3 + 1.5 * IQR


    # ------------------------------------------------------------
    # Límites físicos
    # ------------------------------------------------------------

    # Un nivel negativo no tiene sentido físico
    limite_fisico_inferior = 0

    # Para el límite superior no imponemos un valor arbitrario,
    # porque depende de las características de cada estación.
    limite_fisico_superior = np.inf


    # ------------------------------------------------------------
    # Detectar outliers
    # ------------------------------------------------------------

    df["outlier_iqr"] = (
        (df["nivel"] < limite_inferior_iqr) |
        (df["nivel"] > limite_superior_iqr)
    )

    df["outlier_fisico"] = (
        (df["nivel"] < limite_fisico_inferior) |
        (df["nivel"] > limite_fisico_superior)
    )

    df["outlier"] = (
        df["outlier_iqr"] |
        df["outlier_fisico"]
    )


    cantidad_outliers = df["outlier"].sum()

    print("\n========== OUTLIERS ==========")

    print(f"Q1: {Q1:.4f}")
    print(f"Q3: {Q3:.4f}")
    print(f"IQR: {IQR:.4f}")

    print(
        f"Límite inferior IQR: "
        f"{limite_inferior_iqr:.4f}"
    )

    print(
        f"Límite superior IQR: "
        f"{limite_superior_iqr:.4f}"
    )

    print(
        "Límite físico inferior: 0"
    )

    print(
        f"Cantidad de outliers: "
        f"{cantidad_outliers}"
    )

    print("\nRegistros considerados outliers:")

    display(
        df[df["outlier"]]
    )


# ================================================================
# GRÁFICO DE OUTLIERS
# ================================================================

if not error and registros:

    plt.figure(figsize=(12, 5))

    plt.plot(
        df["fecha"],
        df["nivel"],
        label="Nivel"
    )

    plt.scatter(
        df.loc[df["outlier"], "fecha"],
        df.loc[df["outlier"], "nivel"],
        label="Outliers"
    )

    plt.axhline(
        limite_superior_iqr,
        linestyle="--",
        label="Límite superior IQR"
    )

    plt.axhline(
        limite_inferior_iqr,
        linestyle="--",
        label="Límite inferior IQR"
    )

    plt.title(
        "Detección de outliers - Método IQR"
    )

    plt.xlabel("Fecha")
    plt.ylabel("Nivel")

    plt.legend()

    plt.grid(True)

    plt.show()


# ================================================================
# 7. NORMALIZACIÓN Y ESTANDARIZACIÓN
# ================================================================

if not error and registros:

    # ------------------------------------------------------------
    # Para evitar fuga de información (data leakage),
    # los parámetros se calculan sobre los datos de entrenamiento.
    # ------------------------------------------------------------

    datos_modelo = df[
        ["fecha", "nivel"]
    ].copy()

    # Quitamos outliers antes de preparar el modelo
    datos_modelo = datos_modelo[
        ~df["outlier"]
    ]

    datos_modelo = datos_modelo.dropna()

    datos_modelo = datos_modelo.sort_values(
        "fecha"
    ).reset_index(drop=True)


    # ------------------------------------------------------------
    # Primero dividimos temporalmente
    # ------------------------------------------------------------

    n = len(datos_modelo)

    n_train = int(n * 0.70)

    n_validation = int(n * 0.15)

    train = datos_modelo.iloc[
        :n_train
    ].copy()

    validation = datos_modelo.iloc[
        n_train:n_train + n_validation
    ].copy()

    test = datos_modelo.iloc[
        n_train + n_validation:
    ].copy()


    # ------------------------------------------------------------
    # NORMALIZACIÓN MIN-MAX
    # ------------------------------------------------------------

    minimo = train["nivel"].min()

    maximo = train["nivel"].max()

    if maximo != minimo:

        train["nivel_normalizado"] = (
            (train["nivel"] - minimo) /
            (maximo - minimo)
        )

        validation["nivel_normalizado"] = (
            (validation["nivel"] - minimo) /
            (maximo - minimo)
        )

        test["nivel_normalizado"] = (
            (test["nivel"] - minimo) /
            (maximo - minimo)
        )

    else:

        train["nivel_normalizado"] = 0

        validation["nivel_normalizado"] = 0

        test["nivel_normalizado"] = 0


    # ------------------------------------------------------------
    # ESTANDARIZACIÓN Z-SCORE
    # ------------------------------------------------------------

    media_train = train["nivel"].mean()

    desviacion_train = train["nivel"].std()

    if desviacion_train != 0:

        train["nivel_estandarizado"] = (
            (train["nivel"] - media_train) /
            desviacion_train
        )

        validation["nivel_estandarizado"] = (
            (validation["nivel"] - media_train) /
            desviacion_train
        )

        test["nivel_estandarizado"] = (
            (test["nivel"] - media_train) /
            desviacion_train
        )

    else:

        train["nivel_estandarizado"] = 0

        validation["nivel_estandarizado"] = 0

        test["nivel_estandarizado"] = 0


    print("\n========== NORMALIZACIÓN ==========")

    print(
        f"Mínimo utilizado (TRAIN): {minimo:.4f}"
    )

    print(
        f"Máximo utilizado (TRAIN): {maximo:.4f}"
    )

    print(
        f"Media utilizada (TRAIN): {media_train:.4f}"
    )

    print(
        f"Desviación estándar (TRAIN): "
        f"{desviacion_train:.4f}"
    )


    print("\nDatos normalizados y estandarizados:")

    display(
        train.head(10)
    )


# ================================================================
# 8. TRAIN / VALIDATION / TEST
#    SPLIT CRONOLÓGICO
# ================================================================

if not error and registros:

    print("\n========== DIVISIÓN TEMPORAL ==========")

    print(
        f"TRAIN: {len(train)} registros "
        f"({len(train) / len(datos_modelo) * 100:.1f}%)"
    )

    print(
        f"VALIDATION: {len(validation)} registros "
        f"({len(validation) / len(datos_modelo) * 100:.1f}%)"
    )

    print(
        f"TEST: {len(test)} registros "
        f"({len(test) / len(datos_modelo) * 100:.1f}%)"
    )


    print("\nRangos de fechas:")

    if not train.empty:
        print(
            "TRAIN:",
            train["fecha"].min(),
            "->",
            train["fecha"].max()
        )

    if not validation.empty:
        print(
            "VALIDATION:",
            validation["fecha"].min(),
            "->",
            validation["fecha"].max()
        )

    if not test.empty:
        print(
            "TEST:",
            test["fecha"].min(),
            "->",
            test["fecha"].max()
        )


# ---------------------------------------------------------------
# Gráfico del split
# ---------------------------------------------------------------

if not error and registros:

    plt.figure(figsize=(12, 5))

    if not train.empty:
        plt.plot(
            train["fecha"],
            train["nivel"],
            label="Train"
        )

    if not validation.empty:
        plt.plot(
            validation["fecha"],
            validation["nivel"],
            label="Validation"
        )

    if not test.empty:
        plt.plot(
            test["fecha"],
            test["nivel"],
            label="Test"
        )

    plt.title(
        "División cronológica Train / Validation / Test"
    )

    plt.xlabel("Fecha")
    plt.ylabel("Nivel")

    plt.legend()

    plt.grid(True)

    plt.show()


# ================================================================
# 9. ESTADÍSTICA DESCRIPTIVA
# ================================================================

if not error and registros:

    print("\n========== ESTADÍSTICA DESCRIPTIVA ==========")

    estadistica = df["nivel"].describe()

    display(
        estadistica
    )


    # Estadísticas adicionales
    print("\nMedidas principales:")

    print(
        f"Media: "
        f"{df['nivel'].mean():.4f}"
    )

    print(
        f"Mediana: "
        f"{df['nivel'].median():.4f}"
    )

    print(
        f"Desviación estándar: "
        f"{df['nivel'].std():.4f}"
    )

    print(
        f"Mínimo: "
        f"{df['nivel'].min():.4f}"
    )

    print(
        f"Máximo: "
        f"{df['nivel'].max():.4f}"
    )

    print(
        f"Rango: "
        f"{df['nivel'].max() - df['nivel'].min():.4f}"
    )


# ================================================================
# RESUMEN FINAL
# ================================================================

if not error and registros:

    print("\n")
    print("=" * 60)
    print("RESUMEN DEL ANÁLISIS")
    print("=" * 60)

    print(
        f"Estudiante: {NOMBRE_ESTUDIANTE}"
    )

    print(
        f"Estación: {CODIGO_ESTACION}"
    )

    print(
        f"Periodo: {FECHA_DESDE} hasta {FECHA_HASTA}"
    )

    print(
        f"Lecturas originales: {len(df)}"
    )

    if "cantidad_missing" in locals():

        print(
            f"Missing values reales: "
            f"{cantidad_missing}"
        )

    print(
        f"Outliers detectados: "
        f"{cantidad_outliers}"
    )

    print(
        f"Promedio del nivel: "
        f"{df['nivel'].mean():.4f}"
    )

    print(
        f"Desviación estándar: "
        f"{df['nivel'].std():.4f}"
    )

    print("=" * 60)
