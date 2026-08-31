"""
App Streamlit — Análisis de nivel de ríos/quebradas
CORNARE / MARCO

Actividad individual:
1. Parámetros de consulta
2. Consulta de la API real
3. Construcción del DataFrame
4. Tipos de datos y orden temporal
5. Missing values reales mediante reindexación
6. Outliers mediante IQR + límites físicos
7. Normalización y estandarización
8. Train / Validation / Test cronológico
9. Estadística descriptiva

Para ejecutar:

    streamlit run app_nivel_cornare.py
"""

import requests
import pandas as pd
import numpy as np
import streamlit as st
import urllib3
import matplotlib.pyplot as plt


# ================================================================
# CONFIGURACIÓN
# ================================================================

urllib3.disable_warnings(
    urllib3.exceptions.InsecureRequestWarning
)

st.set_page_config(
    page_title="Nivel de estación — CORNARE",
    page_icon="🌊",
    layout="wide"
)


# ================================================================
# CONSTANTES
# ================================================================

API_BASE_URL = (
    "https://marco.cornare.gov.co/api/v1/estaciones"
)

LLAVE_FECHA = "level_date"
LLAVE_VALOR = "level"

LAT_DEFECTO = 6.2766
LON_DEFECTO = -75.5901

CANDIDATOS_LAT = [
    "lat",
    "latitude",
    "latitud"
]

CANDIDATOS_LON = [
    "lng",
    "lon",
    "longitude",
    "longitud"
]


# ================================================================
# FUNCIONES
# ================================================================

def obtener_serie_nivel(
    codigo_estacion,
    desde,
    hasta,
    calidad=1,
    timeout=30
):
    """
    Consulta la API de CORNARE para obtener
    la serie de nivel de una estación.
    """

    url = (
        f"{API_BASE_URL}/"
        f"{codigo_estacion}/nivel"
    )

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
        "Accept": (
            "application/json, "
            "text/plain, */*"
        )
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

        return (
            None,
            f"HTTP {respuesta.status_code}"
        )

    except requests.exceptions.RequestException as e:

        return (
            None,
            f"Error de red: {e}"
        )


def obtener_todas_las_paginas(
    datos_json,
    timeout=30
):
    """
    Obtiene todos los registros de la API,
    incluyendo las páginas siguientes.
    """

    if not isinstance(datos_json, dict):
        return []

    registros = list(
        datos_json.get("values", [])
    )

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


def detectar_coordenadas(datos_json):
    """
    Busca latitud y longitud en la respuesta de la API.
    Si no existen, utiliza las coordenadas por defecto.
    """

    if not isinstance(datos_json, dict):

        return (
            LAT_DEFECTO,
            LON_DEFECTO,
            False
        )

    lat = next(
        (
            datos_json[k]
            for k in CANDIDATOS_LAT
            if k in datos_json
        ),
        None
    )

    lon = next(
        (
            datos_json[k]
            for k in CANDIDATOS_LON
            if k in datos_json
        ),
        None
    )

    if lat is not None and lon is not None:

        try:

            return (
                float(lat),
                float(lon),
                True
            )

        except (
            TypeError,
            ValueError
        ):

            pass

    return (
        LAT_DEFECTO,
        LON_DEFECTO,
        False
    )


def detectar_frecuencia(df):
    """
    Detecta la frecuencia típica de medición.
    """

    if len(df) < 2:
        return None

    diferencias = (
        df["fecha"]
        .sort_values()
        .diff()
        .dropna()
    )

    if diferencias.empty:
        return None

    moda = diferencias.mode()

    if moda.empty:
        return None

    return moda.iloc[0]


def calcular_missing_values(df):
    """
    Reindexa la serie temporal utilizando
    la frecuencia típica para identificar
    missing values reales.
    """

    frecuencia = detectar_frecuencia(df)

    if frecuencia is None:

        return (
            df.set_index("fecha"),
            None,
            0
        )

    offset = pd.tseries.frequencies.to_offset(
        frecuencia
    )

    indice_completo = pd.date_range(
        start=df["fecha"].min(),
        end=df["fecha"].max(),
        freq=offset
    )

    df_regular = (
        df
        .set_index("fecha")
        .reindex(indice_completo)
    )

    df_regular.index.name = "fecha"

    cantidad_missing = (
        df_regular["nivel"]
        .isna()
        .sum()
    )

    return (
        df_regular,
        frecuencia,
        int(cantidad_missing)
    )


def detectar_outliers(df):
    """
    Detecta outliers mediante IQR
    y límites físicos.
    """

    serie = df["nivel"].dropna()

    if serie.empty:

        return (
            df.copy(),
            0,
            0,
            0,
            0
        )

    q1 = serie.quantile(0.25)
    q3 = serie.quantile(0.75)

    iqr = q3 - q1

    limite_inferior = (
        q1 - 1.5 * iqr
    )

    limite_superior = (
        q3 + 1.5 * iqr
    )

    # Límite físico:
    # un nivel negativo no es válido.
    limite_fisico_inferior = 0

    df_resultado = df.copy()

    df_resultado["outlier_iqr"] = (
        (df_resultado["nivel"] < limite_inferior)
        |
        (df_resultado["nivel"] > limite_superior)
    )

    df_resultado["outlier_fisico"] = (
        df_resultado["nivel"]
        < limite_fisico_inferior
    )

    df_resultado["outlier"] = (
        df_resultado["outlier_iqr"]
        |
        df_resultado["outlier_fisico"]
    )

    cantidad_outliers = int(
        df_resultado["outlier"].sum()
    )

    return (
        df_resultado,
        q1,
        q3,
        limite_inferior,
        limite_superior,
        cantidad_outliers
    )


def dividir_datos_cronologicamente(df):
    """
    Divide los datos en:
    70% Train
    15% Validation
    15% Test

    respetando el orden temporal.
    """

    n = len(df)

    if n == 0:

        return (
            pd.DataFrame(),
            pd.DataFrame(),
            pd.DataFrame()
        )

    n_train = int(n * 0.70)

    n_validation = int(n * 0.15)

    train = df.iloc[
        :n_train
    ].copy()

    validation = df.iloc[
        n_train:
        n_train + n_validation
    ].copy()

    test = df.iloc[
        n_train + n_validation:
    ].copy()

    return (
        train,
        validation,
        test
    )


def aplicar_transformaciones(
    train,
    validation,
    test
):
    """
    Normalización Min-Max y estandarización Z-Score.

    Los parámetros se calculan únicamente
    usando TRAIN para evitar data leakage.
    """

    train = train.copy()
    validation = validation.copy()
    test = test.copy()

    if train.empty:

        return (
            train,
            validation,
            test,
            None
        )

    minimo = train["nivel"].min()
    maximo = train["nivel"].max()

    media = train["nivel"].mean()
    desviacion = train["nivel"].std()

    # ------------------------------------------------------------
    # NORMALIZACIÓN MIN-MAX
    # ------------------------------------------------------------

    if maximo != minimo:

        train["nivel_normalizado"] = (
            (train["nivel"] - minimo)
            /
            (maximo - minimo)
        )

        validation["nivel_normalizado"] = (
            (validation["nivel"] - minimo)
            /
            (maximo - minimo)
        )

        test["nivel_normalizado"] = (
            (test["nivel"] - minimo)
            /
            (maximo - minimo)
        )

    else:

        train["nivel_normalizado"] = 0
        validation["nivel_normalizado"] = 0
        test["nivel_normalizado"] = 0

    # ------------------------------------------------------------
    # ESTANDARIZACIÓN Z-SCORE
    # ------------------------------------------------------------

    if pd.notna(desviacion) and desviacion != 0:

        train["nivel_estandarizado"] = (
            (train["nivel"] - media)
            /
            desviacion
        )

        validation["nivel_estandarizado"] = (
            (validation["nivel"] - media)
            /
            desviacion
        )

        test["nivel_estandarizado"] = (
            (test["nivel"] - media)
            /
            desviacion
        )

    else:

        train["nivel_estandarizado"] = 0
        validation["nivel_estandarizado"] = 0
        test["nivel_estandarizado"] = 0

    parametros = {
        "minimo": minimo,
        "maximo": maximo,
        "media": media,
        "desviacion": desviacion
    }

    return (
        train,
        validation,
        test,
        parametros
    )


# ================================================================
# SIDEBAR
# ================================================================

st.sidebar.header(
    "⚙️ Parámetros de tu consulta"
)

nombre_estudiante = st.sidebar.text_input(
    "Nombre del estudiante",
    "Juan Jose Patiño Amariles"
)

codigo_estacion = st.sidebar.text_input(
    "Código de estación",
    "42"
)

fecha_desde = st.sidebar.date_input(
    "Desde",
    pd.to_datetime("2026-08-23")
).strftime("%Y-%m-%d")

fecha_hasta = st.sidebar.date_input(
    "Hasta",
    pd.to_datetime("2026-08-30")
).strftime("%Y-%m-%d")

calidad = st.sidebar.selectbox(
    "Calidad",
    [1, 0],
    index=0,
    help="1 = solo datos validados"
)

consultar = st.sidebar.button(
    "🔍 Consultar",
    type="primary"
)


# ================================================================
# TÍTULO
# ================================================================

st.title(
    "🌊 Nivel de ríos y quebradas — CORNARE"
)

st.caption(
    f"Estudiante: **{nombre_estudiante}** "
    f"· Estación: **{codigo_estacion}**"
)


# ================================================================
# CONSULTA
# ================================================================

if consultar:

    if fecha_desde > fecha_hasta:

        st.error(
            "❌ La fecha inicial no puede ser "
            "posterior a la fecha final."
        )

        st.stop()

    with st.spinner(
        "Consultando la API de CORNARE..."
    ):

        datos_crudos, error = (
            obtener_serie_nivel(
                codigo_estacion,
                fecha_desde,
                fecha_hasta,
                calidad
            )
        )

    if error:

        st.error(
            f"❌ {error}"
        )

        st.info(
            "Verifica el código de estación "
            "y el rango de fechas."
        )

        st.stop()


    # ============================================================
    # OBTENER TODAS LAS PÁGINAS
    # ============================================================

    registros = obtener_todas_las_paginas(
        datos_crudos
    )

    if not registros:

        st.warning(
            "⚠️ No hay registros para esta "
            "estación y rango de fechas."
        )

        st.stop()


    st.success(
        f"✅ Consulta realizada correctamente. "
        f"Se obtuvieron {len(registros)} registros."
    )


    # ============================================================
    # 3. CONSTRUIR DATAFRAME
    # ============================================================

    df = pd.DataFrame(
        registros
    )

    df = df.rename(
        columns={
            LLAVE_FECHA: "fecha",
            LLAVE_VALOR: "nivel"
        }
    )

    if "fecha" not in df.columns:

        st.error(
            "❌ La API no contiene la columna "
            "'level_date'."
        )

        st.stop()

    if "nivel" not in df.columns:

        st.error(
            "❌ La API no contiene la columna "
            "'level'."
        )

        st.stop()


    # ============================================================
    # 4. TIPOS DE DATOS Y ORDEN TEMPORAL
    # ============================================================

    df["fecha"] = pd.to_datetime(
        df["fecha"],
        errors="coerce"
    )

    df["nivel"] = pd.to_numeric(
        df["nivel"],
        errors="coerce"
    )

    registros_antes = len(df)

    df = df.dropna(
        subset=[
            "fecha",
            "nivel"
        ]
    )

    registros_eliminados = (
        registros_antes - len(df)
    )

    df = (
        df
        .sort_values("fecha")
        .reset_index(drop=True)
    )


    # ============================================================
    # INFORMACIÓN GENERAL
    # ============================================================

    st.subheader(
        "📋 1. Parámetros de la consulta"
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Estación",
        codigo_estacion
    )

    col2.metric(
        "Desde",
        fecha_desde
    )

    col3.metric(
        "Hasta",
        fecha_hasta
    )

    col4.metric(
        "Calidad",
        calidad
    )


    # ============================================================
    # DATAFRAME
    # ============================================================

    st.subheader(
        "📊 3. DataFrame de la serie de tiempo"
    )

    st.dataframe(
        df.head(20),
        use_container_width=True
    )


    # ============================================================
    # TIPOS DE DATOS
    # ============================================================

    with st.expander(
        "🔎 4. Tipos de datos y orden temporal"
    ):

        col1, col2 = st.columns(2)

        with col1:

            st.write(
                "**Tipos de datos:**"
            )

            st.dataframe(
                pd.DataFrame(
                    {
                        "Columna": df.columns,
                        "Tipo": [
                            str(tipo)
                            for tipo in df.dtypes
                        ]
                    }
                ),
                use_container_width=True
            )

        with col2:

            st.write(
                "**Información temporal:**"
            )

            st.write(
                f"📅 Primera fecha: "
                f"**{df['fecha'].min()}**"
            )

            st.write(
                f"📅 Última fecha: "
                f"**{df['fecha'].max()}**"
            )

            st.write(
                f"📈 Total de lecturas válidas: "
                f"**{len(df)}**"
            )

            st.write(
                f"🗑️ Registros eliminados por "
                f"datos inválidos: "
                f"**{registros_eliminados}**"
            )


    # ============================================================
    # 5. MISSING VALUES
    # ============================================================

    st.subheader(
        "🔎 5. Missing values reales"
    )

    (
        df_regular,
        frecuencia,
        cantidad_missing
    ) = calcular_missing_values(df)

    if frecuencia is not None:

        st.write(
            f"**Frecuencia típica detectada:** "
            f"{frecuencia}"
        )

        total_esperado = len(
            df_regular
        )

        porcentaje_missing = (
            cantidad_missing /
            total_esperado *
            100
        ) if total_esperado > 0 else 0

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Registros originales",
            len(df)
        )

        col2.metric(
            "Registros esperados",
            total_esperado
        )

        col3.metric(
            "Missing values",
            cantidad_missing
        )

        st.write(
            f"Porcentaje de missing values: "
            f"**{porcentaje_missing:.2f}%**"
        )

        if cantidad_missing > 0:

            st.warning(
                "⚠️ Se encontraron huecos "
                "reales en la serie temporal."
            )

            st.write(
                "**Fechas donde faltan mediciones:**"
            )

            fechas_missing = (
                df_regular[
                    df_regular["nivel"].isna()
                ]
                .reset_index()
                .rename(
                    columns={
                        "index": "fecha"
                    }
                )
            )

            st.dataframe(
                fechas_missing,
                use_container_width=True
            )

        else:

            st.success(
                "✅ No se encontraron "
                "missing values."
            )

    else:

        st.info(
            "No fue posible determinar "
            "una frecuencia regular."
        )


    # ============================================================
    # 6. OUTLIERS
    # ============================================================

    st.subheader(
        "🚨 6. Outliers — IQR + límites físicos"
    )

    resultado_outliers = detectar_outliers(
        df
    )

    (
        df_outliers,
        q1,
        q3,
        limite_inferior,
        limite_superior,
        cantidad_outliers
    ) = resultado_outliers


    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Q1",
        f"{q1:.4f}"
    )

    col2.metric(
        "Q3",
        f"{q3:.4f}"
    )

    col3.metric(
        "IQR",
        f"{q3 - q1:.4f}"
    )

    col4.metric(
        "Outliers",
        cantidad_outliers
    )


    st.write(
        f"**Límite inferior IQR:** "
        f"{limite_inferior:.4f}"
    )

    st.write(
        f"**Límite superior IQR:** "
        f"{limite_superior:.4f}"
    )

    st.write(
        "**Límite físico inferior:** 0"
    )


    if cantidad_outliers > 0:

        st.warning(
            f"⚠️ Se detectaron "
            f"{cantidad_outliers} outliers."
        )

        st.dataframe(
            df_outliers[
                df_outliers["outlier"]
            ],
            use_container_width=True
        )

    else:

        st.success(
            "✅ No se detectaron outliers."
        )


    # ============================================================
    # GRÁFICO DE OUTLIERS
    # ============================================================

    fig, ax = plt.subplots(
        figsize=(12, 5)
    )

    ax.plot(
        df_outliers["fecha"],
        df_outliers["nivel"],
        label="Nivel"
    )

    outlier_data = df_outliers[
        df_outliers["outlier"]
    ]

    if not outlier_data.empty:

        ax.scatter(
            outlier_data["fecha"],
            outlier_data["nivel"],
            label="Outliers"
        )

    ax.axhline(
        limite_superior,
        linestyle="--",
        label="Límite superior IQR"
    )

    ax.axhline(
        limite_inferior,
        linestyle="--",
        label="Límite inferior IQR"
    )

    ax.set_title(
        "Detección de outliers mediante IQR"
    )

    ax.set_xlabel(
        "Fecha"
    )

    ax.set_ylabel(
        "Nivel"
    )

    ax.legend()

    ax.grid(True)

    st.pyplot(
        fig,
        clear_figure=True
    )


    # ============================================================
    # 7. NORMALIZACIÓN Y ESTANDARIZACIÓN
    # ============================================================

    st.subheader(
        "📐 7. Normalización y estandarización"
    )

    # Eliminamos outliers antes de preparar
    # los conjuntos para el modelo.
    datos_modelo = df_outliers[
        [
            "fecha",
            "nivel"
        ]
    ].copy()

    datos_modelo = datos_modelo[
        ~df_outliers["outlier"]
    ]

    datos_modelo = (
        datos_modelo
        .dropna()
        .sort_values("fecha")
        .reset_index(drop=True)
    )


    if len(datos_modelo) >= 3:

        # ========================================================
        # 8. TRAIN / VALIDATION / TEST
        # ========================================================

        (
            train,
            validation,
            test
        ) = dividir_datos_cronologicamente(
            datos_modelo
        )


        (
            train,
            validation,
            test,
            parametros
        ) = aplicar_transformaciones(
            train,
            validation,
            test
        )


        if parametros is not None:

            col1, col2 = st.columns(2)

            with col1:

                st.write(
                    "**Parámetros Min-Max "
                    "calculados con TRAIN:**"
                )

                st.write(
                    f"Mínimo: "
                    f"**{parametros['minimo']:.4f}**"
                )

                st.write(
                    f"Máximo: "
                    f"**{parametros['maximo']:.4f}**"
                )

            with col2:

                st.write(
                    "**Parámetros Z-Score "
                    "calculados con TRAIN:**"
                )

                st.write(
                    f"Media: "
                    f"**{parametros['media']:.4f}**"
                )

                st.write(
                    f"Desviación estándar: "
                    f"**{parametros['desviacion']:.4f}**"
                )


            st.write(
                "**Ejemplo de datos transformados:**"
            )

            st.dataframe(
                train.head(10),
                use_container_width=True
            )


            # ====================================================
            # 8. DIVISIÓN CRONOLÓGICA
            # ====================================================

            st.subheader(
                "📅 8. Train / Validation / Test"
            )

            total_datos = len(
                datos_modelo
            )

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "TRAIN",
                f"{len(train)} "
                f"({len(train) / total_datos * 100:.1f}%)"
            )

            col2.metric(
                "VALIDATION",
                f"{len(validation)} "
                f"({len(validation) / total_datos * 100:.1f}%)"
            )

            col3.metric(
                "TEST",
                f"{len(test)} "
                f"({len(test) / total_datos * 100:.1f}%)"
            )


            st.write(
                "### Rangos temporales"
            )

            if not train.empty:

                st.write(
                    f"**TRAIN:** "
                    f"{train['fecha'].min()} "
                    f"→ "
                    f"{train['fecha'].max()}"
                )

            if not validation.empty:

                st.write(
                    f"**VALIDATION:** "
                    f"{validation['fecha'].min()} "
                    f"→ "
                    f"{validation['fecha'].max()}"
                )

            if not test.empty:

                st.write(
                    f"**TEST:** "
                    f"{test['fecha'].min()} "
                    f"→ "
                    f"{test['fecha'].max()}"
                )


            # ====================================================
            # GRÁFICO TRAIN VALIDATION TEST
            # ====================================================

            fig2, ax2 = plt.subplots(
                figsize=(12, 5)
            )

            if not train.empty:

                ax2.plot(
                    train["fecha"],
                    train["nivel"],
                    label="Train"
                )

            if not validation.empty:

                ax2.plot(
                    validation["fecha"],
                    validation["nivel"],
                    label="Validation"
                )

            if not test.empty:

                ax2.plot(
                    test["fecha"],
                    test["nivel"],
                    label="Test"
                )

            ax2.set_title(
                "División cronológica "
                "Train / Validation / Test"
            )

            ax2.set_xlabel(
                "Fecha"
            )

            ax2.set_ylabel(
                "Nivel"
            )

            ax2.legend()

            ax2.grid(True)

            st.pyplot(
                fig2,
                clear_figure=True
            )

        else:

            st.warning(
                "No fue posible calcular "
                "las transformaciones."
            )

    else:

        st.warning(
            "⚠️ No hay suficientes datos válidos "
            "para realizar Train / Validation / Test."
        )


    # ============================================================
    # 9. ESTADÍSTICA DESCRIPTIVA
    # ============================================================

    st.subheader(
        "📊 9. Estadística descriptiva"
    )

    estadistica = (
        df["nivel"]
        .describe()
        .to_frame("Valor")
    )

    st.dataframe(
        estadistica,
        use_container_width=True
    )


    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Media",
        f"{df['nivel'].mean():.4f}"
    )

    col2.metric(
        "Mediana",
        f"{df['nivel'].median():.4f}"
    )

    col3.metric(
        "Mínimo",
        f"{df['nivel'].min():.4f}"
    )

    col4.metric(
        "Máximo",
        f"{df['nivel'].max():.4f}"
    )


    st.write(
        f"**Desviación estándar:** "
        f"{df['nivel'].std():.4f}"
    )

    st.write(
        f"**Rango:** "
        f"{df['nivel'].max() - df['nivel'].min():.4f}"
    )


    # ============================================================
    # SERIE COMPLETA
    # ============================================================

    st.subheader(
        "📈 Serie temporal del nivel"
    )

    st.line_chart(
        df.set_index("fecha")["nivel"]
    )


    # ============================================================
    # UBICACIÓN DE LA ESTACIÓN
    # ============================================================

    st.subheader(
        "📍 Ubicación de la estación"
    )

    lat, lon, coords_reales = (
        detectar_coordenadas(
            datos_crudos
        )
    )

    if not coords_reales:

        st.caption(
            "La API no proporcionó "
            "latitud/longitud. "
            "Se muestran las coordenadas "
            "por defecto de Pascual Bravo."
        )

    mapa = pd.DataFrame(
        {
            "lat": [lat],
            "lon": [lon]
        }
    )

    st.map(
        mapa,
        zoom=10
    )


    # ============================================================
    # TABLA DE DATOS
    # ============================================================

    with st.expander(
        "📋 Ver todos los datos"
    ):

        st.dataframe(
            df_outliers,
            use_container_width=True
        )


    # ============================================================
    # DESCARGA CSV
    # ============================================================

    csv = df_outliers.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        "⬇️ Descargar CSV",
        csv,
        file_name=(
            f"nivel_estacion_"
            f"{codigo_estacion}.csv"
        ),
        mime="text/csv"
    )


    # ============================================================
    # RESUMEN FINAL
    # ============================================================

    st.subheader(
        "✅ Resumen del análisis"
    )

    st.write(
        f"**Estudiante:** "
        f"{nombre_estudiante}"
    )

    st.write(
        f"**Estación:** "
        f"{codigo_estacion}"
    )

    st.write(
        f"**Periodo:** "
        f"{fecha_desde} → {fecha_hasta}"
    )

    st.write(
        f"**Lecturas válidas:** "
        f"{len(df)}"
    )

    st.write(
        f"**Missing values:** "
        f"{cantidad_missing}"
    )

    st.write(
        f"**Outliers:** "
        f"{cantidad_outliers}"
    )

    st.write(
        f"**Nivel promedio:** "
        f"{df['nivel'].mean():.4f}"
    )

    st.write(
        f"**Desviación estándar:** "
        f"{df['nivel'].std():.4f}"
    )

else:

    st.info(
        "👈 Ajusta los parámetros en el panel "
        "lateral y presiona **🔍 Consultar**."
    )
