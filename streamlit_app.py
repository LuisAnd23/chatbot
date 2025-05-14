import streamlit as st
from openai import OpenAI

# Título y descripción
st.title("Corrector gramatical en español")
st.write(
    "Esta app **solo corrige errores gramaticales** en textos escritos en español. "
    "No realiza traducciones, resúmenes ni responde preguntas. "
    "Necesitas una clave API de OpenAI para usarla: "
    "[Consíguela aquí](https://platform.openai.com/account/api-keys)."
)

# Ingreso de la API Key
openai_api_key = st.text_input("🔑 Clave API de OpenAI", type="password")
if not openai_api_key:
    st.info("Por favor ingresa tu clave API para continuar.", icon="🗝️")
else:
    # Crear cliente de OpenAI
    client = OpenAI(api_key=openai_api_key)

    # Estado de sesión para guardar mensajes
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Mostrar historial del chat
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Entrada del usuario
    if prompt := st.chat_input("Introduce el texto que deseas corregir:"):

        # Guardar y mostrar el mensaje del usuario
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Definir el sistema: solo corrige gramática, nada más
        system_instruction = (
            "Eres un asistente que únicamente corrige errores gramaticales "
            "en textos escritos en español. Si el usuario pide otra cosa (como traducir, "
            "resumir, responder preguntas, etc.), responde únicamente:\n"
            "\"Lo siento, solo puedo corregir errores gramaticales en textos escritos en español.\""
        )

        # Construcción del stream de respuesta
        try:
            stream = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_instruction},
                    *[
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages
                    ]
                ],
                stream=True,
            )

            # Mostrar y guardar respuesta
            with st.chat_message("assistant"):
                response = st.write_stream(stream)

            st.session_state.messages.append({"role": "assistant", "content": response})

        except Exception as e:
            st.error(f" Error al llamar a la API: {e}")
