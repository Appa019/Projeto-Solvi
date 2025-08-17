# app_cvm.py

import streamlit as st
import pandas as pd
import openai
from io import BytesIO
import PyPDF2
import docx
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
import json
import time
import re
from datetime import datetime

# A classe permanece fora da função main para que possa ser instanciada
class FREAnalyzer:
    def __init__(self, api_key):
        openai.api_key = api_key
        self.client = openai.OpenAI(api_key=api_key)
        
    def extract_text_from_pdf(self, pdf_file):
        # ... (código da classe inalterado) ...
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
        # ... (código da classe inalterado) ...
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
        # ... (código da classe inalterado) ...
        if uploaded_file.type == "application/pdf":
            return self.extract_text_from_pdf(uploaded_file)
        elif uploaded_file.type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", 
                                   "application/msword"]:
            return self.extract_text_from_docx(uploaded_file)
        else:
            st.error("Formato de arquivo não suportado. Use PDF ou Word.")
            return ""
    
    def analyze_fre_section(self, fre_text, cvm_references, section_name, section_content):
        # ... (código da classe inalterado) ...
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
            try:
                json_start = result.find('{')
                json_end = result.rfind('}') + 1
                json_str = result[json_start:json_end]
                return json.loads(json_str)
            except:
                return {
                    "secao": section_name, "conformidade": "ERRO_ANALISE", "criticidade": "ATENCAO",
                    "pontos_atencao": [{"problema": "Erro na análise automática", "criticidade": "ATENCAO", "artigo_cvm": "Resolução CVM nº 80/22", "sugestao": "Revisar manualmente esta seção"}],
                    "resumo": "Erro na análise automática desta seção"
                }
        except Exception as e:
            st.error(f"Erro na análise da seção {section_name}: {str(e)}")
            return None

    def extract_fre_sections(self, fre_text):
        # ... (código da classe inalterado) ...
        sections = {}
        section_patterns = [
            r"1\.1\s+Histórico do emissor", r"1\.2\s+Descrição das principais atividades",
            r"1\.3\s+Informações relacionadas aos segmentos operacionais", r"1\.4\s+Produção/Comercialização/Mercados",
            r"1\.5\s+Principais clientes", r"1\.6\s+Efeitos relevantes da regulação estatal",
            r"1\.9\s+Informações ambientais sociais e de governança", r"2\.1\s+Condições financeiras e patrimoniais",
            r"2\.2\s+Resultados operacional e financeiro", r"4\.1\s+Descrição dos fatores de risco",
            r"7\.1\s+Principais características dos órgãos de administração", r"8\.1\s+Política ou prática de remuneração",
            r"11\.1\s+Regras, políticas e práticas", r"12\.1\s+Informações sobre o capital social"
        ]
        lines = fre_text.split('\n')
        current_section = None
        current_content = []
        for line in lines:
            section_found = False
            for pattern in section_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    if current_section and current_content:
                        sections[current_section] = '\n'.join(current_content)
                    current_section = line.strip()
                    current_content = [line]
                    section_found = True
                    break
            if not section_found and current_section:
                current_content.append(line)
        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content)
        return sections

    def generate_pdf_report(self, analysis_results, fre_filename):
        # ... (código da classe inalterado) ...
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1*inch)
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=24, spaceAfter=30, alignment=TA_CENTER, textColor=colors.HexColor('#1f2937'))
        heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'], fontSize=16, spaceAfter=12, textColor=colors.HexColor('#374151'))
        normal_style = ParagraphStyle('CustomNormal', parent=styles['Normal'], fontSize=11, spaceAfter=6, alignment=TA_JUSTIFY)
        story = []
        story.append(Paragraph("Relatório de Análise FRE vs Normas CVM", title_style))
        story.append(Spacer(1, 20))
        story.append(Paragraph(f"<b>Arquivo analisado:</b> {fre_filename}", normal_style))
        story.append(Paragraph(f"<b>Data da análise:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}", normal_style))
        story.append(Spacer(1, 20))
        story.append(Paragraph("RESUMO EXECUTIVO", heading_style))
        total_sections = len(analysis_results)
        critico_count = sum(1 for r in analysis_results if any(p['criticidade'] == 'CRITICO' for p in r.get('pontos_atencao', [])))
        atencao_count = sum(1 for r in analysis_results if any(p['criticidade'] == 'ATENCAO' for p in r.get('pontos_atencao', [])))
        metrics_data = [
            ['Métrica', 'Valor'], ['Total de seções analisadas', str(total_sections)],
            ['Seções com pontos críticos', str(critico_count)], ['Seções com pontos de atenção', str(atencao_count)],
            ['Taxa de conformidade', f"{((total_sections - critico_count) / total_sections * 100):.1f}%"]
        ]
        metrics_table = Table(metrics_data)
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')), ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12), ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige), ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(metrics_table)
        story.append(PageBreak())
        story.append(Paragraph("ANÁLISE DETALHADA POR SEÇÃO", heading_style))
        for result in analysis_results:
            if not result: continue
            story.append(Paragraph(f"<b>{result.get('secao', 'Seção não identificada')}</b>", heading_style))
            conformidade = result.get('conformidade', 'N/A')
            color = colors.green if conformidade == 'CONFORME' else colors.red if conformidade == 'NAO_CONFORME' else colors.orange
            story.append(Paragraph(f"<b>Status:</b> <font color='{color.hexval()}'>{conformidade}</font>", normal_style))
            story.append(Paragraph(f"<b>Resumo:</b> {result.get('resumo', 'N/A')}", normal_style))
            pontos = result.get('pontos_atencao', [])
            if pontos:
                story.append(Paragraph("<b>Pontos de Atenção:</b>", normal_style))
                for i, ponto in enumerate(pontos, 1):
                    criticidade = ponto.get('criticidade', 'N/A')
                    emoji = "🔴" if criticidade == "CRITICO" else "🟡" if criticidade == "ATENCAO" else "🟢"
                    story.append(Paragraph(f"{emoji} <b>Ponto {i}:</b> {ponto.get('problema', 'N/A')}", normal_style))
                    story.append(Paragraph(f"<b>Base legal:</b> {ponto.get('artigo_cvm', 'N/A')}", normal_style))
                    story.append(Paragraph(f"<b>Sugestão:</b> {ponto.get('sugestao', 'N/A')}", normal_style))
                    story.append(Spacer(1, 10))
            story.append(Spacer(1, 20))
        doc.build(story)
        buffer.seek(0)
        return buffer

# Todo o código do aplicativo agora está dentro desta função
def main():
    # CSS customizado para design limpo
    st.markdown("""
    <style>
        .main-header { font-size: 2.5rem; font-weight: 700; color: #1f2937; text-align: center; margin-bottom: 2rem; padding: 1rem; background: linear-gradient(90deg, #f8fafc 0%, #e2e8f0 100%); border-radius: 10px; border-left: 5px solid #3b82f6; }
        .section-header { font-size: 1.5rem; font-weight: 600; color: #374151; margin: 1.5rem 0 1rem 0; padding-bottom: 0.5rem; border-bottom: 2px solid #e5e7eb; }
        .info-box { background-color: #f0f9ff; border: 1px solid #0ea5e9; border-radius: 8px; padding: 1rem; margin: 1rem 0; }
        .warning-box { background-color: #fef3c7; border: 1px solid #f59e0b; border-radius: 8px; padding: 1rem; margin: 1rem 0; }
        .success-box { background-color: #f0fdf4; border: 1px solid #22c55e; border-radius: 8px; padding: 1rem; margin: 1rem 0; }
        .metric-card { background: white; padding: 1.5rem; border-radius: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); border-left: 4px solid #3b82f6; margin: 0.5rem 0; }
        .stButton > button { background-color: #3b82f6; color: white; border-radius: 8px; border: none; padding: 0.5rem 2rem; font-weight: 600; transition: all 0.3s; }
        .stButton > button:hover { background-color: #2563eb; transform: translateY(-2px); }
    </style>
    """, unsafe_allow_html=True)

    # Inicializar session state se necessário (com chaves únicas para evitar conflitos)
    if 'cvm_analysis_results' not in st.session_state:
        st.session_state.cvm_analysis_results = None
    if 'cvm_fre_filename' not in st.session_state:
        st.session_state.cvm_fre_filename = None
    if 'cvm_analysis_completed' not in st.session_state:
        st.session_state.cvm_analysis_completed = False

    # Sidebar para configurações
    with st.sidebar:
        st.markdown("### ⚙️ Configurações do Analisador")
        api_key = st.text_input("🔑 Chave API OpenAI *", type="password", help="Insira sua chave API da OpenAI (obrigatório)", key="cvm_api_key")
        
        if not api_key:
            st.error("⚠️ Chave API OpenAI é obrigatória!")
            st.stop()
        
        st.markdown("---")
        st.markdown("### 📄 Arquivo FRE")
        fre_file = st.file_uploader("Upload do Formulário de Referência", type=['pdf', 'docx'], help="Faça upload do FRE para análise", key="cvm_fre_uploader")
        
        st.markdown("---")
        st.markdown("### 📚 Documentos CVM (máx. 5)")
        cvm_files = st.file_uploader("Upload dos documentos de referência CVM", type=['pdf', 'docx'], accept_multiple_files=True, help="Faça upload dos documentos CVM (máximo 5)", key="cvm_docs_uploader")
        
        if len(cvm_files) > 5:
            st.error("⚠️ Máximo de 5 documentos CVM permitidos!")
            cvm_files = cvm_files[:5]
        
        if st.session_state.cvm_analysis_completed:
            if st.button("🔄 Nova Análise CVM", help="Limpar resultados e fazer nova análise"):
                st.session_state.cvm_analysis_results = None
                st.session_state.cvm_fre_filename = None
                st.session_state.cvm_analysis_completed = False
                st.rerun()
    
    # Área principal
    if not fre_file:
        st.markdown("""
        <div class="info-box">
            <h3>🚀 Como usar esta ferramenta:</h3>
            <ol>
                <li><b>Configure sua chave API OpenAI</b> na barra lateral.</li>
                <li><b>Faça upload do FRE</b> que deseja analisar.</li>
                <li><b>Adicione documentos CVM</b> de referência (opcional, máx. 5).</li>
                <li><b>Clique em "Analisar FRE"</b> e aguarde o processamento.</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
        return
    
    if not cvm_files:
        st.warning("⚠️ Adicione pelo menos um documento CVM de referência para uma análise mais precisa.")
    
    if not st.session_state.cvm_analysis_completed:
        if st.button("🔍 Analisar FRE", type="primary", key="cvm_analyze_button"):
            if not api_key:
                st.error("⚠️ Chave API OpenAI é obrigatória!")
                return
            
            try:
                analyzer = FREAnalyzer(api_key)
                with st.spinner("📖 Extraindo texto do FRE..."):
                    fre_text = analyzer.extract_text_from_file(fre_file)
                    if not fre_text:
                        st.error("❌ Não foi possível extrair texto do FRE!")
                        return
                
                cvm_text = ""
                if cvm_files:
                    with st.spinner("📚 Processando documentos CVM..."):
                        for cvm_file in cvm_files:
                            cvm_content = analyzer.extract_text_from_file(cvm_file)
                            cvm_text += f"\n\n--- {cvm_file.name} ---\n{cvm_content}"
                
                with st.spinner("🔍 Identificando seções do FRE..."):
                    fre_sections = analyzer.extract_fre_sections(fre_text)
                    if not fre_sections:
                        st.warning("⚠️ Não foi possível identificar seções estruturadas. Analisando documento completo...")
                        fre_sections = {"Documento Completo": fre_text[:10000]}
                
                st.markdown("### 🔄 Progresso da Análise")
                progress_bar = st.progress(0)
                status_text = st.empty()
                analysis_results = []
                total_sections = len(fre_sections)
                
                for i, (section_name, section_content) in enumerate(fre_sections.items()):
                    status_text.text(f"Analisando: {section_name}")
                    result = analyzer.analyze_fre_section(fre_text, cvm_text, section_name, section_content)
                    if result:
                        analysis_results.append(result)
                    progress_bar.progress((i + 1) / total_sections)
                    time.sleep(0.5)
                
                status_text.text("✅ Análise concluída!")
                st.session_state.cvm_analysis_results = analysis_results
                st.session_state.cvm_fre_filename = fre_file.name
                st.session_state.cvm_analysis_completed = True
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Erro durante a análise: {str(e)}")
    
    if st.session_state.cvm_analysis_completed and st.session_state.cvm_analysis_results:
        analysis_results = st.session_state.cvm_analysis_results
        st.markdown("### 📊 Resultados da Análise")
        
        col1, col2, col3, col4 = st.columns(4)
        total_pontos = sum(len(r.get('pontos_atencao', [])) for r in analysis_results)
        criticos = sum(1 for r in analysis_results for p in r.get('pontos_atencao', []) if p.get('criticidade') == 'CRITICO')
        atencao = sum(1 for r in analysis_results for p in r.get('pontos_atencao', []) if p.get('criticidade') == 'ATENCAO')
        sugestoes = sum(1 for r in analysis_results for p in r.get('pontos_atencao', []) if p.get('criticidade') == 'SUGESTAO')
        
        with col1: st.metric("📋 Total de Pontos", total_pontos)
        with col2: st.metric("🔴 Críticos", criticos)
        with col3: st.metric("🟡 Atenção", atencao)
        with col4: st.metric("🟢 Sugestões", sugestoes)
        
        st.markdown("### 🔍 Filtros")
        col1, col2 = st.columns(2)
        with col1:
            categorias_disponiveis = list(set(r.get('secao', 'N/A') for r in analysis_results))
            categoria_filtro = st.selectbox("Filtrar por categoria:", ["Todas"] + categorias_disponiveis, key="cvm_categoria_filter")
        with col2:
            criticidade_filtro = st.selectbox("Filtrar por criticidade:", ["Todas", "CRITICO", "ATENCAO", "SUGESTAO"], key="cvm_criticidade_filter")
        
        for result in analysis_results:
            if categoria_filtro != "Todas" and result.get('secao') != categoria_filtro:
                continue
            pontos_filtrados = result.get('pontos_atencao', [])
            if criticidade_filtro != "Todas":
                pontos_filtrados = [p for p in pontos_filtrados if p.get('criticidade') == criticidade_filtro]
            if not pontos_filtrados and criticidade_filtro != "Todas":
                continue
            
            with st.expander(f"📑 {result.get('secao', 'Seção não identificada')}", expanded=False):
                conformidade = result.get('conformidade', 'N/A')
                if conformidade == 'CONFORME': st.success(f"✅ Status: {conformidade}")
                elif conformidade == 'NAO_CONFORME': st.error(f"❌ Status: {conformidade}")
                else: st.warning(f"⚠️ Status: {conformidade}")
                st.write(f"**Resumo:** {result.get('resumo', 'N/A')}")
                if pontos_filtrados:
                    st.write("**Pontos de Atenção:**")
                    for i, ponto in enumerate(pontos_filtrados, 1):
                        criticidade = ponto.get('criticidade', 'N/A')
                        emoji = "🔴" if criticidade == "CRITICO" else "🟡" if criticidade == "ATENCAO" else "🟢"
                        st.write(f"{emoji} **Ponto {i}:** {ponto.get('problema', 'N/A')}")
                        st.write(f"**Base legal:** {ponto.get('artigo_cvm', 'N/A')}")
                        st.write(f"**Sugestão:** {ponto.get('sugestao', 'N/A')}")
                        st.write("---")
        
        st.markdown("### 📄 Relatório em PDF")
        if st.button("📥 Gerar Relatório PDF", type="secondary", key="cvm_pdf_button"):
            with st.spinner("📄 Gerando relatório PDF..."):
                analyzer = FREAnalyzer(api_key)
                pdf_buffer = analyzer.generate_pdf_report(analysis_results, st.session_state.cvm_fre_filename)
                st.download_button(
                    label="⬇️ Baixar Relatório PDF", data=pdf_buffer.getvalue(),
                    file_name=f"relatorio_fre_analise_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf"
                )
                st.success("✅ Relatório PDF gerado com sucesso!")

# Protege a execução do script para que ele só rode quando chamado diretamente
if __name__ == "__main__":
    # Configurações de página que eram globais agora são chamadas aqui
    st.set_page_config(
        page_title="Analisador FRE vs Normas CVM",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    main()
