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
        db = FAISS.load_local("faiss_harley_global", embeddings, allow_dangerous_deserialization=True)
        retriever = db.as_retriever(search_kwargs={"k": 3})
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
        p = ChatPromptTemplate.from_template("""You are a Master V-Twin Motorcycle Mechanic. 
        You have access to the conversation history to understand context.
        Context from Manuals: {context}
        Chat History: {chat_history}
        User Question: {input}
        Answer professionally based on the context and history:""")
        return llm, retriever, p
    except: return None

# ====================== CSS AJUSTADO ======================
st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none !important; }
    
    /* Fundo escuro + Remover barra branca */
    .stApp, .main, .block-container, section[data-testid="stMain"] {
        background-color: #121212 !important;
    }
    div[data-testid="stVerticalBlock"] > div > div > div:last-child,
    .stApp > div > div > div > div:last-child {
        background-color: #121212 !important;
    }
    .element-container, .stMarkdown {
        background-color: transparent !important;
    }

    /* Centralização do Logo */
    .html-home-motor {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
        margin: 20px 0;
    }
    .html-home-motor img {
        width: 340px;
        height: auto;
        border-radius: 12px;
    }

    /* Centralização do Botão Grande */
    .main-btn-container {
        display: flex;
        justify-content: center;
        width: 100%;
        margin: 40px 0 60px 0;
    }

    .html-giant-btn {
        background-color: #FF6600 !important;
        color: #FFFFFF !important;
        font-size: 28px !important;
        font-weight: bold !important;
        height: 85px !important;
        width: 70% !important;
        max-width: 850px !important;
        border-radius: 15px !important;
        text-transform: uppercase;
        display: flex;
        justify-content: center;
        align-items: center;
        text-decoration: none;
        box-shadow: 0 4px 15px rgba(255, 102, 0, 0.5);
    }

    h1, h2 { text-align: center !important; }
    .sub-title, .promo-text { text-align: center !important; }

    </style>
    """, unsafe_allow_html=True)

# ====================== FUNÇÃO DO CHAT ======================
def enviar_mensagem_chat():
    query_usuario = st.session_state.get("campo_texto_input", "").strip()
    if query_usuario:
        st.session_state["chat_history"].append({"role": "user", "content": query_usuario})
        sistema_ia = carregar_sistema_ia()
        if sistema_ia is not None:
            llm, retriever, p = sistema_ia
            docs = retriever.invoke(query_usuario)
            contexto_texto = "\n".join([doc.page_content for doc in docs])
            historico_texto = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state["chat_history"][-5:]])
            resposta = llm.invoke(p.format(context=contexto_texto, chat_history=historico_texto, input=query_usuario))
            
            imagens_geradas = []
            for doc in docs:
                caminho_pdf = doc.metadata.get("source", "")
                num_pagina = doc.metadata.get("page", 0)
                if caminho_pdf and os.path.exists(caminho_pdf):
                    try:
                        doc_fitz = fitz.open(caminho_pdf)
                        pagina = doc_fitz.load_page(num_pagina)
                        pix = pagina.get_pixmap(matrix=fitz.Matrix(2, 2))
                        imagens_geradas.append((pix.tobytes("png"), f"📍 Reference: {os.path.basename(caminho_pdf)} (Page {num_pagina + 1})"))
                        doc_fitz.close()
                    except: pass
            st.session_state["chat_history"].append({"role": "assistant", "content": resposta.content, "images": imagens_geradas})

# ====================== NAVEGAÇÃO ======================
query_params = st.query_params
if "p" in query_params: st.session_state["page"] = query_params["p"]

# ====================== HOME PAGE ======================
if st.session_state["page"] == "home":
    c_top1, c_top2, c_top3 = st.columns([2, 1, 0.6])
    with c_top3: 
        st.markdown('<a href="?p=login" target="_self" class="html-custom-btn-vazado">👤 Member Log In</a>', unsafe_allow_html=True)
    
    st.markdown("<h1>V-Twin Tech Intelligence</h1>", unsafe_allow_html=True)
    
    if logo_base64: 
        st.markdown(f'<div class="html-home-motor"><img src="data:image/jpeg;base64,{logo_base64}"></div>', unsafe_allow_html=True)
    
    st.markdown('<p class="sub-title">Everything about V-Twins, how to maintenance, how to fix it...</p>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("<h2>WHY CHOOSE V-TWIN TECH INTELLIGENCE?</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="feature-box"><span class="feature-title">⚡ Instant Precision</span>Find torque specs, clearances, and data in seconds. Support up to 2024.</div>', unsafe_allow_html=True)
        st.markdown('<div class="feature-box"><span class="feature-title">🔍 Advanced Diagnostics</span>Identify faults and error codes with our specialized AI.</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="feature-box"><span class="feature-title">🛠️ Interactive Step-by-Step Chat</span>Our model is an advanced conversational assistant. Talk to the mechanic step-by-step.</div>', unsafe_allow_html=True)
        st.markdown('<div class="feature-box"><span class="feature-title">🔊 Hands-Free Voice Expert</span>Talk to the "Master Tech" while your hands are on the tools.</div>', unsafe_allow_html=True)
    
    st.markdown('<p class="promo-text">Get unlimited access to the entire database up to 2024</p>', unsafe_allow_html=True)
    
    # Vídeo
    col_v1, col_v2, col_v3 = st.columns([0.5, 2, 0.5])
    with col_v2:
        if os.path.exists("demo_video.mp4"):
            with open("demo_video.mp4", "rb") as v_file:
                st.video(v_file.read(), format="video/mp4")
    
    # Botão Grande
    st.markdown("""<div class="main-btn-container">
        <a href="?p=pricing" target="_self" class="html-giant-btn">BUY INSTANT ACCESS — CHECK PRICING</a>
    </div>""", unsafe_allow_html=True)
    
    st.markdown("""<div class="footer-contact-box">
        <a href="mailto:support@vtwintechai.com" class="footer-contact-link">📩 Need Help? Contact Us: support@vtwintechai.com</a>
    </div>""", unsafe_allow_html=True)

# ====================== OUTRAS PÁGINAS ======================
elif st.session_state["page"] == "pricing":
    st.markdown('<a href="?p=home" target="_self" class="html-custom-btn-vazado" style="width:160px;">← Back to Home</a>', unsafe_allow_html=True)
    st.markdown("<h1>Choose Your Access Plan</h1>", unsafe_allow_html=True)
    # ... (resto do pricing igual ao teu original)

elif st.session_state["page"] == "login":
    # ... (mantém o teu código de login)

elif st.session_state["page"] == "brain":
    # ... (mantém o teu código do chat)
