import streamlit as st
import httpx
import base64

# =========================
# Configuración general
# =========================
st.set_page_config(
    page_title="Inventario IA",
    layout="wide"
)

st.title("📦 Sistema de Inventario Inteligente")

URL_GRAPHQL = "http://localhost:8000/graphql"

# =========================
# Utilidad GraphQL
# =========================
def run_query(query: str, variables=None):
    try:
        with httpx.Client() as client:
            response = client.post(
                URL_GRAPHQL,
                json={"query": query, "variables": variables},
                timeout=30.0
            )
            return response.json()
    except Exception as e:
        st.error("❌ Error de conexión con el backend")
        print("ERROR GraphQL:", e)
        return None


# =========================
# Queries GraphQL
# =========================
ASK_INVENTORY_QUERY = """
query AskInventory($question: String!) {
  askInventory(question: $question)
}
"""

SEARCH_INTELLIGENT_QUERY = """
query Search($q: String!) {
  searchIntelligent(query: $q)
}
"""

# =========================
# Layout principal
# =========================
col_inv, col_cam = st.columns([1, 1.2])

# =========================
# Inventario
# =========================
with col_inv:
    st.header("📋 Inventario Actual")

    if st.button("🔄 Actualizar"):
        res = run_query("{ products { id name stock } }")
        if res and res.get("data"):
            st.table(res["data"]["products"])
        else:
            st.error("❌ No se pudo obtener el inventario")

    st.header("➕ Registrar producto")

    with st.form("reg"):
        name = st.text_input("Nombre del producto")
        stock = st.number_input(
            "Cantidad (stock)",
            min_value=0,
            step=1
        )

        if st.form_submit_button("Guardar"):
            if not name:
                st.warning("⚠️ El nombre es obligatorio")
            else:
                run_query(
                    f'''
                    mutation {{
                        addProduct(name: "{name}", stock: {stock}) {{
                            id
                        }}
                    }}
                    '''
                )
                st.success("✅ Producto registrado correctamente")


# =========================
# Cámara
# =========================
with col_cam:
    st.header("📸 Detección por Cámara")

    foto = st.camera_input("Capturar imagen")

    if foto:
        with st.spinner("🤖 Analizando imagen..."):
            img_b64 = base64.b64encode(foto.getvalue()).decode()

            mutation = """
            mutation Detect($img: String!) {
              detectProductFromImage(image: $img)
            }
            """

            res = run_query(mutation, {"img": img_b64})

            if res and res.get("data"):
                st.info("💡 Respuesta del Agente")
                st.markdown(res["data"]["detectProductFromImage"])
            else:
                st.error("❌ Error al analizar la imagen")


# =========================
# Asistente Inteligente
# =========================
st.header("🤖 Asistente Inteligente")

user_input = st.text_input(
    "Escribe una pregunta o busca un producto",
    placeholder="Ej: ¿Hay arroz? / Todavía hay leche / Huevos"
)

if st.button("🔍 Analizar") and user_input:

    # 🧠 Heurística simple para detectar preguntas
    is_question = (
        "?" in user_input
        or user_input.lower().startswith("hay")
        or user_input.lower().startswith("todavía")
        or user_input.lower().startswith("todavia")
        or user_input.lower().startswith("existe")
    )

    # =========================
    # Pregunta sobre inventario
    # =========================
    if is_question:
        res = run_query(
            ASK_INVENTORY_QUERY,
            {"question": user_input}
        )

        if res and res.get("data"):
            st.success(res["data"]["askInventory"])
        else:
            st.error("❌ No se pudo obtener respuesta del asistente")

    # =========================
    # Búsqueda normal
    # =========================
    else:
        res = run_query(
            SEARCH_INTELLIGENT_QUERY,
            {"q": user_input}
        )

        if res and res.get("data"):
            items = res["data"].get("searchIntelligent", [])

            if items:
                for item in items:
                    st.success(f"🛒 Producto detectado: {item}")
            else:
                st.warning("⚠️ No se identificaron productos en la frase.")
        else:
            st.error("❌ Error en la búsqueda inteligente")
