"""
🌱 Plataforma Solví - Análise Inteligente de Documentos
Aplicação unificada que combina análise CVM e comparação de documentos
com design fiel ao site oficial da Solví - Versão Corrigida
"""

import streamlit as st
import pandas as pd
import openai
from io import BytesIO
import PyPDF2
import docx
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
import json
import time
import re
from datetime import datetime
import base64
import fitz  # PyMuPDF
import difflib
from typing import List, Tuple, Dict, Optional, Set
import logging
from pathlib import Path
import tempfile
import os

# Configuração da página
st.set_page_config(
    page_title="Plataforma Solví - Análise de Documentos",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado baseado no design oficial da Solví com header expandido
st.markdown("""
<style>
    /* Importar fontes Google */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Reset e configurações globais */
    .main .block-container {
        padding-top: 0rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }
    
    /* Ocultar elementos padrão do Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Remover padding padrão do Streamlit */
    .css-18e3th9 {
        padding-top: 0rem;
    }
    
    .css-1d391kg {
        padding-top: 1rem;
    }
    
    /* Paleta de cores verde escuro Solví */
    :root {
        --solvi-dark-green: #0d4f1c;
        --solvi-primary-green: #1b5e20;
        --solvi-medium-green: #2e7d32;
        --solvi-light-green: #388e3c;
        --solvi-accent-green: #4caf50;
        --solvi-bright-green: #66bb6a;
        --solvi-surface: #f1f8e9;
        --solvi-background: #e8f5e8;
        --solvi-white: #ffffff;
        --solvi-text-dark: #1b5e20;
        --solvi-text-light: #ffffff;
        --solvi-shadow: rgba(13, 79, 28, 0.15);
    }
    
    /* Header principal expandido com logo oficial da Solví */
    .solvi-header {
        background: linear-gradient(135deg, var(--solvi-dark-green) 0%, var(--solvi-primary-green) 30%, var(--solvi-medium-green) 70%, var(--solvi-light-green) 100%);
        color: var(--solvi-text-light);
        padding: 2.5rem 2.5rem;
        border-radius: 0;
        margin: -2rem -2rem 2rem -2rem;
        box-shadow: 0 8px 32px var(--solvi-shadow);
        position: relative;
        overflow: hidden;
        min-height: 180px;
        width: 100vw;
        margin-left: calc(-50vw + 50%);
    }
    
    .solvi-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-image: url('https://images.unsplash.com/photo-1441974231531-c6227db76b6e?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80');
        background-size: cover;
        background-position: center;
        opacity: 0.08;
        z-index: 0;
    }
    
    .solvi-header-content {
        position: relative;
        z-index: 1;
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 2rem;
        max-width: 1400px;
        margin: 0 auto;
        padding: 0 2rem;
    }
    
    .solvi-logo-section {
        display: flex;
        align-items: center;
        gap: 2rem;
    }
    
    .solvi-logo {
        height: 70px;
        width: auto;
        background: var(--solvi-white);
        padding: 12px 20px;
        border-radius: 12px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.15);
        transition: all 0.3s ease;
    }
    
    .solvi-logo:hover {
        transform: scale(1.05);
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
    }
    
    .solvi-title {
        font-size: 3rem;
        font-weight: 800;
        font-family: 'Inter', sans-serif;
        margin: 0;
        text-shadow: 2px 2px 8px rgba(0,0,0,0.3);
        letter-spacing: -1px;
        line-height: 1.1;
    }
    
    .solvi-subtitle {
        font-size: 1.3rem;
        opacity: 0.95;
        margin-top: 0.5rem;
        font-weight: 500;
        letter-spacing: 0.5px;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.2);
    }
    
    .solvi-badge {
        background: rgba(255,255,255,0.2);
        padding: 1.25rem 2.5rem;
        border-radius: 35px;
        font-size: 1.1rem;
        font-weight: 700;
        backdrop-filter: blur(15px);
        border: 2px solid rgba(255,255,255,0.3);
        text-transform: uppercase;
        letter-spacing: 1.5px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    
    .solvi-badge:hover {
        background: rgba(255,255,255,0.3);
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(0,0,0,0.15);
    }
    
    /* Seção de imagens inspiracionais */
    .solvi-inspiration {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 2rem;
        margin: 3rem 0;
        padding: 2.5rem;
        background: linear-gradient(135deg, var(--solvi-surface) 0%, var(--solvi-background) 100%);
        border-radius: 20px;
        border: 2px solid var(--solvi-light-green);
        box-shadow: 0 8px 30px var(--solvi-shadow);
    }
    
    .solvi-inspiration-item {
        position: relative;
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 8px 30px var(--solvi-shadow);
        transition: all 0.3s ease;
        background: var(--solvi-white);
        border: 2px solid var(--solvi-background);
    }
    
    .solvi-inspiration-item:hover {
        transform: translateY(-10px);
        box-shadow: 0 15px 50px var(--solvi-shadow);
        border-color: var(--solvi-light-green);
    }
    
    .solvi-inspiration-image {
        width: 100%;
        height: 180px;
        object-fit: cover;
        border-radius: 16px 16px 0 0;
    }
    
    .solvi-inspiration-content {
        padding: 2rem;
        background: linear-gradient(135deg, var(--solvi-white) 0%, var(--solvi-surface) 100%);
    }
    
    .solvi-inspiration-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: var(--solvi-text-dark);
        margin: 0 0 1rem 0;
        font-family: 'Inter', sans-serif;
    }
    
    .solvi-inspiration-desc {
        font-size: 1rem;
        color: #666;
        line-height: 1.6;
        margin: 0;
        font-weight: 500;
    }
    
    /* Navegação por abas estilo Solví */
    .solvi-navigation {
        background: linear-gradient(135deg, var(--solvi-white) 0%, var(--solvi-surface) 100%);
        border-radius: 20px;
        padding: 1.5rem;
        margin: 3rem 0;
        box-shadow: 0 8px 35px var(--solvi-shadow);
        border: 2px solid var(--solvi-background);
    }
    
    .solvi-nav-button {
        display: inline-flex;
        align-items: center;
        gap: 1.25rem;
        padding: 1.5rem 3rem;
        margin: 0.75rem;
        border-radius: 16px;
        background: transparent;
        color: var(--solvi-text-dark);
        font-weight: 700;
        text-decoration: none;
        transition: all 0.3s ease;
        border: 3px solid transparent;
        cursor: pointer;
        font-family: 'Inter', sans-serif;
        font-size: 1.2rem;
        width: 100%;
        justify-content: center;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .solvi-nav-button:hover {
        background: linear-gradient(135deg, var(--solvi-background) 0%, var(--solvi-surface) 100%);
        transform: translateY(-4px);
        box-shadow: 0 8px 30px var(--solvi-shadow);
        border-color: var(--solvi-light-green);
    }
    
    .solvi-nav-button.active {
        background: linear-gradient(135deg, var(--solvi-primary-green) 0%, var(--solvi-medium-green) 50%, var(--solvi-light-green) 100%);
        color: var(--solvi-text-light);
        box-shadow: 0 10px 35px var(--solvi-shadow);
        border-color: var(--solvi-dark-green);
    }
    
    /* Cards estilo Solví */
    .solvi-card {
        background: linear-gradient(135deg, var(--solvi-white) 0%, var(--solvi-surface) 100%);
        border-radius: 24px;
        padding: 3rem;
        margin: 2.5rem 0;
        box-shadow: 0 15px 50px var(--solvi-shadow);
        border: 2px solid var(--solvi-background);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .solvi-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 8px;
        background: linear-gradient(90deg, var(--solvi-dark-green) 0%, var(--solvi-primary-green) 25%, var(--solvi-medium-green) 50%, var(--solvi-light-green) 75%, var(--solvi-accent-green) 100%);
    }
    
    .solvi-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 25px 70px var(--solvi-shadow);
        border-color: var(--solvi-light-green);
    }
    
    .solvi-card-header {
        display: flex;
        align-items: center;
        margin-bottom: 2.5rem;
        padding-bottom: 2rem;
        border-bottom: 3px solid var(--solvi-background);
    }
    
    .solvi-card-icon {
        width: 64px;
        height: 64px;
        background: linear-gradient(135deg, var(--solvi-medium-green) 0%, var(--solvi-light-green) 50%, var(--solvi-accent-green) 100%);
        border-radius: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 2rem;
        font-size: 2rem;
        box-shadow: 0 8px 25px var(--solvi-shadow);
        border: 3px solid var(--solvi-white);
    }
    
    .solvi-card-title {
        font-size: 2rem;
        font-weight: 800;
        color: var(--solvi-text-dark);
        margin: 0;
        font-family: 'Inter', sans-serif;
        letter-spacing: -0.5px;
        line-height: 1.2;
    }
    
    /* Métricas estilo Solví */
    .solvi-metrics {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
        gap: 2.5rem;
        margin: 3rem 0;
    }
    
    .solvi-metric {
        background: linear-gradient(135deg, var(--solvi-white) 0%, var(--solvi-surface) 50%, var(--solvi-background) 100%);
        border-radius: 24px;
        padding: 3rem;
        text-align: center;
        border: 2px solid var(--solvi-background);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        box-shadow: 0 10px 35px var(--solvi-shadow);
    }
    
    .solvi-metric::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 6px;
        background: linear-gradient(90deg, var(--solvi-primary-green) 0%, var(--solvi-medium-green) 50%, var(--solvi-light-green) 100%);
    }
    
    .solvi-metric:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 60px var(--solvi-shadow);
        border-color: var(--solvi-light-green);
    }
    
    .solvi-metric-value {
        font-size: 4rem;
        font-weight: 900;
        color: var(--solvi-primary-green);
        margin-bottom: 1rem;
        font-family: 'Inter', sans-serif;
        line-height: 1;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .solvi-metric-label {
        color: #555;
        font-size: 1.1rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-family: 'Inter', sans-serif;
    }
    
    /* Botões estilo Solví */
    .stButton > button {
        background: linear-gradient(135deg, var(--solvi-primary-green) 0%, var(--solvi-medium-green) 50%, var(--solvi-light-green) 100%);
        color: var(--solvi-text-light);
        border: none;
        border-radius: 20px;
        padding: 1.5rem 3.5rem;
        font-weight: 700;
        font-size: 1.2rem;
        transition: all 0.3s ease;
        box-shadow: 0 8px 25px var(--solvi-shadow);
        font-family: 'Inter', sans-serif;
        letter-spacing: 1px;
        text-transform: uppercase;
        border: 3px solid transparent;
    }
    
    .stButton > button:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px var(--solvi-shadow);
        background: linear-gradient(135deg, var(--solvi-dark-green) 0%, var(--solvi-primary-green) 50%, var(--solvi-medium-green) 100%);
        border-color: var(--solvi-white);
    }
    
    /* Alertas estilo Solví */
    .solvi-alert {
        border-radius: 20px;
        padding: 2.5rem 3rem;
        margin: 2.5rem 0;
        border-left: 8px solid;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
        position: relative;
        overflow: hidden;
        box-shadow: 0 8px 30px rgba(0,0,0,0.08);
        font-size: 1.1rem;
    }
    
    .solvi-alert.success {
        background: linear-gradient(135deg, var(--solvi-surface) 0%, #f1f8e9 50%, #e8f5e8 100%);
        border-color: var(--solvi-accent-green);
        color: var(--solvi-text-dark);
    }
    
    .solvi-alert.warning {
        background: linear-gradient(135deg, #fff8e1 0%, #fffde7 50%, #f9fbe7 100%);
        border-color: #ff9800;
        color: #e65100;
    }
    
    .solvi-alert.error {
        background: linear-gradient(135deg, #ffebee 0%, #fce4ec 50%, #f3e5f5 100%);
        border-color: #f44336;
        color: #c62828;
    }
    
    .solvi-alert.info {
        background: linear-gradient(135deg, #e3f2fd 0%, #e1f5fe 50%, #e0f2f1 100%);
        border-color: #2196f3;
        color: #0d47a1;
    }
    
    /* Upload areas */
    .solvi-upload {
        border: 4px dashed var(--solvi-light-green);
        border-radius: 24px;
        padding: 4.5rem 3rem;
        text-align: center;
        background: linear-gradient(135deg, var(--solvi-white) 0%, var(--solvi-surface) 50%, var(--solvi-background) 100%);
        transition: all 0.3s ease;
        margin: 2.5rem 0;
        box-shadow: 0 10px 35px var(--solvi-shadow);
    }
    
    .solvi-upload:hover {
        border-color: var(--solvi-primary-green);
        background: linear-gradient(135deg, var(--solvi-surface) 0%, var(--solvi-background) 50%, #dcedc8 100%);
        transform: translateY(-6px);
        box-shadow: 0 15px 50px var(--solvi-shadow);
    }
    
    .solvi-upload-icon {
        font-size: 4.5rem;
        color: var(--solvi-light-green);
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .solvi-upload-text {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--solvi-text-dark);
        margin-bottom: 1.25rem;
        font-family: 'Inter', sans-serif;
    }
    
    .solvi-upload-subtext {
        font-size: 1.1rem;
        color: #666;
        line-height: 1.7;
        font-weight: 500;
    }
    
    /* Footer */
    .solvi-footer {
        background: linear-gradient(135deg, var(--solvi-dark-green) 0%, var(--solvi-primary-green) 50%, var(--solvi-medium-green) 100%);
        color: var(--solvi-text-light);
        padding: 4rem 2rem;
        border-radius: 24px;
        margin: 4rem 0 2rem 0;
        text-align: center;
        box-shadow: 0 15px 50px var(--solvi-shadow);
        position: relative;
        overflow: hidden;
    }
    
    .solvi-footer::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-image: url('https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80');
        background-size: cover;
        background-position: center;
        opacity: 0.05;
        z-index: 0;
    }
    
    .solvi-footer-content {
        position: relative;
        z-index: 1;
    }
    
    .solvi-footer-logo {
        height: 60px;
        margin-bottom: 2rem;
        background: var(--solvi-white);
        padding: 12px 20px;
        border-radius: 12px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.2);
    }
    
    /* Responsividade */
    @media (max-width: 768px) {
        .solvi-header {
            padding: 2rem 1.5rem;
            min-height: 160px;
        }
        
        .solvi-header-content {
            flex-direction: column;
            text-align: center;
            gap: 1.5rem;
            padding: 0 1rem;
        }
        
        .solvi-title {
            font-size: 2.2rem;
        }
        
        .solvi-subtitle {
            font-size: 1.1rem;
        }
        
        .solvi-logo {
            height: 60px;
        }
        
        .solvi-inspiration {
            grid-template-columns: 1fr;
            padding: 2rem;
        }
        
        .solvi-metrics {
            grid-template-columns: 1fr;
        }
        
        .solvi-metric-value {
            font-size: 3.5rem;
        }
        
        .solvi-card {
            padding: 2.5rem;
        }
        
        .solvi-upload {
            padding: 3.5rem 2rem;
        }
    }
    
    /* Animações */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(50px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes pulse {
        0%, 100% {
            transform: scale(1);
        }
        50% {
            transform: scale(1.02);
        }
    }
    
    .solvi-card, .solvi-metric, .solvi-inspiration-item {
        animation: fadeInUp 0.8s ease-out;
    }
    
    .solvi-logo {
        animation: pulse 4s ease-in-out infinite;
    }
    
    /* Scrollbar personalizada */
    ::-webkit-scrollbar {
        width: 12px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--solvi-surface);
        border-radius: 12px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, var(--solvi-medium-green) 0%, var(--solvi-light-green) 100%);
        border-radius: 12px;
        border: 2px solid var(--solvi-surface);
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, var(--solvi-primary-green) 0%, var(--solvi-medium-green) 100%);
    }
</style>
""", unsafe_allow_html=True)

# Inicializar session state
def init_session_state():
    """Inicializa o estado da sessão"""
    if 'current_tab' not in st.session_state:
        st.session_state.current_tab = 'cvm'
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    if 'comparison_results' not in st.session_state:
        st.session_state.comparison_results = None

class FREAnalyzer:
    """Classe para análise de FRE vs Normas CVM"""
    
    def __init__(self, api_key):
        openai.api_key = api_key
        self.client = openai.OpenAI(api_key=api_key)
        
    def extract_text_from_pdf(self, pdf_file):
        """Extrai texto de arquivo PDF"""
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            st.error(f"Erro ao extrair texto do PDF: {str(e)}")
            return ""
    
    def extract_text_from_docx(self, docx_file):
        """Extrai texto de arquivo Word"""
        try:
            doc = docx.Document(docx_file)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            st.error(f"Erro ao extrair texto do Word: {str(e)}")
            return ""
    
    def extract_text_from_file(self, uploaded_file):
        """Extrai texto baseado no tipo de arquivo"""
        if uploaded_file.type == "application/pdf":
            return self.extract_text_from_pdf(uploaded_file)
        elif uploaded_file.type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", 
                                   "application/msword"]:
            return self.extract_text_from_docx(uploaded_file)
        else:
            st.error("Formato de arquivo não suportado. Use PDF ou Word.")
            return ""
    
    def analyze_fre_section(self, fre_text, cvm_references, section_name, section_content):
        """Analisa uma seção específica do FRE contra as normas CVM"""
        
        prompt = f"""
        Você é um especialista em regulamentação CVM e análise de Formulários de Referência (FRE).
        
        Analise a seção "{section_name}" do FRE fornecido contra as normas e orientações CVM.
        
        SEÇÃO ANALISADA:
        {section_content[:3000]}...
        
        NORMAS CVM DE REFERÊNCIA:
        {cvm_references[:5000]}...
        
        Para esta seção, identifique:
        
        1. CONFORMIDADE: Está em conformidade com as normas CVM?
        2. COMPLETUDE: Todas as informações obrigatórias estão presentes?
        3. QUALIDADE: A informação está clara, objetiva e completa?
        4. PONTOS DE ATENÇÃO: Identifique problemas específicos
        5. SUGESTÕES: Recomendações de melhoria com citação obrigatória dos artigos CVM
        
        RESPONDA EM JSON com esta estrutura:
        {{
            "secao": "{section_name}",
            "conformidade": "CONFORME/NAO_CONFORME/PARCIALMENTE_CONFORME",
            "criticidade": "CRITICO/ATENCAO/SUGESTAO",
            "pontos_atencao": [
                {{
                    "problema": "descrição do problema",
                    "criticidade": "CRITICO/ATENCAO/SUGESTAO",
                    "artigo_cvm": "artigo específico da norma CVM",
                    "sugestao": "recomendação específica de melhoria"
                }}
            ],
            "resumo": "resumo geral da análise desta seção"
        }}
        
        IMPORTANTE: 
        - Cite OBRIGATORIAMENTE os artigos específicos das normas CVM
        - Use criticidade CRITICO para não conformidades graves
        - Use ATENCAO para informações incompletas
        - Use SUGESTAO para melhorias recomendadas
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=2000
            )
            
            result = response.choices[0].message.content
            
            # Tenta extrair JSON da resposta
            try:
                json_start = result.find('{')
                json_end = result.rfind('}') + 1
                json_str = result[json_start:json_end]
                return json.loads(json_str)
            except:
                # Se falhar, retorna estrutura padrão
                return {
                    "secao": section_name,
                    "conformidade": "ERRO_ANALISE",
                    "criticidade": "ATENCAO",
                    "pontos_atencao": [{
                        "problema": "Erro na análise automática",
                        "criticidade": "ATENCAO",
                        "artigo_cvm": "Resolução CVM nº 80/22",
                        "sugestao": "Revisar manualmente esta seção"
                    }],
                    "resumo": "Erro na análise automática desta seção"
                }
                
        except Exception as e:
            st.error(f"Erro na análise da seção {section_name}: {str(e)}")
            return None
    
    def extract_fre_sections(self, fre_text):
        """Extrai as seções principais do FRE"""
        sections = {}
        
        # Padrões para identificar seções do FRE
        section_patterns = [
            r"1\.1\s+Histórico do emissor",
            r"1\.2\s+Descrição das principais atividades",
            r"1\.3\s+Informações relacionadas aos segmentos operacionais",
            r"1\.4\s+Produção/Comercialização/Mercados",
            r"1\.5\s+Principais clientes",
            r"1\.6\s+Efeitos relevantes da regulação estatal",
            r"1\.9\s+Informações ambientais sociais e de governança",
            r"2\.1\s+Condições financeiras e patrimoniais",
            r"2\.2\s+Resultados operacional e financeiro",
            r"4\.1\s+Descrição dos fatores de risco",
            r"7\.1\s+Principais características dos órgãos de administração",
            r"8\.1\s+Política ou prática de remuneração",
            r"11\.1\s+Regras, políticas e práticas",
            r"12\.1\s+Informações sobre o capital social"
        ]
        
        # Divide o texto em seções
        lines = fre_text.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            # Verifica se a linha corresponde a uma nova seção
            section_found = False
            for pattern in section_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    # Salva a seção anterior se existir
                    if current_section and current_content:
                        sections[current_section] = '\n'.join(current_content)
                    
                    # Inicia nova seção
                    current_section = line.strip()
                    current_content = [line]
                    section_found = True
                    break
            
            if not section_found and current_section:
                current_content.append(line)
        
        # Salva a última seção
        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content)
        
        return sections

class DocumentComparator:
    """Classe para comparação de documentos"""
    
    def __init__(self):
        self.texto_ref = []
        self.texto_novo = []
        self.diferencas = []
        self.diferencas_detalhadas = []
        
    def detectar_tipo_arquivo(self, nome_arquivo: str) -> str:
        """Detecta o tipo do arquivo baseado na extensão"""
        extensao = Path(nome_arquivo).suffix.lower()
        if extensao == '.pdf':
            return 'pdf'
        elif extensao in ['.docx', '.doc']:
            return 'word'
        else:
            return 'desconhecido'
    
    def extrair_texto_pdf(self, pdf_bytes: bytes) -> List[str]:
        """Extrai texto de cada página do PDF"""
        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            textos = []
            
            for i, pagina in enumerate(doc):
                texto = pagina.get_text()
                textos.append(texto)
            
            doc.close()
            return textos
            
        except Exception as e:
            st.error(f"Erro ao extrair texto do PDF: {str(e)}")
            return []
    
    def extrair_texto_word(self, word_bytes: bytes) -> List[str]:
        """Extrai texto do documento Word"""
        try:
            # Salvar temporariamente para processar
            with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
                tmp_file.write(word_bytes)
                tmp_path = tmp_file.name
            
            try:
                doc = docx.Document(tmp_path)
                
                # Para Word, vamos simular "páginas" agrupando parágrafos
                textos = []
                texto_atual = ""
                contador_paragrafos = 0
                
                for paragrafo in doc.paragraphs:
                    texto_atual += paragrafo.text + "\n"
                    contador_paragrafos += 1
                    
                    # Criar nova "página" a cada 50 parágrafos
                    if contador_paragrafos >= 50:
                        if texto_atual.strip():
                            textos.append(texto_atual)
                            texto_atual = ""
                            contador_paragrafos = 0
                
                # Adicionar último texto se houver
                if texto_atual.strip():
                    textos.append(texto_atual)
                
                # Se não há texto, criar pelo menos uma "página" vazia
                if not textos:
                    textos = [""]
                
                return textos
                
            finally:
                # Limpar arquivo temporário
                try:
                    os.unlink(tmp_path)
                except:
                    pass
                    
        except Exception as e:
            st.error(f"Erro ao extrair texto do Word: {str(e)}")
            return []
    
    def normalizar_texto(self, texto: str) -> str:
        """Normaliza o texto removendo variações que não são alterações reais"""
        # Remover espaços extras e quebras de linha desnecessárias
        texto = re.sub(r'\s+', ' ', texto.strip())
        
        # Remover caracteres de controle e formatação
        texto = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', texto)
        
        # Normalizar pontuação
        texto = re.sub(r'\s+([,.;:!?])', r'\1', texto)
        
        # Normalizar aspas e caracteres especiais
        texto = re.sub(r'["""]', '"', texto)
        texto = re.sub(r"[''']", "'", texto)
        texto = re.sub(r'[–—]', '-', texto)
        
        return texto
    
    def dividir_em_paragrafos(self, texto: str) -> List[str]:
        """Divide o texto em parágrafos de forma inteligente"""
        # Normalizar o texto primeiro
        texto = self.normalizar_texto(texto)
        
        # Dividir por quebras de linha duplas primeiro
        paragrafos_brutos = re.split(r'\n\s*\n', texto)
        paragrafos = []
        
        for paragrafo in paragrafos_brutos:
            paragrafo = paragrafo.strip()
            if paragrafo:
                # Se o parágrafo for muito longo, dividir por frases
                if len(paragrafo) > 500:
                    frases = re.split(r'(?<!\d)\.(?!\d)\s+', paragrafo)
                    for frase in frases:
                        frase = self.normalizar_texto(frase.strip())
                        if frase and len(frase) > 10:
                            paragrafos.append(frase)
                else:
                    paragrafo_normalizado = self.normalizar_texto(paragrafo)
                    if paragrafo_normalizado and len(paragrafo_normalizado) > 10:
                        paragrafos.append(paragrafo_normalizado)
        
        return paragrafos
    
    def calcular_similaridade(self, texto1: str, texto2: str) -> float:
        """Calcula a similaridade entre dois textos"""
        if not texto1 and not texto2:
            return 1.0
        if not texto1 or not texto2:
            return 0.0
        
        texto1_norm = self.normalizar_texto(texto1)
        texto2_norm = self.normalizar_texto(texto2)
        
        matcher = difflib.SequenceMatcher(None, texto1_norm, texto2_norm)
        return matcher.ratio()
    
    def encontrar_alteracoes_reais(self, paragrafos_ref: List[str], paragrafos_novo: List[str]) -> List[Dict]:
        """Encontra apenas alterações reais de conteúdo"""
        alteracoes = []
        
        # Criar conjuntos de parágrafos únicos
        set_ref = set(paragrafos_ref)
        set_novo = set(paragrafos_novo)
        
        # Encontrar parágrafos removidos e adicionados
        paragrafos_removidos = set_ref - set_novo
        paragrafos_adicionados = set_novo - set_ref
        
        # Verificar modificações
        paragrafos_modificados = []
        
        for p_ref in paragrafos_removidos.copy():
            melhor_match = None
            melhor_similaridade = 0.0
            
            for p_novo in paragrafos_adicionados:
                similaridade = self.calcular_similaridade(p_ref, p_novo)
                
                if similaridade > 0.6 and similaridade > melhor_similaridade:
                    melhor_match = p_novo
                    melhor_similaridade = similaridade
            
            if melhor_match and melhor_similaridade > 0.6:
                paragrafos_modificados.append({
                    'original': p_ref,
                    'novo': melhor_match,
                    'similaridade': melhor_similaridade
                })
                paragrafos_removidos.discard(p_ref)
                paragrafos_adicionados.discard(melhor_match)
        
        # Adicionar alterações
        for paragrafo in paragrafos_removidos:
            alteracoes.append({
                'tipo': 'removido',
                'texto': paragrafo,
                'texto_original': paragrafo,
                'texto_novo': ''
            })
        
        for paragrafo in paragrafos_adicionados:
            alteracoes.append({
                'tipo': 'adicionado',
                'texto': paragrafo,
                'texto_original': '',
                'texto_novo': paragrafo
            })
        
        for mod in paragrafos_modificados:
            alteracoes.append({
                'tipo': 'modificado',
                'texto': f"ANTES: {mod['original']}\nDEPOIS: {mod['novo']}",
                'texto_original': mod['original'],
                'texto_novo': mod['novo'],
                'similaridade': mod['similaridade']
            })
        
        return alteracoes

def render_header():
    """Renderiza o header principal da aplicação"""
    st.markdown("""
    <div class="solvi-header">
        <div class="solvi-header-content">
            <div class="solvi-logo-section">
                <img src="https://static.wixstatic.com/media/b5b170_1e07cf7f7f82492a9808f9ae7f038596~mv2.png/v1/crop/x_0,y_0,w_2742,h_1106/fill/w_92,h_37,al_c,q_85,usm_0.66_1.00_0.01,enc_auto/Logotipo%20Solv%C3%AD_edited_edited.png" alt="Solví Logo" class="solvi-logo">
                <div>
                    <h1 class="solvi-title">Plataforma Solví</h1>
                    <p class="solvi-subtitle">🌱 Análise Inteligente de Documentos com IA</p>
                </div>
            </div>
            <div class="solvi-badge">
                Soluções para a vida
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_inspiration_section():
    """Renderiza seção de imagens inspiracionais"""
    st.markdown("""
    <div class="solvi-inspiration">
        <div class="solvi-inspiration-item">
            <img src="https://images.unsplash.com/photo-1558618666-fcd25c85cd64?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80" alt="Tecnologia Sustentável" class="solvi-inspiration-image">
            <div class="solvi-inspiration-content">
                <h3 class="solvi-inspiration-title">🔋 Tecnologia Sustentável</h3>
                <p class="solvi-inspiration-desc">Inovação em energia renovável e soluções tecnológicas verdes para um futuro sustentável e próspero.</p>
            </div>
        </div>
        <div class="solvi-inspiration-item">
            <img src="https://images.unsplash.com/photo-1441974231531-c6227db76b6e?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80" alt="Proteção Ambiental" class="solvi-inspiration-image">
            <div class="solvi-inspiration-content">
                <h3 class="solvi-inspiration-title">🌿 Proteção Ambiental</h3>
                <p class="solvi-inspiration-desc">Preservação da natureza e biodiversidade através de práticas ambientais responsáveis e sustentáveis.</p>
            </div>
        </div>
        <div class="solvi-inspiration-item">
            <img src="https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80" alt="Gestão de Resíduos" class="solvi-inspiration-image">
            <div class="solvi-inspiration-content">
                <h3 class="solvi-inspiration-title">♻️ Gestão de Resíduos</h3>
                <p class="solvi-inspiration-desc">Soluções inteligentes para reciclagem e economia circular, transformando resíduos em recursos valiosos.</p>
            </div>
        </div>
        <div class="solvi-inspiration-item">
            <img src="https://images.unsplash.com/photo-1569163139394-de4e4f43e4e5?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80" alt="Inovação Verde" class="solvi-inspiration-image">
            <div class="solvi-inspiration-content">
                <h3 class="solvi-inspiration-title">💡 Inovação Verde</h3>
                <p class="solvi-inspiration-desc">Desenvolvimento de tecnologias limpas e processos inovadores para sustentabilidade empresarial.</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_navigation():
    """Renderiza a navegação por abas"""
    st.markdown('<div class="solvi-navigation">', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Análise CVM", key="tab_cvm", use_container_width=True):
            st.session_state.current_tab = 'cvm'
    
    with col2:
        if st.button("📚 Comparação de Documentos", key="tab_comparison", use_container_width=True):
            st.session_state.current_tab = 'comparison'
    
    st.markdown("</div>", unsafe_allow_html=True)

def render_cvm_analysis():
    """Renderiza a interface de análise CVM"""
    st.markdown("""
    <div class="solvi-card">
        <div class="solvi-card-header">
            <div class="solvi-card-icon">📊</div>
            <h2 class="solvi-card-title">Análise FRE vs Normas CVM</h2>
        </div>
        <p style="color: #666; font-size: 1.3rem; line-height: 1.8; font-weight: 500;">
            Análise automatizada de Formulários de Referência contra normas CVM com identificação 
            de não conformidades e geração de relatórios detalhados com base legal específica.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar para configurações
    with st.sidebar:
        st.markdown("### ⚙️ Configurações")
        
        # Campo obrigatório para API Key
        api_key = st.text_input(
            "🔑 Chave API OpenAI *",
            type="password",
            help="Insira sua chave API da OpenAI (obrigatório)"
        )
        
        if not api_key:
            st.markdown("""
            <div class="solvi-alert error">
                ⚠️ <strong>Chave API OpenAI é obrigatória!</strong><br>
                Configure sua chave para utilizar a análise CVM.
            </div>
            """, unsafe_allow_html=True)
            return
        
        st.markdown("---")
        
        # Upload do FRE
        st.markdown("### 📄 Arquivo FRE")
        fre_file = st.file_uploader(
            "Upload do Formulário de Referência",
            type=['pdf', 'docx'],
            help="Faça upload do FRE para análise"
        )
        
        st.markdown("---")
        
        # Upload dos documentos CVM
        st.markdown("### 📚 Documentos CVM (máx. 5)")
        cvm_files = st.file_uploader(
            "Upload dos documentos de referência CVM",
            type=['pdf', 'docx'],
            accept_multiple_files=True,
            help="Faça upload dos documentos CVM para comparação"
        )
        
        if len(cvm_files) > 5:
            st.error("⚠️ Máximo de 5 documentos CVM permitidos!")
            cvm_files = cvm_files[:5]
    
    # Área principal
    if not fre_file:
        st.markdown("""
        <div class="solvi-upload">
            <div class="solvi-upload-icon">📄</div>
            <div class="solvi-upload-text">Como usar a Análise CVM</div>
            <div class="solvi-upload-subtext">
                1. Configure sua API Key OpenAI na barra lateral<br>
                2. Faça upload do FRE (Formulário de Referência)<br>
                3. Adicione documentos CVM para comparação<br>
                4. Execute a análise e receba relatório detalhado
            </div>
        </div>
        """, unsafe_allow_html=True)
        return
    
    if not cvm_files:
        st.markdown("""
        <div class="solvi-alert warning">
            ⚠️ <strong>Documentos CVM necessários</strong><br>
            Adicione pelo menos um documento CVM para realizar a análise comparativa.
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Informações dos arquivos carregados
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="solvi-alert success">
            ✅ <strong>FRE Carregado:</strong> {fre_file.name}<br>
            📊 <strong>Tamanho:</strong> {fre_file.size / 1024 / 1024:.2f} MB
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="solvi-alert info">
            📚 <strong>Documentos CVM:</strong> {len(cvm_files)} arquivo(s)<br>
            📊 <strong>Total:</strong> {sum(f.size for f in cvm_files) / 1024 / 1024:.2f} MB
        </div>
        """, unsafe_allow_html=True)
    
    # Botão de análise
    if st.button("🔍 Iniciar Análise CVM", type="primary", use_container_width=True):
        with st.spinner("🔄 Processando análise..."):
            try:
                # Inicializar analisador
                analyzer = FREAnalyzer(api_key)
                
                # Extrair texto do FRE
                fre_text = analyzer.extract_text_from_file(fre_file)
                if not fre_text:
                    st.error("❌ Erro ao extrair texto do FRE")
                    return
                
                # Extrair texto dos documentos CVM
                cvm_text = ""
                for cvm_file in cvm_files:
                    cvm_content = analyzer.extract_text_from_file(cvm_file)
                    cvm_text += cvm_content + "\n\n"
                
                if not cvm_text:
                    st.error("❌ Erro ao extrair texto dos documentos CVM")
                    return
                
                # Extrair seções do FRE
                fre_sections = analyzer.extract_fre_sections(fre_text)
                
                if not fre_sections:
                    st.error("❌ Não foi possível identificar seções no FRE")
                    return
                
                # Analisar cada seção
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                analysis_results = []
                total_sections = len(fre_sections)
                
                for i, (section_name, section_content) in enumerate(fre_sections.items()):
                    status_text.text(f"Analisando: {section_name}")
                    
                    result = analyzer.analyze_fre_section(
                        fre_text, cvm_text, section_name, section_content
                    )
                    
                    if result:
                        analysis_results.append(result)
                    
                    progress_bar.progress((i + 1) / total_sections)
                    time.sleep(0.5)
                
                status_text.text("✅ Análise concluída!")
                progress_bar.empty()
                status_text.empty()
                
                # Salvar resultados
                st.session_state.analysis_results = analysis_results
                st.session_state.fre_filename = fre_file.name
                
                st.markdown("""
                <div class="solvi-alert success">
                    ✅ <strong>Análise CVM concluída com sucesso!</strong><br>
                    Confira os resultados detalhados abaixo.
                </div>
                """, unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"❌ Erro durante a análise: {str(e)}")
    
    # Exibir resultados se disponíveis
    if st.session_state.analysis_results:
        analysis_results = st.session_state.analysis_results
        
        st.markdown("### 📊 Resultados da Análise")
        
        # Métricas gerais
        total_pontos = sum(len(r.get('pontos_atencao', [])) for r in analysis_results)
        criticos = sum(1 for r in analysis_results for p in r.get('pontos_atencao', []) if p.get('criticidade') == 'CRITICO')
        atencao = sum(1 for r in analysis_results for p in r.get('pontos_atencao', []) if p.get('criticidade') == 'ATENCAO')
        sugestoes = sum(1 for r in analysis_results for p in r.get('pontos_atencao', []) if p.get('criticidade') == 'SUGESTAO')
        
        st.markdown(f"""
        <div class="solvi-metrics">
            <div class="solvi-metric">
                <div class="solvi-metric-value">{total_pontos}</div>
                <div class="solvi-metric-label">Total de Pontos</div>
            </div>
            <div class="solvi-metric">
                <div class="solvi-metric-value">{criticos}</div>
                <div class="solvi-metric-label">Críticos</div>
            </div>
            <div class="solvi-metric">
                <div class="solvi-metric-value">{atencao}</div>
                <div class="solvi-metric-label">Atenção</div>
            </div>
            <div class="solvi-metric">
                <div class="solvi-metric-value">{sugestoes}</div>
                <div class="solvi-metric-label">Sugestões</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Exibir resultados detalhados
        for result in analysis_results:
            with st.expander(f"📑 {result.get('secao', 'Seção não identificada')}", expanded=False):
                conformidade = result.get('conformidade', 'N/A')
                if conformidade == 'CONFORME':
                    st.success(f"✅ Status: {conformidade}")
                elif conformidade == 'NAO_CONFORME':
                    st.error(f"❌ Status: {conformidade}")
                else:
                    st.warning(f"⚠️ Status: {conformidade}")
                
                st.write(f"**Resumo:** {result.get('resumo', 'N/A')}")
                
                pontos = result.get('pontos_atencao', [])
                if pontos:
                    st.write("**Pontos de Atenção:**")
                    for i, ponto in enumerate(pontos, 1):
                        criticidade = ponto.get('criticidade', 'N/A')
                        emoji = "🔴" if criticidade == "CRITICO" else "🟡" if criticidade == "ATENCAO" else "🟢"
                        
                        st.write(f"{emoji} **Ponto {i}:** {ponto.get('problema', 'N/A')}")
                        st.write(f"**Base legal:** {ponto.get('artigo_cvm', 'N/A')}")
                        st.write(f"**Sugestão:** {ponto.get('sugestao', 'N/A')}")
                        st.write("---")

def render_document_comparison():
    """Renderiza a interface de comparação de documentos"""
    st.markdown("""
    <div class="solvi-card">
        <div class="solvi-card-header">
            <div class="solvi-card-icon">📚</div>
            <h2 class="solvi-card-title">Comparação Inteligente de Documentos</h2>
        </div>
        <p style="color: #666; font-size: 1.3rem; line-height: 1.8; font-weight: 500;">
            Compare dois documentos (PDF ou Word) e identifique apenas as alterações reais de conteúdo, 
            ignorando mudanças de formatação e posicionamento com algoritmo avançado de normalização.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Layout em colunas para upload
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📄 Documento de Referência")
        arquivo_ref = st.file_uploader(
            "Escolha o arquivo de referência",
            type=['pdf', 'docx'],
            key="ref_uploader",
            help="Este será usado como base para comparação"
        )
        
        if arquivo_ref:
            st.markdown(f"""
            <div class="solvi-alert success">
                ✅ <strong>Arquivo carregado:</strong> {arquivo_ref.name}<br>
                📊 <strong>Tamanho:</strong> {arquivo_ref.size / 1024 / 1024:.2f} MB<br>
                📋 <strong>Tipo:</strong> {arquivo_ref.type.split('/')[-1].upper()}
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 📄 Novo Documento")
        arquivo_novo = st.file_uploader(
            "Escolha o novo arquivo",
            type=['pdf', 'docx'],
            key="novo_uploader",
            help="Este será comparado com o arquivo de referência"
        )
        
        if arquivo_novo:
            st.markdown(f"""
            <div class="solvi-alert success">
                ✅ <strong>Arquivo carregado:</strong> {arquivo_novo.name}<br>
                📊 <strong>Tamanho:</strong> {arquivo_novo.size / 1024 / 1024:.2f} MB<br>
                📋 <strong>Tipo:</strong> {arquivo_novo.type.split('/')[-1].upper()}
            </div>
            """, unsafe_allow_html=True)
    
    # Informações sobre o algoritmo
    if not arquivo_ref or not arquivo_novo:
        st.markdown("""
        <div class="solvi-upload">
            <div class="solvi-upload-icon">📚</div>
            <div class="solvi-upload-text">Algoritmo Inteligente de Comparação</div>
            <div class="solvi-upload-subtext">
                ✅ Ignora mudanças de posicionamento e formatação<br>
                ✅ Foca apenas em alterações reais de conteúdo<br>
                ✅ Detecta modificações com alta precisão<br>
                ✅ Normaliza texto para comparação precisa<br>
                ✅ Análise por similaridade semântica avançada
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Botão de comparação
    if arquivo_ref and arquivo_novo:
        # Verificar compatibilidade de tipos
        comparator = DocumentComparator()
        tipo_ref = comparator.detectar_tipo_arquivo(arquivo_ref.name)
        tipo_novo = comparator.detectar_tipo_arquivo(arquivo_novo.name)
        
        if tipo_ref != tipo_novo:
            st.markdown(f"""
            <div class="solvi-alert warning">
                ⚠️ <strong>Tipos diferentes detectados:</strong> {tipo_ref.upper()} vs {tipo_novo.upper()}<br>
                A comparação ainda é possível, mas pode não ser ideal.
            </div>
            """, unsafe_allow_html=True)
        
        if st.button("🔍 Comparar Documentos", type="primary", use_container_width=True):
            with st.spinner("🔄 Processando comparação..."):
                try:
                    # Extrair textos
                    ref_bytes = arquivo_ref.read()
                    novo_bytes = arquivo_novo.read()
                    
                    if tipo_ref == 'pdf':
                        texto_ref = comparator.extrair_texto_pdf(ref_bytes)
                    else:
                        texto_ref = comparator.extrair_texto_word(ref_bytes)
                    
                    if tipo_novo == 'pdf':
                        texto_novo = comparator.extrair_texto_pdf(novo_bytes)
                    else:
                        texto_novo = comparator.extrair_texto_word(novo_bytes)
                    
                    if not texto_ref or not texto_novo:
                        st.error("❌ Erro ao extrair texto dos documentos")
                        return
                    
                    # Comparar textos
                    diferencas_simples = []
                    
                    max_paginas = max(len(texto_ref), len(texto_novo))
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    for i in range(max_paginas):
                        status_text.text(f"Analisando página/seção {i+1} de {max_paginas}")
                        
                        ref = texto_ref[i] if i < len(texto_ref) else ""
                        novo = texto_novo[i] if i < len(texto_novo) else ""
                        
                        paragrafos_ref = comparator.dividir_em_paragrafos(ref)
                        paragrafos_novo = comparator.dividir_em_paragrafos(novo)
                        
                        alteracoes = comparator.encontrar_alteracoes_reais(paragrafos_ref, paragrafos_novo)
                        
                        if alteracoes:
                            for j, alteracao in enumerate(alteracoes):
                                tipo_mapeado = {
                                    'removido': 'Removido',
                                    'adicionado': 'Adicionado',
                                    'modificado': 'Modificado'
                                }[alteracao['tipo']]
                                
                                diferencas_simples.append({
                                    'pagina': i + 1,
                                    'paragrafo': j + 1,
                                    'tipo': tipo_mapeado,
                                    'conteudo_original': alteracao['texto_original'],
                                    'conteudo_novo': alteracao['texto_novo']
                                })
                        
                        progress_bar.progress((i + 1) / max_paginas)
                    
                    progress_bar.empty()
                    status_text.empty()
                    
                    # Salvar resultados
                    st.session_state.comparison_results = {
                        'diferencas': diferencas_simples,
                        'arquivo_ref': arquivo_ref.name,
                        'arquivo_novo': arquivo_novo.name
                    }
                    
                    st.markdown("""
                    <div class="solvi-alert success">
                        ✅ <strong>Comparação concluída com sucesso!</strong><br>
                        Confira os resultados detalhados abaixo.
                    </div>
                    """, unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"❌ Erro durante a comparação: {str(e)}")
    
    # Exibir resultados se disponíveis
    if st.session_state.comparison_results:
        results = st.session_state.comparison_results
        diferencas = results['diferencas']
        
        st.markdown("### 📊 Resultados da Comparação")
        
        # Métricas
        total_diferencas = len(diferencas)
        adicionados = len([d for d in diferencas if d['tipo'] == 'Adicionado'])
        removidos = len([d for d in diferencas if d['tipo'] == 'Removido'])
        modificados = len([d for d in diferencas if d['tipo'] == 'Modificado'])
        
        st.markdown(f"""
        <div class="solvi-metrics">
            <div class="solvi-metric">
                <div class="solvi-metric-value">{total_diferencas}</div>
                <div class="solvi-metric-label">Total de Alterações</div>
            </div>
            <div class="solvi-metric">
                <div class="solvi-metric-value">{adicionados}</div>
                <div class="solvi-metric-label">Adicionados</div>
            </div>
            <div class="solvi-metric">
                <div class="solvi-metric-value">{removidos}</div>
                <div class="solvi-metric-label">Removidos</div>
            </div>
            <div class="solvi-metric">
                <div class="solvi-metric-value">{modificados}</div>
                <div class="solvi-metric-label">Modificados</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Tabela de diferenças
        if diferencas:
            st.markdown("### 📋 Detalhes das Alterações")
            df = pd.DataFrame(diferencas)
            st.dataframe(df, use_container_width=True)
        else:
            st.markdown("""
            <div class="solvi-alert success">
                ✅ <strong>Nenhuma diferença encontrada!</strong><br>
                Os documentos são idênticos em conteúdo.
            </div>
            """, unsafe_allow_html=True)

def render_footer():
    """Renderiza o footer da aplicação"""
    st.markdown("""
    <div class="solvi-footer">
        <div class="solvi-footer-content">
            <img src="https://static.wixstatic.com/media/b5b170_1e07cf7f7f82492a9808f9ae7f038596~mv2.png/v1/crop/x_0,y_0,w_2742,h_1106/fill/w_92,h_37,al_c,q_85,usm_0.66_1.00_0.01,enc_auto/Logotipo%20Solv%C3%AD_edited_edited.png" alt="Solví Logo" class="solvi-footer-logo">
            <p style="margin: 2rem 0 1rem 0; font-size: 1.4rem; font-weight: 700;">
                🌱 Plataforma Solví - Soluções Inteligentes para Análise de Documentos
            </p>
            <p style="margin: 0; opacity: 0.9; font-size: 1.1rem; font-weight: 500;">
                Desenvolvido com ❤️ para sustentabilidade e inovação • Soluções para a vida
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

def main():
    """Função principal da aplicação"""
    # Inicializar session state
    init_session_state()
    
    # Renderizar header
    render_header()
    
    # Renderizar seção inspiracional
    render_inspiration_section()
    
    # Renderizar navegação
    render_navigation()
    
    # Renderizar conteúdo baseado na aba selecionada
    if st.session_state.current_tab == 'cvm':
        render_cvm_analysis()
    else:
        render_document_comparison()
    
    # Renderizar footer
    render_footer()

if __name__ == "__main__":
    main()
