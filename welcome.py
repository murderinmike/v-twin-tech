import streamlit as st
import os
import base64
import fitz
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="V-Twin Tech Intelligence", page_icon="💀", layout="wide")

if "page" not in st.session_state: st.session_state["page"] = "home"
if "users_db" not in st.session_state: st.session_state["users_db"] = {"admin@vtwin.com": "harley2024"}
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

def obter_imagem_base64(caminho_imagem):
    if os.path.exists(caminho_imagem):
        with open(caminho_imagem, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    return ""

logo_base64 = obter_imagem_base64("logo.jpg")

@st.cache_resource
def carregar_sistema_ia():
    try:
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        db_path = "faiss_harley_global"
        
        if not os.path.exists(db_path):
            return None, "❌ Pasta FAISS não encontrada: " + db_path
        
        db = FAISS.load_local(db_path, embeddings, allow_dangerous_deserialization=True)
        retriever = db.as_retriever(search_kwargs={"k": 3})
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
        
        p = ChatPromptTemplate.from_messages([
            ("system", "You are a Master V-Twin Motorcycle Mechanic. Answer professionally based on context."),
            ("placeholder", "{chat_history}"),
            ("human", "Context from Manuals: {context}\n\nQuestion: {input}")
        ])
        return llm, retriever, p, "✅ Sistema IA carregado com sucesso"
    except Exception as e:
        return None, f"Erro ao carregar IA: {str(e)}"

# ====================== CSS (mantido igual) ======================
st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none !important; }
    .stApp { background-color: #121212; color: #FFFFFF; }
    /* ... resto do teu CSS original ... */
    .chat-bubble-user { background-color: #262626 !important; border-right: 4px solid #FF6600 !important; padding: 12px; border-radius: 8px; margin-bottom: 10px; text-align: right; margin-left: 20%; color: #FFFFFF; }
    .chat-bubble-tech { background-color: #1E1E1E !important; border-left: 4px solid #FF6600 !important; padding: 15px; border-radius: 8px; margin-bottom: 15px; text-align: left; margin-right: 20%; color: #EEEEEE; line-height: 1.5; }
    </style>
    """, unsafe_allow_html=True)

query_params = st.query_params
if "p" in query_params: st.session_state["page"] = query_params["p"]

def enviar_mensagem_chat():
    query_usuario = st.session_state.get("campo_texto_input", "").strip()
    if not query_usuario:
        return
    
    st.session_state["chat_history"].append({"role": "user", "content": query_usuario})
    
    resultado = carregar_sistema_ia()
    if resultado is None or resultado[0] is None:
        st.session_state["chat_history"].append({"role": "assistant", "content": resultado[1] if len(resultado) > 1 else "Erro desconhecido ao carregar IA."})
        return
    
    llm, retriever, prompt, _ = resultado
    docs = retriever.invoke(query_usuario)
    contexto_texto = "\n\n".join([doc.page_content for doc in docs])
    
    chat_history = []
    for msg in st.session_state["chat_history"][-6:]:
        if msg["role"] == "user":
            chat_history.append(("human", msg["content"]))
        else:
            chat_history.append(("ai", msg["content"]))
    
    try:
        resposta = llm.invoke(prompt.format_messages(
            context=contexto_texto,
            chat_history=chat_history,
            input=query_usuario
        ))
        st.session_state["chat_history"].append({"role": "assistant", "content": resposta.content})
    except Exception as e:
        st.session_state["chat_history"].append({"role": "assistant", "content": f"Erro na resposta: {str(e)}"})

# ====================== PÁGINAS ======================
if st.session_state["page"] == "home":
    # ... ( teu código original do home )
    c_top1, c_top2, c_top3 = st.columns([2, 1, 0.6])
    with c_top3: st.markdown('<a href="?p=login" target="_self" class="html-custom-btn-vazado">👤 Member Log In</a>', unsafe_allow_html=True)
    st.markdown("<h1>V-Twin Tech Intelligence</h1>", unsafe_allow_html=True)
    if logo_base64: st.markdown(f'<div class="html-home-motor"><img src="data:image/jpeg;base64,{logo_base64}"></div>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Everything about V-Twins, how to maintenance, how to fix it...</p>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("<h2>WHY CHOOSE V-TWIN TECH INTELLIGENCE?</h2>", unsafe_allow_html=True)
    # ... resto do home igual ...

elif st.session_state["page"] == "brain":
    # ... ( teu código de layout do brain )
    c_b1, c_b2, c_b3 = st.columns([2, 1, 0.6])
    with c_b2: st.markdown('<a href="https://billing.stripe.com/p/login/5kQcN4fLk6p8gvZapZdby00" target="_blank" class="html-custom-btn-vazado" style="width:100%;">💳 Cancel Subscription</a>', unsafe_allow_html=True)
    with c_b3: st.markdown('<a href="?p=home" target="_self" class="html-custom-btn-vazado" style="width:100%;">🚪 Log Out</a>', unsafe_allow_html=True)
    
    if logo_base64: st.markdown(f'<div class="html-brain-motor"><img src="data:image/jpeg;base64,{logo_base64}"></div>', unsafe_allow_html=True)
    st.markdown('<p class="red-slogan">Everything about V-Twins, how to maintenance, how to fix it...</p>', unsafe_allow_html=True)
    st.markdown('<div class="status-box-video">📊 Knowledge Base Status: Models up to 2024</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### 💬 Master Tech Workshop Chat:")
    
    for msg in st.session_state["chat_history"]:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-bubble-user"><b>You:</b> {msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-bubble-tech"><b>💀 Master Tech:</b> {msg["content"]}</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.text_input("🔧 Write your message to the Mechanic:", key="campo_texto_input")
    
    if st.button("🚀 Send Message to Master Tech", use_container_width=True):
        enviar_mensagem_chat()
        st.rerun()

# Outras páginas (pricing, login, register) mantidas como estavam