import streamlit as st
import httpx
import base64

# =========================
# Configuración general
# =========================
st.set_page_config(page_title="Inventario IA", layout="wide")

URL_GRAPHQL = "http://localhost:8000/graphql"

# =========================
# Estado del chat
# =========================
if "chat" not in st.session_state:
    st.session_state.chat = []

if "register_mode" not in st.session_state:
    st.session_state.register_mode = False

if "register_images" not in st.session_state:
    st.session_state.register_images = []

if "last_photo" not in st.session_state:
    st.session_state.last_photo = None

# =========================
# Estilos tipo ChatGPT
# =========================
st.markdown(
    """
<style>

/* panel visual */
.chat-box, .camera-box, .inventory-box {
    background-color: #111827;
    padding: 15px;
    border-radius: 12px;
}

/* altura fija para chat y cámara */
.chat-box, .camera-box {
    height: 75vh;
}

/* chat interno */
.chat-container {
    height: 55vh;
    overflow-y: auto;
    padding: 15px;
    background-color: #0e1117;
    border-radius: 10px;
    margin-bottom: 10px;
}

/* burbujas */
.user-bubble {
    background: linear-gradient(135deg, #6a11cb, #2575fc);
    color: white;
    padding: 10px 14px;
    border-radius: 14px;
    margin: 8px 0;
    max-width: 60%;
    margin-left: auto;
    text-align: right;
}

.agent-bubble {
    background: #1f2937;
    color: white;
    padding: 10px 14px;
    border-radius: 14px;
    margin: 8px 0;
    max-width: 60%;
}
</style>
""",
    unsafe_allow_html=True,
)


# =========================
# Utilidad GraphQL
# =========================
def run_query(query: str, variables=None):
    try:
        with httpx.Client() as client:
            response = client.post(
                URL_GRAPHQL,
                json={"query": query, "variables": variables},
                timeout=60.0,
            )
            return response.json()
    except Exception as e:
        st.error("❌ Error de conexión con el backend")
        print("ERROR GraphQL:", e)
        return None


REPLY_AGENT_MUTATION = """
mutation ReplyAgent($msg: String!) {
  replyToAgent(message: $msg)
}
"""


# =========================
# Función analizar imagen
# =========================
def analyze_image(image_bytes):
    img_b64 = base64.b64encode(image_bytes).decode()

    mutation = """
    mutation Detect($img: String!) {
      detectProductFromImage(image: $img)
    }
    """

    res = run_query(mutation, {"img": img_b64})

    if res and res.get("data"):
        response_text = res["data"]["detectProductFromImage"]
        st.session_state.chat.append({"role": "agent", "content": response_text})
    else:
        st.error("❌ Error al analizar la imagen")


# =========================
# LAYOUT PRINCIPAL
# =========================
main_left, main_right = st.columns([1.3, 1])

# =========================
# CHAT
# =========================
with main_left:
    st.subheader("💬 Chat con el agente")

    chat_panel = st.container(border=True)

    with chat_panel:
        # zona de mensajes con altura fija
        chat_messages = st.container(height=545)

        with chat_messages:
            for msg in st.session_state.chat:
                if msg["role"] == "user":
                    st.markdown(
                        f"""
                        <div style="
                            background: linear-gradient(135deg,#6a11cb,#2575fc);
                            color:white;
                            padding:10px;
                            border-radius:12px;
                            margin:6px 0;
                            max-width:70%;
                            margin-left:auto;
                            text-align:right;">
                            {msg["content"]}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f"""
                        <div style="
                            background:#1f2937;
                            color:white;
                            padding:10px;
                            border-radius:12px;
                            margin:6px 0;
                            max-width:70%;">
                            {msg["content"]}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

        # barra de escritura dentro del mismo panel
        col_input, col_file, col_send = st.columns([6, 1, 1])

        with col_input:
            user_text = st.text_input(
                "Mensaje",
                placeholder="Escribe un mensaje...",
                label_visibility="collapsed",
            )

        with col_file:
            if "open_uploader" not in st.session_state:
                st.session_state.open_uploader = False

            if st.button("📷", key="camera_btn"):
                st.session_state.open_uploader = True

            uploaded = None
            if st.session_state.open_uploader:
                uploaded = st.file_uploader(
                    "",
                    type=["jpg", "jpeg", "png"],
                    label_visibility="collapsed",
                    key="real_uploader",
                )

        with col_send:
            send_clicked = st.button("➤")


# =========================
# CÁMARA + INVENTARIO
# =========================
with main_right:

    # Cámara
    st.subheader("📸 Cámara")

    camera_panel = st.container(border=True)

    with camera_panel:
        camera_box = st.container(height=600)

        with camera_box:
            foto = st.camera_input("Capturar producto")

            if foto:
                image_bytes = foto.getvalue()

                if st.session_state.last_photo != image_bytes:
                    st.session_state.last_photo = image_bytes
                    analyze_image(image_bytes)

    st.divider()

    # Inventario
    st.subheader("📋 Inventario")
    inventory_panel = st.container(border=True)

    with inventory_panel:
        res = run_query("{ products { id name stock } }")
        if res and res.get("data"):
            st.table(res["data"]["products"])
        else:
            st.warning("No se pudo cargar el inventario")

# =========================
# Envío de mensajes
# =========================
if send_clicked:

    if uploaded is not None:

        image_bytes = uploaded.getvalue()

        if st.session_state.register_mode:

            st.session_state.register_images.append(image_bytes)

            st.session_state.chat.append(
                {
                    "role": "user",
                    "content": f"📷 Imagen {len(st.session_state.register_images)} enviada",
                }
            )

            if len(st.session_state.register_images) == 3:

                st.session_state.chat.append(
                    {
                        "role": "agent",
                        "content": "🔍 Analizando las imágenes del producto...",
                    }
                )

                analyze_image(st.session_state.register_images[0])

                st.session_state.register_mode = False
                st.session_state.register_images = []

            st.rerun()

        else:
            st.session_state.chat.append(
                {"role": "user", "content": "📷 Imagen enviada"}
            )

            analyze_image(image_bytes)
            st.rerun()

    elif user_text:

        st.session_state.chat.append({"role": "user", "content": user_text})

        res = run_query(REPLY_AGENT_MUTATION, {"msg": user_text})

        if res and res.get("data"):
            response_text = res["data"]["replyToAgent"]
            st.session_state.chat.append({"role": "agent", "content": response_text})

            if "imagen frontal" in response_text.lower():
                st.session_state.register_mode = True
                st.session_state.register_images = []

        else:
            st.session_state.chat.append(
                {"role": "agent", "content": "❌ El agente no respondió"}
            )

        st.rerun()
