# app.py - Aplicação Unificada Projeto Solvi

import streamlit as st
import sys
import os

# Adicionar o diretório atual ao path para garantir que os módulos sejam encontrados
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configuração da página principal (deve ser a primeira chamada st)
st.set_page_config(
    page_title="Projeto Solvi - Ferramentas de Análise",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Importar as funções 'main' de seus aplicativos com tratamento de erro
try:
    from app_cvm_modified import main as cvm_app
    CVM_AVAILABLE = True
except ImportError as e:
    st.error(f"Erro ao importar app_cvm_modified: {e}")
    CVM_AVAILABLE = False

try:
    from app_comparacao_modified import main as comparacao_app
    COMPARACAO_AVAILABLE = True
except ImportError as e:
    st.error(f"Erro ao importar app_comparacao_modified: {e}")
    COMPARACAO_AVAILABLE = False

def main():
    """Função principal da aplicação unificada"""

    # CSS customizado para a aplicação unificada
    st.markdown("""
    <style>
        /* Estilo para o header principal */
        .main-header {
            background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 50%, #1e40af 100%);
            color: white;
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            text-align: center;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }
        
        .main-title {
            font-size: 3rem;
            font-weight: 700;
            margin: 0;
            background: linear-gradient(45deg, #ffffff, #e0e7ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .main-subtitle {
            font-size: 1.2rem;
            margin: 0.5rem 0 0 0;
            opacity: 0.9;
        }
        
        /* Estilo para as abas */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: #f8fafc;
            border-radius: 10px;
            padding: 8px;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 60px;
            padding: 0px 24px;
            background-color: white;
            border-radius: 8px;
            color: #374151;
            font-weight: 600;
            font-size: 16px;
            border: 2px solid transparent;
            transition: all 0.3s ease;
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #3b82f6 0%, #1e40af 100%);
            color: white;
            border: 2px solid #1e40af;
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            background-color: #e0e7ff;
            transform: translateY(-2px);
        }
        
        .stTabs [aria-selected="true"]:hover {
            background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
            transform: translateY(-2px);
        }
        
        /* Estilo para o conteúdo das abas */
        .stTabs [data-baseweb="tab-panel"] {
            padding: 2rem 0;
        }
        
        /* Estilo para a sidebar */
        .css-1d391kg {
            background: linear-gradient(180deg, #f8fafc 0%, #e2e8f0 100%);
        }
        
        /* Estilo para informações da sidebar */
        .info-box {
            background: linear-gradient(135deg, #3b82f6 0%, #1e40af 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 10px;
            margin: 1rem 0;
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
        }
        
        .info-title {
            font-size: 1.2rem;
            font-weight: 700;
            margin-bottom: 1rem;
            text-align: center;
        }
        
        .info-content {
            font-size: 0.9rem;
            line-height: 1.6;
        }
        
        .feature-list {
            list-style: none;
            padding: 0;
            margin: 1rem 0;
        }
        
        .feature-list li {
            padding: 0.5rem 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .feature-list li:before {
            content: "✓ ";
            color: #10b981;
            font-weight: bold;
            margin-right: 0.5rem;
        }
        
        .error-box {
            background: #fee2e2;
            border: 1px solid #fca5a5;
            color: #dc2626;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
        }
        
        /* Responsividade */
        @media (max-width: 768px) {
            .main-title {
                font-size: 2rem;
            }
            
            .main-subtitle {
                font-size: 1rem;
            }
            
            .stTabs [data-baseweb="tab"] {
                height: 50px;
                font-size: 14px;
                padding: 0px 16px;
            }
        }
    </style>
    """, unsafe_allow_html=True)

    # Header principal da aplicação
    st.markdown("""
    <div class="main-header">
        <h1 class="main-title">📊 Projeto Solvi</h1>
        <p class="main-subtitle">Central de Ferramentas de Análise Documental</p>
    </div>
    """, unsafe_allow_html=True)

    # Verificar se os módulos foram importados corretamente
    if not CVM_AVAILABLE or not COMPARACAO_AVAILABLE:
        st.error("❌ Erro na importação dos módulos!")
        st.markdown("""
        <div class="error-box">
            <h3>🔧 Para corrigir este problema:</h3>
            <ol>
                <li>Certifique-se de que os arquivos estão no mesmo diretório:</li>
                <ul>
                    <li><code>app.py</code></li>
                    <li><code>app_cvm_modified.py</code></li>
                    <li><code>app_comparacao_modified.py</code></li>
                </ul>
                <li>Execute o comando no diretório correto</li>
                <li>Verifique se não há erros de sintaxe nos arquivos importados</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
        return

    # Sidebar com informações gerais
    with st.sidebar:
        st.markdown("""
        <div class="info-box">
            <div class="info-title">🚀 Bem-vindo ao Projeto Solvi</div>
            <div class="info-content">
                Esta aplicação unifica duas poderosas ferramentas de análise documental em uma interface integrada.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-box">
            <div class="info-title">🛠️ Ferramentas Disponíveis</div>
            <ul class="feature-list">
                <li>Analisador FRE vs Normas CVM</li>
                <li>Comparador Inteligente de Documentos</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-box">
            <div class="info-title">📋 Como Usar</div>
            <div class="info-content">
                1. Selecione a ferramenta desejada nas abas acima<br>
                2. Siga as instruções específicas de cada ferramenta<br>
                3. Faça upload dos documentos necessários<br>
                4. Execute a análise e visualize os resultados
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-box">
            <div class="info-title">💡 Dicas</div>
            <div class="info-content">
                • Cada ferramenta mantém seu próprio estado<br>
                • Você pode alternar entre as abas sem perder dados<br>
                • Ambas as ferramentas suportam PDF e Word<br>
                • Os resultados podem ser exportados
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Criação das abas principais
    tab1, tab2 = st.tabs([
        "🔍 Analisador FRE vs Normas CVM", 
        "📚 Comparador de Documentos"
    ])

    # Conteúdo da primeira aba - Analisador FRE
    with tab1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); 
                    padding: 1.5rem; border-radius: 10px; margin-bottom: 2rem; 
                    border-left: 5px solid #0ea5e9;">
            <h2 style="color: #0c4a6e; margin: 0 0 0.5rem 0;">
                📊 Analisador de Formulário de Referência (FRE) vs Normas CVM
            </h2>
            <p style="color: #075985; margin: 0; font-size: 1.1rem;">
                Analise a conformidade do seu FRE com as normas e regulamentações da CVM de forma automatizada e inteligente.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        if CVM_AVAILABLE:
            try:
                # Chama a função principal do aplicativo CVM
                cvm_app()
            except Exception as e:
                st.error(f"Erro ao executar o analisador FRE: {e}")
                st.info("Tente recarregar a página ou verifique os logs do console.")
        else:
            st.error("❌ Módulo do Analisador FRE não disponível")

    # Conteúdo da segunda aba - Comparador de Documentos
    with tab2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%); 
                    padding: 1.5rem; border-radius: 10px; margin-bottom: 2rem; 
                    border-left: 5px solid #22c55e;">
            <h2 style="color: #14532d; margin: 0 0 0.5rem 0;">
                📚 Comparador Inteligente de Documentos
            </h2>
            <p style="color: #166534; margin: 0; font-size: 1.1rem;">
                Compare dois documentos (PDF ou Word) e identifique apenas as alterações reais de conteúdo, ignorando mudanças de formatação.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        if COMPARACAO_AVAILABLE:
            try:
                # Chama a função principal do aplicativo de comparação
                comparacao_app()
            except Exception as e:
                st.error(f"Erro ao executar o comparador de documentos: {e}")
                st.info("Tente recarregar a página ou verifique os logs do console.")
        else:
            st.error("❌ Módulo do Comparador de Documentos não disponível")

    # Footer da aplicação
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6b7280; font-size: 0.9rem; padding: 1rem;">
        <p><strong>Projeto Solvi</strong> - Ferramentas de Análise Documental</p>
        <p>Desenvolvido para otimizar processos de análise e comparação de documentos</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

