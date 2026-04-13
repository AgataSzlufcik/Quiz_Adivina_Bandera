import streamlit as st
import requests
import random
import pandas as pd

TOTAL_PREGUNTAS = 20

# --- FUNCIONES ---

@st.cache_data
def obtener_paises():
    url = "https://restcountries.com/v3.1/all?fields=name,flag,capital,population,region,languages"
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        paises = response.json()
    except Exception as e:
        st.error(f"Error al conectar con la API: {e}")
        st.stop()

    data = []
    for p in paises:
        try:
            nombre     = p["name"]["common"]
            bandera    = p.get("flag", "")
            capital    = p.get("capital", ["?"])[0]
            poblacion  = p.get("population", 0)
            continente = p.get("region", "?")
            idiomas    = p.get("languages", {})
            idioma     = list(idiomas.values())[0] if idiomas else "?"

            if bandera and continente != "?" and idioma != "?":
                data.append({
                    "nombre":     nombre,
                    "bandera":    bandera,
                    "capital":    capital,
                    "poblacion":  poblacion,
                    "continente": continente,
                    "idioma":     idioma
                })
        except:
            pass

    df = pd.DataFrame(data)

    if df.empty:
        st.error("No se pudieron cargar los países.")
        st.stop()

    return df

def generar_pregunta(df):
    pais_correcto = df.sample(1).iloc[0]
    opciones_falsas = df[df["nombre"] != pais_correcto["nombre"]].sample(3)
    opciones = [pais_correcto["nombre"]] + list(opciones_falsas["nombre"])
    random.shuffle(opciones)
    return pais_correcto, opciones

# --- INIT ---

st.set_page_config(page_title="Adivina el País", page_icon="🌍")
st.title("🌍 Adivina el País")

if "puntos" not in st.session_state:
    st.session_state.puntos = 0
    st.session_state.correctas = 0
    st.session_state.falladas = 0
    st.session_state.puntos_gastados_pistas = 0
    st.session_state.pregunta_num = 0
    st.session_state.juego_terminado = False

paises = obtener_paises()

def nueva_pregunta():
    pais, opciones = generar_pregunta(paises)
    st.session_state.pais_actual = pais
    st.session_state.opciones = opciones
    st.session_state.respondido = False
    st.session_state.pistas_mostradas = []

if "pais_actual" not in st.session_state:
    nueva_pregunta()

# --- PANTALLA FINAL ---

if st.session_state.juego_terminado:
    st.balloons()
    st.header("Partida terminada")

    puntos_brutos  = st.session_state.correctas * 10
    puntos_gastados = st.session_state.puntos_gastados_pistas
    puntos_finales  = st.session_state.puntos
    eficiencia = round((puntos_finales / puntos_brutos * 100) if puntos_brutos > 0 else 0)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Puntos finales", puntos_finales)
    col2.metric("Correctas", f"{st.session_state.correctas}/{TOTAL_PREGUNTAS}")
    col3.metric("Gastado en pistas", f"-{puntos_gastados} pts")
    col4.metric("Eficiencia", f"{eficiencia}%")

    st.divider()
    st.write("**Score de eficiencia**")

    if eficiencia == 100:
        st.success("Perfecto — resolviste todo sin usar pistas.")
    elif eficiencia >= 75:
        st.info(f"Muy bien — gastaste {puntos_gastados} puntos en pistas pero mantuviste buen rendimiento.")
    elif eficiencia >= 50:
        st.warning(f"Regular — las pistas te costaron {puntos_gastados} puntos.")
    else:
        st.error(f"Dependiste mucho de las pistas. Perdiste {puntos_gastados} puntos en ayudas.")

    st.progress(eficiencia / 100)

    with st.expander("Ver cómo se calcula la eficiencia"):
        st.write(f"""
        - Puntos posibles sin pistas: **{puntos_brutos}**
        - Puntos gastados en pistas: **{puntos_gastados}**
        - Puntos finales: **{puntos_finales}**
        - Eficiencia = {puntos_finales} / {puntos_brutos} × 100 = **{eficiencia}%**
        """)

    if st.button("Jugar de nuevo", type="primary"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    st.stop()

# --- JUEGO ---

pais = st.session_state.pais_actual

col1, col2, col3, col4 = st.columns(4)
col1.metric("Puntos", st.session_state.puntos)
col2.metric("Correctas", st.session_state.correctas)
col3.metric("Falladas", st.session_state.falladas)
col4.metric("Pregunta", f"{st.session_state.pregunta_num + 1}/{TOTAL_PREGUNTAS}")

st.divider()

st.markdown(f"<h1 style='text-align:center; font-size: 80px'>{pais['bandera']}</h1>", unsafe_allow_html=True)
st.write("### ¿De qué país es esta bandera?")

PISTAS = {
    "continente": ("Continente", pais["continente"]),
    "poblacion":  ("Población",  f"{pais['poblacion']:,} habitantes"),
    "capital":    ("Capital",    pais["capital"]),
    "idioma":     ("Idioma",     pais["idioma"]),
}

st.write("**Pistas disponibles** — cada pista cuesta 1 punto:")

pistas_cols = st.columns(len(PISTAS))
for i, (clave, (label, valor)) in enumerate(PISTAS.items()):
    with pistas_cols[i]:
        if clave in st.session_state.pistas_mostradas:
            st.success(f"**{label}**\n\n{valor}")
        elif st.session_state.respondido:
            st.info(f"**{label}**\n\n{valor}")
        else:
            if st.button(f"Ver {label} (-1 pto)", key=f"pista_{clave}",
                         disabled=st.session_state.puntos < 1):
                st.session_state.puntos -= 1
                st.session_state.puntos_gastados_pistas += 1
                st.session_state.pistas_mostradas.append(clave)
                st.rerun()

st.divider()

for opcion in st.session_state.opciones:
    if st.button(opcion, disabled=st.session_state.respondido, use_container_width=True):
        st.session_state.respondido = True
        if opcion == pais["nombre"]:
            st.success("✅ ¡Correcto! +10 puntos")
            st.session_state.puntos += 10
            st.session_state.correctas += 1
        else:
            st.error(f"❌ Era **{pais['nombre']}**")
            st.session_state.falladas += 1

if st.session_state.respondido:
    if st.session_state.pregunta_num + 1 >= TOTAL_PREGUNTAS:
        if st.button("Ver resultados finales", type="primary"):
            st.session_state.juego_terminado = True
            st.rerun()
    else:
        if st.button("➡️ Siguiente pregunta", type="primary"):
            st.session_state.pregunta_num += 1
            nueva_pregunta()
            st.rerun()

   