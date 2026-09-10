# ================================================================
# ACTIVIDAD INDIVIDUAL
# Análisis de nivel de ríos y quebradas - CORNARE / MARCO
# VERSIÓN STREAMLIT: MISMA LÓGICA DEL ARCHIVO ORIGINAL + PRESENTACIÓN
# ================================================================

import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import urllib3
import streamlit as st

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ================================================================
# CONFIGURACIÓN DE STREAMLIT (SOLO PRESENTACIÓN)
# ================================================================

st.set_page_config(
    page_title="CORNARE · Análisis de nivel",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap');

    :root {
        --navy: #06364a;
        --blue: #0b7285;
        --cyan: #12a6b7;
        --aqua: #22c4b6;
        --green: #2f8f62;
        --bg: #f2f9fa;
        --card: #ffffff;
        --text: #17333d;
        --muted: #6a828a;
        --line: #dbeaed;
        --shadow: 0 12px 32px rgba(6, 54, 74, .08);
    }

    .stApp {
        background:
            radial-gradient(circle at 0% 0%, rgba(34,196,182,.11), transparent 26rem),
            radial-gradient(circle at 100% 0%, rgba(18,166,183,.10), transparent 25rem),
            linear-gradient(180deg, #f6fcfc 0%, #f2f9fa 100%);
        color: var(--text);
        font-family: 'Inter', sans-serif;
    }

    .block-container {
        max-width: 1450px;
        padding: 1.4rem 2rem 3rem;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #06364a 0%, #07556a 58%, #087b80 100%);
    }
    [data-testid="stSidebar"] * { color: #f1ffff; }
    [data-testid="stSidebar"] hr { border-color: rgba(255,255,255,.17); }

    .brand {
        display:flex; align-items:center; gap:.7rem;
        margin-bottom:.2rem;
    }
    .brand-icon {
        width:42px; height:42px; display:flex; align-items:center; justify-content:center;
        border-radius:13px; background:rgba(255,255,255,.13); font-size:1.35rem;
    }
    .brand-title { font:700 1.25rem 'Space Grotesk',sans-serif; }
    .brand-sub { color:#c8f4f5; font-size:.78rem; margin-top:.15rem; line-height:1.45; }

    .hero {
        position:relative; overflow:hidden;
        border-radius:28px;
        padding:2rem 2.15rem;
        background:linear-gradient(135deg,#06364a 0%,#087786 58%,#16aa9e 100%);
        box-shadow:0 20px 46px rgba(6,54,74,.20);
        margin-bottom:1.25rem;
    }
    .hero:after {
        content:""; position:absolute; width:320px; height:320px; border-radius:50%;
        right:-110px; top:-170px; background:rgba(255,255,255,.07);
        box-shadow:-110px 190px 0 26px rgba(255,255,255,.028), -220px 80px 0 52px rgba(255,255,255,.02);
    }
    .eyebrow { color:#c9fbfd; font-size:.76rem; font-weight:800; letter-spacing:.11em; text-transform:uppercase; }
    .hero h1 { color:#fff; font:700 clamp(2rem,4vw,3.2rem) 'Space Grotesk',sans-serif; letter-spacing:-.045em; margin:.45rem 0 .55rem; }
    .hero p { color:#dff8fa; max-width:850px; line-height:1.62; margin:0; }
    .chips { position:relative; z-index:2; display:flex; flex-wrap:wrap; gap:.55rem; margin-top:1.15rem; }
    .chip { padding:.42rem .7rem; border-radius:999px; color:#efffff; background:rgba(255,255,255,.10); border:1px solid rgba(255,255,255,.13); font-size:.78rem; font-weight:700; }

    .section-head {
        display:flex; align-items:flex-end; justify-content:space-between; gap:1rem;
        margin:1.55rem 0 .8rem;
    }
    .section-title { font:700 1.38rem 'Space Grotesk',sans-serif; color:var(--navy); letter-spacing:-.025em; margin:0; }
    .section-desc { color:var(--muted); font-size:.9rem; margin:.2rem 0 0; }

    .info-card, .metric-card {
        background:rgba(255,255,255,.97); border:1px solid var(--line); border-radius:18px;
        padding:1rem 1.05rem; box-shadow:var(--shadow);
    }
    .info-card { min-height:112px; }
    .label { color:#70858c; font-size:.72rem; font-weight:800; text-transform:uppercase; letter-spacing:.08em; }
    .value { color:var(--navy); font:700 1.12rem 'Space Grotesk',sans-serif; margin-top:.42rem; word-break:break-word; }
    .note { color:var(--muted); font-size:.78rem; line-height:1.45; margin-top:.25rem; }

    .metric-card { min-height:105px; }
    .metric-name { color:#72868d; font-size:.72rem; font-weight:800; text-transform:uppercase; letter-spacing:.06em; }
    .metric-value { color:var(--navy); font:700 1.52rem 'Space Grotesk',sans-serif; margin-top:.4rem; }

    .status { border-radius:14px; padding:.82rem 1rem; border:1px solid; font-size:.9rem; font-weight:600; margin:.4rem 0 1rem; }
    .ok { background:#eaf8f0; color:#17643c; border-color:#c8ead6; }
    .bad { background:#fff1f1; color:#9f2020; border-color:#f1cccc; }
    .warn { background:#fff8e9; color:#8a5b10; border-color:#f2dfa9; }
    .info { background:#e9f7fb; color:#0a5870; border-color:#c7e7ef; }

    .mini {
        border:1px solid var(--line); background:rgba(255,255,255,.85); border-radius:16px; padding: .85rem 1rem;
        box-shadow:var(--shadow); margin-bottom:.8rem;
    }
    .mini-title { color:var(--blue); font:700 1rem 'Space Grotesk',sans-serif; margin-bottom:.45rem; }

    .footer { margin-top:2rem; padding-top:1rem; border-top:1px solid var(--line); color:#7b9198; text-align:center; font-size:.75rem; }

    div[data-testid="stExpander"] { border:1px solid var(--line); border-radius:16px; background:rgba(255,255,255,.62); }
    .stButton > button { border-radius:12px; font-weight:700; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ================================================================
# 1. PARÁMETROS DE TU CONSULTA
# ================================================================

# Los valores originales son los valores por defecto, pero ahora sí
# pueden cambiarse desde Streamlit antes de ejecutar la consulta.
NOMBRE_ESTUDIANTE_DEFAULT = "Juan Jose Patiño Amariles"
CODIGO_ESTACION_DEFAULT = "42"
FECHA_DESDE_DEFAULT = "2026-08-23"
FECHA_HASTA_DEFAULT = "2026-08-30"
CALIDAD_DEFAULT = 1

# ================================================================
# CONFIGURACIÓN DE LA API
# ================================================================

API_BASE_URL = "https://marco.cornare.gov.co/api/v1/estaciones"
LLAVE_FECHA = "level_date"
LLAVE_VALOR = "level"

# Coordenadas por defecto (se conservan exactamente del archivo original)
LAT_DEFECTO = 6.2766
LON_DEFECTO = -75.5901
CANDIDATOS_LAT = ["lat", "latitude", "latitud"]
CANDIDATOS_LON = ["lng", "lon", "longitude", "longitud"]

# ================================================================
# FUNCIONES ORIGINALES DE CONSULTA (MISMA LÓGICA)
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
        registros.extend(pagina.get("values", []))
        siguiente_url = pagina.get("next")

    return registros

# ================================================================
# PRESENTACIÓN DE CONFIGURACIÓN
# ================================================================

with st.sidebar:
    st.markdown(
        """
        <div class="brand">
            <div class="brand-icon">🌊</div>
            <div>
                <div class="brand-title">CORNARE / MARCO</div>
                <div class="brand-sub">Monitoreo y análisis de niveles de ríos y quebradas</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("---")
    st.markdown("### Parámetros de la consulta")

    nombre_estudiante = st.text_input(
        "Nombre del estudiante",
        value=NOMBRE_ESTUDIANTE_DEFAULT,
        key="nombre_estudiante",
    )
    codigo_estacion = st.text_input(
        "Código de estación",
        value=CODIGO_ESTACION_DEFAULT,
        key="codigo_estacion",
    )
    fecha_desde = st.date_input(
        "Fecha desde",
        value=pd.to_datetime(FECHA_DESDE_DEFAULT).date(),
        key="fecha_desde",
    )
    fecha_hasta = st.date_input(
        "Fecha hasta",
        value=pd.to_datetime(FECHA_HASTA_DEFAULT).date(),
        key="fecha_hasta",
    )
    calidad = st.radio(
        "Calidad de datos",
        options=[1, 0],
        index=0,
        format_func=lambda x: "1 · Datos validados" if x == 1 else "0 · Todos los datos disponibles",
        key="calidad",
    )

    ejecutar = st.button("🌊 Ejecutar análisis", use_container_width=True, type="primary")

    st.markdown("---")
    st.markdown("**Proceso original**")
    st.caption("1. Consulta de API")
    st.caption("2. Serie de tiempo")
    st.caption("3. Tipos y orden temporal")
    st.caption("4. Missing values reales")
    st.caption("5. Outliers: IQR + límites físicos")
    st.caption("6. Normalización y Z-Score")
    st.caption("7. Train / Validation / Test")
    st.caption("8. Estadística descriptiva")

# Estado inicial: no se ejecuta una consulta distinta al archivo original
# hasta que se presiona el botón con los parámetros deseados.
if "datos_crudos" not in st.session_state:
    st.session_state.datos_crudos = None
    st.session_state.error = None
    st.session_state.registros = None
    st.session_state.config = None

if ejecutar:
    fecha_desde_str = fecha_desde.strftime("%Y-%m-%d")
    fecha_hasta_str = fecha_hasta.strftime("%Y-%m-%d")
    datos_crudos, error = obtener_serie_nivel(
        codigo_estacion,
        fecha_desde_str,
        fecha_hasta_str,
        calidad,
    )
    st.session_state.datos_crudos = datos_crudos
    st.session_state.error = error
    st.session_state.registros = None if error else obtener_todas_las_paginas(datos_crudos)
    st.session_state.config = {
        "nombre_estudiante": nombre_estudiante,
        "codigo_estacion": codigo_estacion,
        "fecha_desde": fecha_desde_str,
        "fecha_hasta": fecha_hasta_str,
        "calidad": calidad,
    }

# Cargar la última consulta ejecutada
config = st.session_state.config
if config is None:
    config = {
        "nombre_estudiante": nombre_estudiante,
        "codigo_estacion": codigo_estacion,
        "fecha_desde": fecha_desde.strftime("%Y-%m-%d"),
        "fecha_hasta": fecha_hasta.strftime("%Y-%m-%d"),
        "calidad": calidad,
    }

datos_crudos = st.session_state.datos_crudos
error = st.session_state.error
registros = st.session_state.registros

# ================================================================
# CABECERA VISUAL
# ================================================================

st.markdown(
    f"""
    <div class="hero">
        <div class="eyebrow">CORNARE / MARCO · ANÁLISIS HIDROLÓGICO</div>
        <h1>Análisis de nivel de ríos y quebradas</h1>
        <p>
            Consulta, limpieza y análisis de la serie temporal de nivel manteniendo
            el procedimiento original del ejercicio.
        </p>
        <div class="chips">
            <span class="chip">Estación {config['codigo_estacion']}</span>
            <span class="chip">{config['fecha_desde']} → {config['fecha_hasta']}</span>
            <span class="chip">Calidad {config['calidad']}</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if config is not None:
    calidad_texto = "Datos validados" if config["calidad"] == 1 else "Todos los datos disponibles"
    c1, c2, c3, c4 = st.columns(4)
    for col, label, value, note in [
        (c1, "Estudiante", config["nombre_estudiante"], "Parámetro editable"),
        (c2, "Estación", config["codigo_estacion"], "Código consultado"),
        (c3, "Periodo", f"{config['fecha_desde']} → {config['fecha_hasta']}", "Rango de consulta"),
        (c4, "Calidad", calidad_texto, f"Valor API: {config['calidad']}"),
    ]:
        with col:
            st.markdown(
                f'<div class="info-card"><div class="label">{label}</div><div class="value">{value}</div><div class="note">{note}</div></div>',
                unsafe_allow_html=True,
            )

# ================================================================
# CONSULTA Y MENSAJE DE ESTADO
# ================================================================

if error:
    st.markdown(f'<div class="status bad">❌ <strong>Error al consultar la API:</strong> {error}</div>', unsafe_allow_html=True)
    st.stop()

if registros is None:
    st.markdown(
        '<div class="status info">ℹ️ Configura los parámetros del panel izquierdo y pulsa <strong>Ejecutar análisis</strong> para consultar la API.</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="footer">CORNARE / MARCO · Panel visual de análisis · La lógica del ejercicio permanece en el código.</div>',
        unsafe_allow_html=True,
    )
    st.stop()

st.markdown(
    f'<div class="status ok">✅ <strong>Consulta realizada correctamente.</strong> Cantidad de registros obtenidos: {len(registros):,}</div>',
    unsafe_allow_html=True,
)

if not registros:
    st.warning("La consulta no devolvió registros para los parámetros seleccionados.")
    st.markdown('<div class="footer">CORNARE / MARCO</div>', unsafe_allow_html=True)
    st.stop()

# ================================================================
# 3. CONSTRUIR EL DATAFRAME DE SERIE DE TIEMPO
# ================================================================

df = pd.DataFrame(registros)
df = df.rename(columns={LLAVE_FECHA: "fecha", LLAVE_VALOR: "nivel"})

st.markdown('<div class="section-head"><div><div class="section-title">3. Serie de tiempo</div><div class="section-desc">Estructura recibida de la API y primeros registros.</div></div></div>', unsafe_allow_html=True)

with st.expander("Ver columnas disponibles", expanded=False):
    st.write(df.columns.tolist())

st.dataframe(df.head(), use_container_width=True, hide_index=True)

# ================================================================
# 4. TIPOS DE DATOS Y ORDEN TEMPORAL
# ================================================================

df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
df["nivel"] = pd.to_numeric(df["nivel"], errors="coerce")
df = df.dropna(subset=["fecha", "nivel"])
df = df.sort_values("fecha").reset_index(drop=True)

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f'<div class="metric-card"><div class="metric-name">Desde</div><div class="metric-value">{df["fecha"].min()}</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="metric-card"><div class="metric-name">Hasta</div><div class="metric-value">{df["fecha"].max()}</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="metric-card"><div class="metric-name">Registros válidos</div><div class="metric-value">{len(df):,}</div></div>', unsafe_allow_html=True)

with st.expander("Ver tipos de datos y DataFrame ordenado", expanded=False):
    st.write(df.dtypes)
    st.dataframe(df.head(10), use_container_width=True, hide_index=True)

# ================================================================
# UBICACIÓN DE LA ESTACIÓN (VISUAL; NO CAMBIA EL ANÁLISIS)
# ================================================================

lat_estacion = LAT_DEFECTO
lon_estacion = LON_DEFECTO
fuente_coord = "Coordenadas por defecto del archivo original"

# Cuando la respuesta trae lat/lon, se muestran automáticamente.
registro_coord = registros[0] if isinstance(registros[0], dict) else {}
for lat_key in CANDIDATOS_LAT:
    if lat_key in registro_coord:
        try:
            lat_estacion = float(registro_coord[lat_key])
            fuente_coord = f"Latitud detectada en la respuesta ({lat_key})"
            break
        except (TypeError, ValueError):
            pass
for lon_key in CANDIDATOS_LON:
    if lon_key in registro_coord:
        try:
            lon_estacion = float(registro_coord[lon_key])
            if fuente_coord == "Coordenadas por defecto del archivo original":
                fuente_coord = f"Longitud detectada en la respuesta ({lon_key})"
            break
        except (TypeError, ValueError):
            pass

st.markdown('<div class="section-head"><div><div class="section-title">Ubicación de la estación</div><div class="section-desc">Referencia geográfica disponible para la estación consultada.</div></div></div>', unsafe_allow_html=True)
loc1, loc2, loc3 = st.columns(3)
with loc1:
    st.markdown(f'<div class="info-card"><div class="label">Código</div><div class="value">{config["codigo_estacion"]}</div><div class="note">Estación consultada</div></div>', unsafe_allow_html=True)
with loc2:
    st.markdown(f'<div class="info-card"><div class="label">Latitud</div><div class="value">{lat_estacion:.6f}</div><div class="note">Coordenada geográfica</div></div>', unsafe_allow_html=True)
with loc3:
    st.markdown(f'<div class="info-card"><div class="label">Longitud</div><div class="value">{lon_estacion:.6f}</div><div class="note">Coordenada geográfica</div></div>', unsafe_allow_html=True)

st.caption(f"Fuente de la ubicación mostrada: {fuente_coord}.")
map_df = pd.DataFrame({"lat": [lat_estacion], "lon": [lon_estacion]})
st.map(map_df, latitude="lat", longitude="lon", zoom=11)

# ================================================================
# 5. MISSING VALUES REALES
# MÉTODO ORIGINAL: REINDEXAR A FRECUENCIA REGULAR
# ================================================================

st.markdown('<div class="section-head"><div><div class="section-title">5. Missing values reales</div><div class="section-desc">Detección mediante frecuencia típica y reindexación regular.</div></div></div>', unsafe_allow_html=True)

if len(df) > 1:
    diferencias = df["fecha"].sort_values().diff().dropna()
    frecuencia_tipica = diferencias.mode()

    if len(frecuencia_tipica) > 0:
        frecuencia = frecuencia_tipica.iloc[0]
        frecuencia_texto = str(frecuencia)
    else:
        frecuencia = None
        frecuencia_texto = "No fue posible determinar la frecuencia."

    if frecuencia is not None:
        frecuencia_str = pd.tseries.frequencies.to_offset(frecuencia)
        indice_completo = pd.date_range(
            start=df["fecha"].min(),
            end=df["fecha"].max(),
            freq=frecuencia_str,
        )
        df_missing = df.set_index("fecha").reindex(indice_completo)
        df_missing.index.name = "fecha"
        cantidad_missing = df_missing["nivel"].isna().sum()
        total_esperado = len(df_missing)
        porcentaje_missing = (cantidad_missing / total_esperado) * 100
    else:
        df_missing = df.set_index("fecha").copy()
        cantidad_missing = 0
        total_esperado = len(df_missing)
        porcentaje_missing = 0

    a, b, c, d = st.columns(4)
    for col, label, val in [
        (a, "Frecuencia típica", frecuencia_texto),
        (b, "Registros esperados", f"{total_esperado:,}"),
        (c, "Missing reales", f"{cantidad_missing:,}"),
        (d, "% missing", f"{porcentaje_missing:.2f}%"),
    ]:
        with col:
            st.markdown(f'<div class="metric-card"><div class="metric-name">{label}</div><div class="metric-value">{val}</div></div>', unsafe_allow_html=True)

    with st.expander("Ver primeros registros con estructura regular", expanded=False):
        st.dataframe(df_missing.head(20), use_container_width=True)
else:
    cantidad_missing = 0
    total_esperado = len(df)
    porcentaje_missing = 0
    st.markdown('<div class="status warn">⚠️ No hay suficientes datos para analizar missing values.</div>', unsafe_allow_html=True)

# ================================================================
# 6. OUTLIERS CON IQR + LÍMITES FÍSICOS
# ================================================================

st.markdown('<div class="section-head"><div><div class="section-title">6. Outliers con IQR + límites físicos</div><div class="section-desc">Se conserva el método IQR y el límite físico inferior igual a 0.</div></div></div>', unsafe_allow_html=True)

serie_nivel = df["nivel"].dropna()
Q1 = serie_nivel.quantile(0.25)
Q3 = serie_nivel.quantile(0.75)
IQR = Q3 - Q1
limite_inferior_iqr = Q1 - 1.5 * IQR
limite_superior_iqr = Q3 + 1.5 * IQR
limite_fisico_inferior = 0
limite_fisico_superior = np.inf

df["outlier_iqr"] = (df["nivel"] < limite_inferior_iqr) | (df["nivel"] > limite_superior_iqr)
df["outlier_fisico"] = (df["nivel"] < limite_fisico_inferior) | (df["nivel"] > limite_fisico_superior)
df["outlier"] = df["outlier_iqr"] | df["outlier_fisico"]
cantidad_outliers = df["outlier"].sum()

a, b, c, d, e = st.columns(5)
for col, label, val in [
    (a, "Q1", f"{Q1:.4f}"),
    (b, "Q3", f"{Q3:.4f}"),
    (c, "IQR", f"{IQR:.4f}"),
    (d, "Límite superior", f"{limite_superior_iqr:.4f}"),
    (e, "Outliers", f"{cantidad_outliers:,}"),
]:
    with col:
        st.markdown(f'<div class="metric-card"><div class="metric-name">{label}</div><div class="metric-value">{val}</div></div>', unsafe_allow_html=True)

with st.expander("Ver límites completos y registros considerados outliers", expanded=False):
    st.write(f"Límite inferior IQR: {limite_inferior_iqr:.4f}")
    st.write(f"Límite superior IQR: {limite_superior_iqr:.4f}")
    st.write("Límite físico inferior: 0")
    st.dataframe(df[df["outlier"]], use_container_width=True, hide_index=True)

# ================================================================
# GRÁFICO DE OUTLIERS — MISMA INFORMACIÓN DEL ORIGINAL
# ================================================================

fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(df["fecha"], df["nivel"], label="Nivel")
ax.scatter(df.loc[df["outlier"], "fecha"], df.loc[df["outlier"], "nivel"], label="Outliers")
ax.axhline(limite_superior_iqr, linestyle="--", label="Límite superior IQR")
ax.axhline(limite_inferior_iqr, linestyle="--", label="Límite inferior IQR")
ax.set_title("Detección de outliers - Método IQR")
ax.set_xlabel("Fecha")
ax.set_ylabel("Nivel")
ax.legend()
ax.grid(True, alpha=.25)
st.pyplot(fig, use_container_width=True)
plt.close(fig)

# ================================================================
# 7. NORMALIZACIÓN Y ESTANDARIZACIÓN
# ================================================================

st.markdown('<div class="section-head"><div><div class="section-title">7. Normalización y estandarización</div><div class="section-desc">Parámetros calculados sobre TRAIN para evitar fuga de información.</div></div></div>', unsafe_allow_html=True)

datos_modelo = df[["fecha", "nivel"]].copy()
datos_modelo = datos_modelo[~df["outlier"]]
datos_modelo = datos_modelo.dropna()
datos_modelo = datos_modelo.sort_values("fecha").reset_index(drop=True)

n = len(datos_modelo)
n_train = int(n * 0.70)
n_validation = int(n * 0.15)
train = datos_modelo.iloc[:n_train].copy()
validation = datos_modelo.iloc[n_train:n_train + n_validation].copy()
test = datos_modelo.iloc[n_train + n_validation:].copy()

minimo = train["nivel"].min()
maximo = train["nivel"].max()
if maximo != minimo:
    train["nivel_normalizado"] = (train["nivel"] - minimo) / (maximo - minimo)
    validation["nivel_normalizado"] = (validation["nivel"] - minimo) / (maximo - minimo)
    test["nivel_normalizado"] = (test["nivel"] - minimo) / (maximo - minimo)
else:
    train["nivel_normalizado"] = 0
    validation["nivel_normalizado"] = 0
    test["nivel_normalizado"] = 0

media_train = train["nivel"].mean()
desviacion_train = train["nivel"].std()
if desviacion_train != 0:
    train["nivel_estandarizado"] = (train["nivel"] - media_train) / desviacion_train
    validation["nivel_estandarizado"] = (validation["nivel"] - media_train) / desviacion_train
    test["nivel_estandarizado"] = (test["nivel"] - media_train) / desviacion_train
else:
    train["nivel_estandarizado"] = 0
    validation["nivel_estandarizado"] = 0
    test["nivel_estandarizado"] = 0

m1, m2, m3, m4 = st.columns(4)
for col, label, val in [
    (m1, "Mínimo TRAIN", f"{minimo:.4f}"),
    (m2, "Máximo TRAIN", f"{maximo:.4f}"),
    (m3, "Media TRAIN", f"{media_train:.4f}"),
    (m4, "Desv. estándar TRAIN", f"{desviacion_train:.4f}"),
]:
    with col:
        st.markdown(f'<div class="metric-card"><div class="metric-name">{label}</div><div class="metric-value">{val}</div></div>', unsafe_allow_html=True)

with st.expander("Ver datos normalizados y estandarizados", expanded=False):
    st.dataframe(train.head(10), use_container_width=True, hide_index=True)

# ================================================================
# 8. TRAIN / VALIDATION / TEST — SPLIT CRONOLÓGICO
# ================================================================

st.markdown('<div class="section-head"><div><div class="section-title">8. Train / Validation / Test</div><div class="section-desc">División cronológica 70% / 15% / 15%, igual que el original.</div></div></div>', unsafe_allow_html=True)

total_modelo = len(datos_modelo)
porc_train = len(train) / total_modelo * 100 if total_modelo else 0
porc_validation = len(validation) / total_modelo * 100 if total_modelo else 0
porc_test = len(test) / total_modelo * 100 if total_modelo else 0

p1, p2, p3 = st.columns(3)
for col, label, count, pct in [
    (p1, "TRAIN", len(train), porc_train),
    (p2, "VALIDATION", len(validation), porc_validation),
    (p3, "TEST", len(test), porc_test),
]:
    with col:
        st.markdown(f'<div class="metric-card"><div class="metric-name">{label}</div><div class="metric-value">{count:,}</div><div class="note">{pct:.1f}%</div></div>', unsafe_allow_html=True)

with st.expander("Ver rangos de fechas", expanded=False):
    if not train.empty:
        st.write("TRAIN:", train["fecha"].min(), "→", train["fecha"].max())
    if not validation.empty:
        st.write("VALIDATION:", validation["fecha"].min(), "→", validation["fecha"].max())
    if not test.empty:
        st.write("TEST:", test["fecha"].min(), "→", test["fecha"].max())

fig, ax = plt.subplots(figsize=(12, 5))
if not train.empty:
    ax.plot(train["fecha"], train["nivel"], label="Train")
if not validation.empty:
    ax.plot(validation["fecha"], validation["nivel"], label="Validation")
if not test.empty:
    ax.plot(test["fecha"], test["nivel"], label="Test")
ax.set_title("División cronológica Train / Validation / Test")
ax.set_xlabel("Fecha")
ax.set_ylabel("Nivel")
ax.legend()
ax.grid(True, alpha=.25)
st.pyplot(fig, use_container_width=True)
plt.close(fig)

# ================================================================
# 9. ESTADÍSTICA DESCRIPTIVA
# ================================================================

st.markdown('<div class="section-head"><div><div class="section-title">9. Estadística descriptiva</div><div class="section-desc">Resumen estadístico de la variable nivel.</div></div></div>', unsafe_allow_html=True)

estadistica = df["nivel"].describe()
st.dataframe(estadistica.to_frame(name="nivel"), use_container_width=True)

s1, s2, s3, s4, s5, s6 = st.columns(6)
for col, label, val in [
    (s1, "Media", df["nivel"].mean()),
    (s2, "Mediana", df["nivel"].median()),
    (s3, "Desv. estándar", df["nivel"].std()),
    (s4, "Mínimo", df["nivel"].min()),
    (s5, "Máximo", df["nivel"].max()),
    (s6, "Rango", df["nivel"].max() - df["nivel"].min()),
]:
    with col:
        st.markdown(f'<div class="metric-card"><div class="metric-name">{label}</div><div class="metric-value">{val:.4f}</div></div>', unsafe_allow_html=True)

# ================================================================
# RESUMEN FINAL — MISMAS VARIABLES DEL ORIGINAL
# ================================================================

st.markdown('<div class="section-head"><div><div class="section-title">Resumen del análisis</div><div class="section-desc">Consolidado final de la consulta y sus resultados.</div></div></div>', unsafe_allow_html=True)

r1, r2, r3, r4 = st.columns(4)
summary_items = [
    (r1, "Estudiante", config["nombre_estudiante"]),
    (r2, "Estación", config["codigo_estacion"]),
    (r3, "Lecturas originales", f"{len(df):,}"),
    (r4, "Outliers detectados", f"{cantidad_outliers:,}"),
]
for col, label, val in summary_items:
    with col:
        st.markdown(f'<div class="info-card"><div class="label">{label}</div><div class="value">{val}</div></div>', unsafe_allow_html=True)

r5, r6, r7, r8 = st.columns(4)
for col, label, val in [
    (r5, "Periodo", f"{config['fecha_desde']} → {config['fecha_hasta']}"),
    (r6, "Missing reales", f"{cantidad_missing:,}"),
    (r7, "Promedio del nivel", f"{df['nivel'].mean():.4f}"),
    (r8, "Desv. estándar", f"{df['nivel'].std():.4f}"),
]:
    with col:
        st.markdown(f'<div class="info-card"><div class="label">{label}</div><div class="value">{val}</div></div>', unsafe_allow_html=True)

st.markdown(
    '<div class="footer">CORNARE / MARCO · Análisis de nivel de ríos y quebradas · Interfaz rediseñada sin sustituir el procedimiento analítico original.</div>',
    unsafe_allow_html=True,
)
