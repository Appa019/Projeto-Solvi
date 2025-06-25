"""
📚 Document Comparator - Aplicação Streamlit
Compara dois arquivos (PDF ou Word) e mostra diferenças lado a lado
Versão com frases completas e identificação clara de alterações
"""

import streamlit as st
import fitz  # PyMuPDF
import difflib
import pandas as pd
import io
from datetime import datetime
import base64
from typing import List, Tuple, Dict, Optional
import logging
from pathlib import Path
import tempfile
import os
import re

# Importações condicionais para Word
try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

# Configuração da página
st.set_page_config(
    page_title="Document Comparator",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado para comparação lado a lado
st.markdown("""
<style>
    /* Estilo para comparação lado a lado */
    .comparison-container {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        margin: 20px 0;
        overflow: hidden;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .page-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px 20px;
        font-weight: bold;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .comparison-content {
        display: flex;
        min-height: 400px;
    }
    
    .document-side {
        flex: 1;
        padding: 0;
        border-right: 1px solid #e0e0e0;
    }
    
    .document-side:last-child {
        border-right: none;
    }
    
    .document-title {
        background: #f8f9fa;
        padding: 12px 20px;
        font-weight: bold;
        color: #495057;
        border-bottom: 1px solid #e0e0e0;
        text-align: center;
    }
    
    .document-content {
        padding: 20px;
        font-family: 'Georgia', 'Times New Roman', serif;
        font-size: 14px;
        line-height: 1.8;
        background: #fafafa;
        min-height: 350px;
    }
    
    .sentence-block {
        margin: 12px 0;
        padding: 10px 15px;
        border-radius: 6px;
        border-left: 4px solid transparent;
        position: relative;
    }
    
    .sentence-normal {
        background-color: #f9f9f9;
        border-left-color: #e0e0e0;
        color: #555;
    }
    
    .sentence-added {
        background-color: #e8f5e8;
        border-left-color: #4caf50;
        color: #2e7d32;
        font-weight: 500;
    }
    
    .sentence-removed {
        background-color: #ffebee;
        border-left-color: #f44336;
        color: #c62828;
        text-decoration: line-through;
    }
    
    .sentence-modified {
        background-color: #fff3cd;
        border-left-color: #ffc107;
        color: #856404;
    }
    
    .line-number {
        position: absolute;
        left: -35px;
        top: 10px;
        width: 30px;
        font-size: 11px;
        color: #666;
        font-family: 'Courier New', monospace;
        text-align: right;
    }
    
    .change-indicator {
        position: absolute;
        right: 10px;
        top: 10px;
        font-size: 12px;
        font-weight: bold;
    }
    
    .indicator-added { color: #4caf50; }
    .indicator-removed { color: #f44336; }
    .indicator-modified { color: #ff9800; }
    
    .summary-stats {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 15px;
        margin: 20px 0;
    }
    
    .stat-card {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .stat-number {
        font-size: 2.5em;
        font-weight: bold;
        color: #667eea;
        display: block;
        margin-bottom: 5px;
    }
    
    .stat-label {
        color: #666;
        font-size: 0.9em;
    }
    
    .legend-container {
        display: flex;
        justify-content: center;
        gap: 30px;
        margin: 20px 0;
        padding: 15px;
        background: #f8f9fa;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
    }
    
    .legend-item {
        display: flex;
        align-items: center;
        gap: 8px;
        font-weight: 500;
    }
    
    .legend-sample {
        padding: 6px 12px;
        border-radius: 4px;
        font-size: 12px;
        border-left: 3px solid;
    }
    
    .legend-added { 
        background-color: #e8f5e8; 
        border-left-color: #4caf50; 
        color: #2e7d32; 
    }
    
    .legend-removed { 
        background-color: #ffebee; 
        border-left-color: #f44336; 
        color: #c62828; 
        text-decoration: line-through; 
    }
    
    .legend-modified { 
        background-color: #fff3cd; 
        border-left-color: #ffc107; 
        color: #856404; 
    }
    
    .no-changes {
        text-align: center;
        padding: 60px 20px;
        background: linear-gradient(135deg, #e8f5e8 0%, #f1f8e9 100%);
        border: 2px dashed #4caf50;
        border-radius: 12px;
        margin: 20px 0;
    }
    
    .no-changes h2 {
        color: #2e7d32;
        font-size: 2rem;
        margin-bottom: 15px;
    }
    
    .no-changes p {
        color: #4caf50;
        font-size: 1.1rem;
    }
</style>
""", unsafe_allow_html=True)

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentComparator:
    """Classe principal para comparação de documentos (PDF e Word)"""
    
    def __init__(self):
        self.texto_ref = []
        self.texto_novo = []
        self.comparacoes_lado_a_lado = []
        self.tipo_ref = None
        self.tipo_novo = None
        
    def detectar_tipo_arquivo(self, nome_arquivo: str) -> str:
        """Detecta o tipo do arquivo baseado na extensão"""
        extensao = Path(nome_arquivo).suffix.lower()
        if extensao == '.pdf':
            return 'pdf'
        elif extensao in ['.docx', '.doc']:
            return 'word'
        else:
            return 'desconhecido'
    
    def validar_arquivo(self, arquivo_bytes: bytes, nome_arquivo: str) -> bool:
        """Valida se o arquivo é válido baseado no tipo"""
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
                    st.error("❌ Biblioteca python-docx não está disponível. Instale com: pip install python-docx")
                    return False
                
                # Salvar temporariamente para validar
                with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
                    tmp_file.write(arquivo_bytes)
                    tmp_path = tmp_file.name
                
                try:
                    doc = Document(tmp_path)
                    # Verificar se tem pelo menos um parágrafo
                    if len(doc.paragraphs) == 0:
                        st.error(f"❌ O arquivo Word '{nome_arquivo}' não contém texto.")
                        return False
                    return True
                except Exception as e:
                    st.error(f"❌ Erro ao abrir arquivo Word '{nome_arquivo}': {str(e)}")
                    return False
                finally:
                    # Limpar arquivo temporário
                    try:
                        os.unlink(tmp_path)
                    except:
                        pass
            else:
                st.error(f"❌ Tipo de arquivo não suportado: {nome_arquivo}")
                return False
                
        except Exception as e:
            st.error(f"❌ Erro ao validar '{nome_arquivo}': {str(e)}")
            return False
    
    def extrair_texto_pdf(self, pdf_bytes: bytes) -> List[str]:
        """Extrai texto de cada página do PDF"""
        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            textos = []
            
            total_paginas = doc.page_count
            
            for i, pagina in enumerate(doc):
                texto = pagina.get_text()
                textos.append(texto)
            
            doc.close()
            return textos
            
        except Exception as e:
            st.error(f"❌ Erro ao extrair texto do PDF: {str(e)}")
            return []
    
    def extrair_texto_word(self, word_bytes: bytes) -> List[str]:
        """Extrai texto do documento Word (simula páginas por seções)"""
        try:
            # Salvar temporariamente para processar
            with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
                tmp_file.write(word_bytes)
                tmp_path = tmp_file.name
            
            try:
                doc = Document(tmp_path)
                
                # Para Word, vamos simular "páginas" agrupando parágrafos
                # Cada "página" terá aproximadamente 50 parágrafos ou quebras de seção
                textos = []
                texto_atual = ""
                contador_paragrafos = 0
                
                for paragrafo in doc.paragraphs:
                    texto_atual += paragrafo.text + "\n"
                    contador_paragrafos += 1
                    
                    # Criar nova "página" a cada 50 parágrafos ou quebra de seção
                    if contador_paragrafos >= 50 or "page-break" in paragrafo.text.lower():
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
    
    def extrair_texto_por_pagina(self, arquivo_bytes: bytes, nome_arquivo: str) -> List[str]:
        """Extrai texto baseado no tipo do arquivo"""
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
    
    def dividir_em_sentencas(self, texto: str) -> List[str]:
        """Divide o texto em sentenças mais inteligentemente"""
        # Dividir por quebras de linha primeiro
        linhas = texto.split('\n')
        sentencas = []
        
        for linha in linhas:
            linha = linha.strip()
            if linha:
                # Dividir por pontos, mas preservar números decimais
                partes = re.split(r'(?<!\d)\.(?!\d)', linha)
                for parte in partes:
                    parte = parte.strip()
                    if parte:
                        sentencas.append(parte)
            else:
                # Preservar linhas vazias como separadores
                sentencas.append("")
        
        return sentencas
    
    def gerar_comparacao_lado_a_lado(self, texto_ref: List[str], texto_novo: List[str]) -> List[Dict]:
        """Gera comparação lado a lado com frases completas"""
        comparacoes = []
        
        max_paginas = max(len(texto_ref), len(texto_novo))
        progress_bar = st.progress(0)
        
        for i in range(max_paginas):
            # Garantir que ambos os textos existam
            ref = texto_ref[i] if i < len(texto_ref) else ""
            novo = texto_novo[i] if i < len(texto_novo) else ""
            
            if ref.strip() != novo.strip():
                # Dividir em sentenças
                sentencas_ref = self.dividir_em_sentencas(ref)
                sentencas_novo = self.dividir_em_sentencas(novo)
                
                # Usar SequenceMatcher para encontrar diferenças
                matcher = difflib.SequenceMatcher(None, sentencas_ref, sentencas_novo)
                
                blocos_ref = []
                blocos_novo = []
                total_alteracoes = 0
                
                for tag, i1, i2, j1, j2 in matcher.get_opcodes():
                    if tag == 'equal':
                        # Sentenças iguais
                        for idx in range(i1, i2):
                            if idx < len(sentencas_ref) and sentencas_ref[idx].strip():
                                blocos_ref.append({
                                    'linha': idx + 1,
                                    'texto': sentencas_ref[idx],
                                    'tipo': 'normal'
                                })
                        
                        for idx in range(j1, j2):
                            if idx < len(sentencas_novo) and sentencas_novo[idx].strip():
                                blocos_novo.append({
                                    'linha': idx + 1,
                                    'texto': sentencas_novo[idx],
                                    'tipo': 'normal'
                                })
                                
                    elif tag == 'delete':
                        # Sentenças removidas
                        for idx in range(i1, i2):
                            if idx < len(sentencas_ref) and sentencas_ref[idx].strip():
                                blocos_ref.append({
                                    'linha': idx + 1,
                                    'texto': sentencas_ref[idx],
                                    'tipo': 'removido'
                                })
                                total_alteracoes += 1
                        
                        # Adicionar espaço vazio no lado novo
                        for idx in range(i1, i2):
                            if idx < len(sentencas_ref) and sentencas_ref[idx].strip():
                                blocos_novo.append({
                                    'linha': idx + 1,
                                    'texto': '[TEXTO REMOVIDO]',
                                    'tipo': 'vazio'
                                })
                                
                    elif tag == 'insert':
                        # Sentenças adicionadas
                        for idx in range(j1, j2):
                            if idx < len(sentencas_novo) and sentencas_novo[idx].strip():
                                blocos_novo.append({
                                    'linha': idx + 1,
                                    'texto': sentencas_novo[idx],
                                    'tipo': 'adicionado'
                                })
                                total_alteracoes += 1
                        
                        # Adicionar espaço vazio no lado referência
                        for idx in range(j1, j2):
                            if idx < len(sentencas_novo) and sentencas_novo[idx].strip():
                                blocos_ref.append({
                                    'linha': idx + 1,
                                    'texto': '[TEXTO ADICIONADO NO NOVO DOCUMENTO]',
                                    'tipo': 'vazio'
                                })
                                
                    elif tag == 'replace':
                        # Sentenças modificadas
                        max_len = max(i2 - i1, j2 - j1)
                        
                        for idx in range(max_len):
                            # Lado referência
                            if idx < (i2 - i1) and (i1 + idx) < len(sentencas_ref):
                                texto_ref_atual = sentencas_ref[i1 + idx]
                                if texto_ref_atual.strip():
                                    blocos_ref.append({
                                        'linha': i1 + idx + 1,
                                        'texto': texto_ref_atual,
                                        'tipo': 'modificado'
                                    })
                                    total_alteracoes += 1
                            
                            # Lado novo
                            if idx < (j2 - j1) and (j1 + idx) < len(sentencas_novo):
                                texto_novo_atual = sentencas_novo[j1 + idx]
                                if texto_novo_atual.strip():
                                    blocos_novo.append({
                                        'linha': j1 + idx + 1,
                                        'texto': texto_novo_atual,
                                        'tipo': 'modificado'
                                    })
                
                if blocos_ref or blocos_novo:
                    comparacoes.append({
                        'pagina': i + 1,
                        'blocos_ref': blocos_ref,
                        'blocos_novo': blocos_novo,
                        'total_alteracoes': total_alteracoes
                    })
            
            progress_bar.progress((i + 1) / max_paginas)
        
        progress_bar.empty()
        return comparacoes

def exibir_comparacao_lado_a_lado(comparacoes: List[Dict], nome_ref: str, nome_novo: str):
    """Exibe a comparação lado a lado com frases completas"""
    if not comparacoes:
        st.markdown("""
        <div class="no-changes">
            <h2>✅ Documentos Idênticos</h2>
            <p>Nenhuma diferença foi encontrada entre os documentos analisados.</p>
            <p style="margin-top: 15px; font-size: 0.9rem; opacity: 0.8;">
                💡 Os documentos possuem conteúdo textual idêntico.
            </p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Legenda
    st.markdown("""
    <div class="legend-container">
        <div class="legend-item">
            <span class="legend-sample legend-added">Texto adicionado</span>
        </div>
        <div class="legend-item">
            <span class="legend-sample legend-removed">Texto removido</span>
        </div>
        <div class="legend-item">
            <span class="legend-sample legend-modified">Texto modificado</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Exibir cada página com diferenças
    for comparacao in comparacoes:
        st.markdown(f"""
        <div class="comparison-container">
            <div class="page-header">
                <span>🔸 Página/Seção {comparacao['pagina']}</span>
                <span>{comparacao['total_alteracoes']} alteração(ões) encontrada(s)</span>
            </div>
            <div class="comparison-content">
                <div class="document-side">
                    <div class="document-title">📄 {nome_ref}</div>
                    <div class="document-content">
        """, unsafe_allow_html=True)
        
        # Exibir blocos do documento de referência
        for bloco in comparacao['blocos_ref']:
            tipo_classe = f"sentence-{bloco['tipo']}"
            indicador = ""
            
            if bloco['tipo'] == 'removido':
                indicador = '<span class="change-indicator indicator-removed">🗑️</span>'
            elif bloco['tipo'] == 'modificado':
                indicador = '<span class="change-indicator indicator-modified">✏️</span>'
            elif bloco['tipo'] == 'vazio':
                tipo_classe = "sentence-normal"
                bloco['texto'] = ""
            
            st.markdown(f"""
                <div class="sentence-block {tipo_classe}">
                    <span class="line-number">{bloco['linha']}</span>
                    {indicador}
                    {bloco['texto']}
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("""
                    </div>
                </div>
                <div class="document-side">
                    <div class="document-title">📄 """ + nome_novo + """</div>
                    <div class="document-content">
        """, unsafe_allow_html=True)
        
        # Exibir blocos do novo documento
        for bloco in comparacao['blocos_novo']:
            tipo_classe = f"sentence-{bloco['tipo']}"
            indicador = ""
            
            if bloco['tipo'] == 'adicionado':
                indicador = '<span class="change-indicator indicator-added">➕</span>'
            elif bloco['tipo'] == 'modificado':
                indicador = '<span class="change-indicator indicator-modified">✏️</span>'
            elif bloco['tipo'] == 'vazio':
                tipo_classe = "sentence-normal"
                bloco['texto'] = ""
            
            st.markdown(f"""
                <div class="sentence-block {tipo_classe}">
                    <span class="line-number">{bloco['linha']}</span>
                    {indicador}
                    {bloco['texto']}
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("""
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)

def main():
    """Função principal da aplicação"""
    
    # Título e descrição
    st.title("📚 Document Comparator")
    st.markdown("**Compare dois documentos lado a lado com frases completas e identificação clara das alterações**")
    
    # Verificar se python-docx está disponível
    if not DOCX_AVAILABLE:
        st.warning("⚠️ Para suporte completo a documentos Word, instale: `pip install python-docx`")
    
    # Sidebar com informações
    with st.sidebar:
        st.header("ℹ️ Informações")
        st.markdown("""
        **Como usar:**
        1. Faça upload do documento de referência
        2. Faça upload do novo documento
        3. Clique em 'Comparar Documentos'
        4. Visualize as diferenças lado a lado
        5. Veja número da página e linha
        
        **Formatos suportados:**
        - PDF (.pdf)
        - Word (.docx)
        
        **Funcionalidades:**
        - ✅ Visualização lado a lado
        - ✅ Numeração de páginas e linhas
        - ✅ Frases completas
        - ✅ Contexto das alterações
        - ✅ Layout como "foto" do documento
        
        **Dicas:**
        - Verde: texto adicionado
        - Vermelho riscado: texto removido
        - Amarelo: texto modificado
        - Cinza: contexto (texto inalterado)
        """)
    
    # Inicializar o comparador
    if 'comparador' not in st.session_state:
        st.session_state.comparador = DocumentComparator()
    
    # Layout em colunas para upload
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📄 Documento de Referência")
        arquivo_ref = st.file_uploader(
            "Escolha o arquivo de referência",
            type=['pdf', 'docx'] if DOCX_AVAILABLE else ['pdf'],
            key="ref_uploader",
            help="Este será usado como base para comparação"
        )
        
        if arquivo_ref:
            tipo_ref = st.session_state.comparador.detectar_tipo_arquivo(arquivo_ref.name)
            st.success(f"✅ Arquivo carregado: {arquivo_ref.name}")
            st.info(f"📊 Tamanho: {arquivo_ref.size / 1024 / 1024:.2f} MB")
            st.info(f"📋 Tipo: {tipo_ref.upper()}")
    
    with col2:
        st.subheader("📄 Novo Documento")
        arquivo_novo = st.file_uploader(
            "Escolha o novo arquivo",
            type=['pdf', 'docx'] if DOCX_AVAILABLE else ['pdf'],
            key="novo_uploader",
            help="Este será comparado com o arquivo de referência"
        )
        
        if arquivo_novo:
            tipo_novo = st.session_state.comparador.detectar_tipo_arquivo(arquivo_novo.name)
            st.success(f"✅ Arquivo carregado: {arquivo_novo.name}")
            st.info(f"📊 Tamanho: {arquivo_novo.size / 1024 / 1024:.2f} MB")
            st.info(f"📋 Tipo: {tipo_novo.upper()}")
    
    # Botão de comparação
    if arquivo_ref and arquivo_novo:
        # Verificar se os tipos são compatíveis
        tipo_ref = st.session_state.comparador.detectar_tipo_arquivo(arquivo_ref.name)
        tipo_novo = st.session_state.comparador.detectar_tipo_arquivo(arquivo_novo.name)
        
        if tipo_ref != tipo_novo:
            st.warning(f"⚠️ Atenção: Você está comparando arquivos de tipos diferentes ({tipo_ref.upper()} vs {tipo_novo.upper()}). A comparação ainda é possível, mas pode não ser ideal.")
        
        if st.button("🔍 Comparar Documentos", type="primary", use_container_width=True):
            
            with st.spinner("🔄 Processando arquivos..."):
                # Validar arquivos
                ref_bytes = arquivo_ref.read()
                novo_bytes = arquivo_novo.read()
                
                if not st.session_state.comparador.validar_arquivo(ref_bytes, arquivo_ref.name):
                    st.stop()
                
                if not st.session_state.comparador.validar_arquivo(novo_bytes, arquivo_novo.name):
                    st.stop()
                
                # Extrair textos
                texto_ref = st.session_state.comparador.extrair_texto_por_pagina(ref_bytes, arquivo_ref.name)
                texto_novo = st.session_state.comparador.extrair_texto_por_pagina(novo_bytes, arquivo_novo.name)
                
                if not texto_ref or not texto_novo:
                    st.error("❌ Erro ao extrair texto dos documentos")
                    st.stop()
                
                # Gerar comparação lado a lado
                st.info("🔍 Analisando diferenças...")
                comparacoes = st.session_state.comparador.gerar_comparacao_lado_a_lado(texto_ref, texto_novo)
                
                # Armazenar resultados no session state
                st.session_state.comparacoes = comparacoes
                st.session_state.arquivo_ref_nome = arquivo_ref.name
                st.session_state.arquivo_novo_nome = arquivo_novo.name
                st.session_state.tipo_ref = tipo_ref
                st.session_state.tipo_novo = tipo_novo
    
    # Exibir resultados se existirem
    if 'comparacoes' in st.session_state:
        comparacoes = st.session_state.comparacoes
        
        st.divider()
        
        # Resumo dos resultados
        total_alteracoes = sum(comp['total_alteracoes'] for comp in comparacoes)
        paginas_afetadas = len(comparacoes)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="stat-card">
                <span class="stat-number">{total_alteracoes}</span>
                <div class="stat-label">Alterações Encontradas</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="stat-card">
                <span class="stat-number">{paginas_afetadas}</span>
                <div class="stat-label">Páginas/Seções Afetadas</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            tipos_alteracao = set()
            for comp in comparacoes:
                for bloco in comp['blocos_ref'] + comp['blocos_novo']:
                    if bloco['tipo'] in ['adicionado', 'removido', 'modificado']:
                        tipos_alteracao.add(bloco['tipo'])
            
            st.markdown(f"""
            <div class="stat-card">
                <span class="stat-number">{len(tipos_alteracao)}</span>
                <div class="stat-label">Tipos de Alteração</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            compatibilidade = "✅ Mesmos tipos" if st.session_state.tipo_ref == st.session_state.tipo_novo else "⚠️ Tipos diferentes"
            st.markdown(f"""
            <div class="stat-card">
                <span class="stat-number" style="font-size: 1.2em;">{compatibilidade}</span>
                <div class="stat-label">Compatibilidade</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Exibir comparação lado a lado
        st.subheader("📋 Comparação Lado a Lado")
        st.markdown("*Visualize as diferenças com frases completas, número da página e linha:*")
        
        exibir_comparacao_lado_a_lado(
            comparacoes, 
            st.session_state.arquivo_ref_nome, 
            st.session_state.arquivo_novo_nome
        )
        
        if not comparacoes:
            st.balloons()

if __name__ == "__main__":
    main()

