# ================================================================
# ACTIVIDAD INDIVIDUAL
# Análisis de nivel de ríos y quebradas - CORNARE / MARCO
# ================================================================

import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import urllib3
import streamlit as st

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ================================================================
# CONFIGURACIÓN VISUAL DE STREAMLIT
# ================================================================

st.set_page_config(
    page_title="CORNARE | Análisis de niveles",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap');

    :root {
        --water: #0b7285;
        --water-dark: #075985;
        --water-deep: #083344;
        --river: #14b8a6;
        --leaf: #2f855a;
        --mist: #eff8fb;
        --card: #ffffff;
        --ink: #16323a;
        --muted: #61757d;
        --line: #dcebef;
        --soft-blue: #e5f6fa;
        --soft-green: #eaf7f0;
        --soft-yellow: #fff8e6;
        --soft-red: #fff0ef;
        --shadow: 0 12px 30px rgba(7, 89, 133, 0.08);
    }

    .stApp {
        background:
            radial-gradient(circle at 0% 0%, rgba(20,184,166,0.10), transparent 23rem),
            radial-gradient(circle at 100% 5%, rgba(11,114,133,0.10), transparent 24rem),
            linear-gradient(180deg, #f5fbfc 0%, #f8fbfc 52%, #eef8f7 100%);
        color: var(--ink);
        font-family: 'Inter', sans-serif;
    }

    .main .block-container {
        max-width: 1400px;
        padding: 2rem 2.2rem 3.5rem;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #062f3b 0%, #08485a 54%, #0b6572 100%);
        border-right: 1px solid rgba(255,255,255,0.08);
    }

    [data-testid="stSidebar"] * {
        color: #eefcff;
    }

    [data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.15);
    }

    .hero {
        position: relative;
        overflow: hidden;
        padding: 2rem 2.1rem;
        border-radius: 28px;
        background:
            linear-gradient(135deg, rgba(5,59,72,0.98) 0%, rgba(8,98,113,0.97) 58%, rgba(20,184,166,0.96) 100%);
        box-shadow: 0 20px 45px rgba(8, 67, 82, 0.20);
        margin-bottom: 1.4rem;
        border: 1px solid rgba(255,255,255,0.08);
    }

    .hero::after {
        content: "";
        position: absolute;
        width: 270px;
        height: 270px;
        border-radius: 50%;
        right: -90px;
        top: -130px;
        background: rgba(255,255,255,0.08);
        box-shadow:
            -85px 155px 0 20px rgba(255,255,255,0.035),
            -170px 65px 0 48px rgba(255,255,255,0.025);
    }

    .hero-kicker {
        display: inline-flex;
        padding: 0.35rem 0.7rem;
        border-radius: 999px;
        background: rgba(255,255,255,0.13);
        border: 1px solid rgba(255,255,255,0.14);
        font-size: 0.77rem;
        font-weight: 700;
        letter-spacing: .08em;
        text-transform: uppercase;
        color: #d7fbff;
        margin-bottom: 0.8rem;
    }

    .hero-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: clamp(2rem, 4vw, 3.3rem);
        line-height: 1.02;
        font-weight: 700;
        letter-spacing: -0.04em;
        margin: 0;
        color: #ffffff;
    }

    .hero-subtitle {
        margin: 0.85rem 0 0;
        max-width: 780px;
        color: #d9f8fb;
        font-size: 1rem;
        line-height: 1.65;
    }

    .hero-stats {
        position: relative;
        z-index: 2;
        display: flex;
        flex-wrap: wrap;
        gap: 0.65rem;
        margin-top: 1.3rem;
    }

    .hero-chip {
        padding: .48rem .72rem;
        border-radius: 11px;
        background: rgba(255,255,255,0.10);
        border: 1px solid rgba(255,255,255,0.12);
        color: #eefcff;
        font-size: .82rem;
        font-weight: 600;
    }

    .section-title {
        font-family: 'Space Grotesk', sans-serif;
        color: var(--water-deep);
        font-size: 1.35rem;
        font-weight: 700;
        margin: .5rem 0 .8rem;
        letter-spacing: -.02em;
    }

    .section-caption {
        color: var(--muted);
        margin: -0.45rem 0 1rem;
        font-size: .92rem;
    }

    .card {
        background: rgba(255,255,255,0.95);
        border: 1px solid var(--line);
        border-radius: 19px;
        padding: 1rem 1.05rem;
        box-shadow: var(--shadow);
    }

    .info-card {
        min-height: 115px;
    }

    .card-label {
        font-size: .74rem;
        letter-spacing: .08em;
        text-transform: uppercase;
        color: #6e858d;
        font-weight: 800;
        margin-bottom: .45rem;
    }

    .card-value {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.26rem;
        font-weight: 700;
        color: var(--water-deep);
        word-break: break-word;
    }

    .card-note {
        margin-top: .3rem;
        color: var(--muted);
        font-size: .82rem;
    }

    .status {
        display: flex;
        gap: .55rem;
        align-items: center;
        padding: .8rem 1rem;
        border-radius: 14px;
        border: 1px solid;
        font-weight: 600;
        font-size: .9rem;
    }

    .status-ok {
        color: #166534;
        background: var(--soft-green);
        border-color: #ccebdd;
    }

    .status-info {
        color: #0c4a6e;
        background: var(--soft-blue);
        border-color: #ccecf3;
    }

    .status-warn {
        color: #854d0e;
        background: var(--soft-yellow);
        border-color: #f5dfaa;
    }

    .status-danger {
        color: #991b1b;
        background: var(--soft-red);
        border-color: #f2c9c6;
    }

    .metric-card {
        background: rgba(255,255,255,0.96);
        border-radius: 18px;
        border: 1px solid var(--line);
        padding: .95rem 1rem;
        box-shadow: var(--shadow);
        min-height: 110px;
    }

    .metric-icon {
        font-size: 1.1rem;
        margin-bottom: .4rem;
    }

    .metric-name {
        color: #71858c;
        font-size: .76rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: .06em;
    }

    .metric-number {
        font-family: 'Space Grotesk', sans-serif;
        color: var(--water-deep);
        font-size: 1.65rem;
        line-height: 1.15;
        font-weight: 700;
        margin-top: .3rem;
    }

    .table-wrap {
        border-radius: 18px;
        border: 1px solid var(--line);
        overflow: hidden;
        box-shadow: var(--shadow);
        background: white;
    }

    .mini-title {
        font-family: 'Space Grotesk', sans-serif;
        color: var(--water-dark);
        font-size: 1rem;
        font-weight: 700;
        margin-bottom: .55rem;
    }

    .sidebar-brand {
        padding: .25rem 0 .9rem;
    }

    .sidebar-brand .big {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.35rem;
        font-weight: 700;
        color: #ffffff;
    }

    .sidebar-brand .small {
        color: #bfeef2;
        font-size: .82rem;
        line-height: 1.55;
        margin-top: .3rem;
    }

    .sidebar-pill {
        display: inline-block;
        padding: .35rem .62rem;
        border-radius: 999px;
        background: rgba(255,255,255,0.10);
        border: 1px solid rgba(255,255,255,0.10);
        color: #e6fbfd;
        font-size: .73rem;
        font-weight: 700;
        margin: .22rem .18rem .05rem 0;
    }

    div[data-testid="stExpander"] {
        border: 1px solid var(--line);
        border-radius: 16px;
        background: rgba(255,255,255,0.72);
        overflow: hidden;
    }

    .footer {
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid var(--line);
        color: #789098;
        font-size: .78rem;
        text-align: center;
    }

    /* Ajustes generales de widgets para integrarlos al diseño */
    .stButton > button, .stDownloadButton > button {
        border-radius: 12px;
    }

    [data-testid="stMetric"] {
        background: white;
        border: 1px solid var(--line);
        padding: .85rem 1rem;
        border-radius: 16px;
        box-shadow: var(--shadow);
    }

    </style>
    """,
    unsafe_allow_html=True
)

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
# COMPONENTES VISUALES (SOLO PRESENTACIÓN)
# ================================================================

def tarjeta_info(label, value, note=""):
    nota_html = f'<div class="card-note">{note}</div>' if note else ""
    st.markdown(
        f"""
        <div class="card info-card">
            <div class="card-label">{label}</div>
            <div class="card-value">{value}</div>
            {nota_html}
        </div>
        """,
        unsafe_allow_html=True
    )


def tarjeta_metrica(icono, nombre, valor):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-icon">{icono}</div>
            <div class="metric-name">{nombre}</div>
            <div class="metric-number">{valor}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def estado(mensaje, tipo="info"):
    st.markdown(
        f'<div class="status status-{tipo}">{mensaje}</div>',
        unsafe_allow_html=True
    )


# ================================================================
# CABECERA VISUAL
# ================================================================

st.markdown(
    f"""
    <div class="hero">
        <div class="hero-kicker">🌊 CORNARE / MARCO · MONITOREO HIDROLÓGICO</div>
        <div class="hero-title">Análisis de nivel de ríos y quebradas</div>
        <div class="hero-subtitle">
            Visualización y análisis de la serie de nivel de la estación
            <strong>{CODIGO_ESTACION}</strong>, conservando el proceso original de
            consulta, limpieza, calidad de datos y análisis estadístico.
        </div>
        <div class="hero-stats">
            <div class="hero-chip">Estación {CODIGO_ESTACION}</div>
            <div class="hero-chip">Periodo {FECHA_DESDE} → {FECHA_HASTA}</div>
            <div class="hero-chip">Datos validados</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ================================================================
# BARRA LATERAL INFORMATIVA
# ================================================================

with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="big">🌊 CORNARE</div>
            <div class="small">
                Panel de análisis hidrológico basado en la consulta
                de datos de MARCO.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")
    st.markdown("### Configuración actual")

    st.markdown(
        f"""
        <span class="sidebar-pill">Estación {CODIGO_ESTACION}</span>
        <span class="sidebar-pill">Calidad {CALIDAD}</span>
        <span class="sidebar-pill">2026</span>
        """,
        unsafe_allow_html=True
    )

    st.markdown("**Estudiante**")
    st.caption(NOMBRE_ESTUDIANTE)

    st.markdown("**Periodo consultado**")
    st.caption(f"{FECHA_DESDE} → {FECHA_HASTA}")

    st.markdown("---")
    st.markdown("### Proceso del análisis")
    st.caption("01 · Consulta de API")
    st.caption("02 · Serie temporal")
    st.caption("03 · Missing values")
    st.caption("04 · Outliers con IQR")
    st.caption("05 · Normalización / Z-Score")
    st.caption("06 · Train / Validation / Test")
    st.caption("07 · Estadística descriptiva")

    st.markdown("---")
    st.caption("Los parámetros y operaciones del análisis original se mantienen sin cambios.")


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


# ================================================================
# 3. CONSTRUIR EL DATAFRAME DE SERIE DE TIEMPO
# ================================================================

if error:
    estado(f"⚠️ <strong>Error al consultar la API:</strong> {error}", "danger")

else:

    registros = obtener_todas_las_paginas(datos_crudos)

    estado(
        f"✅ <strong>Consulta realizada correctamente.</strong> "
        f"Se obtuvieron {len(registros):,} registros.",
        "ok"
    )


# ================================================================
# 3.1 RESUMEN DE CONSULTA
# ================================================================

if not error and registros:
    st.markdown('<div class="section-title">Resumen de la consulta</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-caption">Información principal de la fuente y del periodo analizado.</div>',
        unsafe_allow_html=True
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        tarjeta_info("Estación", CODIGO_ESTACION, "Código consultado en MARCO")
    with c2:
        tarjeta_info("Lecturas", f"{len(registros):,}", "Registros recibidos desde la API")
    with c3:
        tarjeta_info("Periodo", f"{FECHA_DESDE} → {FECHA_HASTA}", "Rango configurado")
    with c4:
        tarjeta_info("Calidad", str(CALIDAD), "1 = datos validados")

    st.markdown("")

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

    st.markdown('<div class="section-title">Serie de datos recibida</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-caption">Primeras observaciones obtenidas directamente de la consulta.</div>',
        unsafe_allow_html=True
    )

    with st.expander("Ver columnas y primeros registros", expanded=False):
        st.write("**Columnas disponibles:**")
        st.code(", ".join(df.columns.tolist()), language="text")
        st.dataframe(df.head(), use_container_width=True, hide_index=True)


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

    st.markdown('<div class="section-title">Preparación de la serie temporal</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-caption">Conversión de tipos, limpieza básica y orden cronológico.</div>',
        unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        tarjeta_info("Desde", str(df["fecha"].min()), "Fecha mínima después de limpiar")
    with c2:
        tarjeta_info("Hasta", str(df["fecha"].max()), "Fecha máxima después de limpiar")
    with c3:
        tarjeta_info("Registros válidos", f"{len(df):,}", "Observaciones con fecha y nivel")

    with st.expander("Ver tipos y primeros 10 registros", expanded=False):
        tipos = pd.DataFrame({
            "Columna": df.dtypes.index,
            "Tipo": [str(t) for t in df.dtypes.values]
        })
        st.dataframe(tipos, use_container_width=True, hide_index=True)
        st.dataframe(df.head(10), use_container_width=True, hide_index=True)


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

        frecuencia_texto = str(frecuencia)

    else:

        frecuencia = None

        frecuencia_texto = "No determinada"

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

        porcentaje_missing = (
            cantidad_missing / total_esperado
        ) * 100

        st.markdown('<div class="section-title">Missing values reales</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-caption">Identificación mediante reindexación a la frecuencia típica de medición.</div>',
            unsafe_allow_html=True
        )

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            tarjeta_metrica("⏱️", "Frecuencia típica", frecuencia_texto)
        with m2:
            tarjeta_metrica("📅", "Registros esperados", f"{total_esperado:,}")
        with m3:
            tarjeta_metrica("📥", "Registros originales", f"{len(df):,}")
        with m4:
            tarjeta_metrica("🕳️", "Missing values", f"{cantidad_missing:,}")

        if cantidad_missing == 0:
            estado("✅ No se detectaron espacios faltantes en la estructura regular de la serie.", "ok")
        else:
            estado(
                f"⚠️ Se detectaron {cantidad_missing:,} registros faltantes "
                f"({porcentaje_missing:.2f}% del total esperado).",
                "warn"
            )

        with st.expander("Ver primeros registros con estructura regular", expanded=False):
            st.dataframe(
                df_missing.head(20),
                use_container_width=True
            )

    else:

        df_missing = df.set_index("fecha").copy()

        st.markdown('<div class="section-title">Missing values reales</div>', unsafe_allow_html=True)
        estado("ℹ️ No fue posible determinar la frecuencia típica; se conserva la estructura disponible.", "info")

else:

    if not error:
        st.markdown('<div class="section-title">Missing values reales</div>', unsafe_allow_html=True)
        estado("⚠️ No hay suficientes datos para analizar missing values.", "warn")


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

    st.markdown('<div class="section-title">Detección de outliers</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-caption">Método IQR combinado con el límite físico inferior de nivel igual a 0.</div>',
        unsafe_allow_html=True
    )

    o1, o2, o3, o4, o5 = st.columns(5)
    with o1:
        tarjeta_metrica("Q1", "Primer cuartil", f"{Q1:.4f}")
    with o2:
        tarjeta_metrica("Q3", "Tercer cuartil", f"{Q3:.4f}")
    with o3:
        tarjeta_metrica("↔", "IQR", f"{IQR:.4f}")
    with o4:
        tarjeta_metrica("↘", "Límite inferior", f"{limite_inferior_iqr:.4f}")
    with o5:
        tarjeta_metrica("↗", "Límite superior", f"{limite_superior_iqr:.4f}")

    if cantidad_outliers == 0:
        estado("✅ No se detectaron outliers con el criterio aplicado.", "ok")
    else:
        estado(
            f"⚠️ Se detectaron {cantidad_outliers:,} observaciones clasificadas como outliers.",
            "warn"
        )

    with st.expander("Ver registros considerados outliers", expanded=False):
        st.dataframe(
            df[df["outlier"]],
            use_container_width=True,
            hide_index=True
        )


# ================================================================
# GRÁFICO DE OUTLIERS
# ================================================================

if not error and registros:

    fig_outliers, ax_outliers = plt.subplots(figsize=(12, 5))

    ax_outliers.plot(
        df["fecha"],
        df["nivel"],
        label="Nivel",
        linewidth=2.1
    )

    ax_outliers.scatter(
        df.loc[df["outlier"], "fecha"],
        df.loc[df["outlier"], "nivel"],
        label="Outliers",
        s=42,
        zorder=3
    )

    ax_outliers.axhline(
        limite_superior_iqr,
        linestyle="--",
        linewidth=1.2,
        label="Límite superior IQR"
    )

    ax_outliers.axhline(
        limite_inferior_iqr,
        linestyle="--",
        linewidth=1.2,
        label="Límite inferior IQR"
    )

    ax_outliers.set_title(
        "Detección de outliers - Método IQR",
        fontweight="bold"
    )

    ax_outliers.set_xlabel("Fecha")
    ax_outliers.set_ylabel("Nivel")
    ax_outliers.legend()
    ax_outliers.grid(True, alpha=0.22)
    fig_outliers.tight_layout()

    st.pyplot(fig_outliers, use_container_width=True)
    plt.close(fig_outliers)


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


    st.markdown('<div class="section-title">Normalización y estandarización</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-caption">Los parámetros se calculan sobre TRAIN para mantener el mismo criterio del análisis original.</div>',
        unsafe_allow_html=True
    )

    n1, n2, n3, n4 = st.columns(4)
    with n1:
        tarjeta_metrica("MIN", "Mínimo TRAIN", f"{minimo:.4f}")
    with n2:
        tarjeta_metrica("MAX", "Máximo TRAIN", f"{maximo:.4f}")
    with n3:
        tarjeta_metrica("μ", "Media TRAIN", f"{media_train:.4f}")
    with n4:
        tarjeta_metrica("σ", "Desv. estándar TRAIN", f"{desviacion_train:.4f}")

    with st.expander("Ver datos normalizados y estandarizados", expanded=False):
        st.dataframe(
            train.head(10),
            use_container_width=True,
            hide_index=True
        )


# ================================================================
# 8. TRAIN / VALIDATION / TEST
#    SPLIT CRONOLÓGICO
# ================================================================

if not error and registros:

    st.markdown('<div class="section-title">División temporal</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-caption">Separación cronológica 70% / 15% / 15% del conjunto sin outliers.</div>',
        unsafe_allow_html=True
    )

    s1, s2, s3 = st.columns(3)
    with s1:
        tarjeta_metrica("01", "TRAIN", f"{len(train):,} · {len(train) / len(datos_modelo) * 100:.1f}%")
    with s2:
        tarjeta_metrica("02", "VALIDATION", f"{len(validation):,} · {len(validation) / len(datos_modelo) * 100:.1f}%")
    with s3:
        tarjeta_metrica("03", "TEST", f"{len(test):,} · {len(test) / len(datos_modelo) * 100:.1f}%")

    rangos = []
    if not train.empty:
        rangos.append({"Conjunto": "TRAIN", "Desde": train["fecha"].min(), "Hasta": train["fecha"].max(), "Registros": len(train)})
    if not validation.empty:
        rangos.append({"Conjunto": "VALIDATION", "Desde": validation["fecha"].min(), "Hasta": validation["fecha"].max(), "Registros": len(validation)})
    if not test.empty:
        rangos.append({"Conjunto": "TEST", "Desde": test["fecha"].min(), "Hasta": test["fecha"].max(), "Registros": len(test)})

    if rangos:
        with st.expander("Ver rangos de fechas de cada conjunto", expanded=False):
            st.dataframe(pd.DataFrame(rangos), use_container_width=True, hide_index=True)


# ---------------------------------------------------------------
# Gráfico del split
# ---------------------------------------------------------------

if not error and registros:

    fig_split, ax_split = plt.subplots(figsize=(12, 5))

    if not train.empty:
        ax_split.plot(
            train["fecha"],
            train["nivel"],
            label="Train",
            linewidth=2
        )

    if not validation.empty:
        ax_split.plot(
            validation["fecha"],
            validation["nivel"],
            label="Validation",
            linewidth=2
        )

    if not test.empty:
        ax_split.plot(
            test["fecha"],
            test["nivel"],
            label="Test",
            linewidth=2
        )

    ax_split.set_title(
        "División cronológica Train / Validation / Test",
        fontweight="bold"
    )

    ax_split.set_xlabel("Fecha")
    ax_split.set_ylabel("Nivel")
    ax_split.legend()
    ax_split.grid(True, alpha=0.22)
    fig_split.tight_layout()

    st.pyplot(fig_split, use_container_width=True)
    plt.close(fig_split)


# ================================================================
# 9. ESTADÍSTICA DESCRIPTIVA
# ================================================================

if not error and registros:

    st.markdown('<div class="section-title">Estadística descriptiva</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-caption">Medidas principales calculadas sobre la serie limpia.</div>',
        unsafe_allow_html=True
    )

    estadistica = df["nivel"].describe()

    e1, e2, e3 = st.columns(3)
    with e1:
        tarjeta_metrica("x̄", "Media", f"{df['nivel'].mean():.4f}")
    with e2:
        tarjeta_metrica("Md", "Mediana", f"{df['nivel'].median():.4f}")
    with e3:
        tarjeta_metrica("σ", "Desviación estándar", f"{df['nivel'].std():.4f}")

    e4, e5, e6 = st.columns(3)
    with e4:
        tarjeta_metrica("↓", "Mínimo", f"{df['nivel'].min():.4f}")
    with e5:
        tarjeta_metrica("↑", "Máximo", f"{df['nivel'].max():.4f}")
    with e6:
        tarjeta_metrica("↔", "Rango", f"{df['nivel'].max() - df['nivel'].min():.4f}")

    with st.expander("Ver estadística descriptiva completa", expanded=False):
        estadistica_df = estadistica.to_frame(name="valor")
        st.dataframe(estadistica_df, use_container_width=True)


# ================================================================
# RESUMEN FINAL
# ================================================================

if not error and registros:

    st.markdown('<div class="section-title">Resumen final del análisis</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-caption">Concentrado de los resultados principales obtenidos en todo el proceso.</div>',
        unsafe_allow_html=True
    )

    summary_cols = st.columns(2)

    resumen_izq = pd.DataFrame({
        "Indicador": [
            "Estudiante",
            "Estación",
            "Periodo",
            "Lecturas originales",
        ],
        "Resultado": [
            NOMBRE_ESTUDIANTE,
            CODIGO_ESTACION,
            f"{FECHA_DESDE} hasta {FECHA_HASTA}",
            len(df),
        ]
    })

    resumen_der = pd.DataFrame({
        "Indicador": [
            "Missing values reales",
            "Outliers detectados",
            "Promedio del nivel",
            "Desviación estándar",
        ],
        "Resultado": [
            cantidad_missing if "cantidad_missing" in locals() else "No calculado",
            cantidad_outliers,
            f"{df['nivel'].mean():.4f}",
            f"{df['nivel'].std():.4f}",
        ]
    })

    with summary_cols[0]:
        st.dataframe(resumen_izq, use_container_width=True, hide_index=True)

    with summary_cols[1]:
        st.dataframe(resumen_der, use_container_width=True, hide_index=True)

    st.markdown(
        """
        <div class="status status-info">
            💧 El flujo conserva la consulta a MARCO, la limpieza de la serie,
            la identificación de missing values, el análisis de outliers,
            la normalización, la división temporal y las estadísticas del código original.
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown(
    """
    <div class="footer">
        CORNARE / MARCO · Panel académico de análisis de nivel de ríos y quebradas
    </div>
    """,
    unsafe_allow_html=True
)
