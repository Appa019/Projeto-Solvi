# app_comparacao.py

import streamlit as st
import fitz  # PyMuPDF
import difflib
import pandas as pd
import io
from datetime import datetime
import base64
from typing import List, Tuple, Dict, Optional, Set
import logging
from pathlib import Path
import tempfile
import os
import re

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

# A classe permanece fora da função main
class DocumentComparator:
    # ... (todo o código da classe DocumentComparator permanece inalterado) ...
    def __init__(self):
        self.texto_ref = []
        self.texto_novo = []
        self.diferencas = []
        self.diferencas_detalhadas = []
        self.tipo_ref = None
        self.tipo_novo = None
        
    def detectar_tipo_arquivo(self, nome_arquivo: str) -> str:
        extensao = Path(nome_arquivo).suffix.lower()
        if extensao == '.pdf': return 'pdf'
        elif extensao in ['.docx', '.doc']: return 'word'
        else: return 'desconhecido'
    
    def validar_arquivo(self, arquivo_bytes: bytes, nome_arquivo: str) -> bool:
        tipo = self.detectar_tipo_arquivo(nome_arquivo)
        try:
            if tipo == 'pdf':
                doc = fitz.open(stream=arquivo_bytes, filetype="pdf")
                if doc.page_count == 0:
                    st.error(f"❌ O arquivo PDF '{nome_arquivo}' não contém páginas.")
                    return False
                doc.close()
                return True
            elif tipo == 'word':
                if not DOCX_AVAILABLE:
                    st.error("❌ Biblioteca python-docx não está disponível.")
                    return False
                with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
                    tmp_file.write(arquivo_bytes)
                    tmp_path = tmp_file.name
                try:
                    doc = Document(tmp_path)
                    if len(doc.paragraphs) == 0:
                        st.error(f"❌ O arquivo Word '{nome_arquivo}' não contém texto.")
                        return False
                    return True
                except Exception as e:
                    st.error(f"❌ Erro ao abrir arquivo Word '{nome_arquivo}': {str(e)}")
                    return False
                finally:
                    try: os.unlink(tmp_path)
                    except: pass
            else:
                st.error(f"❌ Tipo de arquivo não suportado: {nome_arquivo}")
                return False
        except Exception as e:
            st.error(f"❌ Erro ao validar '{nome_arquivo}': {str(e)}")
            return False
    
    def extrair_texto_pdf(self, pdf_bytes: bytes) -> List[str]:
        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            textos = [pagina.get_text() for pagina in doc]
            doc.close()
            return textos
        except Exception as e:
            st.error(f"❌ Erro ao extrair texto do PDF: {str(e)}")
            return []

    def extrair_texto_word(self, word_bytes: bytes) -> List[str]:
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
                tmp_file.write(word_bytes)
                tmp_path = tmp_file.name
            try:
                doc = Document(tmp_path)
                textos, texto_atual, contador_paragrafos = [], "", 0
                for paragrafo in doc.paragraphs:
                    texto_atual += paragrafo.text + "\n"
                    contador_paragrafos += 1
                    if contador_paragrafos >= 50 or "page-break" in paragrafo.text.lower():
                        if texto_atual.strip(): textos.append(texto_atual)
                        texto_atual, contador_paragrafos = "", 0
                if texto_atual.strip(): textos.append(texto_atual)
                if not textos: textos = [""]
                return textos
            finally:
                try: os.unlink(tmp_path)
                except: pass
        except Exception as e:
            st.error(f"❌ Erro ao extrair texto do Word: {str(e)}")
            return []

    def extrair_texto_por_pagina(self, arquivo_bytes: bytes, nome_arquivo: str) -> List[str]:
        tipo = self.detectar_tipo_arquivo(nome_arquivo)
        progress_bar = st.progress(0)
        try:
            if tipo == 'pdf':
                st.info("📖 Extraindo texto do PDF...")
                textos = self.extrair_texto_pdf(arquivo_bytes)
            elif tipo == 'word':
                st.info("📖 Extraindo texto do documento Word...")
                textos = self.extrair_texto_word(arquivo_bytes)
            else:
                st.error(f"❌ Tipo de arquivo não suportado: {tipo}")
                return []
            progress_bar.progress(1.0)
            progress_bar.empty()
            return textos
        except Exception as e:
            progress_bar.empty()
            st.error(f"❌ Erro ao extrair texto: {str(e)}")
            return []

    def normalizar_texto(self, texto: str) -> str:
        texto = re.sub(r'\s+', ' ', texto.strip())
        texto = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', texto)
        texto = re.sub(r'\s+([,.;:!?])', r'\1', texto)
        texto = re.sub(r'["""]', '"', texto)
        texto = re.sub(r"[''']", "'", texto)
        texto = re.sub(r'[–—]', '-', texto)
        return texto

    def dividir_em_paragrafos(self, texto: str) -> List[str]:
        texto = self.normalizar_texto(texto)
        paragrafos_brutos = re.split(r'\n\s*\n', texto)
        paragrafos = []
        for paragrafo in paragrafos_brutos:
            paragrafo = paragrafo.strip()
            if paragrafo:
                if len(paragrafo) > 500:
                    frases = re.split(r'(?<!\d)\.(?!\d)\s+', paragrafo)
                    for frase in frases:
                        frase = self.normalizar_texto(frase.strip())
                        if frase and len(frase) > 10: paragrafos.append(frase)
                else:
                    paragrafo_normalizado = self.normalizar_texto(paragrafo)
                    if paragrafo_normalizado and len(paragrafo_normalizado) > 10:
                        paragrafos.append(paragrafo_normal
