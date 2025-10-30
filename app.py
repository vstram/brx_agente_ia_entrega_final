
import streamlit as st
import os
from src.agent import get_agent_executor, load_fiscal_notes_tool
import time

# --- 1. Configuração da Página e Título ---
st.set_page_config(page_title="Análise Gerencial de Notas Fiscais", layout="wide")

st.title("🤖 Agente de Análise Gerencial de Notas Fiscais")
st.caption("Uma ferramenta de IA para extrair insights valiosos de seus dados fiscais.")

# --- 2. Barra Lateral para Configuração ---
with st.sidebar:
    st.header("Configurações")
    st.markdown("""
    Esta aplicação utiliza a API do Google Gemini para a inteligência artificial e a API da Tavily para pesquisas na web. 
    Por favor, insira suas chaves de API abaixo.
    """)
    
    google_api_key = st.text_input("Chave da API do Google Gemini", type="password", key="google_api_key")
    tavily_api_key = st.text_input("Chave da API da Tavily", type="password", key="tavily_api_key")

    st.markdown("---")
    st.subheader("Sobre")
    st.markdown("""
    Este agente foi construído com **LangGraph** e **Streamlit** para fornecer uma interface de análise de dados conversacional e poderosa.
    """)

# --- 3. Lógica Principal ---

# Verifica se as chaves de API foram inseridas
if google_api_key and tavily_api_key:
    os.environ["GOOGLE_API_KEY"] = google_api_key
    os.environ["TAVILY_API_KEY"] = tavily_api_key

    # Inicializa o agente (executor do grafo LangGraph)
    try:
        app = get_agent_executor()
        st.sidebar.success("Agente pronto para operar!")
    except Exception as e:
        st.sidebar.error(f"Erro ao inicializar o agente: {e}")
        st.stop()

    # Inicializa o estado da sessão para o histórico de chat
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Exibe o histórico de mensagens
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "image" in message:
                st.image(message["image"], caption="Gráfico Gerado pela Análise")

    # --- 4. Interface de Chat ---
    if prompt := st.chat_input("Qual análise você gostaria de fazer?"):
        # Adiciona a mensagem do usuário ao histórico
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Exibe a resposta do agente
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            # Prepara a entrada para o agente
            inputs = {"messages": [("user", prompt)]}
            
            with st.spinner("Analisando..."):
                # Executa o agente em stream para uma experiência mais interativa
                for chunk in app.stream(inputs):
                    # O stream retorna um dicionário com a chave do nó que produziu a saída
                    if "agent" in chunk:
                        content = chunk["agent"].get("messages", [{}])[-1].content
                        if content:
                            full_response += content
                            message_placeholder.markdown(full_response + "▌")
                
                message_placeholder.markdown(full_response)

            # Verifica se um gráfico foi gerado e o exibe
            if os.path.exists("plot.png"):
                st.image("plot.png", caption="Gráfico Gerado pela Análise")
                # Adiciona a imagem ao histórico para ser re-exibida
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": full_response,
                    "image": "plot.png"
                })
            else:
                 st.session_state.messages.append({"role": "assistant", "content": full_response})

else:
    st.warning("Por favor, insira suas chaves de API na barra lateral para começar.")

