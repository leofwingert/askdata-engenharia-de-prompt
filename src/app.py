import os
import sys
import time
import json
from pathlib import Path
import streamlit as st
from pypdf import PdfReader

# Importação blindada do motor RAG
try:
    from rag_engine import RAGEngine
except ImportError:
    from src.rag_engine import RAGEngine

# 1. Configuração da Página
st.set_page_config(
    page_title="AskData Workspace",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Design System Enterprise - Pixel Perfect Compact Gemini Dock
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    :root {
        --bg-canvas: #090B0E;
        --sidebar-surface: #060709;
        --card-surface: #111418;
        --card-hover: #161A20;
        --menu-surface: #101317;
        --border-glass: rgba(255, 255, 255, 0.07);
        --text-headline: #F8FAFC;
        --text-body: #94A3B8;
        --text-subtle: #64748B;
        --emerald-primary: #10B981;
        --emerald-glow: rgba(16, 185, 129, 0.16);
        --emerald-border: rgba(16, 185, 129, 0.45);
    }

    /* Tipografia e Fundo */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
        color: var(--text-headline);
    }
    code, pre { font-family: 'JetBrains Mono', monospace !important; }
    .stApp { background-color: var(--bg-canvas); }
    
    .block-container { 
        max-width: 740px !important; 
        padding-top: 2rem; 
        padding-bottom: 8.5rem; 
        margin: 0 auto; 
    }

    header[data-testid="stHeader"] {
        background: transparent !important;
        border: none !important;
    }
    #MainMenu, footer, .stDeployButton, [data-testid="stDeployButton"] {
        display: none !important;
    }

    /* ========================================================
       SIDEBAR ESTÁTICA COM TOPO E RODAPÉ FIXOS
       ======================================================== */
    [data-testid="stSidebar"] {
        background-color: var(--sidebar-surface) !important;
        border-right: 1px solid var(--border-glass) !important;
        z-index: 100 !important;
    }
    [data-testid="stSidebar"] [data-testid="stSidebarContent"] {
        background-color: var(--sidebar-surface) !important;
        padding-top: 5rem !important;
        padding-bottom: 7.5rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        overflow-y: auto !important;
    }

    /* Header Fixo da Sidebar */
    .sidebar-brand-fixed {
        position: fixed;
        top: 0;
        left: 0;
        width: 18rem;
        height: 4.8rem;
        background: var(--sidebar-surface);
        border-bottom: 1px solid var(--border-glass);
        display: flex;
        align-items: center;
        padding: 0 1.2rem;
        gap: 12px;
        z-index: 110;
    }
    .brand-icon-box {
        width: 36px;
        height: 36px;
        background: linear-gradient(135deg, #059669, #10B981);
        border-radius: 9px;
        display: grid;
        place-items: center;
        font-weight: 700;
        color: #07090C;
        font-size: 17px;
        box-shadow: 0 0 14px rgba(16, 185, 129, 0.3);
        flex-shrink: 0;
    }
    .brand-text-col {
        display: flex;
        flex-direction: column;
        line-height: 1.15;
    }
    .brand-title {
        font-size: 1.1rem;
        font-weight: 800;
        color: #F8FAFC;
        letter-spacing: -0.02em;
    }
    .brand-sub {
        font-size: 0.65rem;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        font-weight: 700;
        margin-top: 2px;
    }

    /* Rodapé Fixo da Sidebar */
    .sidebar-dock-fixed {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 18rem;
        height: 6.8rem;
        background: linear-gradient(180deg, rgba(6, 7, 9, 0.85) 0%, #060709 35%);
        border-top: 1px solid var(--border-glass);
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: flex-start;
        padding-left: 1.4rem;
        gap: 12px;
        z-index: 110;
    }
    .action-gear-btn {
        font-size: 1.3rem;
        color: #94A3B8;
        cursor: pointer;
        line-height: 1;
        transition: transform 0.25s ease, color 0.2s ease;
    }
    .action-gear-btn:hover {
        color: var(--emerald-primary);
        transform: rotate(45deg);
    }
    .action-avatar-box {
        width: 38px;
        height: 38px;
        border-radius: 50%;
        background: #10B981;
        display: grid;
        place-items: center;
        position: relative;
        cursor: pointer;
        box-shadow: 0 0 16px rgba(16, 185, 129, 0.4);
    }
    .avatar-inner-icon {
        font-size: 1.1rem;
        line-height: 1;
    }
    .avatar-live-indicator {
        position: absolute;
        bottom: -1px;
        right: -1px;
        width: 11px;
        height: 11px;
        border-radius: 50%;
        background: #10B981;
        border: 2px solid #060709;
    }

    /* Mini-Rail Recolhido */
    .collapsed-rail-static {
        position: fixed;
        left: 0;
        top: 0;
        bottom: 0;
        width: 58px;
        background: var(--sidebar-surface);
        border-right: 1px solid var(--border-glass);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        align-items: center;
        padding: 56px 0 20px 0;
        z-index: 35;
    }
    .rail-top-btn {
        width: 34px;
        height: 34px;
        background: var(--card-surface);
        border: 1px solid var(--emerald-border);
        border-radius: 8px;
        display: grid;
        place-items: center;
        color: var(--emerald-primary);
        font-size: 0.95rem;
    }
    .rail-bottom-stack {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 14px;
    }

    /* Linhas dos Documentos */
    .doc-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 8px 10px;
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid var(--border-glass);
        border-radius: 8px;
        margin-bottom: 6px;
        gap: 10px;
    }
    .doc-name {
        font-size: 0.78rem;
        color: #E2E8F0;
        font-weight: 500;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .doc-pill {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.70rem;
        font-weight: 600;
        color: var(--emerald-primary);
        background: rgba(16, 185, 129, 0.08);
        border: 1px solid rgba(16, 185, 129, 0.25);
        padding: 2px 7px;
        border-radius: 6px;
        white-space: nowrap;
        flex-shrink: 0;
    }

    .metric-badge-box {
        background: var(--card-surface);
        border: 1px solid var(--border-glass);
        border-radius: 10px;
        padding: 10px 12px;
        margin: 10px 0;
    }
    .metric-title { font-size: 0.68rem; text-transform: uppercase; color: var(--text-subtle); font-weight: 700; letter-spacing: 0.08em; }
    .metric-val { font-size: 1.1rem; font-weight: 700; color: var(--text-headline); margin-top: 2px; }

    /* Saudação Minimalista */
    .greeting-container {
        padding: 3.5rem 0.2rem 2.2rem 0.2rem;
        text-align: left;
    }
    .greeting-kicker {
        font-size: 0.92rem;
        font-weight: 500;
        color: #34D399;
        margin-bottom: 0.4rem;
        letter-spacing: -0.01em;
    }
    .greeting-heading {
        font-size: 2.25rem;
        font-weight: 600;
        letter-spacing: -0.035em;
        color: #F8FAFC;
        line-height: 1.2;
    }

    /* Mensagens do Chat */
    [data-testid="stChatMessage"] {
        background-color: var(--card-surface);
        border: 1px solid var(--border-glass);
        border-radius: 14px;
        padding: 1.2rem 1.4rem;
        margin: 0.9rem 0;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.35);
    }
    [data-testid="stChatMessage"][data-testid*="user"] {
        background: linear-gradient(180deg, rgba(18, 21, 26, 0.7) 0%, rgba(14, 17, 21, 0.9) 100%);
        border-color: var(--emerald-border);
    }

    .source-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(16, 185, 129, 0.08);
        border: 1px solid rgba(16, 185, 129, 0.28);
        color: var(--emerald-primary);
        border-radius: 6px;
        padding: 4px 10px;
        font-size: 0.76rem;
        font-weight: 500;
        margin-right: 6px;
        margin-top: 8px;
    }

    .executive-telemetry {
        display: flex;
        align-items: center;
        gap: 16px;
        flex-wrap: wrap;
        font-size: 0.75rem;
        color: var(--text-subtle);
        padding-top: 10px;
        margin-top: 14px;
        border-top: 1px solid var(--border-glass);
    }
    .executive-cost { color: var(--emerald-primary); font-weight: 600; }

    /* =========================================================================
       CÁPSULA PERPLEXITY DOCK: COMPACTA (740px) E COM CONTROLOS DA DIREITA UNIDOS
       ========================================================================= */
    div[data-testid="stBottom"] {
        background: transparent !important;
        border: none !important;
    }
    div[data-testid="stBottom"] > div {
        background: transparent !important;
        border: none !important;
        max-width: 740px !important;
        margin: 0 auto 16px auto !important;
        padding: 0 !important;
    }

    /* O CONTAINER DE COLUNAS É A PRÓPRIA CÁPSULA COM PADDING COMPACTO */
    div[data-testid="stBottom"] div[data-testid="stHorizontalBlock"] {
        background: #0D1014 !important;
        border: 1.5px solid var(--emerald-border) !important;
        border-radius: 32px !important;
        box-shadow: 0 0 20px rgba(16, 185, 129, 0.16), 0 8px 30px rgba(0, 0, 0, 0.85) !important;
        padding: 3px 6px !important;
        display: flex !important;
        align-items: center !important;
        width: 100% !important;
        box-sizing: border-box !important;
        gap: 2px !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
    }
    div[data-testid="stBottom"] div[data-testid="stHorizontalBlock"]:focus-within {
        border-color: rgba(16, 185, 129, 0.9) !important;
        box-shadow: 0 0 28px rgba(16, 185, 129, 0.28), 0 10px 40px rgba(0, 0, 0, 0.9) !important;
    }

    /* 1. Botão '+' Popover da esquerda */
    div[data-testid="stBottom"] div[data-testid="stColumn"]:first-child button {
        background: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: var(--emerald-primary) !important;
        font-size: 1.2rem !important;
        width: 34px !important;
        height: 34px !important;
        min-height: 34px !important;
        border-radius: 50% !important;
        padding: 0 !important;
        display: grid !important;
        place-items: center !important;
        margin: 0 !important;
        transition: all 0.2s ease !important;
    }
    div[data-testid="stBottom"] div[data-testid="stColumn"]:first-child button svg {
        display: none !important;
    }
    div[data-testid="stBottom"] div[data-testid="stColumn"]:first-child button:hover {
        background: rgba(16, 185, 129, 0.2) !important;
        border-color: var(--emerald-border) !important;
        transform: scale(1.06) !important;
    }

    /* 2. Campo de Chat Central Transparente */
    div[data-testid="stBottom"] div[data-testid="stColumn"]:nth-child(2) div[data-testid="stChatInput"],
    div[data-testid="stBottom"] div[data-testid="stColumn"]:nth-child(2) div[data-testid="stChatInput"] > div {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
        margin: 0 !important;
        width: 100% !important;
    }
    div[data-testid="stBottom"] div[data-testid="stColumn"]:nth-child(2) div[data-testid="stChatInput"] textarea {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: #F8FAFC !important;
        font-size: 0.90rem !important;
        padding: 8px 6px !important;
        min-height: 36px !important;
        max-height: 70px !important;
    }

    /* Remove o botão cinza nativo duplicado */
    div[data-testid="stBottom"] div[data-testid="stColumn"]:nth-child(2) div[data-testid="stChatInputSubmitButton"],
    div[data-testid="stBottom"] div[data-testid="stColumn"]:nth-child(2) button[data-testid="stChatInputSubmitButton"] {
        display: none !important;
        visibility: hidden !important;
    }

    /* 3. Seletor de Modelo Compacto e Colado ao Botão de Envio */
    div[data-testid="stBottom"] div[data-testid="stColumn"]:nth-child(3) button {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        color: #CBD5E1 !important;
        font-size: 0.72rem !important;
        font-weight: 600 !important;
        height: 32px !important;
        min-height: 32px !important;
        padding: 0 8px !important;
        border-radius: 8px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        white-space: nowrap !important;
        margin: 0 2px 0 0 !important;
        transition: all 0.2s ease !important;
    }
    div[data-testid="stBottom"] div[data-testid="stColumn"]:nth-child(3) button:hover {
        background: rgba(16, 185, 129, 0.16) !important;
        border-color: var(--emerald-border) !important;
        color: var(--emerald-primary) !important;
    }

    /* 4. Botão de Envio Verde (↑) */
    div[data-testid="stBottom"] div[data-testid="stColumn"]:last-child button {
        background: var(--emerald-primary) !important;
        color: #060709 !important;
        border: none !important;
        border-radius: 50% !important;
        width: 32px !important;
        height: 32px !important;
        min-height: 32px !important;
        font-size: 1.05rem !important;
        font-weight: 700 !important;
        display: grid !important;
        place-items: center !important;
        padding: 0 !important;
        margin: 0 !important;
        box-shadow: 0 0 12px rgba(16, 185, 129, 0.45) !important;
        transition: all 0.18s ease !important;
    }
    div[data-testid="stBottom"] div[data-testid="stColumn"]:last-child button:hover {
        background: #34D399 !important;
        transform: scale(1.06) !important;
    }

    /* Menus Suspensos / Popovers */
    [data-testid="stPopoverBody"] {
        background-color: var(--menu-surface) !important;
        border: 1px solid var(--border-glass) !important;
        border-radius: 12px !important;
        box-shadow: 0 16px 40px rgba(0, 0, 0, 0.85) !important;
        padding: 1.1rem !important;
        min-width: 320px !important;
    }
    .popover-header { font-size: 0.82rem; font-weight: 700; color: #F8FAFC; margin-bottom: 2px; }
    .popover-desc { font-size: 0.70rem; color: #94A3B8; margin-bottom: 10px; line-height: 1.4; }

    /* Botões da Sidebar */
    [data-testid="stSidebar"] button {
        background-color: var(--card-surface);
        color: var(--text-body);
        border: 1px solid var(--border-glass);
        border-radius: 8px;
        font-size: 0.8rem;
        padding: 0.5rem 0.8rem;
    }
    [data-testid="stSidebar"] button:hover {
        background-color: var(--card-hover);
        color: var(--emerald-primary);
        border-color: var(--emerald-border);
    }
</style>
""", unsafe_allow_html=True)

# 3. Inicialização do Motor RAG
@st.cache_resource(show_spinner=False)
def carregar_motor_rag():
    return RAGEngine()

try:
    engine = carregar_motor_rag()
except Exception as erro:
    st.error(f"Erro ao inicializar workspace: {erro}")
    st.stop()

# 4. Catálogo Oficial de Fontes
FONTES_DISPONIVEIS = {
    "doc_1": {"arquivo": "PDF 1 -21 - PAGINAS.pdf", "titulo": "Guia Inovacoop", "paginas": 21},
    "doc_2": {"arquivo": "PDF 2 -15 - PAGINAS.pdf", "titulo": "Diretrizes ANIA - TCESP", "paginas": 15},
    "doc_3": {"arquivo": "PDF 3 -12 - PAGINAS.pdf", "titulo": "Survey Avançado (Sahoo)", "paginas": 12},
    "doc_4": {"arquivo": "PDF 4 -25 - PAGINAS.pdf", "titulo": "Framework Sistemático (Liu)", "paginas": 25}
}

MAPA_ARQUIVO_TITULO = {v["arquivo"]: v["titulo"] for v in FONTES_DISPONIVEIS.values()}

def formatar_titulo_documento(nome_bruto: str) -> str:
    return MAPA_ARQUIVO_TITULO.get(nome_bruto, nome_bruto.replace(".pdf", "").replace("-", " ").strip())

# 5. Modelos Disponíveis
OPCOES_MODELOS = {
    "gemini-3.5-flash-lite": {
        "label": "3.5 Flash Lite",
        "subtitulo": "Mais rápido · Menor custo",
        "status": "Ativo no Motor"
    },
    "gemini-3.8-flash": {
        "label": "3.8 Flash",
        "subtitulo": "Equilibrado · Síntese ampla",
        "status": "Disponível na v2"
    },
    "gemini-3.1-pro": {
        "label": "3.1 Pro",
        "subtitulo": "Raciocínio profundo · Auditoria",
        "status": "Disponível na v2"
    }
}

# 6. Estado da Sessão & Controle de Fontes
if "mensagens" not in st.session_state:
    st.session_state.mensagens = []

if "modelo_selecionado" not in st.session_state:
    st.session_state.modelo_selecionado = "gemini-3.5-flash-lite"

if "fontes_ativas" not in st.session_state:
    st.session_state.fontes_ativas = set(FONTES_DISPONIVEIS.keys())

if "chk_todas" not in st.session_state:
    st.session_state.chk_todas = True

for k in FONTES_DISPONIVEIS:
    if f"chk_{k}" not in st.session_state:
        st.session_state[f"chk_{k}"] = True

def ao_mudar_master_todas():
    novo_valor = st.session_state.chk_todas
    if novo_valor:
        st.session_state.fontes_ativas = set(FONTES_DISPONIVEIS.keys())
        for k in FONTES_DISPONIVEIS:
            st.session_state[f"chk_{k}"] = True
    else:
        st.session_state.fontes_ativas = set()
        for k in FONTES_DISPONIVEIS:
            st.session_state[f"chk_{k}"] = False

def ao_mudar_individual(chave: str):
    if st.session_state[f"chk_{chave}"]:
        st.session_state.fontes_ativas.add(chave)
    else:
        st.session_state.fontes_ativas.discard(chave)

    if len(st.session_state.fontes_ativas) == len(FONTES_DISPONIVEIS):
        st.session_state.chk_todas = True
    else:
        st.session_state.chk_todas = False

pergunta_para_processar = None
PASTA_DATA = Path("data")
PASTA_DATA.mkdir(exist_ok=True)

# 7. Mini-Rail Visível Quando a Barra Lateral é Recolhida
st.markdown("""
<div class="collapsed-rail-static">
    <div class="rail-top-btn" title="AskData">⚡</div>
    <div class="rail-bottom-stack">
        <div class="action-gear-btn" title="Configurações">⚙️</div>
        <div class="action-avatar-box" title="Usuário Ativo">
            <span class="avatar-inner-icon">🤖</span>
            <span class="avatar-live-indicator"></span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# 8. Barra Lateral Expandida
with st.sidebar:
    # Topo Fixo e Estático: AskData ENTERPRISE
    st.markdown("""
    <div class="sidebar-brand-fixed">
        <div class="brand-icon-box">⚡</div>
        <div class="brand-text-col">
            <span class="brand-title">AskData</span>
            <span class="brand-sub">ENTERPRISE WORKSPACE</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Base Documental
    with st.expander("📁 Base Documental Ativa", expanded=True):
        st.caption("Fontes homologadas na base vetorial:")
        for doc_info in FONTES_DISPONIVEIS.values():
            st.markdown(f"""
            <div class="doc-row">
                <span class="doc-name" title="{doc_info['titulo']}">{doc_info['titulo']}</span>
                <span class="doc-pill">{doc_info['paginas']} págs</span>
            </div>
            """, unsafe_allow_html=True)

    # Painel de Governança
    st.markdown("""
    <div class="metric-badge-box">
        <div class="metric-title">Volume de Conhecimento</div>
        <div class="metric-val">73 páginas <span style="font-size: 0.75rem; color: #94A3B8; font-weight: 400;">(477 vetores)</span></div>
        <div style="margin-top: 6px; font-size: 0.72rem; color: #10B981; font-weight: 600;">● ChromaDB Local Persistente (HNSW)</div>
    </div>
    """, unsafe_allow_html=True)

    # Slider Oficial de Top-K Chunks
    st.markdown('<div style="font-size: 0.68rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; color: #64748B; margin: 1.2rem 0 0.4rem;">Profundidade de Busca (Top-K Chunks)</div>', unsafe_allow_html=True)
    top_k_chunks = st.slider(
        "Quantidade de Chunks recuperados:",
        min_value=2,
        max_value=6,
        value=4,
        help="Quantidade de fragmentos resgatados do ChromaDB via similaridade de cosseno."
    )

    # Consultas Recentes
    perguntas_feitas = [m["content"] for m in st.session_state.mensagens if m["role"] == "user"]
    if perguntas_feitas:
        st.markdown('<div style="font-size: 0.68rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: #64748B; margin: 1rem 0 0.4rem;">Consultas Recentes</div>', unsafe_allow_html=True)
        for p in reversed(perguntas_feitas[-3:]):
            st.caption(f"• {p[:36]}..." if len(p) > 36 else f"• {p}")

    st.markdown("---")
    col_limpar, col_exportar = st.columns(2)
    with col_limpar:
        if st.button("Nova Consulta", use_container_width=True):
            st.session_state.mensagens = []
            st.rerun()
    with col_exportar:
        if len(st.session_state.mensagens) > 0:
            dados_json = json.dumps(st.session_state.mensagens, indent=2, ensure_ascii=False)
            st.download_button(
                "📥 Baixar JSON",
                data=dados_json,
                file_name="historico_askdata.json",
                mime="application/json",
                use_container_width=True
            )

    # Rodapé Fixo e Estático: Engrenagem e Avatar
    st.markdown("""
    <div class="sidebar-dock-fixed">
        <div class="action-gear-btn" title="Configurações do Sistema">⚙️</div>
        <div class="action-avatar-box" title="Usuário Ativo">
            <span class="avatar-inner-icon">🤖</span>
            <span class="avatar-live-indicator"></span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# 9. Área Central: Saudação Minimalista Estilo Gemini/Claude
if not st.session_state.mensagens:
    st.markdown("""
    <div class="greeting-container">
        <div class="greeting-kicker">Workspace</div>
        <div class="greeting-heading">No que vamos trabalhar?</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: #64748B; margin-bottom: 0.8rem;">Consultas Estratégicas Frequentes</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Matriz PACIF: Estrutura dos 5 pilares para prompts eficazes", use_container_width=True):
            pergunta_para_processar = "O que significa a matriz PACIF e suas 5 letras?"
        if st.button("Chain of Verification (CoVe): Mitigação sistemática de alucinações", use_container_width=True):
            pergunta_para_processar = "O que é a técnica Chain of Verification (CoVe) e qual problema ela busca resolver?"
    with c2:
        if st.button("Projeto ANIA (TCESP): Módulos e aplicação de IA no setor público", use_container_width=True):
            pergunta_para_processar = "Quais são as ferramentas do projeto ANIA do TCESP?"
        if st.button("Teste de Guardrail: Pergunta externa fora de escopo (Copa 2002)", use_container_width=True):
            pergunta_para_processar = "Qual foi a escalação titular da seleção brasileira na final da Copa de 2002?"

else:
    for msg in st.session_state.mensagens:
        with st.chat_message(msg["role"]):
            if msg["role"] == "user" and msg.get("escopo_rotulo"):
                st.caption(f"🎯 Escopo da pesquisa: **{msg['escopo_rotulo']}**")
            
            st.markdown(msg["content"])

            if msg.get("latencia", 0.0) > 0:
                fontes = msg.get("fontes", [])
                
                if fontes:
                    citacoes_unicas = set()
                    tags_html = ""
                    for f in fontes:
                        nome_formatado = formatar_titulo_documento(f['arquivo'])
                        chave = f"{nome_formatado} · p. {f['pagina']}"
                        if chave not in citacoes_unicas:
                            citacoes_unicas.add(chave)
                            tags_html += f'<span class="source-badge">📄 {nome_formatado} · Página {f["pagina"]}</span>'
                    st.markdown(tags_html, unsafe_allow_html=True)

                tempo = msg.get('latencia', 0.0)
                custo = msg.get('custo_usd', 0.0)
                confianca = "Alta Fidelidade" if msg.get('confianca') == "ALTA" else "Fidelidade Parcial"
                modelo_usado = msg.get('modelo', '3.5 Flash Lite')
                
                st.markdown(f"""
                <div class="executive-telemetry">
                    <span>Tempo de resposta: <strong>{tempo:.2f}s</strong></span>
                    <span>Ancoragem: <strong>{confianca}</strong></span>
                    <span>Modelo: <strong>{modelo_usado}</strong></span>
                    <span>Custo do processamento: <span class="executive-cost">${custo:.6f} USD</span></span>
                </div>
                """, unsafe_allow_html=True)

                if fontes:
                    with st.expander("📚 Inspecionar Chunks Resgatados & Similaridade de Cosseno"):
                        for idx, f in enumerate(fontes, 1):
                            titulo = formatar_titulo_documento(f['arquivo'])
                            st.markdown(f"**Fonte [{idx}]:** `{f['arquivo']}` ({titulo}) — **Página {f['pagina']}** · *Similaridade: {f['similaridade']:.2%}*")
                            st.caption(f['texto'])
                            st.markdown("---")

# 10. Gestão do Escopo de Fontes
arquivos_para_filtro = [FONTES_DISPONIVEIS[k]["arquivo"] for k in st.session_state.fontes_ativas]

if len(st.session_state.fontes_ativas) == len(FONTES_DISPONIVEIS):
    rotulo_escopo_atual = "Toda a Base (Pesquisa Global)"
elif len(st.session_state.fontes_ativas) == 0:
    rotulo_escopo_atual = "Nenhuma fonte selecionada"
else:
    nomes_selecionados = [FONTES_DISPONIVEIS[k]["titulo"] for k in st.session_state.fontes_ativas]
    rotulo_escopo_atual = ", ".join(nomes_selecionados)

# 11. CÁPSULA PERPLEXITY DOCK: COMPACTA E COM ELEMENTOS AGRUPADOS NA DIREITA
with st.bottom:
    col_add, col_input, col_model, col_send = st.columns([0.05, 0.77, 0.13, 0.05])

    with col_add:
        with st.popover("＋"):
            st.markdown('<div class="popover-header">Fontes de Consulta</div>', unsafe_allow_html=True)
            st.markdown('<div class="popover-desc">Selecione as bases para direcionar a busca semântica:</div>', unsafe_allow_html=True)

            st.checkbox(
                "Selecionar todas as fontes",
                value=st.session_state.chk_todas,
                key="chk_todas",
                on_change=ao_mudar_master_todas
            )

            st.markdown('<hr style="border: none; border-top: 1px solid rgba(255,255,255,0.08); margin: 8px 0;">', unsafe_allow_html=True)
            for k, v in FONTES_DISPONIVEIS.items():
                st.checkbox(
                    f"{v['titulo']} ({v['paginas']} págs)",
                    value=st.session_state[f"chk_{k}"],
                    key=f"chk_{k}",
                    on_change=ao_mudar_individual,
                    args=(k,)
                )

            st.markdown('<hr style="border: none; border-top: 1px solid rgba(255,255,255,0.08); margin: 8px 0;">', unsafe_allow_html=True)
            arquivo_up = st.file_uploader("Upload de PDF ou MD:", type=["pdf", "md"], label_visibility="collapsed")
            if arquivo_up:
                if st.button("Sincronizar Arquivo", use_container_width=True):
                    caminho = PASTA_DATA / arquivo_up.name
                    with open(caminho, "wb") as f:
                        f.write(arquivo_up.getvalue())
                    st.success(f"'{arquivo_up.name}' pronto para pesquisa!")
                    time.sleep(0.6)
                    st.rerun()

    with col_input:
        prompt_digitado = st.chat_input("Consulte qualquer norma, procedimento ou técnica...")

    with col_model:
        modelo_atual_info = OPCOES_MODELOS[st.session_state.modelo_selecionado]
        with st.popover(f"⚡ {modelo_atual_info['label']} ▾"):
            st.markdown('<div class="popover-header">Modelo de Linguagem</div>', unsafe_allow_html=True)
            for chave_mod, dados_mod in OPCOES_MODELOS.items():
                escolhido = (chave_mod == st.session_state.modelo_selecionado)
                prefixo = "✓ " if escolhido else "○ "
                if st.button(
                    f"{prefixo}{dados_mod['label']} · {dados_mod['status']}", 
                    key=f"mod_btn_{chave_mod}", 
                    use_container_width=True
                ):
                    st.session_state.modelo_selecionado = chave_mod
                    st.rerun()

    with col_send:
        enviar_clicado = st.button("↑", key="btn_submit_dock")

# 12. Processamento da Pergunta e Invocação do RAG
if prompt_digitado:
    pergunta_para_processar = prompt_digitado
elif enviar_clicado and prompt_digitado:
    pergunta_para_processar = prompt_digitado

if pergunta_para_processar:
    st.session_state.mensagens.append({
        "role": "user",
        "content": pergunta_para_processar,
        "escopo_rotulo": rotulo_escopo_atual,
        "fontes": [],
        "latencia": 0.0
    })
    with st.chat_message("user"):
        if rotulo_escopo_atual != "Toda a Base (Pesquisa Global)":
            st.caption(f"🎯 Escopo da pesquisa: **{rotulo_escopo_atual}**")
        st.markdown(pergunta_para_processar)

    with st.chat_message("assistant"):
        with st.spinner("Analisando base documental e validando evidências..."):
            resultado = engine.responder_pergunta(
                pergunta_para_processar, 
                top_k=top_k_chunks, 
                arquivos_filtro=arquivos_para_filtro if len(st.session_state.fontes_ativas) < len(FONTES_DISPONIVEIS) else None
            )
            resposta = resultado["resposta"]
            fontes = resultado["fontes"]
            latencia = resultado["latencia"]
            tokens_in = resultado["tokens_in"]
            tokens_out = resultado["tokens_out"]
            custo = resultado["custo_usd"]
            confianca = resultado["confianca"]

            for arq_bruto, titulo_limpo in MAPA_ARQUIVO_TITULO.items():
                resposta = resposta.replace(arq_bruto, titulo_limpo)

            area_texto = st.empty()
            texto_acumulado = ""
            for char in resposta:
                texto_acumulado += char
                area_texto.markdown(texto_acumulado + "▌")
                time.sleep(0.003)
            area_texto.markdown(resposta)

            if fontes:
                citacoes_unicas = set()
                tags_html = ""
                for f in fontes:
                    nome_formatado = formatar_titulo_documento(f['arquivo'])
                    chave = f"{nome_formatado} · p. {f['pagina']}"
                    if chave not in citacoes_unicas:
                        citacoes_unicas.add(chave)
                        tags_html += f'<span class="source-badge">📄 {nome_formatado} · Página {f["pagina"]}</span>'
                st.markdown(tags_html, unsafe_allow_html=True)

            conf_legivel = "Alta Fidelidade" if confianca == "ALTA" else "Fidelidade Parcial"
            modelo_rotulo = OPCOES_MODELOS[st.session_state.modelo_selecionado]["label"]
            st.markdown(f"""
            <div class="executive-telemetry">
                <span>Tempo de resposta: <strong>{latencia:.2f}s</strong></span>
                <span>Ancoragem: <strong>{conf_legivel}</strong></span>
                <span>Modelo: <strong>{modelo_rotulo}</strong></span>
                <span>Custo do processamento: <span class="executive-cost">${custo:.6f} USD</span></span>
            </div>
            """, unsafe_allow_html=True)

            if fontes:
                with st.expander("📚 Inspecionar Chunks Resgatados & Similaridade de Cosseno"):
                    for idx, f in enumerate(fontes, 1):
                        titulo = formatar_titulo_documento(f['arquivo'])
                        st.markdown(f"**Fonte [{idx}]:** `{f['arquivo']}` ({titulo}) — **Página {f['pagina']}** · *Similaridade: {f['similaridade']:.2%}*")
                        st.caption(f['texto'])
                        st.markdown("---")

            st.session_state.mensagens.append({
                "role": "assistant",
                "content": resposta,
                "fontes": fontes,
                "latencia": latencia,
                "tokens_in": tokens_in,
                "tokens_out": tokens_out,
                "custo_usd": custo,
                "confianca": confianca,
                "modelo": modelo_rotulo
            })
            st.rerun()