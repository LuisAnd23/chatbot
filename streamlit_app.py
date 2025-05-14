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
            if message["role"] == "assistant" and (
                "$$" in message["content"] or "\\int" in message["content"]
            ):
                st.latex(message["content"].strip("$$"))
            else:
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
            "Siempre devuelve la solución en formato LaTeX entre delimitadores `$$ ... $$`."
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

            response_text = ""
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                for chunk in stream:
                    content = chunk.choices[0].delta.content or ""
                    response_text += content
                    message_placeholder.markdown(response_text)

                # Mostrar en LaTeX si corresponde
                if "$$" in response_text or "\\int" in response_text:
                    message_placeholder.empty()
                    st.latex(response_text.strip("$$"))

            st.session_state.messages.append({"role": "assistant", "content": response_text})

        except Exception as e:
            st.error(f"❌ Error al llamar a la API: {e}")
