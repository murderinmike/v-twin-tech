import streamlit as st
import os
from openai import OpenAI
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
import io
import fitz
from PIL import Image
from streamlit_mic_recorder import mic_recorder

# 1. FUNÇÃO DE LOGIN
def check_password():
    """Retorna True se o utilizador introduziu a password correta."""
    def password_entered():
        if st.session_state["password"] == "harley2024": # <--- MUDA A TUA PASS AQUI
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # remove a password do estado por segurança
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # Primeiro acesso: mostra o campo de password
        st.title("🔐 V-Twin Tech Access")
        st.text_input("Enter Access Code:", type="password", on_change=password_entered, key="password")
        st.warning("Authorized Personnel Only.")
        return False
    elif not st.session_state["password_correct"]:
        # Password errada
        st.title("🔐 V-Twin Tech Access")
        st.text_input("Enter Access Code:", type="password", on_change=password_entered, key="password")
        st.error("❌ Invalid Code. Access Denied.")
        return False
    else:
        # Password correta
        return True

# SÓ MOSTRA O SITE SE A PASSWORD ESTIVER CORRETA
if check_password():

    # 2. SETUP E ESTILO (O que já tínhamos)
    st.set_page_config(page_title="V-Twin Tech Intelligence", page_icon="💀")

    st.markdown("""
        <style>
        .stApp { background-color: #121212; color: #FFFFFF; }
        input { color: #FFFFFF !important; -webkit-text-fill-color: #FFFFFF !important; }
        .stTextInput>div>div>input { background-color: #262626 !important; border: 2px solid #FF6600 !important; color: white !important; }
        .stAlert { background-color: #262626; border: 1px solid #FF6600; color: white; }
        button { border: 1px solid #FF6600 !important; color: #FF6600 !important; }
        </style>
        """, unsafe_allow_html=True)

    # 3. CHAVE API
    api_key = "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" 
    os.environ["OPENAI_API_KEY"] = api_key
    client = OpenAI(api_key=api_key)

    # --- TOPO ---
    st.markdown('<h1 style="color: #FF6600; text-align: center; font-family: Arial Black; font-size: 45px; text-transform: uppercase; line-height: 0.9;">V-TWIN TECH<br>INTELLIGENCE</h1>', unsafe_allow_html=True)

    if os.path.exists("logo.jpg") or os.path.exists("logo.png"):
        img_p = "logo.jpg" if os.path.exists("logo.jpg") else "logo.png"
        col1, col2, col3 = st.columns(3)
        with col2: st.image(Image.open(img_p), use_container_width=True)

    st.markdown('<p style="color: #FF6600; text-align: center; font-family: Courier; font-weight: bold; font-size: 18px;">Everything about V-Twins, how to maintenance, how to fix it...</p>', unsafe_allow_html=True)
    st.warning("📊 Knowledge Base Status: Models up to 2018")
    st.markdown("---")

    # 4. LÓGICA DO SISTEMA
    @st.cache_resource
    def carregar_cerebro():
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        return FAISS.load_local("faiss_harley_global", embeddings, allow_dangerous_deserialization=True)

    try:
        db = carregar_cerebro()
        llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)
        
        st.write("### Ask the Master Mechanic:")
        
        # Interface de Voz e Texto
        audio_data = mic_recorder(start_prompt="🎤 Click to Talk", stop_prompt="🛑 Stop", key='recorder')
        texto_escrito = st.text_input("OR TYPE HERE:", placeholder="e.g. 2018 Softail wheel torque")

        pergunta = ""

        if audio_data and 'bytes' in audio_data:
            with st.spinner("The Expert is listening..."):
                audio_bio = io.BytesIO(audio_data['bytes'])
                audio_bio.name = "audio.wav"
                trans = client.audio.transcriptions.create(model="whisper-1", file=audio_bio)
                pergunta = trans.text
                st.info(f"You said: '{pergunta}'")

        if texto_escrito:
            pergunta = texto_escrito

        if pergunta:
            with st.spinner("Analyzing manuals..."):
                docs = db.similarity_search(pergunta, k=3)
                ctx = "\n\n".join([d.page_content for d in docs])
                prompt = f"Master Mechanic. User language. Context: {ctx}"
                res = llm.invoke([("system", prompt), ("user", pergunta)]).content
                
                st.subheader("💡 TECHNICAL ADVICE:")
                st.markdown(f'<div style="background-color:#262626; padding:20px; border-radius:10px; border-left: 5px solid #FF6600;">{res}</div>', unsafe_allow_html=True)
                
                audio_out = client.audio.speech.create(model="tts-1", voice="onyx", input=res)
                st.audio(audio_out.content, format='audio/mp3')

                st.markdown("---")
                for d in docs:
                    path = d.metadata.get('source')
                    pag = d.metadata.get('page')
                    with st.expander(f"View Technical Page {pag + 1}"):
                        doc_pdf = fitz.open(path)
                        st.image(Image.open(io.BytesIO(doc_pdf.load_page(pag).get_pixmap(matrix=fitz.Matrix(2, 2)).tobytes("png"))))

    except Exception as e:
        st.error(f"Error: {e}")
