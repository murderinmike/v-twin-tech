import streamlit as st
import os
import base64
import fitz  # PyMuPDF para renderizar os diagramas
from PIL import Image
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

# COFRE DE SEGURANÇA ATIVO (.env)
load_dotenv()

# SE ESTIVER NA NUVEM, FORÇA A LEITURA DOS SECRETS
if "OPENAI_API_KEY" in st.secrets:
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

# 1. SETUP DA PÁGINA MESTRE
st.set_page_config(page_title="V-Twin Tech Intelligence", page_icon="💀", layout="wide")

if "page" not in st.session_state: st.session_state["page"] = "home"
if "users_db" not in st.session_state: st.session_state["users_db"] = {"admin@vtwin.com": "harley2024"}

# HISTÓRICO DE CONVERSA COM MEMÓRIA ATIVA
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
        
        p = ChatPromptTemplate.from_messages([
            ("system", "You are a Master V-Twin Motorcycle Mechanic. Answer professionally based on context."),
            ("placeholder", "{chat_history}"),
            ("human", "Context from Manuals: {context}\n\nQuestion: {input}")
        ])
        return llm, retriever, p
    except Exception as e:
        st.error(f"Erro ao carregar IA: {str(e)}")
        return None

# 2. DESIGN VISUAL (CSS mantido igual ao teu)
st.markdown("""
    <style>
    [data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"], [data-testid="stSidebarNav"] { display: none !important; }
    .stApp { background-color: #121212; color: #FFFFFF; }
    h1 { color: #FF6600 !important; text-align: center; font-family: 'Arial Black'; font-size: 50px; text-transform: uppercase; margin-top: 10px; margin-bottom: 5px; }
    h2 { color: #FF6600 !important; text-align: center; font-family: 'Arial Black'; font-size: 30px; text-transform: uppercase; margin-top: 30px; margin-bottom: 20px; }
    .sub-title { color: #FF6600; text-align: center; font-size: 22px; font-weight: bold; margin-top: 10px; margin-bottom: 30px; }
    .red-slogan { color: #FF2222 !important; text-align: center; font-size: 18px; font-weight: bold; font-family: 'Courier New', monospace; margin-top: 15px; margin-bottom: 15px; text-transform: uppercase; }
    .status-box-video { background-color: #1E2511 !important; border: 1px solid #FF6600; padding: 10px; border-radius: 4px; color: #CC9900; font-size: 14px; width: 100%; margin-bottom: 25px; }
    .feature-box { background-color: #262626; padding: 20px; border-radius: 10px; border-left: 5px solid #FF6600; margin-bottom: 20px; min-height: 140px; font-size: 16px; color: #DDDDDD; font-family: sans-serif; }
    .feature-title { color: #FF6600; font-weight: bold; font-size: 18px; text-transform: uppercase; display: block; margin-bottom: 8px; }
    
    .pricing-card { background-color: #262626; padding: 35px 25px 20px 25px; border-radius: 15px; text-align: center; border: 1px solid #333333; margin-bottom: 10px; min-height: 280px; }
    .pricing-card h3 { color: #FF6600 !important; font-family: 'Arial Black'; font-size: 24px; text-transform: uppercase; margin-bottom: 10px; }
    .pricing-card h2 { font-size: 42px !important; margin-top: 10px; margin-bottom: 10px; color: #FFFFFF !important; }
    .pricing-card p { color: #CCCCCC !important; font-size: 15px; line-height: 1.6; margin-bottom: 10px; font-family: sans-serif; }
    .promo-text { text-align: center !important; font-family: 'Arial Black'; font-size: 32px; color: #FF6600 !important; margin-top: 40px; margin-bottom: 25px; text-transform: uppercase; }
    
    .chat-bubble-user { background-color: #262626 !important; border-right: 4px solid #FF6600 !important; padding: 12px; border-radius: 8px; margin-bottom: 10px; text-align: right; margin-left: 20%; color: #FFFFFF; font-family: sans-serif; }
    .chat-bubble-tech { background-color: #1E1E1E !important; border-left: 4px solid #FF6600 !important; padding: 15px; border-radius: 8px; margin-bottom: 15px; text-align: left; margin-right: 20%; color: #EEEEEE; font-family: sans-serif; line-height: 1.5; }
    
    div[data-testid="stTextInputRootElement"], .stTextInput>div { background-color: #121212 !important; border: 1px solid #666666 !important; border-radius: 8px !important; }
    .stTextInput input { background-color: #121212 !important; color: white !important; border: none !important; }
    </style>
    """, unsafe_allow_html=True)

query_params = st.query_params
if "p" in query_params: st.session_state["page"] = query_params["p"]

# ====================== FUNÇÃO DA IA ======================
def enviar_mensagem_chat(query_usuario):
    if not query_usuario.strip():
        return None
    
    st.session_state["chat_history"].append({"role": "user", "content": query_usuario})
    
    sistema_ia = carregar_sistema_ia()
    if sistema_ia is None:
        return "Erro: Sistema IA não carregado. Verifique a pasta faiss_harley_global e a chave OPENAI_API_KEY."
    
    llm, retriever, p = sistema_ia
    docs = retriever.invoke(query_usuario)
    contexto_texto = "\n".join([doc.page_content for doc in docs])
    
    chat_history = []
    for msg in st.session_state["chat_history"][-6:]:
        if msg["role"] == "user":
            chat_history.append(("human", msg["content"]))
        else:
            chat_history.append(("ai", msg["content"]))
    
    try:
        resposta = llm.invoke(p.format_messages(
            context=contexto_texto,
            chat_history=chat_history,
            input=query_usuario
        ))
        st.session_state["chat_history"].append({"role": "assistant", "content": resposta.content})
        return resposta.content
    except Exception as e:
        return f"Erro ao gerar resposta: {str(e)}"

# ==========================================
# RENDERIZAÇÃO DOS ECRÃS MESTRE
# ==========================================
if st.session_state["page"] == "home":
    # ... teu código do home (mantido igual) ...
    c_top1, c_top2, c_top3 = st.columns([2, 1, 0.6])
    with c_top3: st.markdown('<a href="?p=login" target="_self" class="html-custom-btn-vazado">👤 Member Log In</a>', unsafe_allow_html=True)
    st.markdown("<h1>V-Twin Tech Intelligence</h1>", unsafe_allow_html=True)
    if logo_base64: st.markdown(f'<div class="html-home-motor"><img src="data:image/jpeg;base64,{logo_base64}"></div>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Everything about V-Twins, how to maintenance, how to fix it...</p>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("<h2>WHY CHOOSE V-TWIN TECH INTELLIGENCE?</h2>", unsafe_allow_html=True)
    col_row1_left, col_row1_right = st.columns([1, 1])
    with col_row1_left: st.markdown('<div class="feature-box"><span class="feature-title">⚡ Instant Precision</span>Find torque specs, clearances, and data in seconds. Support up to 2024.</div>', unsafe_allow_html=True)
    with col_row1_right: st.markdown('<div class="feature-box"><span class="feature-title">🛠️ Interactive Step-by-Step Chat</span>Our model is an advanced conversational assistant. Talk to the mechanic step-by-step.</div>', unsafe_allow_html=True)
    col_row2_left, col_row2_right = st.columns([1, 1])
    with col_row2_left: st.markdown('<div class="feature-box"><span class="feature-title">🔍 Advanced Diagnostics</span>Identify faults and error codes with our specialized AI.</div>', unsafe_allow_html=True)
    with col_row2_right: st.markdown('<div class="feature-box"><span class="feature-title">🔊 Hands-Free Voice Expert</span>Talk to the "Master Tech" while your hands are on the tools.</div>', unsafe_allow_html=True)
    st.markdown('<p class="promo-text">Get unlimited access to the entire database up to 2024</p>', unsafe_allow_html=True)
    
    col_v1, col_v2, col_v3 = st.columns([0.5, 2, 0.5])
    with col_v2:
     if os.path.exists("demo_video.mp4"):
        with open("demo_video.mp4", "rb") as v_file:
            st.video(v_file.read(), format="video/mp4")

    st.markdown("""<div class="main-btn-container"><a href="?p=pricing" target="_self" class="html-giant-btn">BUY INSTANT ACCESS — CHECK PRICING</a></div>""", unsafe_allow_html=True)
    st.markdown("""<div class="footer-contact-box"><a href="mailto:support@vtwintechai.com" class="footer-contact-link">📩 Need Help? Contact Us: support@vtwintechai.com</a></div>""", unsafe_allow_html=True)

# ... (pricing, login, register mantidos) ...

elif st.session_state["page"] == "brain":
    c_b1, c_b2, c_b3 = st.columns([2, 1, 0.6])
    with c_b2: st.markdown('<a href="https://billing.stripe.com/p/login/5kQcN4fLk6p8gvZapZdby00" target="_blank" class="html-custom-btn-vazado" style="width:100%;">💳 Cancel Subscription</a>', unsafe_allow_html=True)
    with c_b3: st.markdown('<a href="?p=home" target="_self" class="html-custom-btn-vazado" style="width:100%;">🚪 Log Out</a>', unsafe_allow_html=True)
    if logo_base64: st.markdown(f'<div class="html-brain-motor"><img src="data:image/jpeg;base64,{logo_base64}"></div>', unsafe_allow_html=True)
    st.markdown('<p class="red-slogan">Everything about V-Twins, how to maintenance, how to fix it...</p>', unsafe_allow_html=True)
    st.markdown('<div class="status-box-video">📊 Knowledge Base Status: Models up to 2024</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### 💬 Master Tech Workshop Chat:")
    
    for msg in st.session_state["chat_history"]:
        if msg["role"] == "user": st.markdown(f'<div class="chat-bubble-user"><b>You:</b> {msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-bubble-tech"><b>💀 Master Tech:</b> {msg["content"]}</div>', unsafe_allow_html=True)
            if "images" in msg:
                for img_bytes, ref_title in msg["images"]: st.markdown(f"**{ref_title}**"); st.image(img_bytes, use_container_width=True)
    st.markdown("---")
    
    if query_usuario := st.chat_input("Write your message to the Mechanic..."):
        with st.chat_message("user"):
            st.markdown(query_usuario)
        
        with st.chat_message("assistant"):
            with st.spinner("A consultar os manuais..."):
                resposta = enviar_mensagem_chat(query_usuario)
                if resposta:
                    st.markdown(resposta)
                else:
                    st.error("Não foi possível obter resposta.")