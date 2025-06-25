"""
📚 Document Comparator - Aplicação Streamlit
Compara dois arquivos (PDF ou Word) e gera relatório de diferenças
Versão com visualização de texto alterado grifado
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

# CSS customizado para visualização de texto grifado
st.markdown("""
<style>
    /* Estilo para texto alterado grifado */
    .text-highlight-container {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        margin: 15px 0;
        overflow: hidden;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .highlight-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 12px 20px;
        font-weight: bold;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .highlight-content {
        padding: 20px;
        font-family: 'Georgia', 'Times New Roman', serif;
        font-size: 14px;
        line-height: 1.8;
        background: #fafafa;
    }
    
    .line-context {
        margin: 8px 0;
        padding: 8px 12px;
        border-radius: 4px;
        position: relative;
    }
    
    .line-number {
        display: inline-block;
        width: 35px;
        color: #666;
        font-weight: bold;
        font-family: 'Courier New', monospace;
        font-size: 12px;
        margin-right: 15px;
        text-align: right;
    }
    
    .line-text {
        display: inline;
    }
    
    .text-removed {
        background-color: #ffebee;
        border-left: 4px solid #f44336;
        text-decoration: line-through;
        color: #c62828;
    }
    
    .text-added {
        background-color: #e8f5e8;
        border-left: 4px solid #4caf50;
        color: #2e7d32;
        font-weight: 500;
    }
    
    .text-normal {
        background-color: #f9f9f9;
        border-left: 4px solid #e0e0e0;
        color: #555;
    }
    
    .page-info {
        background: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 6px;
        padding: 10px 15px;
        margin: 10px 0;
        font-size: 13px;
        color: #495057;
    }
    
    .change-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .indicator-added { background-color: #4caf50; }
    .indicator-removed { background-color: #f44336; }
    
    .summary-card {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 20px;
        margin: 15px 0;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .summary-number {
        font-size: 2.5em;
        font-weight: bold;
        color: #667eea;
        display: block;
        margin-bottom: 5px;
    }
    
    .summary-label {
        color: #666;
        font-size: 0.9em;
    }
    
    .legend-highlight {
        display: flex;
        justify-content: center;
        gap: 30px;
        margin: 20px 0;
        padding: 15px;
        background: #f8f9fa;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
    }
    
    .legend-item-highlight {
        display: flex;
        align-items: center;
        gap: 8px;
        font-weight: 500;
    }
    
    .legend-sample {
        padding: 4px 8px;
        border-radius: 3px;
        font-family: 'Courier New', monospace;
        font-size: 12px;
    }
    
    .legend-added-sample {
        background-color: #e8f5e8;
        border-left: 3px solid #4caf50;
        color: #2e7d32;
    }
    
    .legend-removed-sample {
        background-color: #ffebee;
        border-left: 3px solid #f44336;
        color: #c62828;
        text-decoration: line-through;
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
        self.alteracoes_grifadas = []
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
    
    def gerar_alteracoes_grifadas(self, texto_ref: List[str], texto_novo: List[str]) -> List[Dict]:
        """Gera visualização de texto com alterações grifadas"""
        alteracoes_grifadas = []
        
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
                
                # Usar SequenceMatcher para encontrar diferenças mais precisas
                matcher = difflib.SequenceMatcher(None, linhas_ref, linhas_novo)
                
                linhas_contexto = []
                linha_atual = 1
                
                for tag, i1, i2, j1, j2 in matcher.get_opcodes():
                    if tag == 'equal':
                        # Linhas iguais - mostrar algumas para contexto
                        for idx in range(i1, min(i1 + 2, i2)):  # Mostrar até 2 linhas de contexto
                            if idx < len(linhas_ref):
                                linhas_contexto.append({
                                    'numero': linha_atual + idx,
                                    'texto': linhas_ref[idx],
                                    'tipo': 'normal'
                                })
                        linha_atual += (i2 - i1)
                        
                    elif tag == 'delete':
                        # Linhas removidas
                        for idx in range(i1, i2):
                            if idx < len(linhas_ref):
                                linhas_contexto.append({
                                    'numero': linha_atual + idx,
                                    'texto': linhas_ref[idx],
                                    'tipo': 'removido'
                                })
                        linha_atual += (i2 - i1)
                        
                    elif tag == 'insert':
                        # Linhas adicionadas
                        for idx in range(j1, j2):
                            if idx < len(linhas_novo):
                                linhas_contexto.append({
                                    'numero': linha_atual,
                                    'texto': linhas_novo[idx],
                                    'tipo': 'adicionado'
                                })
                        
                    elif tag == 'replace':
                        # Linhas modificadas - mostrar ambas
                        for idx in range(i1, i2):
                            if idx < len(linhas_ref):
                                linhas_contexto.append({
                                    'numero': linha_atual + idx,
                                    'texto': linhas_ref[idx],
                                    'tipo': 'removido'
                                })
                        
                        for idx in range(j1, j2):
                            if idx < len(linhas_novo):
                                linhas_contexto.append({
                                    'numero': linha_atual + (idx - j1),
                                    'texto': linhas_novo[idx],
                                    'tipo': 'adicionado'
                                })
                        
                        linha_atual += max(i2 - i1, j2 - j1)
                
                if linhas_contexto:
                    alteracoes_grifadas.append({
                        'pagina': i + 1,
                        'linhas': linhas_contexto,
                        'total_alteracoes': len([l for l in linhas_contexto if l['tipo'] != 'normal'])
                    })
            
            progress_bar.progress((i + 1) / max_paginas)
        
        progress_bar.empty()
        return alteracoes_grifadas
    
    def comparar_textos_simples(self, texto_ref: List[str], texto_novo: List[str]) -> List[Dict]:
        """Compara textos e retorna diferenças simples para tabela"""
        diferencas_simples = []
        
        max_paginas = max(len(texto_ref), len(texto_novo))
        
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
        
        return diferencas_simples

def exibir_texto_grifado(alteracoes_grifadas: List[Dict]):
    """Exibe o texto com alterações grifadas como uma 'foto' do documento"""
    if not alteracoes_grifadas:
        st.success("✅ Nenhuma alteração encontrada!")
        return
    
    # Legenda
    st.markdown("""
    <div class="legend-highlight">
        <div class="legend-item-highlight">
            <span class="legend-sample legend-added-sample">Texto adicionado</span>
        </div>
        <div class="legend-item-highlight">
            <span class="legend-sample legend-removed-sample">Texto removido</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Exibir cada página com alterações
    for alteracao in alteracoes_grifadas:
        # Cabeçalho da página
        st.markdown(f"""
        <div class="text-highlight-container">
            <div class="highlight-header">
                <span>🔸 Página/Seção {alteracao['pagina']}</span>
                <span>{alteracao['total_alteracoes']} alteração(ões) encontrada(s)</span>
            </div>
            <div class="highlight-content">
        """, unsafe_allow_html=True)
        
        # Exibir linhas com contexto
        for linha in alteracao['linhas']:
            tipo_classe = f"text-{linha['tipo']}"
            
            # Determinar o indicador visual
            indicador = ""
            if linha['tipo'] == 'adicionado':
                indicador = '<span class="change-indicator indicator-added"></span>'
            elif linha['tipo'] == 'removido':
                indicador = '<span class="change-indicator indicator-removed"></span>'
            
            st.markdown(f"""
                <div class="line-context {tipo_classe}">
                    <span class="line-number">{linha['numero']}</span>
                    {indicador}
                    <span class="line-text">{linha['texto']}</span>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div></div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

def main():
    """Função principal da aplicação"""
    
    # Título e descrição
    st.title("📚 Document Comparator")
    st.markdown("**Compare dois documentos e visualize apenas o texto alterado, como uma 'foto' grifada**")
    
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
        4. Visualize apenas o texto alterado
        5. Veja número da página e linha
        
        **Formatos suportados:**
        - PDF (.pdf)
        - Word (.docx)
        
        **Funcionalidades:**
        - ✅ Visualização de texto grifado
        - ✅ Numeração de páginas e linhas
        - ✅ Contexto das alterações
        - ✅ Layout como "foto" do documento
        
        **Dicas:**
        - Verde: texto adicionado
        - Vermelho riscado: texto removido
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
                
                # Gerar visualização de texto grifado
                st.info("🔍 Analisando alterações...")
                alteracoes_grifadas = st.session_state.comparador.gerar_alteracoes_grifadas(texto_ref, texto_novo)
                
                # Gerar diferenças simples para tabela
                diferencas_simples = st.session_state.comparador.comparar_textos_simples(texto_ref, texto_novo)
                
                # Armazenar resultados no session state
                st.session_state.alteracoes_grifadas = alteracoes_grifadas
                st.session_state.diferencas = diferencas_simples
                st.session_state.arquivo_ref_nome = arquivo_ref.name
                st.session_state.arquivo_novo_nome = arquivo_novo.name
                st.session_state.tipo_ref = tipo_ref
                st.session_state.tipo_novo = tipo_novo
    
    # Exibir resultados se existirem
    if 'alteracoes_grifadas' in st.session_state:
        alteracoes_grifadas = st.session_state.alteracoes_grifadas
        diferencas = st.session_state.diferencas
        
        st.divider()
        
        # Resumo dos resultados
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="summary-card">
                <span class="summary-number">{len(diferencas)}</span>
                <div class="summary-label">Alterações Encontradas</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            paginas_afetadas = len(alteracoes_grifadas)
            st.markdown(f"""
            <div class="summary-card">
                <span class="summary-number">{paginas_afetadas}</span>
                <div class="summary-label">Páginas/Seções Afetadas</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            total_linhas_alteradas = sum(alt['total_alteracoes'] for alt in alteracoes_grifadas)
            st.markdown(f"""
            <div class="summary-card">
                <span class="summary-number">{total_linhas_alteradas}</span>
                <div class="summary-label">Linhas Modificadas</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            compatibilidade = "✅ Mesmos tipos" if st.session_state.tipo_ref == st.session_state.tipo_novo else "⚠️ Tipos diferentes"
            st.markdown(f"""
            <div class="summary-card">
                <span class="summary-number" style="font-size: 1.2em;">{compatibilidade}</span>
                <div class="summary-label">Compatibilidade</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Exibir texto grifado
        if alteracoes_grifadas:
            st.subheader("📝 Texto Alterado (Visualização Grifada)")
            st.markdown("*Visualize apenas o que foi alterado, com número da página e linha:*")
            exibir_texto_grifado(alteracoes_grifadas)
        else:
            st.success("✅ Nenhuma diferença encontrada entre os documentos!")
            st.balloons()
        
        # Tabela resumo (opcional, em expander)
        if diferencas:
            with st.expander("📋 Ver Tabela Resumo das Diferenças", expanded=False):
                # Converter para DataFrame para melhor visualização
                df_diferencas = pd.DataFrame(diferencas)
                
                # Configurar exibição da tabela
                st.dataframe(
                    df_diferencas,
                    use_container_width=True,
                    column_config={
                        "pagina": st.column_config.NumberColumn("Página/Seção", format="%d"),
                        "linha": st.column_config.NumberColumn("Linha", format="%d"),
                        "tipo": st.column_config.TextColumn("Tipo"),
                        "conteudo_original": st.column_config.TextColumn("Conteúdo Original"),
                        "conteudo_novo": st.column_config.TextColumn("Conteúdo Novo")
                    }
                )

if __name__ == "__main__":
    main()

