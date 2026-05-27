import streamlit as st
import os
import base64
import fitz
from PIL import Image
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
        Context from Manuals: {context}
        Chat History: {chat_history}
        User Question: {input}
        Answer professionally based on the context and history:""")
        return llm, retriever, p
    except: 
        return None

# ====================== CSS MELHORADO ======================
st.markdown("""
    <style>
    [data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"], [data-testid="stSidebarNav"] { display: none !important; }
    
    /* Remove fundo branco do Streamlit */
    .stApp, .main, .block-container, section[data-testid="stMain"] {
        background-color: #121212 !important;
    }
    
    .stApp > header, .stApp > footer { display: none !important; }
    
    h1, h2, h3 { color: #FF6600 !important; }
    
    /* Remove barras brancas */
    div[data-testid="stVerticalBlock"] > div > div > div {
        background-color: transparent !important;
    }
    
    .stTextInput input, .stTextInput > div {
        background-color: #1E1E1E !important;
        color: white !important;
        border: 1px solid #444 !important;
    }
    
    .footer-contact-box { 
        text-align: center; 
        margin-top: 50px; 
        padding: 20px; 
        border-top: 1px solid #222; 
    }
    
    .chat-bubble-user { 
        background-color: #262626 !important; 
        border-right: 4px solid #FF6600 !important; 
        padding: 12px 15px; 
        border-radius: 8px; 
        margin: 8px 0; 
        text-align: right; 
        margin-left: 20%; 
    }
    .chat-bubble-tech { 
        background-color: #1E1E1E !important; 
        border-left: 4px solid #FF6600 !important; 
        padding: 12px 15px; 
        border-radius: 8px; 
        margin: 8px 0; 
        text-align: left; 
        margin-right: 20%; 
    }
    
    .html-giant-btn, .html-custom-btn-solid {
        background-color: #FF6600 !important;
        color: white !important;
        font-weight: bold !important;
        text-transform: uppercase;
    }
    </style>
    """, unsafe_allow_html=True)

# ====================== FUNÇÃO DO CHAT ======================
def enviar_mensagem_chat():
    query = st.session_state.get("campo_texto_input", "").strip()
    if not query:
        return
    
    st.session_state["chat_history"].append({"role": "user", "content": query})
    
    sistema_ia = carregar_sistema_ia()
    if sistema_ia:
        llm, retriever, prompt = sistema_ia
        docs = retriever.invoke(query)
        contexto = "\n".join([doc.page_content for doc in docs])
        historico = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state["chat_history"][-6:]])
        
        resposta = llm.invoke(prompt.format(context=contexto, chat_history=historico, input=query))
        
        st.session_state["chat_history"].append({
            "role": "assistant", 
            "content": resposta.content
        })
    else:
        st.session_state["chat_history"].append({
            "role": "assistant", 
            "content": "Erro ao carregar o modelo de IA."
        })

# ====================== PÁGINAS ======================
query_params = st.query_params
if "p" in query_params: 
    st.session_state["page"] = query_params["p"]

if st.session_state["page"] == "home":
    c_top1, c_top2, c_top3 = st.columns([2, 1, 0.6])
    with c_top3: 
        st.markdown('<a href="?p=login" class="html-custom-btn-vazado">👤 Member Log In</a>', unsafe_allow_html=True)
    
    st.markdown("<h1>V-Twin Tech Intelligence</h1>", unsafe_allow_html=True)
    if logo_base64: 
        st.markdown(f'<div class="html-home-motor"><img src="data:image/jpeg;base64,{logo_base64}"></div>', unsafe_allow_html=True)
    
    st.markdown('<p class="sub-title">Everything about V-Twins, how to maintenance, how to fix it...</p>', unsafe_allow_html=True)
    
    # ... (resto do home igual, só mantendo o footer melhorado)
    st.markdown("""<div class="footer-contact-box">
        <a href="mailto:support@vtwintechai.com" style="color:#FF6600; font-weight:bold; text-decoration:underline;">
            📩 Need Help? Contact Us: support@vtwintechai.com
        </a>
    </div>""", unsafe_allow_html=True)

elif st.session_state["page"] == "login":
    st.markdown('<a href="?p=home" class="html-custom-btn-vazado" style="width:160px;">← Back to Home</a>', unsafe_allow_html=True)
    st.markdown("<h1>Secure Member Portal</h1>", unsafe_allow_html=True)
    
    cl1, cl2, cl3 = st.columns([1, 1.5, 1])
    with cl2:
        u_email = st.text_input("Email Address", key="login_usr")
        u_pass = st.text_input("Password", type="password", key="login_pwd")
        
        if st.button("ACCESS DASHBOARD", use_container_width=True):
            if u_email in st.session_state["users_db"] and st.session_state["users_db"][u_email] == u_pass:
                st.session_state["page"] = "brain"
                st.rerun()
            else:
                st.error("Credenciais inválidas")

elif st.session_state["page"] == "brain":
    c_b1, c_b2, c_b3 = st.columns([2, 1, 0.6])
    with c_b2: 
        st.markdown('<a href="https://billing.stripe.com/..." class="html-custom-btn-vazado">💳 Cancel Subscription</a>', unsafe_allow_html=True)
    with c_b3: 
        st.markdown('<a href="?p=home" class="html-custom-btn-vazado">🚪 Log Out</a>', unsafe_allow_html=True)
    
    if logo_base64: 
        st.markdown(f'<div class="html-brain-motor"><img src="data:image/jpeg;base64,{logo_base64}"></div>', unsafe_allow_html=True)
    
    st.markdown('<p class="red-slogan">Everything about V-Twins, how to maintenance, how to fix it...</p>', unsafe_allow_html=True)
    st.markdown('<div class="status-box-video">📊 Knowledge Base Status: Models up to 2024</div>', unsafe_allow_html=True)
    
    st.markdown("### 💬 Master Tech Workshop Chat:")
    
    for msg in st.session_state["chat_history"]:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-bubble-user"><b>You:</b> {msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-bubble-tech"><b>💀 Master Tech:</b> {msg["content"]}</div>', unsafe_allow_html=True)
    
    st.text_input("🔧 Write your message to the Mechanic:", key="campo_texto_input")
    
    if st.button("🚀 Send Message to Master Tech", use_container_width=True, type="primary"):
        enviar_mensagem_chat()
        st.rerun()

# Outras páginas (pricing, register) podem ficar iguais