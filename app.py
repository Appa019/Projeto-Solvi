"""
📚 Document Comparator - Aplicação Streamlit
Compara dois arquivos (PDF ou Word) e gera relatório de diferenças
Versão com relatório visual melhorado
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

# CSS customizado para destacar filtros
st.markdown("""
<style>
    /* Estilo para filtros em destaque */
    .filtros-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .filtros-title {
        font-size: 1.3em;
        font-weight: bold;
        margin-bottom: 15px;
        text-align: center;
    }
    
    .filtros-content {
        background: rgba(255, 255, 255, 0.1);
        padding: 15px;
        border-radius: 8px;
        backdrop-filter: blur(10px);
    }
    
    /* Estilo para métricas */
    .metric-container {
        background: white;
        padding: 20px;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .metric-value {
        font-size: 2em;
        font-weight: bold;
        color: #667eea;
        margin-bottom: 5px;
    }
    
    .metric-label {
        color: #666;
        font-size: 0.9em;
    }
    
    /* Melhorar tabelas do difflib */
    .diff table {
        width: 100%;
        border-collapse: collapse;
        font-family: 'Courier New', monospace;
        font-size: 12px;
        margin: 0;
    }
    
    .diff th {
        background: #f8f9fa;
        padding: 8px 12px;
        text-align: left;
        border: 1px solid #dee2e6;
        font-weight: bold;
        color: #495057;
    }
    
    .diff td {
        padding: 4px 8px;
        border: 1px solid #dee2e6;
        vertical-align: top;
        word-wrap: break-word;
    }
    
    .diff_add {
        background-color: #d4edda !important;
        border-left: 3px solid #28a745 !important;
    }
    
    .diff_sub {
        background-color: #f8d7da !important;
        border-left: 3px solid #dc3545 !important;
    }
    
    .diff_chg {
        background-color: #fff3cd !important;
        border-left: 3px solid #ffc107 !important;
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
        self.diferencas = []
        self.diferencas_detalhadas = []
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
    
    def comparar_textos_detalhado(self, texto_ref: List[str], texto_novo: List[str]) -> Tuple[List[Dict], List[Dict]]:
        """Compara textos e retorna diferenças simples e detalhadas"""
        diferencas_simples = []
        diferencas_detalhadas = []
        
        max_paginas = max(len(texto_ref), len(texto_novo))
        progress_bar = st.progress(0)
        
        for i in range(max_paginas):
            # Garantir que ambos os textos existam
            ref = texto_ref[i] if i < len(texto_ref) else ""
            novo = texto_novo[i] if i < len(texto_novo) else ""
            
            if ref.strip() != novo.strip():
                # Dividir em linhas para comparação detalhada
                linhas_ref = ref.splitlines()
                linhas_novo = novo.splitlines()
                
                # Usar difflib para encontrar diferenças linha por linha
                differ = difflib.unified_diff(
                    linhas_ref, 
                    linhas_novo, 
                    lineterm='',
                    n=0  # Sem contexto para focar apenas nas diferenças
                )
                
                diferenca_texto = list(differ)
                
                if diferenca_texto:
                    # Processar diferenças linha por linha para tabela simples
                    linha_atual = 0
                    for linha in diferenca_texto:
                        if linha.startswith('@@'):
                            # Extrair número da linha do cabeçalho @@
                            try:
                                partes = linha.split()
                                if len(partes) >= 2:
                                    linha_info = partes[1].split(',')[0]
                                    linha_atual = abs(int(linha_info))
                            except:
                                linha_atual += 1
                        elif linha.startswith('-'):
                            # Linha removida
                            diferencas_simples.append({
                                'pagina': i + 1,
                                'linha': linha_atual,
                                'tipo': 'Removido',
                                'conteudo_original': linha[1:],
                                'conteudo_novo': ''
                            })
                        elif linha.startswith('+'):
                            # Linha adicionada
                            diferencas_simples.append({
                                'pagina': i + 1,
                                'linha': linha_atual,
                                'tipo': 'Adicionado',
                                'conteudo_original': '',
                                'conteudo_novo': linha[1:]
                            })
                        
                        if linha.startswith(('+', '-')):
                            linha_atual += 1
                
                # Criar comparação visual lado a lado para esta página
                differ_html = difflib.HtmlDiff(wrapcolumn=80)
                diff_html = differ_html.make_table(
                    linhas_ref,
                    linhas_novo,
                    fromdesc='Documento de Referência',
                    todesc='Novo Documento',
                    context=True,
                    numlines=3
                )
                
                diferencas_detalhadas.append({
                    'pagina': i + 1,
                    'html_diff': diff_html,
                    'total_linhas_ref': len(linhas_ref),
                    'total_linhas_novo': len(linhas_novo)
                })
            
            progress_bar.progress((i + 1) / max_paginas)
        
        progress_bar.empty()
        return diferencas_simples, diferencas_detalhadas

def exibir_diferencas_visual(diferencas_detalhadas: List[Dict]):
    """Exibe as diferenças de forma visual no Streamlit"""
    if not diferencas_detalhadas:
        st.success("✅ Nenhuma diferença encontrada!")
        return
    
    st.subheader("🔍 Comparação Visual por Página")
    
    # Legenda
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("🟢 **Verde:** Texto Adicionado")
    with col2:
        st.markdown("🔴 **Vermelho:** Texto Removido")
    with col3:
        st.markdown("🟡 **Amarelo:** Texto Modificado")
    
    st.divider()
    
    # Exibir cada página com diferenças
    for diff_detail in diferencas_detalhadas:
        with st.expander(f"🔸 Página/Seção {diff_detail['pagina']} ({diff_detail['total_linhas_ref']} → {diff_detail['total_linhas_novo']} linhas)", expanded=True):
            # Aplicar CSS customizado para melhor visualização
            st.markdown("""
            <style>
            .diff table { width: 100%; font-family: 'Courier New', monospace; font-size: 12px; }
            .diff th { background: #f5f5f5; padding: 8px; }
            .diff td { padding: 6px 8px; vertical-align: top; }
            .diff_add { background-color: #d4edda !important; }
            .diff_sub { background-color: #f8d7da !important; }
            .diff_chg { background-color: #fff3cd !important; }
            </style>
            """, unsafe_allow_html=True)
            
            st.markdown(diff_detail['html_diff'], unsafe_allow_html=True)

def main():
    """Função principal da aplicação"""
    
    # Título e descrição
    st.title("📚 Document Comparator")
    st.markdown("**Compare dois documentos (PDF ou Word) e identifique as diferenças de forma detalhada**")
    
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
        4. Visualize as diferenças
        5. Use os filtros para análise específica
        
        **Formatos suportados:**
        - PDF (.pdf)
        - Word (.docx)
        
        **Limitações:**
        - Máximo 200MB por arquivo
        - Documentos Word são divididos em seções de ~50 parágrafos
        
        **Dicas:**
        - Funciona melhor com documentos de texto
        - Imagens e formatação não são comparadas
        - Use os filtros para focar em tipos específicos de alteração
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
                
                # Comparar textos
                st.info("🔍 Comparando textos...")
                diferencas_simples, diferencas_detalhadas = st.session_state.comparador.comparar_textos_detalhado(texto_ref, texto_novo)
                
                # Armazenar resultados no session state
                st.session_state.diferencas = diferencas_simples
                st.session_state.diferencas_detalhadas = diferencas_detalhadas
                st.session_state.arquivo_ref_nome = arquivo_ref.name
                st.session_state.arquivo_novo_nome = arquivo_novo.name
                st.session_state.tipo_ref = tipo_ref
                st.session_state.tipo_novo = tipo_novo
    
    # Exibir resultados se existirem
    if 'diferencas' in st.session_state and 'diferencas_detalhadas' in st.session_state:
        diferencas = st.session_state.diferencas
        diferencas_detalhadas = st.session_state.diferencas_detalhadas
        
        st.divider()
        
        # Resumo dos resultados com layout melhorado
        st.subheader("📊 Resumo da Análise")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-value">{len(diferencas)}</div>
                <div class="metric-label">Diferenças Encontradas</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            paginas_afetadas = len(set(d['pagina'] for d in diferencas)) if diferencas else 0
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-value">{paginas_afetadas}</div>
                <div class="metric-label">Páginas/Seções Afetadas</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            tipos_mudanca = len(set(d['tipo'] for d in diferencas)) if diferencas else 0
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-value">{tipos_mudanca}</div>
                <div class="metric-label">Tipos de Mudança</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            compatibilidade = "✅ Mesmos tipos" if st.session_state.tipo_ref == st.session_state.tipo_novo else "⚠️ Tipos diferentes"
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-value" style="font-size: 1.2em;">{compatibilidade}</div>
                <div class="metric-label">Compatibilidade</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Exibir comparação visual
        exibir_diferencas_visual(diferencas_detalhadas)
        
        if diferencas:
            # Filtros Avançados em destaque
            st.markdown("""
            <div class="filtros-container">
                <div class="filtros-title">🔍 Filtros Avançados</div>
                <div class="filtros-content">
                    <p style="margin-bottom: 15px; text-align: center;">Use os filtros abaixo para analisar tipos específicos de alterações</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Converter para DataFrame para melhor visualização
            df_diferencas = pd.DataFrame(diferencas)
            
            col1, col2 = st.columns(2)
            
            with col1:
                tipos_selecionados = st.multiselect(
                    "🏷️ Filtrar por tipo de mudança:",
                    options=df_diferencas['tipo'].unique(),
                    default=df_diferencas['tipo'].unique(),
                    help="Selecione os tipos de alteração que deseja visualizar"
                )
            
            with col2:
                paginas_selecionadas = st.multiselect(
                    "📄 Filtrar por página/seção:",
                    options=sorted(df_diferencas['pagina'].unique()),
                    default=sorted(df_diferencas['pagina'].unique()),
                    help="Selecione as páginas/seções que deseja analisar"
                )
            
            # Aplicar filtros
            df_filtrado = df_diferencas[
                (df_diferencas['tipo'].isin(tipos_selecionados)) &
                (df_diferencas['pagina'].isin(paginas_selecionadas))
            ]
            
            # Tabela Resumo das Diferenças (retrátil)
            with st.expander("📋 Tabela Resumo das Diferenças", expanded=False):
                if len(df_filtrado) != len(df_diferencas):
                    st.info(f"📊 Mostrando {len(df_filtrado)} de {len(df_diferencas)} diferenças (filtros aplicados)")
                
                # Configurar exibição da tabela
                st.dataframe(
                    df_filtrado,
                    use_container_width=True,
                    column_config={
                        "pagina": st.column_config.NumberColumn("Página/Seção", format="%d"),
                        "linha": st.column_config.NumberColumn("Linha", format="%d"),
                        "tipo": st.column_config.TextColumn("Tipo"),
                        "conteudo_original": st.column_config.TextColumn("Conteúdo Original"),
                        "conteudo_novo": st.column_config.TextColumn("Conteúdo Novo")
                    }
                )
                
                # Estatísticas dos dados filtrados
                if len(df_filtrado) > 0:
                    st.markdown("### 📈 Estatísticas dos Dados Filtrados")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Total de Alterações", len(df_filtrado))
                    
                    with col2:
                        paginas_filtradas = len(df_filtrado['pagina'].unique())
                        st.metric("Páginas Afetadas", paginas_filtradas)
                    
                    with col3:
                        tipos_filtrados = len(df_filtrado['tipo'].unique())
                        st.metric("Tipos de Mudança", tipos_filtrados)
        
        if not diferencas:
            st.balloons()

if __name__ == "__main__":
    main()

