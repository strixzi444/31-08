# ================================================================
# ACTIVIDAD INDIVIDUAL
# Análisis de nivel de ríos y quebradas - CORNARE / MARCO
# ================================================================

import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
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



# ================================================================
# INTERFAZ STREAMLIT - DISEÑO PROFESIONAL
# La lógica de análisis original se conserva.
# ================================================================

st.set_page_config(
    page_title="CORNARE | Monitor de Niveles",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #06191d 0%, #08272c 48%, #06191d 100%);
        color: #eaf8f5;
    }

    [data-testid="stHeader"] {
        background: rgba(0,0,0,0);
    }

    [data-testid="stSidebar"] {
        background: #071f24;
        border-right: 1px solid #17464b;
    }

    .hero {
        padding: 28px 32px;
        border-radius: 22px;
        background: linear-gradient(135deg, #0b3439, #0a2429);
        border: 1px solid #1c5559;
        box-shadow: 0 12px 35px rgba(0,0,0,.24);
        margin-bottom: 22px;
    }

    .hero-small {
        color: #6ee3d1;
        font-size: 14px;
        font-weight: 800;
        letter-spacing: 2px;
        margin-bottom: 4px;
    }

    .hero-title {
        color: #f0fffc;
        font-size: 34px;
        font-weight: 800;
        margin: 0;
    }

    .hero-sub {
        color: #9dc9c3;
        font-size: 14px;
        margin-top: 7px;
    }

    .section-title {
        color: #eaf8f5;
        font-size: 18px;
        font-weight: 800;
        margin: 8px 0 14px;
    }

    .metric-card {
        background: linear-gradient(145deg, #0d3439, #0a292e);
        border: 1px solid #1a4d51;
        border-radius: 17px;
        padding: 18px 18px 16px;
        min-height: 116px;
        box-shadow: 0 8px 24px rgba(0,0,0,.16);
    }

    .metric-label {
        color: #8fbab5;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 1px;
    }

    .metric-value {
        color: #69e2d0;
        font-size: 27px;
        font-weight: 800;
        margin-top: 5px;
    }

    .metric-desc {
        color: #6f9995;
        font-size: 11px;
        margin-top: 3px;
    }

    .info-box {
        background: #0b2c31;
        border: 1px solid #1b5054;
        border-radius: 17px;
        padding: 20px 22px;
        color: #b5d7d2;
        line-height: 1.65;
        margin-top: 10px;
    }

    .status {
        display: inline-block;
        padding: 7px 12px;
        border-radius: 20px;
        background: #103d3e;
        color: #6ee3d1;
        font-weight: 800;
        font-size: 12px;
        border: 1px solid #23665f;
    }

    div.stButton > button {
        width: 100%;
        border-radius: 12px;
        border: 1px solid #2bc2af;
        background: linear-gradient(135deg, #27b6a5, #1c968b);
        color: #052126;
        font-weight: 800;
        padding: 11px 15px;
        transition: .2s;
    }

    div.stButton > button:hover {
        border-color: #73ead9;
        background: #43ccb9;
        color: #04181c;
    }

    .footer {
        text-align: center;
        color: #648e8a;
        font-size: 11px;
        padding: 18px 0 4px;
    }
</style>
""", unsafe_allow_html=True)

# Estado
if "resultado" not in st.session_state:
    st.session_state.resultado = None
if "error" not in st.session_state:
    st.session_state.error = None

# ------------------------------------------------
# ENCABEZADO
# ------------------------------------------------
st.markdown("""
<div class="hero">
    <div class="hero-small">💧 CORNARE / MARCO</div>
    <div class="hero-title">Monitor de Niveles Hídricos</div>
    <div class="hero-sub">
        Análisis de niveles de ríos y quebradas · Control de calidad ·
        Estadística y preparación de series temporales
    </div>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------
# CONFIGURACIÓN EN SIDEBAR
# ------------------------------------------------
with st.sidebar:
    st.markdown("## ⚙️ Parámetros")
    st.caption("Configura la consulta antes de ejecutar el análisis.")

    nombre = st.text_input("Estudiante", value=NOMBRE_ESTUDIANTE)
    estacion = st.text_input("Código de estación", value=CODIGO_ESTACION)
    desde = st.date_input("Fecha desde", value=pd.to_datetime(FECHA_DESDE).date())
    hasta = st.date_input("Fecha hasta", value=pd.to_datetime(FECHA_HASTA).date())
    calidad = st.selectbox(
        "Calidad de datos",
        options=[1, 0],
        index=0 if CALIDAD == 1 else 1,
        format_func=lambda x: "Datos validados" if x == 1 else "Todos los disponibles"
    )

    st.markdown("---")
    st.markdown("### 🔬 Procesamiento")
    st.caption(
        "La aplicación conserva el análisis original: "
        "missing values, outliers IQR, normalización, "
        "estandarización y división temporal."
    )

    ejecutar = st.button("💧 EJECUTAR ANÁLISIS", use_container_width=True)

# ------------------------------------------------
# EJECUCIÓN
# ------------------------------------------------
if ejecutar:
    if desde > hasta:
        st.error("La fecha inicial no puede ser posterior a la fecha final.")
    elif not estacion.strip():
        st.error("Ingresa un código de estación.")
    else:
        with st.spinner("Consultando MARCO y procesando la serie temporal..."):
            try:
                datos_crudos, error = obtener_serie_nivel(
                    estacion.strip(),
                    str(desde),
                    str(hasta),
                    calidad
                )

                if error:
                    raise RuntimeError(error)

                registros = obtener_todas_las_paginas(datos_crudos)

                if not registros:
                    raise RuntimeError(
                        "La API no devolvió registros para el periodo seleccionado."
                    )

                df = pd.DataFrame(registros)
                df = df.rename(
                    columns={
                        LLAVE_FECHA: "fecha",
                        LLAVE_VALOR: "nivel"
                    }
                )

                df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
                df["nivel"] = pd.to_numeric(df["nivel"], errors="coerce")
                df = df.dropna(subset=["fecha", "nivel"])
                df = df.sort_values("fecha").reset_index(drop=True)

                if df.empty:
                    raise RuntimeError(
                        "No quedaron datos válidos después de limpiar la consulta."
                    )

                # --------------------------------------------
                # MISSING VALUES — MISMA LÓGICA ORIGINAL
                # --------------------------------------------
                cantidad_missing = 0

                if len(df) > 1:
                    diferencias = (
                        df["fecha"].sort_values().diff().dropna()
                    )
                    frecuencia_tipica = diferencias.mode()

                    if len(frecuencia_tipica) > 0:
                        frecuencia = frecuencia_tipica.iloc[0]

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
                        cantidad_missing = int(
                            df_missing["nivel"].isna().sum()
                        )
                    else:
                        df_missing = df.set_index("fecha").copy()
                else:
                    df_missing = df.set_index("fecha").copy()

                # --------------------------------------------
                # OUTLIERS — MISMA LÓGICA ORIGINAL
                # --------------------------------------------
                serie_nivel = df["nivel"].dropna()

                Q1 = serie_nivel.quantile(0.25)
                Q3 = serie_nivel.quantile(0.75)
                IQR = Q3 - Q1

                limite_inferior_iqr = Q1 - 1.5 * IQR
                limite_superior_iqr = Q3 + 1.5 * IQR

                limite_fisico_inferior = 0
                limite_fisico_superior = np.inf

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

                cantidad_outliers = int(df["outlier"].sum())

                # --------------------------------------------
                # NORMALIZACIÓN / ESTANDARIZACIÓN
                # --------------------------------------------
                datos_modelo = df[
                    ["fecha", "nivel"]
                ].copy()

                datos_modelo = datos_modelo[
                    ~df["outlier"]
                ]

                datos_modelo = datos_modelo.dropna()

                datos_modelo = datos_modelo.sort_values(
                    "fecha"
                ).reset_index(drop=True)

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

                if not train.empty:

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

                else:
                    minimo = maximo = media_train = desviacion_train = np.nan

                st.session_state.resultado = {
                    "df": df,
                    "df_missing": df_missing,
                    "train": train,
                    "validation": validation,
                    "test": test,
                    "cantidad_missing": cantidad_missing,
                    "cantidad_outliers": cantidad_outliers,
                    "Q1": Q1,
                    "Q3": Q3,
                    "IQR": IQR,
                    "limite_inferior_iqr": limite_inferior_iqr,
                    "limite_superior_iqr": limite_superior_iqr,
                    "minimo": minimo,
                    "maximo": maximo,
                    "media_train": media_train,
                    "desviacion_train": desviacion_train,
                    "nombre": nombre,
                    "estacion": estacion,
                    "desde": str(desde),
                    "hasta": str(hasta),
                    "calidad": calidad
                }

                st.session_state.error = None
                st.success("✅ Análisis realizado correctamente.")

            except Exception as e:
                st.session_state.resultado = None
                st.session_state.error = str(e)

# ------------------------------------------------
# MOSTRAR ERROR
# ------------------------------------------------
if st.session_state.error:
    st.error(f"❌ Error al consultar o procesar los datos: {st.session_state.error}")

# ------------------------------------------------
# DASHBOARD
# ------------------------------------------------
r = st.session_state.resultado

if r is not None:

    df = r["df"]

    st.markdown('<div class="section-title">📊 Indicadores principales</div>',
                unsafe_allow_html=True)

    c1, c2, c3, c4, c5, c6 = st.columns(6)

    metrics = [
        (c1, "LECTURAS", f"{len(df):,}", "Registros válidos"),
        (c2, "PROMEDIO", f"{df['nivel'].mean():.3f}", "Nivel medio"),
        (c3, "MÍNIMO", f"{df['nivel'].min():.3f}", "Nivel registrado"),
        (c4, "MÁXIMO", f"{df['nivel'].max():.3f}", "Nivel registrado"),
        (c5, "MISSING", str(r["cantidad_missing"]), "Valores faltantes"),
        (c6, "OUTLIERS", str(r["cantidad_outliers"]), "Valores atípicos")
    ]

    for col, label, value, desc in metrics:
        with col:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value">{value}</div>
                    <div class="metric-desc">{desc}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown("")
    st.markdown(
        f"""
        <div class="info-box">
            <b>📍 Estación:</b> {r["estacion"]}
            &nbsp;&nbsp;•&nbsp;&nbsp;
            <b>📅 Periodo:</b> {r["desde"]} → {r["hasta"]}
            <br>
            <b>👤 Estudiante:</b> {r["nombre"]}
            <br><br>
            El análisis obtuvo <b>{len(df)}</b> lecturas válidas.
            El nivel promedio fue <b>{df["nivel"].mean():.3f}</b>,
            con un mínimo de <b>{df["nivel"].min():.3f}</b> y un máximo de
            <b>{df["nivel"].max():.3f}</b>.
            Se detectaron <b>{r["cantidad_missing"]}</b> valores faltantes
            reales y <b>{r["cantidad_outliers"]}</b> valores atípicos.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("### 📈 Comportamiento del nivel")

    fig1, ax1 = plt.subplots(figsize=(12, 4.5))
    fig1.patch.set_facecolor("#0b2c31")
    ax1.set_facecolor("#0b2c31")

    ax1.plot(
        df["fecha"],
        df["nivel"],
        linewidth=1.7,
        label="Nivel"
    )

    outliers_df = df[df["outlier"]]

    if not outliers_df.empty:
        ax1.scatter(
            outliers_df["fecha"],
            outliers_df["nivel"],
            s=35,
            label="Outliers",
            zorder=3
        )

    ax1.axhline(
        r["limite_superior_iqr"],
        linestyle="--",
        linewidth=1,
        label="Límite superior IQR"
    )

    ax1.axhline(
        r["limite_inferior_iqr"],
        linestyle="--",
        linewidth=1,
        label="Límite inferior IQR"
    )

    ax1.set_xlabel("Fecha", color="#9dc9c3")
    ax1.set_ylabel("Nivel", color="#9dc9c3")
    ax1.tick_params(colors="#9dc9c3")
    ax1.grid(True, alpha=0.15)
    ax1.legend()
    fig1.tight_layout()

    st.pyplot(fig1, use_container_width=True)
    plt.close(fig1)

    st.markdown("### 🧪 División cronológica")

    fig2, ax2 = plt.subplots(figsize=(12, 4.2))
    fig2.patch.set_facecolor("#0b2c31")
    ax2.set_facecolor("#0b2c31")

    if not r["train"].empty:
        ax2.plot(
            r["train"]["fecha"],
            r["train"]["nivel"],
            label="Train"
        )

    if not r["validation"].empty:
        ax2.plot(
            r["validation"]["fecha"],
            r["validation"]["nivel"],
            label="Validation"
        )

    if not r["test"].empty:
        ax2.plot(
            r["test"]["fecha"],
            r["test"]["nivel"],
            label="Test"
        )

    ax2.set_xlabel("Fecha", color="#9dc9c3")
    ax2.set_ylabel("Nivel", color="#9dc9c3")
    ax2.tick_params(colors="#9dc9c3")
    ax2.grid(True, alpha=0.15)
    ax2.legend()
    fig2.tight_layout()

    st.pyplot(fig2, use_container_width=True)
    plt.close(fig2)

    # ------------------------------------------------
    # TABS DE INFORMACIÓN
    # ------------------------------------------------
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Datos",
        "🔎 Outliers",
        "📐 Normalización",
        "📊 Estadística"
    ])

    with tab1:
        st.subheader("Serie temporal")
        st.dataframe(
            df,
            use_container_width=True,
            height=430
        )

    with tab2:
        st.subheader("Detección de valores atípicos")
        a, b, c, d = st.columns(4)

        a.metric("Q1", f"{r['Q1']:.4f}")
        b.metric("Q3", f"{r['Q3']:.4f}")
        c.metric("IQR", f"{r['IQR']:.4f}")
        d.metric("Outliers", r["cantidad_outliers"])

        st.write(
            f"**Límite inferior IQR:** {r['limite_inferior_iqr']:.4f}"
        )
        st.write(
            f"**Límite superior IQR:** {r['limite_superior_iqr']:.4f}"
        )
        st.write("**Límite físico inferior:** 0")

        st.dataframe(
            df[df["outlier"]],
            use_container_width=True
        )

    with tab3:
        st.subheader("Preparación para modelado")

        a, b, c = st.columns(3)
        a.metric("Train", len(r["train"]))
        b.metric("Validation", len(r["validation"]))
        c.metric("Test", len(r["test"]))

        st.write(
            f"**Mínimo usado en TRAIN:** "
            f"{r['minimo']:.4f}"
            if not pd.isna(r["minimo"])
            else "**Mínimo usado en TRAIN:** —"
        )

        st.write(
            f"**Máximo usado en TRAIN:** "
            f"{r['maximo']:.4f}"
            if not pd.isna(r["maximo"])
            else "**Máximo usado en TRAIN:** —"
        )

        st.write(
            f"**Media usada en TRAIN:** "
            f"{r['media_train']:.4f}"
            if not pd.isna(r["media_train"])
            else "**Media usada en TRAIN:** —"
        )

        st.write(
            f"**Desviación estándar usada en TRAIN:** "
            f"{r['desviacion_train']:.4f}"
            if not pd.isna(r["desviacion_train"])
            else "**Desviación estándar usada en TRAIN:** —"
        )

        if not r["train"].empty:
            st.write("### Primeros datos de TRAIN")
            st.dataframe(
                r["train"].head(10),
                use_container_width=True
            )

    with tab4:
        st.subheader("Estadística descriptiva")

        estadistica = df["nivel"].describe()

        st.dataframe(
            estadistica.to_frame(name="valor"),
            use_container_width=True
        )

        a, b, c = st.columns(3)

        a.metric("Media", f"{df['nivel'].mean():.4f}")
        b.metric("Mediana", f"{df['nivel'].median():.4f}")
        c.metric("Desv. estándar", f"{df['nivel'].std():.4f}")

        a, b, c = st.columns(3)

        a.metric("Mínimo", f"{df['nivel'].min():.4f}")
        b.metric("Máximo", f"{df['nivel'].max():.4f}")
        c.metric("Rango", f"{df['nivel'].max()-df['nivel'].min():.4f}")

else:
    st.markdown(
        """
        <div class="info-box">
            <b>🌿 Monitor ambiental listo.</b><br><br>
            Configura la estación y el periodo en el panel lateral y
            ejecuta el análisis para consultar los datos de nivel.
            <br><br>
            <span class="status">● SISTEMA LISTO</span>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown(
    '<div class="footer">CORNARE / MARCO · Monitor de Niveles Hídricos · Análisis ambiental</div>',
    unsafe_allow_html=True
)
