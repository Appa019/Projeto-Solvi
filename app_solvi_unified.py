"""
🌱 Plataforma Solví - Análise Inteligente de Documentos
Versão Profissional • Design institucional + funcionalidades completas
"""

import streamlit as st
import pandas as pd
import openai
import PyPDF2
import docx
import fitz
import tempfile
import os
import json
import time
import re
from pathlib import Path
from datetime import datetime
import difflib


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
# 🎨 CSS PROFISSIONAL - ESTILO INSTITUCIONAL SOLVÍ
# ======================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    :root {
        --solvi-dark: #0b3d1a;
        --solvi-primary: #194D33;
        --solvi-medium: #236E45;
        --solvi-light: #2E8B57;
        --solvi-accent: #4CAF50;
        --solvi-bg: #f7faf7;
        --solvi-surface: #ffffff;
        --solvi-text-dark: #143b24;
        --solvi-shadow: rgba(0,0,0,0.1);
    }

    body, .main, .block-container {
        font-family: 'Inter', sans-serif !important;
        background-color: var(--solvi-bg);
        color: var(--solvi-text-dark);
    }

    #MainMenu, footer, header {visibility: hidden;}
    .main .block-container {padding-top: 1.5rem; max-width: 1400px;}

    .solvi-header {
        background: linear-gradient(165deg, rgba(25,77,51,0.96) 0%, rgba(46,125,50,0.93) 100%);
        color: white;
        padding: 4.5rem 3rem;
        border-radius: 0;
        margin: -2rem -2rem 2rem -2rem;
        box-shadow: 0 10px 40px var(--solvi-shadow);
        position: relative;
        overflow: hidden;
        width: 100vw;
        margin-left: calc(-50vw + 50%);
    }
    .solvi-header::before {
        content: '';
        position: absolute;
        inset: 0;
        background: url('https://images.unsplash.com/photo-1558618666-fcd25c85cd64?auto=format&fit=crop&w=1920&q=80') center/cover no-repeat;
        opacity: 0.15;
        z-index: 0;
        filter: brightness(0.7);
    }
    .solvi-header-content {
        position: relative;
        z-index: 1;
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 2rem;
        max-width: 1300px;
        margin: 0 auto;
    }
    .solvi-logo {
        height: 70px;
        padding: 10px 20px;
        border-radius: 12px;
        background: rgba(255,255,255,0.1);
        border: 2px solid rgba(255,255,255,0.2);
        box-shadow: 0 6px 15px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
    }
    .solvi-title {
        font-size: 3rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -1px;
    }
    .solvi-subtitle {font-size: 1.2rem; opacity: 0.9; margin-top: 0.5rem;}
    .solvi-badge {
        background: rgba(255,255,255,0.15);
        padding: 1rem 2rem;
        border-radius: 50px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        border: 2px solid rgba(255,255,255,0.3);
    }

    .solvi-navigation {
        display: flex;
        justify-content: center;
        flex-wrap: wrap;
        background: var(--solvi-surface);
        border-bottom: 3px solid var(--solvi-light);
        padding: 0.8rem 1rem;
        margin-bottom: 2rem;
        gap: 1rem;
        box-shadow: 0 5px 20px var(--solvi-shadow);
    }
    .solvi-nav-button {
        background: transparent;
        color: var(--solvi-primary);
        border: none;
        font-weight: 700;
        font-size: 1rem;
        padding: 1rem 2rem;
        border-radius: 8px;
        transition: 0.3s;
    }
    .solvi-nav-button:hover {background: var(--solvi-light); color: white; transform: translateY(-2px);}
    .solvi-nav-button.active {background: var(--solvi-primary); color: white; box-shadow: 0 4px 15px var(--solvi-shadow);}

    .solvi-card {
        background: var(--solvi-surface);
        border-radius: 20px;
        padding: 2.5rem;
        margin: 2rem 0;
        box-shadow: 0 10px 40px var(--solvi-shadow);
        border-top: 6px solid var(--solvi-medium);
    }
    .solvi-card-title {font-size: 1.9rem; font-weight: 800; color: var(--solvi-primary);}

    .solvi-upload {
        border: 3px dashed rgba(46,139,87,0.3);
        border-radius: 20px;
        background: #f9fbf9;
        text-align: center;
        padding: 3rem;
        margin: 2rem 0;
        transition: 0.3s;
    }
    .solvi-upload:hover {border-color: var(--solvi-medium); background: #eef8ef; transform: translateY(-3px);}
    .solvi-upload-icon {font-size: 3rem; color: var(--solvi-medium); margin-bottom: 1rem;}

    .solvi-alert {
        border-radius: 12px;
        padding: 1.5rem 2rem;
        margin: 1rem 0;
        box-shadow: 0 5px 20px var(--solvi-shadow);
        font-weight: 600;
    }
    .solvi-alert.success {background: #edf7ed; border-left: 5px solid var(--solvi-light);}
    .solvi-alert.warning {background: #fff9e5; border-left: 5px solid #ffb300;}
    .solvi-alert.error {background: #ffebee; border-left: 5px solid #e53935;}
    .solvi-alert.info {background: #e3f2fd; border-left: 5px solid #2196f3;}

    .solvi-metrics {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
        gap: 1.5rem;
        margin: 2.5rem 0;
    }
    .solvi-metric {
        background: white;
        border-radius: 16px;
        padding: 2.5rem;
        text-align: center;
        border: 2px solid #eaf3ea;
        box-shadow: 0 6px 25px var(--solvi-shadow);
    }
    .solvi-metric-value {font-size: 2.8rem; font-weight: 900; color: var(--solvi-primary);}
    .solvi-metric-label {text-transform: uppercase; font-size: 0.9rem; color: #555; letter-spacing: 1px;}

    .solvi-footer {
        background: linear-gradient(180deg, var(--solvi-primary), var(--solvi-medium));
        color: white;
        padding: 3rem 2rem;
        border-radius: 20px;
        text-align: center;
        margin-top: 3rem;
        box-shadow: 0 10px 40px var(--solvi-shadow);
    }
    .solvi-footer p {text-transform: uppercase; letter-spacing: 1px; margin: 0.5rem 0;}
    a.solvi-link {color: white; text-decoration: none; font-weight: 700; border-bottom: 2px solid rgba(255,255,255,0.4);}
    a.solvi-link:hover {border-color: white;}
</style>
""", unsafe_allow_html=True)


# ======================================================
# 🧠 FUNÇÕES DE ANÁLISE
# ======================================================
class FREAnalyzer:
    def __init__(self, api_key):
        openai.api_key = api_key
        self.client = openai.OpenAI(api_key=api_key)

    def extract_text_from_pdf(self, pdf_file):
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            return "\n".join([page.extract_text() for page in pdf_reader.pages])
        except Exception as e:
            st.error(f"Erro ao ler PDF: {e}")
            return ""

    def extract_text_from_docx(self, docx_file):
        try:
            doc = docx.Document(docx_file)
            return "\n".join([p.text for p in doc.paragraphs])
        except Exception as e:
            st.error(f"Erro ao ler DOCX: {e}")
            return ""

    def extract_text_from_file(self, uploaded_file):
        if uploaded_file.type == "application/pdf":
            return self.extract_text_from_pdf(uploaded_file)
        elif uploaded_file.type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword"]:
            return self.extract_text_from_docx(uploaded_file)
        else:
            st.error("Formato não suportado.")
            return ""

    def analyze_fre_section(self, fre_text, cvm_text, section_name, section_content):
        prompt = f"""
        Você é um especialista da CVM.
        Compare a seção '{section_name}' do FRE abaixo com as normas CVM e gere um parecer JSON estruturado.
        FRE:
        {section_content[:3000]}
        Normas CVM:
        {cvm_text[:5000]}
        """
        try:
            resp = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=1800
            )
            content = resp.choices[0].message.content
            json_start, json_end = content.find("{"), content.rfind("}") + 1
            return json.loads(content[json_start:json_end])
        except Exception:
            return {
                "secao": section_name,
                "conformidade": "ERRO",
                "pontos_atencao": [{"problema": "Falha na análise automática"}]
            }

    def extract_fre_sections(self, text):
        sections, current = {}, None
        patterns = [r"\d+\.\d+\s+.+"]

        lines = text.split("\n")
        for l in lines:
            if re.match(patterns[0], l.strip()):
                if current:
                    sections[current] = "\n".join(current_content)
                current = l.strip()
                current_content = []
            elif current:
                current_content.append(l)
        if current:
            sections[current] = "\n".join(current_content)
        return sections


class DocumentComparator:
    def calcular_similaridade(self, t1, t2):
        return difflib.SequenceMatcher(None, t1, t2).ratio()

    def dividir_em_paragrafos(self, texto):
        texto = re.sub(r"\s+", " ", texto.strip())
        return [p for p in re.split(r"(?<=\.)\s+", texto) if len(p) > 10]

    def encontrar_alteracoes_reais(self, ref, novo):
        alteracoes = []
        for par in ref:
            if par not in novo:
                alteracoes.append({"tipo": "Removido", "texto": par})
        for par in novo:
            if par not in ref:
                alteracoes.append({"tipo": "Adicionado", "texto": par})
        return alteracoes


# ======================================================
# 🧩 INTERFACE
# ======================================================
def init_session_state():
    if "current_tab" not in st.session_state:
        st.session_state.current_tab = "cvm"


def render_header():
    st.markdown("""
    <div class="solvi-header">
        <div class="solvi-header-content">
            <img src="https://static.wixstatic.com/media/b5b170_1e07cf7f7f82492a9808f9ae7f038596~mv2.png"
                 alt="Solví Logo" class="solvi-logo">
            <div>
                <h1 class="solvi-title">Plataforma Solví</h1>
                <p class="solvi-subtitle">🌱 Análise Inteligente de Documentos com IA</p>
            </div>
            <div class="solvi-badge">Soluções para a Vida</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_navigation():
    st.markdown('<div class="solvi-navigation">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 Análise CVM", key="tab_cvm", use_container_width=True):
            st.session_state.current_tab = "cvm"
            st.experimental_set_query_params(tab="cvm")
            st.rerun()
    with col2:
        if st.button("📚 Comparação de Documentos", key="tab_comparison", use_container_width=True):
            st.session_state.current_tab = "comparison"
            st.experimental_set_query_params(tab="comparison")
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def render_cvm_analysis():
    with st.sidebar:
        st.markdown("### ⚙️ Configurações da Análise")
        api_key = st.text_input("🔑 Chave API OpenAI *", type="password")
        fre_file = st.file_uploader("📄 Upload do FRE", type=["pdf", "docx"])
        cvm_files = st.file_uploader("📚 Documentos CVM", type=["pdf", "docx"], accept_multiple_files=True)

    if not api_key:
        st.warning("Insira sua chave API para continuar.")
        return

    if not fre_file or not cvm_files:
        st.markdown("""
        <div class="solvi-upload">
            <div class="solvi-upload-icon">📄</div>
            <p>Envie o FRE e ao menos um documento CVM para iniciar a análise.</p>
        </div>
        """, unsafe_allow_html=True)
        return

    if st.button("🔍 Iniciar Análise CVM", use_container_width=True):
        analyzer = FREAnalyzer(api_key)
        fre_text = analyzer.extract_text_from_file(fre_file)
        cvm_text = "\n".join([analyzer.extract_text_from_file(f) for f in cvm_files])
        sections = analyzer.extract_fre_sections(fre_text)
        results = []
        progress = st.progress(0)
        for i, (nome, conteudo) in enumerate(sections.items()):
            results.append(analyzer.analyze_fre_section(fre_text, cvm_text, nome, conteudo))
            progress.progress((i + 1) / len(sections))
        st.session_state.analysis_results = results
        st.success("✅ Análise concluída com sucesso!")

    if st.session_state.get("analysis_results"):
        total = sum(len(r.get("pontos_atencao", [])) for r in st.session_state.analysis_results)
        st.markdown(f"""
        <div class="solvi-metrics">
            <div class="solvi-metric"><div class="solvi-metric-value">{total}</div><div class="solvi-metric-label">Pontos Identificados</div></div>
        </div>
        """, unsafe_allow_html=True)


def render_document_comparison():
    col1, col2 = st.columns(2)
    with col1:
        arquivo_ref = st.file_uploader("📄 Documento de Referência", type=["pdf", "docx"])
    with col2:
        arquivo_novo = st.file_uploader("📄 Novo Documento", type=["pdf", "docx"])

    if not arquivo_ref or not arquivo_novo:
        st.markdown("""
        <div class="solvi-upload">
            <div class="solvi-upload-icon">📚</div>
            <p>Envie dois documentos para comparar versões.</p>
        </div>
        """, unsafe_allow_html=True)
        return

    if st.button("🔍 Comparar Documentos", use_container_width=True):
        comp = DocumentComparator()
        text_ref = docx.Document(arquivo_ref).paragraphs if arquivo_ref.name.endswith(".docx") else []
        text_novo = docx.Document(arquivo_novo).paragraphs if arquivo_novo.name.endswith(".docx") else []
        ref_par = [p.text for p in text_ref]
        novo_par = [p.text for p in text_novo]
        alteracoes = comp.encontrar_alteracoes_reais(ref_par, novo_par)
        st.success(f"✅ {len(alteracoes)} alterações detectadas.")


def render_footer():
    st.markdown("""
    <div class="solvi-footer">
        <p>🌱 Plataforma Solví • Soluções Inteligentes para Análise de Documentos</p>
        <p>Desenvolvido com ❤️ para sustentabilidade e inovação</p>
        <p><a href="https://www.solvi.com" class="solvi-link" target="_blank">Visite solvi.com</a></p>
    </div>
    """, unsafe_allow_html=True)


# ======================================================
# 🚀 MAIN
# ======================================================
def main():
   
