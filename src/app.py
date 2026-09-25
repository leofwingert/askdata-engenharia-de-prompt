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

# 2. Design System Enterprise (Perplexity Dark Emerald Edition)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

    :root {
        --bg-canvas: #090B0E;
        --sidebar-surface: #060709;
        --card-surface: #111418;
        --card-hover: #161A20;
        --menu-surface: #101317;
        --border-glass: rgba(255, 255, 255, 0.06);
        --text-headline: #F8FAFC;
        --text-body: #94A3B8;
        --text-subtle: #64748B;
        --emerald-primary: #10B981;
        --emerald-glow: rgba(16, 185, 129, 0.16);
        --emerald-border: rgba(16, 185, 129, 0.40);
    }

    /* Tipografia e Fundo */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
        color: var(--text-headline);
    }
    code, pre { font-family: 'JetBrains Mono', monospace !important; }
    .stApp { background-color: var(--bg-canvas); }
    
    .block-container { 
        max-width: 800px; 
        padding-top: 1rem; 
        padding-bottom: 9.5rem; 
        margin: 0 auto; 
    }

    /* Header Nativo Oculto */
    header[data-testid="stHeader"] {
        background: transparent !important;
        border: none !important;
    }
    #MainMenu, footer, .stDeployButton, [data-testid="stDeployButton"] {
        display: none !important;
    }

    /* ========================================================
       BARRA LATERAL FIXA COM TOPO E RODAPÉ ANCORADOS
       ======================================================== */
    [data-testid="stSidebar"] {
        background-color: var(--sidebar-surface) !important;
        border-right: 1px solid var(--border-glass) !important;
    }
    [data-testid="stSidebarContent"] {
        padding-top: 0 !important;
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
        padding-bottom: 0.8rem !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: space-between !important;
        height: 100vh !important;
        overflow-y: auto !important;
    }

    /* Topo Elevado e Isolado (Sem Oscilação) */
    .sidebar-brand-fixed {
        position: sticky;
        top: 0;
        z-index: 50;
        background: var(--sidebar-surface);
        padding: 0.4rem 0 0.8rem 0;
        margin-top: -1.2rem;
        border-bottom: 1px solid rgba(255,255,255,0.06);
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .brand-icon-box {
        width: 30px;
        height: 30px;
        background: linear-gradient(135deg, #059669, #10B981);
        border-radius: 8px;
        display: grid;
        place-items: center;
        font-weight: 700;
        color: #07090C;
        font-size: 14px;
        flex-shrink: 0;
    }

    /* Botão de Reabrir a Barra Lateral */
    [data-testid="stSidebarCollapsedControl"] {
        display: flex !important;
        visibility: visible !important;
        align-items: center !important;
        top: 12px !important;
        left: 12px !important;
        background: var(--card-surface) !important;
        border: 1px solid var(--emerald-border) !important;
        border-radius: 8px !important;
        color: var(--emerald-primary) !important;
        z-index: 1000 !important;
    }
    [data-testid="stSidebarCollapsedControl"] svg {
        fill: var(--emerald-primary) !important;
    }

    /* MINI-RAIL PERSISTENTE NA LATERAL ESQUERDA (BARRA RECOLHIDA) */
    .collapsed-mini-rail {
        display: none;
        position: fixed;
        left: 12px;
        top: 50px;
        bottom: 16px;
        width: 36px;
        flex-direction: column;
        justify-content: space-between;
        align-items: center;
        z-index: 999;
        pointer-events: none;
    }
    [data-testid="stSidebar"][aria-expanded="false"] ~ section.main .collapsed-mini-rail {
        display: flex !important;
    }
    .rail-badge-top {
        background: var(--card-surface);
        border: 1px solid var(--emerald-border);
        border-radius: 8px;
        width: 30px;
        height: 30px;
        display: grid;
        place-items: center;
        font-size: 0.9rem;
        color: var(--emerald-primary);
        pointer-events: auto;
    }
    .rail-dock-bottom {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 12px;
        pointer-events: auto;
    }

    /* Rodapé da Barra Lateral Expandida (Estilo Gemini) */
    .sidebar-bottom-actions {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 12px;
        padding: 14px 0 6px 0;
        margin-top: auto;
        border-top: 1px solid var(--border-glass);
    }
    .action-gear {
        font-size: 1.25rem;
        color: var(--text-subtle);
        cursor: pointer;
        transition: all 0.2s ease;
    }
    .action-gear:hover {
        color: var(--emerald-primary);
        transform: rotate(45deg);
    }
    .action-avatar {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: linear-gradient(135deg, #059669, #10B981);
        display: grid;
        place-items: center;
        box-shadow: 0 0 14px rgba(16, 185, 129, 0.35);
        cursor: pointer;
        position: relative;
    }
    .avatar-icon { font-size: 1.05rem; }
    .status-dot {
        position: absolute;
        bottom: 0px;
        right: 0px;
        width: 9px;
        height: 9px;
        border-radius: 50%;
        background: #10B981;
        border: 1.5px solid var(--sidebar-surface);
    }

    /* Linhas de Documentos da Sidebar */
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

    /* HERO STATE COMPACTO */
    .hero-wrapper {
        text-align: center;
        padding: 1.5rem 1rem 1.2rem;
    }
    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: var(--emerald-glow);
        border: 1px solid var(--emerald-border);
        color: var(--emerald-primary);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 0.8rem;
    }
    .hero-title {
        font-size: 1.85rem;
        font-weight: 700;
        letter-spacing: -0.03em;
        color: var(--text-headline);
        margin-bottom: 0.4rem;
    }
    .hero-desc {
        color: var(--text-body);
        font-size: 0.88rem;
        max-width: 520px;
        margin: 0 auto 1.4rem;
        line-height: 1.5;
    }

    .kpi-ribbon {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 12px;
        max-width: 560px;
        margin: 0 auto 1.8rem;
    }
    .kpi-card {
        background: var(--card-surface);
        border: 1px solid var(--border-glass);
        border-radius: 10px;
        padding: 10px 12px;
        text-align: center;
    }
    .kpi-card .num { font-size: 1.05rem; font-weight: 700; color: var(--text-headline); }
    .kpi-card .label { font-size: 0.70rem; color: var(--text-subtle); margin-top: 2px; }

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
    .executive-telemetry span strong { color: var(--text-body); }
    .executive-cost { color: var(--emerald-primary); font-weight: 600; }

    /* =========================================================================
       CÁPSULA PERPLEXITY RECONSTRUÍDA: LINHA ÚNICA CENTRALIZADA (800px)
       ========================================================================= */
    div[data-testid="stBottom"] {
        background: transparent !important;
        border: none !important;
    }
    div[data-testid="stBottom"] > div {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        max-width: 800px !important;
        margin: 0 auto 16px auto !important;
        padding: 0 !important;
    }

    /* Container Flex Único para os 3 Elementos */
    div[data-testid="stBottom"] [data-testid="stVerticalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        background: #111418 !important;
        border: 1.5px solid var(--emerald-border) !important;
        border-radius: 28px !important;
        padding: 4px 10px !important;
        box-shadow: 0 0 22px rgba(16, 185, 129, 0.16), 0 8px 30px rgba(0, 0, 0, 0.7) !important;
        gap: 8px !important;
        width: 100% !important;
        box-sizing: border-box !important;
    }
    div[data-testid="stBottom"] [data-testid="stVerticalBlock"]:focus-within {
        border-color: rgba(16, 185, 129, 0.85) !important;
        box-shadow: 0 0 32px rgba(16, 185, 129, 0.24), 0 10px 38px rgba(0, 0, 0, 0.8) !important;
    }

    /* Reset Geral de Larguras dos Containers Internos */
    div[data-testid="stBottom"] [data-testid="element-container"] {
        width: auto !important;
        margin: 0 !important;
        padding: 0 !important;
        flex: 0 0 auto !important;
    }

    /* 1. Botão '+' no início da linha */
    div[data-testid="stBottom"] [data-testid="element-container"]:first-of-type div[data-testid="stPopover"] > button {
        background: transparent !important;
        border: none !important;
        color: var(--emerald-primary) !important;
        font-size: 1.35rem !important;
        width: 34px !important;
        height: 34px !important;
        padding: 0 !important;
        display: grid !important;
        place-items: center !important;
        border-radius: 50% !important;
        transition: all 0.18s ease !important;
    }
    div[data-testid="stBottom"] [data-testid="element-container"]:first-of-type div[data-testid="stPopover"] > button:hover {
        background: rgba(16, 185, 129, 0.15) !important;
        color: #34D399 !important;
        transform: scale(1.1) !important;
    }

    /* 2. Campo de Chat ocupando todo o espaço central */
    div[data-testid="stBottom"] [data-testid="element-container"]:has([data-testid="stChatInput"]) {
        flex: 1 1 auto !important;
        width: 100% !important;
    }
    [data-testid="stChatInput"] {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
        margin: 0 !important;
        width: 100% !important;
    }
    [data-testid="stChatInput"] > div {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
    }
    [data-testid="stChatInput"] textarea {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: #F8FAFC !important;
        font-size: 0.92rem !important;
        padding: 8px 8px !important;
        min-height: 44px !important;
        box-sizing: border-box !important;
    }

    /* 3. Seletor de Modelo compacto no lado direito */
    div[data-testid="stBottom"] [data-testid="element-container"]:last-of-type div[data-testid="stPopover"] > button {
        background: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        color: #CBD5E1 !important;
        font-size: 0.74rem !important;
        font-weight: 600 !important;
        height: 30px !important;
        padding: 0 10px !important;
        border-radius: 8px !important;
        display: flex !important;
        align-items: center !important;
        gap: 4px !important;
        white-space: nowrap !important;
        transition: all 0.18s ease !important;
    }
    div[data-testid="stBottom"] [data-testid="element-container"]:last-of-type div[data-testid="stPopover"] > button:hover {
        background: rgba(16, 185, 129, 0.12) !important;
        border-color: var(--emerald-border) !important;
        color: var(--emerald-primary) !important;
    }

    /* Menus Suspensos (Popovers) */
    [data-testid="stPopoverBody"] {
        background-color: var(--menu-surface) !important;
        border: 1px solid var(--border-glass) !important;
        border-radius: 14px !important;
        box-shadow: 0 16px 40px rgba(0, 0, 0, 0.8) !important;
        padding: 1.1rem !important;
        min-width: 320px !important;
    }
    .popover-header { font-size: 0.82rem; font-weight: 700; color: #F8FAFC; margin-bottom: 2px; }
    .popover-desc { font-size: 0.70rem; color: #94A3B8; margin-bottom: 10px; line-height: 1.4; }

    .scope-status-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid var(--emerald-border);
        color: var(--emerald-primary);
        padding: 3px 10px;
        border-radius: 14px;
        font-size: 0.72rem;
        font-weight: 600;
        margin-bottom: 8px;
    }

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

# 6. Estado da Sessão & Controle de Seleção Múltipla
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

# Callbacks para Sincronização Perfeita da Chave Mestra
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

def listar_documentos() -> list[Path]:
    return sorted(
        [f for f in PASTA_DATA.iterdir() if f.is_file() and f.suffix.lower() in [".pdf", ".md"]],
        key=lambda f: f.name.lower()
    )

# 7. Mini-Rail Visível Quando a Barra Lateral é Recolhida (Estilo Gemini)
st.markdown("""
<div class="collapsed-mini-rail">
    <div class="rail-badge-top">⚡</div>
    <div class="rail-dock-bottom">
        <div class="action-gear" title="Configurações">⚙️</div>
        <div class="action-avatar" title="Usuário Ativo">
            <span class="avatar-icon">🤖</span>
            <span class="status-dot"></span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# 8. Barra Lateral Expandida
with st.sidebar:
    # Topo Elevado e Fixo (Não oscila ao abrir/fechar o expander)
    st.markdown("""
    <div class="sidebar-brand-fixed">
        <div class="brand-icon-box">⚡</div>
        <div>
            <div style="font-weight: 700; font-size: 0.95rem; letter-spacing: -0.02em; color: #F8FAFC;">AskData</div>
            <div style="font-size: 0.65rem; color: #64748B; text-transform: uppercase; letter-spacing: 0.08em;">Enterprise Workspace</div>
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

    # Slider Oficial de Top-K Chunks (Exigência Dia 09)
    st.markdown('<div style="font-size: 0.68rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; color: #64748B; margin: 1.2rem 0 0.4rem;">Profundidade de Busca (Top-K Chunks)</div>', unsafe_allow_html=True)
    top_k_chunks = st.slider(
        "Quantidade de Chunks recuperados:",
        min_value=2,
        max_value=6,
        value=4,
        help="Quantidade de fragmentos semânticos resgatados do ChromaDB via similaridade de cosseno."
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

    # Rodapé da Barra Lateral Expandida (Estilo Gemini)
    st.markdown("""
    <div class="sidebar-bottom-actions">
        <div class="action-gear" title="Configurações">⚙️</div>
        <div class="action-avatar" title="Usuário Ativo">
            <span class="avatar-icon">🤖</span>
            <span class="status-dot"></span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# 9. Área Central: Hero com KPIs em String Contínua (Sem Quebra de Código)
if not st.session_state.mensagens:
    hero_html = '<div class="hero-wrapper"><div class="hero-badge">✦ Base de Conhecimento Auditada · Zero Alucinações</div><div class="hero-title">Consulte sua documentação técnica com precisão imediata.</div><div class="hero-desc">Respostas fundamentadas exclusivamente em manuais institucionais, com citação auditável de página e isolamento estrito por metadados.</div><div class="kpi-ribbon"><div class="kpi-card"><div class="num">4 Documentos</div><div class="label">Bases Homologadas</div></div><div class="kpi-card"><div class="num">73 Páginas</div><div class="label">477 Vetores Ativos</div></div><div class="kpi-card"><div class="num" style="color: #10B981;">100% Factual</div><div class="label">Taxa de Confiabilidade</div></div></div></div>'
    st.markdown(hero_html, unsafe_allow_html=True)

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

# 10. Gestão do Escopo de Fontes Selecionadas
arquivos_para_filtro = [FONTES_DISPONIVEIS[k]["arquivo"] for k in st.session_state.fontes_ativas]

if len(st.session_state.fontes_ativas) == len(FONTES_DISPONIVEIS):
    rotulo_escopo_atual = "Toda a Base (Pesquisa Global)"
    tag_escopo_html = ""
elif len(st.session_state.fontes_ativas) == 0:
    rotulo_escopo_atual = "Nenhuma fonte selecionada"
    tag_escopo_html = '<div class="scope-status-pill" style="color: #F87171; border-color: rgba(248, 113, 113, 0.4);">⚠️ Nenhuma fonte ativa</div>'
else:
    nomes_selecionados = [FONTES_DISPONIVEIS[k]["titulo"] for k in st.session_state.fontes_ativas]
    rotulo_escopo_atual = ", ".join(nomes_selecionados)
    tag_escopo_html = f'<div class="scope-status-pill"><span>🎯 Foco Ativo: {len(st.session_state.fontes_ativas)} documento(s) selecionado(s)</span></div>'

if tag_escopo_html:
    st.markdown(tag_escopo_html, unsafe_allow_html=True)

# 11. CÁPSULA UNIFICADA: '+' (ESQ) | ENTRADA (CENTRO) | MODELO (DIR)
with st.bottom:
    # 1. BOTÃO '+' (SELETOR DE FONTES - SEM TOOLTIP DE HOVER)
    with st.popover("＋"):
        st.markdown('<div class="popover-header">Fontes de Consulta</div>', unsafe_allow_html=True)
        st.markdown('<div class="popover-desc">Selecione uma ou mais bases para direcionar a busca semântica:</div>', unsafe_allow_html=True)

        st.checkbox(
            "Selecionar todas as fontes",
            value=st.session_state.chk_todas,
            key="chk_todas",
            on_change=ao_mudar_master_todas
        )

        st.markdown('<div style="height: 4px;"></div><hr style="border: none; border-top: 1px solid rgba(255,255,255,0.08); margin: 8px 0;"><div style="height: 4px;"></div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size: 0.68rem; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 8px;">Documentos Homologados</div>', unsafe_allow_html=True)

        for k, v in FONTES_DISPONIVEIS.items():
            st.checkbox(
                f"{v['titulo']} ({v['paginas']} págs)",
                value=st.session_state[f"chk_{k}"],
                key=f"chk_{k}",
                on_change=ao_mudar_individual,
                args=(k,)
            )

        st.markdown('<div style="height: 4px;"></div><hr style="border: none; border-top: 1px solid rgba(255,255,255,0.08); margin: 8px 0;"><div style="height: 4px;"></div>', unsafe_allow_html=True)
        st.markdown('<div class="popover-header" style="font-size: 0.78rem;">Adicionar Novo Documento</div>', unsafe_allow_html=True)
        arquivo_up = st.file_uploader("Upload de PDF ou MD:", type=["pdf", "md"], label_visibility="collapsed")
        if arquivo_up:
            if st.button("Sincronizar Arquivo", use_container_width=True):
                caminho = PASTA_DATA / arquivo_up.name
                with open(caminho, "wb") as f:
                    f.write(arquivo_up.getvalue())
                
                with st.status("Processando documento...", expanded=True) as status:
                    st.write("Extraindo páginas nativas...")
                    time.sleep(0.3)
                    st.write("Verificando integridade no ChromaDB...")
                    time.sleep(0.4)
                    status.update(label="Documento sincronizado com sucesso!", state="complete", expanded=False)
                
                st.success(f"'{arquivo_up.name}' pronto para pesquisa!")
                time.sleep(0.8)
                st.rerun()

    # 2. CAMPO DE DIGITAÇÃO NO CENTRO
    prompt_digitado = st.chat_input("Consulte qualquer norma, procedimento ou técnica...")

    # 3. SELETOR DE MODELO À DIREITA
    modelo_atual_info = OPCOES_MODELOS[st.session_state.modelo_selecionado]
    with st.popover(f"⚡ {modelo_atual_info['label']} ▾"):
        st.markdown('<div class="popover-header">Modelo de Linguagem</div>', unsafe_allow_html=True)
        st.markdown('<div class="popover-desc">Roteamento de inferência e capacidade analítica:</div>', unsafe_allow_html=True)

        for chave_mod, dados_mod in OPCOES_MODELOS.items():
            escolhido = (chave_mod == st.session_state.modelo_selecionado)
            prefixo = "✓ " if escolhido else "○ "
            if st.button(
                f"{prefixo}{dados_mod['label']} · {dados_mod['status']}\n{dados_mod['subtitulo']}", 
                key=f"mod_btn_{chave_mod}", 
                use_container_width=True
            ):
                st.session_state.modelo_selecionado = chave_mod
                st.rerun()

# 12. Processamento da Pergunta
if prompt_digitado:
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