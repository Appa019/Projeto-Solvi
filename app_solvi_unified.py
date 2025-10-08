"""
🌱 Plataforma Solví - Análise Inteligente de Documentos
Versão Masterpiece - Bizarramente parecida com o site oficial da Solví
Aplicação premium que combina análise CVM e comparação de documentos
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

# Configuração da página com tema Solví
st.set_page_config(
    page_title="Plataforma Solví - Soluções Inteligentes",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.solvi.com',
        'Report a bug': 'https://www.solvi.com/contato',
        'About': "Plataforma Solví - Soluções para a vida com sustentabilidade e inovação"
    }
)

# CSS Premium Masterpiece - Bizarramente parecido com Solví
st.markdown("""
<style>
    /* Importar fontes oficiais */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800;900&display=swap');
    
    /* Reset completo e configurações globais */
    * {
        box-sizing: border-box;
        margin: 0;
        padding: 0;
    }
    
    .main .block-container {
        padding-top: 0rem;
        padding-bottom: 3rem;
        max-width: 1400px;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    
    /* Ocultar elementos padrão do Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {visibility: hidden;}
    
    /* Remover padding padrão do Streamlit */
    .css-18e3th9, .css-1d391kg {
        padding-top: 0rem;
    }
    
    /* Paleta de cores oficial Solví - Verde Escuro Dominante */
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
        --solvi-shadow-strong: rgba(13, 79, 28, 0.25);
        --solvi-gradient-primary: linear-gradient(135deg, var(--solvi-dark-green) 0%, var(--solvi-primary-green) 30%, var(--solvi-medium-green) 70%, var(--solvi-light-green) 100%);
        --solvi-gradient-surface: linear-gradient(135deg, var(--solvi-white) 0%, var(--solvi-surface) 50%, var(--solvi-background) 100%);
    }
    
    /* Header Masterpiece - Largura total e impacto visual máximo */
    .solvi-header {
        background: var(--solvi-gradient-primary);
        color: var(--solvi-text-light);
        padding: 3rem 0;
        border-radius: 0;
        margin: -2rem calc(-50vw + 50%) 3rem calc(-50vw + 50%);
        box-shadow: 0 12px 40px var(--solvi-shadow-strong);
        position: relative;
        overflow: hidden;
        min-height: 200px;
        width: 100vw;
        z-index: 10;
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
    
    .solvi-header::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        height: 8px;
        background: linear-gradient(90deg, 
            var(--solvi-bright-green) 0%, 
            var(--solvi-accent-green) 25%, 
            var(--solvi-light-green) 50%, 
            var(--solvi-medium-green) 75%, 
            var(--solvi-primary-green) 100%);
        z-index: 1;
    }
    
    .solvi-header-content {
        position: relative;
        z-index: 2;
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 2.5rem;
        max-width: 1400px;
        margin: 0 auto;
        padding: 0 3rem;
    }
    
    .solvi-logo-section {
        display: flex;
        align-items: center;
        gap: 2.5rem;
        flex: 1;
    }
    
    /* Logo Premium com Background Verde Escuro */
    .solvi-logo {
        height: 80px;
        width: auto;
        background: var(--solvi-dark-green);
        padding: 15px 25px;
        border-radius: 16px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.2);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        border: 4px solid var(--solvi-primary-green);
        filter: brightness(1.1);
    }
    
    .solvi-logo:hover {
        transform: scale(1.08) rotate(2deg);
        box-shadow: 0 12px 40px rgba(0,0,0,0.3);
        background: var(--solvi-primary-green);
        border-color: var(--solvi-medium-green);
        filter: brightness(1.2);
    }
    
    .solvi-title-section {
        flex: 2;
    }
    
    .solvi-title {
        font-size: 3.5rem;
        font-weight: 900;
        font-family: 'Poppins', sans-serif;
        margin: 0;
        text-shadow: 3px 3px 12px rgba(0,0,0,0.4);
        letter-spacing: -2px;
        line-height: 1;
        background: linear-gradient(45deg, #ffffff 0%, #f0f8ff 50%, #ffffff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .solvi-subtitle {
        font-size: 1.4rem;
        opacity: 0.95;
        margin-top: 0.8rem;
        font-weight: 600;
        letter-spacing: 0.8px;
        text-shadow: 2px 2px 6px rgba(0,0,0,0.3);
        font-family: 'Inter', sans-serif;
    }
    
    .solvi-badge {
        background: rgba(255,255,255,0.15);
        padding: 1.5rem 3rem;
        border-radius: 50px;
        font-size: 1.2rem;
        font-weight: 800;
        backdrop-filter: blur(20px);
        border: 3px solid rgba(255,255,255,0.25);
        text-transform: uppercase;
        letter-spacing: 2px;
        box-shadow: 0 6px 25px rgba(0,0,0,0.15);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        font-family: 'Poppins', sans-serif;
        white-space: nowrap;
    }
    
    .solvi-badge:hover {
        background: rgba(255,255,255,0.25);
        transform: translateY(-3px) scale(1.05);
        box-shadow: 0 10px 35px rgba(0,0,0,0.2);
        border-color: rgba(255,255,255,0.4);
    }
    
    /* Seção de imagens inspiracionais premium */
    .solvi-inspiration {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 2.5rem;
        margin: 4rem 0;
        padding: 3rem;
        background: var(--solvi-gradient-surface);
        border-radius: 28px;
        border: 3px solid var(--solvi-light-green);
        box-shadow: 0 12px 40px var(--solvi-shadow);
        position: relative;
        overflow: hidden;
    }
    
    .solvi-inspiration::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 6px;
        background: var(--solvi-gradient-primary);
        z-index: 1;
    }
    
    .solvi-inspiration-item {
        position: relative;
        border-radius: 20px;
        overflow: hidden;
        box-shadow: 0 10px 35px var(--solvi-shadow);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        background: var(--solvi-white);
        border: 3px solid var(--solvi-background);
        transform-origin: center;
    }
    
    .solvi-inspiration-item:hover {
        transform: translateY(-12px) scale(1.02);
        box-shadow: 0 20px 60px var(--solvi-shadow-strong);
        border-color: var(--solvi-light-green);
    }
    
    .solvi-inspiration-image {
        width: 100%;
        height: 200px;
        object-fit: cover;
        border-radius: 20px 20px 0 0;
        transition: all 0.4s ease;
    }
    
    .solvi-inspiration-item:hover .solvi-inspiration-image {
        transform: scale(1.05);
        filter: brightness(1.1) saturate(1.2);
    }
    
    .solvi-inspiration-content {
        padding: 2.5rem;
        background: var(--solvi-gradient-surface);
        position: relative;
    }
    
    .solvi-inspiration-title {
        font-size: 1.4rem;
        font-weight: 800;
        color: var(--solvi-text-dark);
        margin: 0 0 1.2rem 0;
        font-family: 'Poppins', sans-serif;
        letter-spacing: -0.5px;
    }
    
    .solvi-inspiration-desc {
        font-size: 1.05rem;
        color: #555;
        line-height: 1.7;
        margin: 0;
        font-weight: 500;
        font-family: 'Inter', sans-serif;
    }
    
    /* Navegação premium estilo Solví */
    .solvi-navigation {
        background: var(--solvi-gradient-surface);
        border-radius: 24px;
        padding: 2rem;
        margin: 4rem 0;
        box-shadow: 0 12px 45px var(--solvi-shadow);
        border: 3px solid var(--solvi-background);
        position: relative;
        overflow: hidden;
    }
    
    .solvi-navigation::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 6px;
        background: var(--solvi-gradient-primary);
        z-index: 1;
    }
    
    /* Cards premium estilo Solví */
    .solvi-card {
        background: var(--solvi-gradient-surface);
        border-radius: 28px;
        padding: 3.5rem;
        margin: 3rem 0;
        box-shadow: 0 20px 60px var(--solvi-shadow);
        border: 3px solid var(--solvi-background);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
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
        background: var(--solvi-gradient-primary);
        z-index: 1;
    }
    
    .solvi-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 30px 80px var(--solvi-shadow-strong);
        border-color: var(--solvi-light-green);
    }
    
    .solvi-card-header {
        display: flex;
        align-items: center;
        margin-bottom: 3rem;
        padding-bottom: 2.5rem;
        border-bottom: 4px solid var(--solvi-background);
        position: relative;
    }
    
    .solvi-card-icon {
        width: 80px;
        height: 80px;
        background: var(--solvi-gradient-primary);
        border-radius: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 2.5rem;
        font-size: 2.5rem;
        box-shadow: 0 10px 30px var(--solvi-shadow);
        border: 4px solid var(--solvi-white);
        transition: all 0.3s ease;
    }
    
    .solvi-card-icon:hover {
        transform: scale(1.1) rotate(5deg);
        box-shadow: 0 15px 40px var(--solvi-shadow-strong);
    }
    
    .solvi-card-title {
        font-size: 2.2rem;
        font-weight: 900;
        color: var(--solvi-text-dark);
        margin: 0;
        font-family: 'Poppins', sans-serif;
        letter-spacing: -1px;
        line-height: 1.2;
    }
    
    /* Métricas premium estilo Solví */
    .solvi-metrics {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
        gap: 3rem;
        margin: 4rem 0;
    }
    
    .solvi-metric {
        background: var(--solvi-gradient-surface);
        border-radius: 28px;
        padding: 3.5rem;
        text-align: center;
        border: 3px solid var(--solvi-background);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
        box-shadow: 0 15px 50px var(--solvi-shadow);
    }
    
    .solvi-metric::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 8px;
        background: var(--solvi-gradient-primary);
        z-index: 1;
    }
    
    .solvi-metric:hover {
        transform: translateY(-12px) scale(1.02);
        box-shadow: 0 25px 70px var(--solvi-shadow-strong);
        border-color: var(--solvi-light-green);
    }
    
    .solvi-metric-value {
        font-size: 4.5rem;
        font-weight: 900;
        color: var(--solvi-primary-green);
        margin-bottom: 1.5rem;
        font-family: 'Poppins', sans-serif;
        line-height: 1;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.1);
        background: var(--solvi-gradient-primary);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .solvi-metric-label {
        color: #555;
        font-size: 1.2rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-family: 'Inter', sans-serif;
    }
    
    /* Botões premium estilo Solví */
    .stButton > button {
        background: var(--solvi-gradient-primary);
        color: var(--solvi-text-light);
        border: none;
        border-radius: 24px;
        padding: 1.8rem 4rem;
        font-weight: 800;
        font-size: 1.3rem;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 10px 30px var(--solvi-shadow);
        font-family: 'Poppins', sans-serif;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        border: 4px solid transparent;
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s;
    }
    
    .stButton > button:hover::before {
        left: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-6px) scale(1.02);
        box-shadow: 0 15px 50px var(--solvi-shadow-strong);
        background: linear-gradient(135deg, var(--solvi-dark-green) 0%, var(--solvi-primary-green) 50%, var(--solvi-medium-green) 100%);
        border-color: var(--solvi-white);
    }
    
    /* Alertas premium estilo Solví */
    .solvi-alert {
        border-radius: 24px;
        padding: 3rem 3.5rem;
        margin: 3rem 0;
        border-left: 10px solid;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
        position: relative;
        overflow: hidden;
        box-shadow: 0 12px 40px rgba(0,0,0,0.1);
        font-size: 1.15rem;
        line-height: 1.6;
    }
    
    .solvi-alert.success {
        background: var(--solvi-gradient-surface);
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
    
    /* Upload areas premium com pontilhado contínuo */
    .solvi-upload {
        border: 5px dashed var(--solvi-light-green);
        border-radius: 28px;
        padding: 5rem 4rem;
        text-align: center;
        background: var(--solvi-gradient-surface);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        margin: 3rem 0;
        box-shadow: 0 15px 50px var(--solvi-shadow);
        position: relative;
        overflow: hidden;
    }
    
    /* Pontilhado contínuo animado premium */
    .solvi-upload::before {
        content: '';
        position: absolute;
        top: -3px;
        left: -3px;
        right: -3px;
        bottom: -3px;
        border: 5px dashed var(--solvi-primary-green);
        border-radius: 28px;
        animation: dash 25s linear infinite;
        opacity: 0.7;
        z-index: 0;
    }
    
    @keyframes dash {
        0% {
            stroke-dashoffset: 0;
            transform: rotate(0deg);
        }
        100% {
            stroke-dashoffset: 50px;
            transform: rotate(360deg);
        }
    }
    
    .solvi-upload:hover {
        border-color: var(--solvi-primary-green);
        background: linear-gradient(135deg, var(--solvi-surface) 0%, var(--solvi-background) 50%, #dcedc8 100%);
        transform: translateY(-8px) scale(1.01);
        box-shadow: 0 20px 70px var(--solvi-shadow-strong);
    }
    
    .solvi-upload:hover::before {
        border-color: var(--solvi-dark-green);
        opacity: 0.9;
        animation-duration: 15s;
    }
    
    .solvi-upload-icon {
        font-size: 5rem;
        color: var(--solvi-light-green);
        margin-bottom: 2.5rem;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.1);
        position: relative;
        z-index: 1;
        transition: all 0.3s ease;
    }
    
    .solvi-upload:hover .solvi-upload-icon {
        transform: scale(1.1) rotate(5deg);
        color: var(--solvi-primary-green);
    }
    
    .solvi-upload-text {
        font-size: 1.8rem;
        font-weight: 800;
        color: var(--solvi-text-dark);
        margin-bottom: 1.5rem;
        font-family: 'Poppins', sans-serif;
        position: relative;
        z-index: 1;
        letter-spacing: -0.5px;
    }
    
    .solvi-upload-subtext {
        font-size: 1.2rem;
        color: #666;
        line-height: 1.8;
        font-weight: 500;
        position: relative;
        z-index: 1;
        font-family: 'Inter', sans-serif;
    }
    
    /* Footer premium */
    .solvi-footer {
        background: var(--solvi-gradient-primary);
        color: var(--solvi-text-light);
        padding: 5rem 3rem;
        border-radius: 28px;
        margin: 5rem 0 3rem 0;
        text-align: center;
        box-shadow: 0 20px 60px var(--solvi-shadow-strong);
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
        opacity: 0.06;
        z-index: 0;
    }
    
    .solvi-footer-content {
        position: relative;
        z-index: 1;
    }
    
    .solvi-footer-logo {
        height: 70px;
        margin-bottom: 2.5rem;
        background: var(--solvi-dark-green);
        padding: 15px 25px;
        border-radius: 16px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.3);
        border: 4px solid var(--solvi-primary-green);
        transition: all 0.3s ease;
    }
    
    .solvi-footer-logo:hover {
        transform: scale(1.05);
        box-shadow: 0 12px 35px rgba(0,0,0,0.4);
    }
    
    /* Responsividade premium */
    @media (max-width: 768px) {
        .solvi-header {
            padding: 2.5rem 0;
            min-height: 180px;
        }
        
        .solvi-header-content {
            flex-direction: column;
            text-align: center;
            gap: 2rem;
            padding: 0 1.5rem;
        }
        
        .solvi-title {
            font-size: 2.5rem;
        }
        
        .solvi-subtitle {
            font-size: 1.2rem;
        }
        
        .solvi-logo {
            height: 70px;
        }
        
        .solvi-inspiration {
            grid-template-columns: 1fr;
            padding: 2.5rem;
        }
        
        .solvi-metrics {
            grid-template-columns: 1fr;
        }
        
        .solvi-metric-value {
            font-size: 4rem;
        }
        
        .solvi-card {
            padding: 3rem;
        }
        
        .solvi-upload {
            padding: 4rem 2.5rem;
        }
        
        .solvi-badge {
            padding: 1.2rem 2.5rem;
            font-size: 1rem;
        }
    }
    
    /* Animações premium */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(60px);
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
            transform: scale(1.03);
        }
    }
    
    @keyframes float {
        0%, 100% {
            transform: translateY(0px);
        }
        50% {
            transform: translateY(-10px);
        }
    }
    
    .solvi-card, .solvi-metric, .solvi-inspiration-item {
        animation: fadeInUp 0.8s ease-out;
    }
    
    .solvi-logo {
        animation: pulse 5s ease-in-out infinite;
    }
    
    .solvi-badge {
        animation: float 6s ease-in-out infinite;
    }
    
    /* Scrollbar premium personalizada */
    ::-webkit-scrollbar {
        width: 14px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--solvi-surface);
        border-radius: 14px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--solvi-gradient-primary);
        border-radius: 14px;
        border: 3px solid var(--solvi-surface);
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, var(--solvi-dark-green) 0%, var(--solvi-primary-green) 100%);
    }
    
    /* Efeitos especiais premium */
    .solvi-glow {
        box-shadow: 0 0 20px var(--solvi-accent-green);
    }
    
    .solvi-shimmer {
        background: linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.5) 50%, transparent 70%);
        background-size: 200% 200%;
        animation: shimmer 3s ease-in-out infinite;
    }
    
    @keyframes shimmer {
        0% {
            background-position: -200% -200%;
        }
        100% {
            background-position: 200% 200%;
        }
    }
</style>
""", unsafe_allow_html=True)

# Inicializar session state
def init_session_state():
    """Inicializa o estado da sessão com configurações premium"""
    if 'current_tab' not in st.session_state:
        st.session_state.current_tab = 'cvm'
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    if 'comparison_results' not in st.session_state:
        st.session_state.comparison_results = None
    if 'sidebar_expanded' not in st.session_state:
        st.session_state.sidebar_expanded = True

class FREAnalyzer:
    """Classe premium para análise de FRE vs Normas CVM"""
    
    def __init__(self, api_key):
        openai.api_key = api_key
        self.client = openai.OpenAI(api_key=api_key)
        
    def extract_text_from_pdf(self, pdf_file):
        """Extrai texto de arquivo PDF com tratamento premium"""
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            st.error(f"❌ Erro ao extrair texto do PDF: {str(e)}")
            return ""
    
    def extract_text_from_docx(self, docx_file):
        """Extrai texto de arquivo Word com tratamento premium"""
        try:
            doc = docx.Document(docx_file)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            st.error(f"❌ Erro ao extrair texto do Word: {str(e)}")
            return ""
    
    def extract_text_from_file(self, uploaded_file):
        """Extrai texto baseado no tipo de arquivo"""
        if uploaded_file.type == "application/pdf":
            return self.extract_text_from_pdf(uploaded_file)
        elif uploaded_file.type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", 
                                   "application/msword"]:
            return self.extract_text_from_docx(uploaded_file)
        else:
            st.error("❌ Formato de arquivo não suportado. Use PDF ou Word.")
            return ""
    
    def analyze_fre_section(self, fre_text, cvm_references, section_name, section_content):
        """Analisa uma seção específica do FRE contra as normas CVM"""
        
        prompt = f"""
        Você é um especialista premium em regulamentação CVM e análise de Formulários de Referência (FRE).
        
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
            st.error(f"❌ Erro na análise da seção {section_name}: {str(e)}")
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
    """Classe premium para comparação de documentos"""
    
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
            st.error(f"❌ Erro ao extrair texto do PDF: {str(e)}")
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
            st.error(f"❌ Erro ao extrair texto do Word: {str(e)}")
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
    """Renderiza o header masterpiece da aplicação"""
    st.markdown("""
    <div class="solvi-header">
        <div class="solvi-header-content">
            <div class="solvi-logo-section">
                <img src="https://static.wixstatic.com/media/b5b170_1e07cf7f7f82492a9808f9ae7f038596~mv2.png/v1/crop/x_0,y_0,w_2742,h_1106/fill/w_92,h_37,al_c,q_85,usm_0.66_1.00_0.01,enc_auto/Logotipo%20Solv%C3%AD_edited_edited.png" alt="Solví Logo" class="solvi-logo">
                <div class="solvi-title-section">
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
    """Renderiza seção de imagens inspiracionais premium"""
    st.markdown("""
    <div class="solvi-inspiration">
        <div class="solvi-inspiration-item">
            <img src="https://images.unsplash.com/photo-1558618666-fcd25c85cd64?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80" alt="Tecnologia Sustentável" class="solvi-inspiration-image">
            <div class="solvi-inspiration-content">
                <h3 class="solvi-inspiration-title">🔋 Tecnologia Sustentável</h3>
                <p class="solvi-inspiration-desc">Inovação em energia renovável e soluções tecnológicas verdes para um futuro sustentável e próspero para todas as gerações.</p>
            </div>
        </div>
        <div class="solvi-inspiration-item">
            <img src="https://images.unsplash.com/photo-1441974231531-c6227db76b6e?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80" alt="Proteção Ambiental" class="solvi-inspiration-image">
            <div class="solvi-inspiration-content">
                <h3 class="solvi-inspiration-title">🌿 Proteção Ambiental</h3>
                <p class="solvi-inspiration-desc">Preservação da natureza e biodiversidade através de práticas ambientais responsáveis e sustentáveis que protegem nosso planeta.</p>
            </div>
        </div>
        <div class="solvi-inspiration-item">
            <img src="https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80" alt="Gestão de Resíduos" class="solvi-inspiration-image">
            <div class="solvi-inspiration-content">
                <h3 class="solvi-inspiration-title">♻️ Gestão de Resíduos</h3>
                <p class="solvi-inspiration-desc">Soluções inteligentes para reciclagem e economia circular, transformando resíduos em recursos valiosos para a sociedade.</p>
            </div>
        </div>
        <div class="solvi-inspiration-item">
            <img src="https://static.wixstatic.com/media/b5b170_b587909825174509a2a6a71af0106cc3~mv2.png/v1/fill/w_245,h_357,al_c,q_85,enc_auto/Group%2041.png" alt="Inovação Verde" class="solvi-inspiration-image">
            <div class="solvi-inspiration-content">
                <h3 class="solvi-inspiration-title">💡 Inovação Verde</h3>
                <p class="solvi-inspiration-desc">Desenvolvimento de tecnologias limpas e processos inovadores para sustentabilidade empresarial e crescimento responsável.</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_navigation():
    """Renderiza a navegação premium por abas"""
    st.markdown('<div class="solvi-navigation">', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Botão que abre sidebar automaticamente
        if st.button("📊 Análise CVM", key="tab_cvm", use_container_width=True):
            st.session_state.current_tab = 'cvm'
            st.session_state.sidebar_expanded = True
            st.rerun()
    
    with col2:
        if st.button("📚 Comparação de Documentos", key="tab_comparison", use_container_width=True):
            st.session_state.current_tab = 'comparison'
    
    st.markdown("</div>", unsafe_allow_html=True)

def render_cvm_analysis():
    """Renderiza a interface premium de análise CVM"""
    st.markdown("""
    <div class="solvi-card">
        <div class="solvi-card-header">
            <div class="solvi-card-icon">📊</div>
            <h2 class="solvi-card-title">Análise FRE vs Normas CVM</h2>
        </div>
        <p style="color: #666; font-size: 1.4rem; line-height: 1.8; font-weight: 500; font-family: 'Inter', sans-serif;">
            Análise automatizada premium de Formulários de Referência contra normas CVM com identificação 
            inteligente de não conformidades e geração de relatórios detalhados com base legal específica 
            e recomendações de melhoria personalizadas.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar premium para configurações
    with st.sidebar:
        st.markdown("### ⚙️ Configurações Premium")
        
        # Campo obrigatório para API Key
        api_key = st.text_input(
            "🔑 Chave API OpenAI *",
            type="password",
            help="Insira sua chave API da OpenAI (obrigatório para análise premium)"
        )
        
        if not api_key:
            st.markdown("""
            <div class="solvi-alert error">
                ⚠️ <strong>Chave API OpenAI é obrigatória!</strong><br>
                Configure sua chave para utilizar a análise CVM premium com IA avançada.
            </div>
            """, unsafe_allow_html=True)
            return
        
        st.markdown("---")
        
        # Upload do FRE
        st.markdown("### 📄 Arquivo FRE")
        fre_file = st.file_uploader(
            "Upload do Formulário de Referência",
            type=['pdf', 'docx'],
            help="Faça upload do FRE para análise premium"
        )
        
        st.markdown("---")
        
        # Upload dos documentos CVM
        st.markdown("### 📚 Documentos CVM (máx. 5)")
        cvm_files = st.file_uploader(
            "Upload dos documentos de referência CVM",
            type=['pdf', 'docx'],
            accept_multiple_files=True,
            help="Faça upload dos documentos CVM para comparação avançada"
        )
        
        if len(cvm_files) > 5:
            st.error("⚠️ Máximo de 5 documentos CVM permitidos para análise premium!")
            cvm_files = cvm_files[:5]
    
    # Área principal premium
    if not fre_file:
        st.markdown("""
        <div class="solvi-upload">
            <div class="solvi-upload-icon">📄</div>
            <div class="solvi-upload-text">Como usar a Análise CVM Premium</div>
            <div class="solvi-upload-subtext">
                1. Configure sua API Key OpenAI na barra lateral<br>
                2. Faça upload do FRE (Formulário de Referência)<br>
                3. Adicione documentos CVM para comparação avançada<br>
                4. Execute a análise premium e receba relatório detalhado<br>
                5. Baixe relatórios em PDF com recomendações personalizadas
            </div>
        </div>
        """, unsafe_allow_html=True)
        return
    
    if not cvm_files:
        st.markdown("""
        <div class="solvi-alert warning">
            ⚠️ <strong>Documentos CVM necessários para análise premium</strong><br>
            Adicione pelo menos um documento CVM para realizar a análise comparativa avançada com IA.
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Informações premium dos arquivos carregados
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="solvi-alert success">
            ✅ <strong>FRE Carregado:</strong> {fre_file.name}<br>
            📊 <strong>Tamanho:</strong> {fre_file.size / 1024 / 1024:.2f} MB<br>
            🎯 <strong>Status:</strong> Pronto para análise premium
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="solvi-alert info">
            📚 <strong>Documentos CVM:</strong> {len(cvm_files)} arquivo(s)<br>
            📊 <strong>Total:</strong> {sum(f.size for f in cvm_files) / 1024 / 1024:.2f} MB<br>
            🚀 <strong>Análise:</strong> IA avançada habilitada
        </div>
        """, unsafe_allow_html=True)
    
    # Botão de análise premium
    if st.button("🔍 Iniciar Análise CVM Premium", type="primary", use_container_width=True):
        with st.spinner("🔄 Processando análise premium com IA..."):
            try:
                # Inicializar analisador premium
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
                
                # Analisar cada seção com IA premium
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                analysis_results = []
                total_sections = len(fre_sections)
                
                for i, (section_name, section_content) in enumerate(fre_sections.items()):
                    status_text.text(f"🤖 Analisando com IA: {section_name}")
                    
                    result = analyzer.analyze_fre_section(
                        fre_text, cvm_text, section_name, section_content
                    )
                    
                    if result:
                        analysis_results.append(result)
                    
                    progress_bar.progress((i + 1) / total_sections)
                    time.sleep(0.5)
                
                status_text.text("✅ Análise premium concluída com sucesso!")
                progress_bar.empty()
                status_text.empty()
                
                # Salvar resultados premium
                st.session_state.analysis_results = analysis_results
                st.session_state.fre_filename = fre_file.name
                
                st.markdown("""
                <div class="solvi-alert success">
                    ✅ <strong>Análise CVM Premium concluída com sucesso!</strong><br>
                    Confira os resultados detalhados e insights avançados abaixo.
                </div>
                """, unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"❌ Erro durante a análise premium: {str(e)}")
    
    # Exibir resultados premium se disponíveis
    if st.session_state.analysis_results:
        analysis_results = st.session_state.analysis_results
        
        st.markdown("### 📊 Resultados da Análise Premium")
        
        # Métricas premium
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
        
        # Exibir resultados detalhados premium
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
    """Renderiza a interface premium de comparação de documentos"""
    st.markdown("""
    <div class="solvi-card">
        <div class="solvi-card-header">
            <div class="solvi-card-icon">📚</div>
            <h2 class="solvi-card-title">Comparação Inteligente de Documentos</h2>
        </div>
        <p style="color: #666; font-size: 1.4rem; line-height: 1.8; font-weight: 500; font-family: 'Inter', sans-serif;">
            Compare dois documentos (PDF ou Word) com algoritmo premium de IA e identifique apenas as alterações 
            reais de conteúdo, ignorando mudanças de formatação e posicionamento com normalização avançada 
            e análise semântica inteligente.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Layout premium em colunas para upload
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📄 Documento de Referência")
        arquivo_ref = st.file_uploader(
            "Escolha o arquivo de referência",
            type=['pdf', 'docx'],
            key="ref_uploader",
            help="Este será usado como base para comparação premium"
        )
        
        if arquivo_ref:
            st.markdown(f"""
            <div class="solvi-alert success">
                ✅ <strong>Arquivo carregado:</strong> {arquivo_ref.name}<br>
                📊 <strong>Tamanho:</strong> {arquivo_ref.size / 1024 / 1024:.2f} MB<br>
                📋 <strong>Tipo:</strong> {arquivo_ref.type.split('/')[-1].upper()}<br>
                🎯 <strong>Status:</strong> Pronto para análise premium
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
                📋 <strong>Tipo:</strong> {arquivo_novo.type.split('/')[-1].upper()}<br>
                🚀 <strong>Análise:</strong> IA avançada habilitada
            </div>
            """, unsafe_allow_html=True)
    
    # Informações premium sobre o algoritmo com pontilhado contínuo
    if not arquivo_ref or not arquivo_novo:
        st.markdown("""
        <div class="solvi-upload">
            <div class="solvi-upload-icon">📚</div>
            <div class="solvi-upload-text">Algoritmo Inteligente de Comparação</div>
            <div class="solvi-upload-subtext">
                ✅ Ignora mudanças de posicionamento e formatação<br>
                ✅ Foca apenas em alterações reais de conteúdo<br>
                ✅ Detecta modificações com alta precisão e IA<br>
                ✅ Normaliza texto para comparação precisa<br>
                ✅ Análise por similaridade semântica avançada<br>
                ✅ Relatórios detalhados com insights premium
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Botão de comparação premium
    if arquivo_ref and arquivo_novo:
        # Verificar compatibilidade de tipos
        comparator = DocumentComparator()
        tipo_ref = comparator.detectar_tipo_arquivo(arquivo_ref.name)
        tipo_novo = comparator.detectar_tipo_arquivo(arquivo_novo.name)
        
        if tipo_ref != tipo_novo:
            st.markdown(f"""
            <div class="solvi-alert warning">
                ⚠️ <strong>Tipos diferentes detectados:</strong> {tipo_ref.upper()} vs {tipo_novo.upper()}<br>
                A comparação premium ainda é possível com algoritmo adaptativo, mas pode não ser ideal.
            </div>
            """, unsafe_allow_html=True)
        
        if st.button("🔍 Comparar Documentos Premium", type="primary", use_container_width=True):
            with st.spinner("🔄 Processando comparação premium com IA..."):
                try:
                    # Extrair textos premium
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
                    
                    # Comparar textos com algoritmo premium
                    diferencas_simples = []
                    
                    max_paginas = max(len(texto_ref), len(texto_novo))
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    for i in range(max_paginas):
                        status_text.text(f"🤖 Analisando com IA página/seção {i+1} de {max_paginas}")
                        
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
                    
                    # Salvar resultados premium
                    st.session_state.comparison_results = {
                        'diferencas': diferencas_simples,
                        'arquivo_ref': arquivo_ref.name,
                        'arquivo_novo': arquivo_novo.name
                    }
                    
                    st.markdown("""
                    <div class="solvi-alert success">
                        ✅ <strong>Comparação premium concluída com sucesso!</strong><br>
                        Confira os resultados detalhados e insights avançados abaixo.
                    </div>
                    """, unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"❌ Erro durante a comparação premium: {str(e)}")
    
    # Exibir resultados premium se disponíveis
    if st.session_state.comparison_results:
        results = st.session_state.comparison_results
        diferencas = results['diferencas']
        
        st.markdown("### 📊 Resultados da Comparação Premium")
        
        # Métricas premium
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
        
        # Tabela premium de diferenças
        if diferencas:
            st.markdown("### 📋 Detalhes das Alterações Premium")
            df = pd.DataFrame(diferencas)
            st.dataframe(df, use_container_width=True)
        else:
            st.markdown("""
            <div class="solvi-alert success">
                ✅ <strong>Nenhuma diferença encontrada!</strong><br>
                Os documentos são idênticos em conteúdo após análise premium com IA.
            </div>
            """, unsafe_allow_html=True)

def render_footer():
    """Renderiza o footer premium da aplicação"""
    st.markdown("""
    <div class="solvi-footer">
        <div class="solvi-footer-content">
            <img src="https://static.wixstatic.com/media/b5b170_1e07cf7f7f82492a9808f9ae7f038596~mv2.png/v1/crop/x_0,y_0,w_2742,h_1106/fill/w_92,h_37,al_c,q_85,usm_0.66_1.00_0.01,enc_auto/Logotipo%20Solv%C3%AD_edited_edited.png" alt="Solví Logo" class="solvi-footer-logo">
            <p style="margin: 3rem 0 1.5rem 0; font-size: 1.6rem; font-weight: 800; font-family: 'Poppins', sans-serif;">
                🌱 Plataforma Solví - Soluções Inteligentes Premium para Análise de Documentos
            </p>
            <p style="margin: 0; opacity: 0.95; font-size: 1.2rem; font-weight: 600; font-family: 'Inter', sans-serif;">
                Desenvolvido com ❤️ para sustentabilidade e inovação • Soluções para a vida • Tecnologia Premium
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

def main():
    """Função principal masterpiece da aplicação"""
    # Inicializar session state premium
    init_session_state()
    
    # Renderizar header masterpiece
    render_header()
    
    # Renderizar seção inspiracional premium
    render_inspiration_section()
    
    # Renderizar navegação premium
    render_navigation()
    
    # Renderizar conteúdo premium baseado na aba selecionada
    if st.session_state.current_tab == 'cvm':
        render_cvm_analysis()
    else:
        render_document_comparison()
    
    # Renderizar footer premium
    render_footer()

if __name__ == "__main__":
    main()
