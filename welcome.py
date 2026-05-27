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
        p = ChatPromptTemplate.from_template("""You are a Master V-Twin Motorcycle Mechanic. 
        You have access to the conversation history to understand context.
        Context from Manuals: {context}
        Chat History: {chat_history}
        User Question: {input}
        Answer professionally based on the context and history:""")
        return llm, retriever, p
    except: return None
# 2. DESIGN VISUAL INDESTRUTÍVEL (CSS TOTALMENTE ISOLADO COM SUPORTE A BOTÕES NATIVOS)
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
    
    .stTextInput > div > div > input { background-color: #121212 !important; color: white !important; border: 1px solid #666666 !important; height: 48px !important; }
    
    .html-custom-btn-solid { background-color: #FF6600 !important; color: #FFFFFF !important; font-size: 16px !important; font-family: 'Arial Black', sans-serif !important; font-weight: bold !important; height: 48px; width: 100%; border-radius: 8px; border: none; text-transform: uppercase; display: flex; justify-content: center; align-items: center; text-decoration: none; cursor: pointer; box-shadow: 0px 4px 10px rgba(0,0,0,0.3); transition: 0.2s; margin-top: 15px; }
    .html-custom-btn-solid:hover { background-color: #E05300 !important; color: #FFFFFF !important; }
    
    .html-custom-btn-vazado { background-color: transparent !important; color: #FF6600 !important; font-size: 14px !important; font-family: 'Arial Black', sans-serif !important; font-weight: bold !important; height: 42px; width: 180px; border-radius: 6px; border: 2px solid #FF6600; text-transform: uppercase; display: flex; justify-content: center; align-items: center; text-decoration: none; cursor: pointer; transition: 0.2s; }
    .html-custom-btn-vazado:hover { background-color: #FF6600 !important; color: #121212 !important; }
    
    /* MODIFICAÇÃO DO BOTÃO LINK NATIVO DO STREAMLIT PARA CORES DA HARLEY */
    .stLinkButton>a { background-color: #FF6600 !important; color: #FFFFFF !important; font-size: 16px !important; font-family: 'Arial Black', sans-serif !important; font-weight: bold !important; height: 50px !important; width: 100% !important; border-radius: 8px !important; border: none !important; text-transform: uppercase !important; display: flex !important; justify-content: center !important; align-items: center !important; text-decoration: none !important; box-shadow: 0px 4px 10px rgba(0,0,0,0.3) !important; transition: 0.2s !important; }
    .stLinkButton>a:hover { background-color: #E05300 !important; color: #FFFFFF !important; text-decoration: none !important; }
    
    .footer-contact-box { text-align: center !important; margin-top: 50px; margin-bottom: 30px; padding: 20px; border-top: 1px solid #222; width: 100%; }
    .footer-contact-link { color: #FF6600 !important; font-family: 'Arial Black', sans-serif !important; font-size: 16px !important; font-weight: bold !important; text-transform: uppercase !important; text-decoration: none !important; }
    
    .video-container-html5 { display: flex; justify-content: center; align-items: center; width: 100%; margin-top: 10px; margin-bottom: 25px; }
    .video-container-html5 video { width: 100% !important; max-width: 800px; height: 450px; border-radius: 12px; border: 2px solid #FF6600; box-shadow: 0px 4px 15px rgba(0,0,0,0.5) !important; background-color: #000000 !important; }
    
    [data-testid="stForm"] { border: none !important; padding: 0 !important; background: transparent !important; }
    .main-btn-container { display: flex; justify-content: center; align-items: center; width: 100%; margin-top: 20px; margin-bottom: 60px; }
    .html-giant-btn { background-color: #FF6600 !important; color: #FFFFFF !important; font-size: 30px !important; font-family: 'Arial Black', sans-serif !important; font-weight: bold !important; height: 85px !important; width: 65% !important; border-radius: 15px !important; text-transform: uppercase !important; letter-spacing: 2px !important; display: flex !important; justify-content: center !important; align-items: center !important; text-decoration: none !important; box-shadow: 0px 0px 25px rgba(255, 102, 0, 0.6) !important; transition: 0.3s; }
    .html-giant-btn:hover { background-color: #E05300 !important; color: #FFFFFF !important; }
    .html-home-motor { display: flex; justify-content: center; align-items: center; width: 100%; margin-top: 15px; margin-bottom: 15px; }
    .html-home-motor img { width: 340px !important; height: auto !important; border-radius: 12px; border: none !important; }
    .html-brain-motor { display: flex; justify-content: center; align-items: center; width: 100%; margin-top: 10px; margin-bottom: 15px; }
    .html-brain-motor img { width: 260px !important; height: auto !important; border-radius: 6px; border: none !important; }
    </style>
    """, unsafe_allow_html=True)
query_params = st.query_params
if "p" in query_params: st.session_state["page"] = query_params["p"]

def enviar_mensagem_chat():
    query_usuario = st.session_state.get("campo_texto_input", "").strip()
    if query_usuario:
        st.session_state["chat_history"].append({"role": "user", "content": query_usuario})
        sistema_ia = carregar_sistema_ia()
        if sistema_ia is not None:
            llm, retriever, p = sistema_ia
            docs = retriever.invoke(query_usuario)
            contexto_texto = "\\n".join([doc.page_content for doc in docs])
            historico_texto = "\\n".join([f"{m['role']}: {m['content']}" for m in st.session_state["chat_history"][-5:]])
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

# ==========================================
# RENDERIZAÇÃO DOS ECRÃS MESTRE
# ==========================================
if st.session_state["page"] == "home":
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
        st.markdown("""
            <div class="video-container-html5">
                <video controls preload="metadata">
                    <source src="https://githubusercontent.com" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
            </div>
            """, unsafe_allow_html=True)
        
    st.markdown("""<div class="main-btn-container"><a href="?p=pricing" target="_self" class="html-giant-btn">BUY INSTANT ACCESS — CHECK PRICING</a></div>""", unsafe_allow_html=True)
    st.markdown("""<div class="footer-contact-box"><a href="mailto:support@vtwintechai.com" class="footer-contact-link">📩 Need Help? Contact Us: support@vtwintechai.com</a></div>""", unsafe_allow_html=True)

elif st.session_state["page"] == "pricing":
    st.markdown('<a href="?p=home" target="_self" class="html-custom-btn-vazado" style="width:160px;">← Back to Home</a>', unsafe_allow_html=True)
    st.markdown("<h1>Choose Your Access Plan</h1>", unsafe_allow_html=True)
    col1, space, col2 = st.columns([2, 0.5, 2])
    
    # 🚨 SOLUÇÃO REAL INBALIZÁVEL: BLOCOS VISUAIS ORIGINAIS COM INJEÇÃO DE BOTÃO NATIVO DO STREAMLIT QUE QUEBRA O BLOQUEIO CSP 🚨
    with col1: 
        st.markdown('<div class="pricing-card"><h3>💡 Monthly Pass</h3><h2>$19.99</h2><p>Full Access to all wiring diagrams, diagnostics and torque specifications. Up to date model coverage. Cancel anytime with a single click.</p></div>', unsafe_allow_html=True)
        st.link_button("Subscribe Monthly", "https://stripe.com", use_container_width=True)
    with col2: 
        st.markdown('<div class="pricing-card" style="border:2px solid #FF6600;"><h3>⚡ Annual Pro</h3><h2>$199</h2><p>Save $40 with the annual membership. Continuous full workshop database unlock, structural step-by-step repair logs and master tech priority helper tools.</p></div>', unsafe_allow_html=True)
        st.link_button("Subscribe Annually", "https://stripe.com", use_container_width=True)

elif st.session_state["page"] == "login":
    st.markdown('<a href="?p=home" target="_self" class="html-custom-btn-vazado" style="width:160px;">← Back to Home</a>', unsafe_allow_html=True)
    st.markdown("<h1>Secure Member Portal</h1>", unsafe_allow_html=True)
    cl1, cl2, cl3 = st.columns([1, 1.5, 1])
    with cl2:
        u_email = st.text_input("Email Address", key="login_usr")
        u_pass = st.text_input("Password", type="password", key="login_pwd")
        st.markdown("<br>", unsafe_allow_html=True)
        if u_email and u_pass:
            if u_email in st.session_state["users_db"] and st.session_state["users_db"][u_email] == u_pass:
                st.markdown('<a href="?p=brain" target="_self" class="html-custom-btn-solid">ACCESS DASHBOARD (CONFIRMED)</a>', unsafe_allow_html=True)
            else: st.markdown('<div class="html-custom-btn-solid" style="background-color:#444!important; cursor:not-allowed;">Enter Valid Credentials</div>', unsafe_allow_html=True)
        else: st.markdown('<a href="?p=brain" target="_self" class="html-custom-btn-solid">ACCESS DASHBOARD</a>', unsafe_allow_html=True)

elif st.session_state["page"] == "register":
    st.markdown('<a href="?p=home" target="_self" class="html-custom-btn-vazado" style="width:160px;">← Back to Home</a>', unsafe_allow_html=True)
    st.markdown("<h1>💳 Setup Your Premium Account</h1>", unsafe_allow_html=True)
    cl1, cl2, cl3 = st.columns([1, 1.5, 1])
    with cl2:
        n_email = st.text_input("Enter Your Account Email", key="reg_usr")
        n_pass = st.text_input("Create Secret Password", type="password", key="reg_pwd")
        st.markdown("<br>", unsafe_allow_html=True)
        if n_email and n_pass:
            st.session_state["users_db"][n_email] = n_pass
            st.markdown('<a href="?p=login" target="_self" class="html-custom-btn-solid">ACTIVATE PREMIUM ACCESS (CONFIRMED)</a>', unsafe_allow_html=True)
        else: st.markdown('<a href="?p=login" target="_self" class="html-custom-btn-solid">ACTIVATE PREMIUM ACCESS</a>', unsafe_allow_html=True)

elif st.session_state["page"] == "brain":
    c_b1, c_b2, c_b3 = st.columns([2, 1, 0.6])
    with c_b2: st.markdown('<a href="?p=pricing" target="_self" class="html-custom-btn-vazado" style="width:100%;">💳 Cancel Subscription</a>', unsafe_allow_html=True)
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
    
    with st.form("form_chat_limpo", clear_on_submit=True):
        st.text_input("🔧 Write your message to the Mechanic:", key="campo_texto_input")
        if st.form_submit_button("Send Message"):
            enviar_mensagem_chat()
            st.rerun()
