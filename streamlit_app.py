import streamlit as st
from openai import OpenAI

# Título y descripción
st.title("∫ Calculadora de Integrales con IA")
st.write(
    "Esta app **solo resuelve integrales** de funciones matemáticas. "
    "Para usarla, escribe:\n\n"
    "- `integrar: f(x) = x^2` para integrales indefinidas.\n"
    "- `integrar: f(x) = x^2, a = 0, b = 1` para integrales definidas.\n\n"
    "**No realiza ningún otro tipo de tarea.**"
)

# Clave API
api_key = st.text_input("🔑 Clave API de OpenAI", type="password")
if not api_key:
    st.info("Por favor, ingresa tu clave API para continuar.", icon="🗝️")
else:
    client = OpenAI(api_key=api_key)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Mostrar historial
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Entrada del usuario
    if prompt := st.chat_input("Ejemplo: integrar: f(x) = sin(x)"):

        # Mostrar mensaje del usuario
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Instrucción del sistema
        system_prompt = (
            "Eres un asistente matemático que **solo resuelve integrales**. "
            "No debes responder preguntas ni realizar otras tareas. "
            "Si el usuario pide algo que no sea calcular una integral, responde con: "
            "\"Lo siento, solo puedo calcular integrales de funciones matemáticas.\"\n\n"
            "El usuario puede dar funciones como `f(x) = x^2`, o incluir límites `a = 0, b = 1`. "
            "Devuelve la solución en formato LaTeX si es posible."
        )

        try:
            stream = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    *[
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages
                    ]
                ],
                stream=True,
            )

            with st.chat_message("assistant"):
                response = st.write_stream(stream)

            st.session_state.messages.append({"role": "assistant", "content": response})

        except Exception as e:
            st.error(f"❌ Error al llamar a la API: {e}")

