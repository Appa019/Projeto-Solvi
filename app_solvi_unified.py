"""
🌱 Plataforma Solví - Análise Inteligente de Documentos
Versão revisada — layout corrigido e visual institucional idêntico ao site oficial
"""

import streamlit as st
import pandas as pd
import openai
import PyPDF2
import docx
import difflib
import re
import json
import time

# ======================================================
# 🔧 CONFIGURAÇÃO DA PÁGINA
# ======================================================
st.set_page_config(
    page_title="Plataforma Solví - Análise de Documentos",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ======================================================
# 🎨 CSS FINAL - INSTITUCIONAL SOLVÍ
# ======================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    :root {
        --solvi-green-dark: #1c3b28;
        --solvi-green: #236e45;
        --solvi-green-light: #2e8b57;
        --solvi-gray-bg: #f7faf7;
        --solvi-shadow: 0 4px 20px rgba(0,0,0,0.08);
    }

    body, .main, .block-container {
        font-family: 'Inter', sans-serif !important;
        background-color: var(--solvi-gray-bg);
        color: #1d3425;
    }
    #MainMenu, footer, header {visibility: hidden;}

    /* === HEADER === */
    .solvi-header {
        background: linear-gradient(145deg, var(--solvi-green-dark), var(--solvi-green));
        padding: 3rem 2rem;
        border-radius: 16px;
        color: white;
        box-shadow: var(--solvi-shadow);
        margin-bottom: 2rem;
    }
    .solvi-header h1 {
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }
    .solvi-header p {
        font-size: 1.1rem;
        opacity: 0.9;
    }

    /* === NAVEGAÇÃO === */
    .solvi-nav {
        display: flex;
        justify-content: center;
        gap: 1rem;
        margin: 1.5rem 0 2rem;
        flex-wrap: wrap;
    }
    .solvi-nav button {
        border: none;
        padding: 0.8rem 1.5rem;
        border-radius: 8px;
        background: #fff;
        color: var(--solvi-green-dark);
        font-weight: 600;
        box-shadow: var(--solvi-shadow);
        cursor: pointer;
        transition: 0.3s;
    }
    .solvi-nav button:hover {
        background: var(--solvi-green);
        color: white;
    }
    .solvi-nav .active {
        background: var(--solvi-green);
        color: white;
    }

    /* === BLOCO PADRÃO === */
    .solvi-card {
        background: white;
        border-radius: 16px;
        box-shadow: var(--solvi-shadow);
        padding: 2rem;
        margin-bottom: 2rem;
    }
    .solvi-card h2 {
        color: var(--solvi-green-dark);
        font-weight: 700;
    }

    /* === UPLOAD === */
    .solvi-upload {
        border: 2px dashed var(--solvi-green-light);
        border-radius: 12px;
        background: #f9fef9;
        text-align: center;
        padding: 2rem;
        color: var(--solvi-green-dark);
        font-weight: 500;
    }

    /* === MÉTRICAS === */
    .solvi-metrics {
        display: flex;
        justify-content: center;
        flex-wrap: wrap;
        gap: 1.5rem;
        margin-top: 2rem;
    }
    .solvi-metric {
        background: white;
        padding: 1.5rem 2rem;
        border-radius: 12px;
        box-shadow: var(--solvi-shadow);
        text-align: center;
    }
    .solvi-metric h3 {
        color: var(--solvi-green);
        font-size: 2rem;
        margin: 0;
    }
    .solvi-metric p {
        margin: 0;
        color: #444;
    }

    /* === FOOTER === */
    .solvi-footer {
        background: var(--solvi-green-dark);
        color: white;
        text-align: center;
        padding: 2rem;
        border-radius: 16px;
        margin-top: 3rem;
    }
</style>
""", unsafe_allow_html=True)

# ======================================================
# 🧠 CLASSES DE ANÁLISE
# ======================================================
class FREAnalyzer:
    def __init__(self, api_key):
        openai.api_key = api_key
        self.client = openai.OpenAI(api_key=api_key)

    def extract_text_from_pdf(self, file):
        reader = PyPDF2.PdfReader(file)
        return "\n".join([page.extract_text() for page in reader.pages])

    def extract_text_from_docx(self, file):
        doc = docx.Document(file)
        return "\n".join([p.text for p in doc.paragraphs])

    def extract_text(self, file):
        if file.type == "application/pdf":
            return self.extract_text_from_pdf(file)
        elif "word" in file.type:
            return self.extract_text_from_docx(file)
        return ""

    def analyze(self, fre_text, cvm_text):
        prompt = f"""
        Analise o seguinte FRE e compare com as normas CVM.
        Identifique seções não conformes e explique brevemente o motivo.
        Gere um JSON com chaves: "conformidade", "pontos_criticos", "sugestoes".
        FRE: {fre_text[:3000]}
        CVM: {cvm_text[:3000]}
        """
        try:
            resp = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            content = resp.choices[0].message.content
            start, end = content.find("{"), content.rfind("}") + 1
            return json.loads(content[start:end])
        except Exception as e:
            return {"erro": str(e)}

class DocumentComparator:
    def compare(self, text1, text2):
        ratio = difflib.SequenceMatcher(None, text1, text2).ratio()
        return round(ratio * 100, 2)

# ======================================================
# 🧩 INTERFACE
# ======================================================
def render_header():
    st.markdown("""
    <div class="solvi-header">
        <h1>Plataforma Solví</h1>
        <p>🌱 Análise Inteligente de Documentos com IA</p>
    </div>
    """, unsafe_allow_html=True)

def render_navigation():
    st.markdown('<div class="solvi-nav">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 Análise CVM", use_container_width=True):
            st.session_state.current_tab = "cvm"
            st.experimental_rerun()
    with col2:
        if st.button("📚 Comparação de Documentos", use_container_width=True):
            st.session_state.current_tab = "compare"
            st.experimental_rerun()
    st.markdown("</div>", unsafe_allow_html=True)

def render_cvm_tab():
    with st.sidebar:
        st.markdown("### ⚙️ Configurações da Análise")
        api_key = st.text_input("🔑 Chave API OpenAI *", type="password")
        fre_file = st.file_uploader("📄 FRE (PDF ou DOCX)", type=["pdf", "docx"])
        cvm_files = st.file_uploader("📚 Documentos CVM", type=["pdf", "docx"], accept_multiple_files=True)
    if not api_key:
        st.info("Insira sua chave API para iniciar.")
        return
    if not fre_file or not cvm_files:
        st.markdown('<div class="solvi-upload">Envie o FRE e pelo menos um documento CVM.</div>', unsafe_allow_html=True)
        return
    analyzer = FREAnalyzer(api_key)
    if st.button("🔍 Iniciar Análise", use_container_width=True):
        with st.spinner("Analisando..."):
            fre_text = analyzer.extract_text(fre_file)
            cvm_text = "\n".join([analyzer.extract_text(f) for f in cvm_files])
            result = analyzer.analyze(fre_text, cvm_text)
        if "erro" in result:
            st.error(f"Erro: {result['erro']}")
        else:
            st.success("✅ Análise concluída com sucesso!")
            st.json(result)

def render_compare_tab():
    col1, col2 = st.columns(2)
    with col1:
        ref = st.file_uploader("📄 Documento Original", type=["pdf", "docx"])
    with col2:
        novo = st.file_uploader("📄 Documento Novo", type=["pdf", "docx"])
    if not ref or not novo:
        st.markdown('<div class="solvi-upload">Envie dois documentos para comparar.</div>', unsafe_allow_html=True)
        return
    if st.button("🔍 Comparar", use_container_width=True):
        comp = DocumentComparator()
        doc_ref = docx.Document(ref)
        doc_new = docx.Document(novo)
        text_ref = "\n".join([p.text for p in doc_ref.paragraphs])
        text_new = "\n".join([p.text for p in doc_new.paragraphs])
        sim = comp.compare(text_ref, text_new)
        st.markdown(f"""
        <div class="solvi-metrics">
            <div class="solvi-metric"><h3>{sim}%</h3><p>Similaridade entre versões</p></div>
        </div>
        """, unsafe_allow_html=True)

def render_footer():
    st.markdown("""
    <div class="solvi-footer">
        <p>🌱 Plataforma Solví • Soluções Inteligentes para Análise de Documentos</p>
        <p><a href="https://www.solvi.com" target="_blank" style="color:white; text-decoration:none; font-weight:600;">Visite solvi.com</a></p>
    </div>
    """, unsafe_allow_html=True)

# ======================================================
# 🚀 MAIN
# ======================================================
if "current_tab" not in st.session_state:
    st.session_state.current_tab = "cvm"

render_header()
render_navigation()

if st.session_state.current_tab == "cvm":
    render_cvm_tab()
else:
    render_compare_tab()

render_footer()
