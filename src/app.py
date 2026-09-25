import os
import sys
import time
import json
from pathlib import Path
import streamlit as st
from collections import defaultdict
from pypdf import PdfReader

try:
    from rag_engine import RAGEngine
except ImportError:
    from src.rag_engine import RAGEngine

# 1. Configuração da Página e Identidade Visual
st.set_page_config(
    page_title="AskData | Enterprise Knowledge Hub",
    page_icon="A",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização da casca do produto: clara, silenciosa e orientada a leitura.
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

    :root {
        color-scheme: dark;
        --canvas: #121416;
        --sidebar: #0d0f11;
        --surface: #1b1f22;
        --surface-soft: #202529;
        --ink: #f2f4f1;
        --muted: #a2aaa6;
        --line: #30373a;
        --accent: #69c39a;
        --accent-soft: #1c3b2d;
        --shadow: 0 14px 32px rgba(0, 0, 0, 0.24);
    }

    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; color: var(--ink); }
    .stApp { background: var(--canvas); }
    .stApp, .stApp p, .stApp label, .stApp span, .stApp li, .stApp [data-testid="stMarkdownContainer"] { color: var(--ink); }
    .block-container { max-width: 1120px; padding: 2.5rem 3rem 8rem; }
    [data-testid="stHeader"] { background: var(--canvas); }
    [data-testid="stSidebar"] { background: var(--sidebar); border-right: 1px solid var(--line); }
    [data-testid="stSidebar"] > div:first-child { padding: 1.5rem 1.1rem 1rem; }
    [data-testid="stSidebar"] .block-container { padding: 0; }
    h1, h2, h3 { font-family: 'Space Grotesk', sans-serif; letter-spacing: 0; color: var(--ink); }
    h1 { font-size: 2rem; line-height: 1.1; }
    h2 { font-size: 1.35rem; }
    h3 { font-size: 1rem; }
    .eyebrow { color: var(--accent) !important; font-size: .72rem; font-weight: 700; letter-spacing: .13em; text-transform: uppercase; }
    .workspace-header { padding: .2rem 0 1.6rem; }
    .workspace-header h1 { margin: .45rem 0 .5rem; }
    .workspace-header p { color: var(--muted) !important; margin: 0; max-width: 650px; }
    .sidebar-brand { display: flex; align-items: center; gap: .7rem; margin-bottom: 1.6rem; }
    .brand-mark { display: grid; place-items: center; width: 34px; height: 34px; border-radius: 10px; background: var(--accent); color: white; font: 700 1.1rem 'Space Grotesk'; }
    .brand-name { font: 700 1.05rem 'Space Grotesk'; }
    .sidebar-label { color: var(--muted); font-size: .68rem; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; margin: 1.25rem 0 .5rem; }
    .sidebar-note { background: var(--surface); border: 1px solid var(--line); border-radius: 12px; padding: .75rem .8rem; color: var(--muted) !important; font-size: .78rem; line-height: 1.45; }
    .sidebar-note strong { color: var(--ink); }
    .profile { display: flex; align-items: center; gap: .65rem; border-top: 1px solid var(--line); padding-top: 1rem; margin-top: 1.5rem; }
    .profile-avatar { display: grid; place-items: center; width: 30px; height: 30px; border-radius: 50%; background: #d5e3da; color: var(--accent); font-weight: 700; font-size: .75rem; }
    .profile strong { display: block; font-size: .8rem; }
    .profile span, [data-testid="stSidebar"] .stCaption { color: var(--muted) !important; font-size: .7rem; }
    .stTabs [data-baseweb="tab-list"] { gap: .35rem; border-bottom: 1px solid var(--line); }
    .stTabs [data-baseweb="tab"] { height: 2.6rem; padding: 0 .9rem; color: var(--muted); font-weight: 600; }
    .stTabs [aria-selected="true"] { color: var(--accent) !important; }
    .stTabs [data-baseweb="tab-highlight"] { background: var(--accent); }
    [data-testid="stChatMessage"] { background: var(--surface); border: 1px solid var(--line); border-radius: 16px; box-shadow: var(--shadow); padding: 1.25rem 1.35rem; margin: 1rem 0; }
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] { line-height: 1.65; }
    [data-testid="stChatMessage"] [data-testid="stChatMessageAvatarUser"] { background: var(--accent-soft); color: var(--accent); }
    [data-testid="stChatMessage"] [data-testid="stChatMessageAvatarAssistant"] { background: var(--accent); color: #fff; }
    [data-testid="stChatInput"] { background: var(--surface); border-color: var(--line); box-shadow: 0 12px 34px rgba(0,0,0,.28); }
    [data-testid="stChatInput"] textarea { background: var(--surface); color: var(--ink); caret-color: var(--accent); }
    [data-testid="stChatInput"] textarea::placeholder { color: #89928d; opacity: 1; }
    [data-testid="stChatInput"] button { background: var(--surface-soft); color: var(--accent); }
    [data-testid="stSidebar"] button { background: var(--surface); color: var(--ink); border: 1px solid var(--line); }
    [data-testid="stSidebar"] button:hover { border-color: var(--accent); color: var(--accent); }
    [data-testid="stSlider"] [role="slider"] { background: var(--accent); }
    [data-testid="stExpander"] { background: var(--surface-soft); border: 1px solid var(--line); }
    [data-testid="stExpander"] summary { color: var(--ink); }
    [data-testid="stTextInput"] input, [data-testid="stNumberInput"] input { background: var(--surface); color: var(--ink); border-color: var(--line); }
    [data-testid="stTextInput"] input::placeholder { color: #89928d; }
    [data-testid="stAlert"] { background: var(--surface-soft); color: var(--ink); border-color: var(--line); }
    .metric-card { background: var(--surface); border: 1px solid var(--line); border-radius: 14px; padding: .2rem .9rem; box-shadow: var(--shadow); }
    .audit-island { background: var(--surface); border: 1px solid var(--line); border-radius: 16px; padding: 1rem 1.2rem; box-shadow: var(--shadow); margin: 1rem 0; }
    .file-card { background: var(--surface); border: 1px solid var(--line); border-radius: 14px; padding: 1rem 1.1rem; margin: .65rem 0; box-shadow: var(--shadow); }
    .file-name { color: var(--ink); font-weight: 600; word-break: break-word; }
    .file-meta { color: var(--muted); font-size: .78rem; margin-top: .2rem; }
    .file-viewer { background: #15191b; border: 1px solid var(--line); border-radius: 12px; padding: 1rem; }

    .finops-badge {
        display: inline-flex;
        align-items: center;
        gap: 12px;
        flex-wrap: wrap;
        background: #1d3027;
        border: 1px solid #315a46;
        border-radius: 10px;
        padding: 6px 14px;
        font-size: 0.82rem;
        color: var(--muted);
        margin-top: 8px;
        margin-bottom: 8px;
    }
    .finops-badge strong { color: var(--ink); }
    .finops-highlight { color: var(--accent); font-weight: 700; }
    .confidence-tag {
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.78rem;
        text-transform: uppercase;
    }
    .conf-alta { background: #1d3b2b; color: #8de0ae; border: 1px solid #32704b; }
    .conf-media { background: #41351a; color: #f0cc70; border: 1px solid #806623; }
    .conf-baixa { background: #422321; color: #f09b91; border: 1px solid #86423b; }
    @media (max-width: 700px) {
        .block-container { padding: 1.5rem 1rem 7rem; }
        h1 { font-size: 1.55rem; }
        .finops-badge { gap: 7px; font-size: .72rem; }
    }
</style>
""", unsafe_allow_html=True)

# 2. Inicialização do Motor RAG com Cache Persistente
@st.cache_resource(show_spinner=False)
def carregar_motor_rag():
    return RAGEngine()

try:
    engine = carregar_motor_rag()
except Exception as erro:
    st.error(f"Erro fatal ao carregar o motor RAG: {erro}")
    st.info("Verifique se o arquivo .env contém a GEMINI_API_KEY e se a pasta chroma_db/ existe.")
    st.stop()

# 3. Estado da Sessão
if "mensagens" not in st.session_state:
    st.session_state.mensagens = [
        {
            "role": "assistant",
            "content": "Olá! Sou o **AskData**, assistente corporativo de documentação técnica. Consulte diretrizes, manuais e conceitos de Engenharia de Prompt com respaldo factual auditável.",
            "fontes": [],
            "latencia": 0.0,
            "tokens_in": 0,
            "tokens_out": 0,
            "custo_usd": 0.0,
            "confianca": "ALTA",
            "score_max": 1.0,
            "feedback": None
        }
    ]

pergunta_para_processar = None

def renderizar_badge_confianca(nivel: str) -> str:
    classe = "conf-alta" if nivel == "ALTA" else ("conf-media" if nivel == "MEDIA" else "conf-baixa")
    rotulo = "🟢 Alta Confiança" if nivel == "ALTA" else ("🟡 Relevância Moderada" if nivel == "MEDIA" else "🔴 Baixa Confiança")
    return f'<span class="confidence-tag {classe}">{rotulo}</span>'


PASTA_DATA = Path("data")
EXTENSOES_PERMITIDAS = {".pdf", ".md"}
PASTA_DATA.mkdir(exist_ok=True)


def listar_arquivos_data() -> list[Path]:
    """Lista somente documentos suportados diretamente dentro de data/."""
    return sorted(
        (arquivo for arquivo in PASTA_DATA.iterdir() if arquivo.is_file() and arquivo.suffix.lower() in EXTENSOES_PERMITIDAS),
        key=lambda arquivo: arquivo.name.lower()
    )


def extrair_visualizacao_pdf(caminho: Path) -> str:
    """Extrai texto para uma prévia rápida sem alterar o arquivo original."""
    paginas = PdfReader(str(caminho)).pages
    trechos = []
    for numero, pagina in enumerate(paginas, 1):
        texto = (pagina.extract_text() or "").strip()
        if texto:
            trechos.append(f"### Página {numero}\n\n{texto}")
    return "\n\n".join(trechos)

# 4. Barra Lateral (navegação, atalhos e perfil)
with st.sidebar:
    st.markdown('<div class="sidebar-brand"><div class="brand-mark">A</div><div class="brand-name">AskData</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-label">Workspace</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-note">Base local de conhecimento<br><strong>Engenharia de Prompt</strong></div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-label">Atalhos</div>', unsafe_allow_html=True)
    st.caption("⌘  Nova conversa")
    st.caption("⌕  Explorar base vetorial")
    st.caption("↗  Exportar histórico")

    st.markdown('<div class="sidebar-label">Histórico recente</div>', unsafe_allow_html=True)
    perguntas_recentes = [
        mensagem["content"] for mensagem in st.session_state.mensagens
        if mensagem["role"] == "user"
    ][-3:]
    if perguntas_recentes:
        for pergunta in reversed(perguntas_recentes):
            st.caption(f"{pergunta[:48]}{'...' if len(pergunta) > 48 else ''}")
    else:
        st.caption("Nenhuma conversa nesta sessão")

    st.markdown('<div class="sidebar-label">Profundidade de busca</div>', unsafe_allow_html=True)
    top_k = st.slider(
        label="Chunks por consulta",
        min_value=2,
        max_value=6,
        value=4,
        help="Quantidade de fragmentos semânticos resgatados do ChromaDB via similaridade de cosseno."
    )

    st.markdown('<div class="sidebar-label">Perguntas rápidas</div>', unsafe_allow_html=True)
    perguntas_demo = [
        "O que significa a matriz PACIF e suas 5 letras?",
        "Quais módulos compõem o ecossistema ANIA.core do TCESP?",
        "O que é a técnica Chain of Verification (CoVe)?",
        "Qual foi a escalação do Brasil na Copa de 2002?"
    ]

    for p in perguntas_demo:
        if st.button(p, key=f"btn_{p}", use_container_width=True):
            pergunta_para_processar = p

    st.markdown('<div class="sidebar-label">Sessão</div>', unsafe_allow_html=True)
    if st.button("Limpar conversa", use_container_width=True):
        st.session_state.mensagens = [st.session_state.mensagens[0]]
        st.rerun()

    if len(st.session_state.mensagens) > 1:
        dados_json = json.dumps(st.session_state.mensagens, indent=2, ensure_ascii=False)
        st.download_button(
            label="Baixar histórico",
            data=dados_json,
            file_name="historico_askdata.json",
            mime="application/json",
            use_container_width=True
        )

    st.markdown('<div class="profile"><div class="profile-avatar">LM</div><div><strong>Leonardo & Marcos</strong><span>Workspace privado</span></div></div>', unsafe_allow_html=True)

# 5. Navegação em Abas (Clean & Estruturada)
aba_chat, aba_auditoria, aba_arquivos = st.tabs([
    "💬 Chat Corporativo com IA",
    "📊 Auditoria da Base Vetorial (ChromaDB)",
    "🗂️ Arquivos"
])

# ==============================================================================
# ABA 1: CHAT CORPORATIVO & TELEMETRIA
# ==============================================================================
with aba_chat:
    st.markdown('<div class="workspace-header"><div class="eyebrow">Knowledge workspace</div><h1>Assistente de documentação técnica</h1><p>Consulte a base de Engenharia de Prompt com respostas fundamentadas, fontes rastreáveis e métricas de uso.</p></div>', unsafe_allow_html=True)

    # Renderização do histórico persistente
    for idx_msg, msg in enumerate(st.session_state.mensagens):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
            # Linha de Telemetria FinOps (Apenas para respostas do assistente com latência > 0)
            if msg.get("latencia", 0.0) > 0:
                conf_badge = renderizar_badge_confianca(msg.get("confianca", "MEDIA"))
                st.markdown(f"""
                <div class="finops-badge">
                    {conf_badge}
                    <span>⏱️ Latência: <strong>{msg['latencia']:.2f}s</strong></span>
                    <span>🔢 Tokens: <strong>{msg.get('tokens_in', 0)}</strong> in / <strong>{msg.get('tokens_out', 0)}</strong> out</span>
                    <span>💰 Custo Est.: <strong class="finops-highlight">${msg.get('custo_usd', 0.0):.6f} USD</strong></span>
                </div>
                """, unsafe_allow_html=True)

            # Painel Retrátil de Explicabilidade
            if msg.get("fontes"):
                with st.expander("📚 Inspecionar Chunks Resgatados & Similaridade de Cosseno"):
                    for idx_fonte, fonte in enumerate(msg["fontes"], 1):
                        col_doc, col_score = st.columns([3, 1])
                        with col_doc:
                            st.markdown(f"**Fonte [{idx_fonte}]:** `{fonte['arquivo']}` — **Página {fonte['pagina']}**")
                        with col_score:
                            st.markdown(f"**Similaridade:** `{fonte['similaridade']:.2%}`")
                        st.info(fonte["texto"])

    # Captura de input manual via teclado
    if prompt_digitado := st.chat_input("Digite sua dúvida técnica sobre os documentos..."):
        pergunta_para_processar = prompt_digitado

    # Processamento Unificado (Gatilho por Teclado ou Botão)
    if pergunta_para_processar:
        # 1. Registra pergunta do usuário
        st.session_state.mensagens.append({
            "role": "user",
            "content": pergunta_para_processar,
            "fontes": [],
            "latencia": 0.0,
            "tokens_in": 0,
            "tokens_out": 0,
            "custo_usd": 0.0,
            "confianca": "ALTA",
            "score_max": 0.0,
            "feedback": None
        })
        with st.chat_message("user"):
            st.markdown(pergunta_para_processar)

        # 2. Execução RAG
        with st.chat_message("assistant"):
            with st.spinner("Consultando vetores e checando evidências..."):
                resultado = engine.responder_pergunta(pergunta_para_processar, top_k=top_k)
                resposta = resultado["resposta"]
                fontes = resultado["fontes"]
                latencia = resultado["latencia"]
                tokens_in = resultado["tokens_in"]
                tokens_out = resultado["tokens_out"]
                custo = resultado["custo_usd"]
                confianca = resultado["confianca"]
                score_max = resultado["score_max"]

                # Streaming visual de resposta
                area_texto = st.empty()
                texto_acumulado = ""
                for char in resposta:
                    texto_acumulado += char
                    area_texto.markdown(texto_acumulado + "▌")
                    time.sleep(0.003)
                area_texto.markdown(resposta)

                # Telemetria imediata
                conf_badge = renderizar_badge_confianca(confianca)
                st.markdown(f"""
                <div class="finops-badge">
                    {conf_badge}
                    <span>⏱️ Latência: <strong>{latencia:.2f}s</strong></span>
                    <span>🔢 Tokens: <strong>{tokens_in}</strong> in / <strong>{tokens_out}</strong> out</span>
                    <span>💰 Custo Est.: <strong class="finops-highlight">${custo:.6f} USD</strong></span>
                </div>
                """, unsafe_allow_html=True)

                if fontes:
                    with st.expander("📚 Inspecionar Chunks Resgatados & Similaridade de Cosseno"):
                        for idx_fonte, fonte in enumerate(fontes, 1):
                            col_doc, col_score = st.columns([3, 1])
                            with col_doc:
                                st.markdown(f"**Fonte [{idx_fonte}]:** `{fonte['arquivo']}` — **Página {fonte['pagina']}**")
                            with col_score:
                                st.markdown(f"**Similaridade:** `{fonte['similaridade']:.2%}`")
                            st.info(fonte["texto"])

                # 3. Salva no histórico da sessão
                st.session_state.mensagens.append({
                    "role": "assistant",
                    "content": resposta,
                    "fontes": fontes,
                    "latencia": latencia,
                    "tokens_in": tokens_in,
                    "tokens_out": tokens_out,
                    "custo_usd": custo,
                    "confianca": confianca,
                    "score_max": score_max,
                    "feedback": None
                })
                st.rerun()

# ==============================================================================
# ABA 2: EXPLORADOR DA BASE VETORIAL (CHROMADB)
# ==============================================================================
with aba_auditoria:
    st.markdown('<div class="workspace-header"><div class="eyebrow">Observability</div><h1>Auditoria da base vetorial</h1><p>Volumetria, metadados persistidos e simulação de busca semântica no ChromaDB.</p></div>', unsafe_allow_html=True)

    try:
        dados_col = engine.collection.get(include=["metadatas", "documents"])
        total_chunks = len(dados_col["ids"])

        # Cards com Métricas Globais
        m1, m2, m3 = st.columns(3)
        m1.metric("Total de Chunks Indexados", total_chunks)
        
        chunks_por_arquivo = defaultdict(int)
        for meta in dados_col["metadatas"]:
            arq = meta.get("arquivo", "Documento")
            chunks_por_arquivo[arq] += 1
            
        m2.metric("Documentos Mapeados", len(chunks_por_arquivo))
        tamanho_medio = sum(len(d) for d in dados_col["documents"]) / total_chunks if total_chunks else 0
        m3.metric("Tamanho Médio dos Chunks", f"{tamanho_medio:.0f} chars")

        st.markdown("---")
        st.subheader("Distribuição de Chunks por Arquivo")
        st.bar_chart(chunks_por_arquivo)

        st.markdown("---")
        st.subheader("🔍 Simulador de Busca Semântica Pura (Sem LLM)")
        st.caption("Recupera os blocos de texto diretamente do espaço de cosseno do ChromaDB sem gerar custos de API.")
        
        termo_pesquisa = st.text_input("Digite um termo para pesquisar nos vetores:", placeholder="ex: PACIF, ANIA, Chain of Thought...")
        top_k_sim = st.slider("Quantidade de resultados (Simulador):", 1, 6, 3, key="slider_sim")

        if termo_pesquisa:
            trechos_brutos = engine.recuperar_contexto(termo_pesquisa, top_k=top_k_sim)
            if trechos_brutos:
                for idx, ch in enumerate(trechos_brutos, 1):
                    st.markdown(f"**Resultado [{idx}]:** `{ch['arquivo']}` (Página {ch['pagina']}) — **Similaridade:** `{ch['similaridade']:.2%}`")
                    st.code(ch['texto'], language="text")
            else:
                st.warning("Nenhum trecho correspondente encontrado no banco vetorial.")

    except Exception as e:
        st.error(f"Erro ao auditar a coleção do ChromaDB: {e}")

# ==============================================================================
# ABA 3: GERENCIADOR DE ARQUIVOS DA BASE
# ==============================================================================
with aba_arquivos:
    st.markdown('<div class="workspace-header"><div class="eyebrow">Knowledge sources</div><h1>Arquivos da base</h1><p>Adicione, consulte ou remova os documentos disponíveis na pasta data/.</p></div>', unsafe_allow_html=True)

    st.info("Formatos aceitos: PDF e Markdown. Depois de adicionar ou remover arquivos, execute a ingestão para atualizar os embeddings da base vetorial.")

    arquivos_enviados = st.file_uploader(
        "Adicionar documentos",
        type=["pdf", "md"],
        accept_multiple_files=True,
        help="Os arquivos serão salvos diretamente em data/."
    )
    if arquivos_enviados:
        arquivos_salvos = []
        for arquivo_enviado in arquivos_enviados:
            nome_seguro = Path(arquivo_enviado.name).name
            extensao = Path(nome_seguro).suffix.lower()
            if not nome_seguro or extensao not in EXTENSOES_PERMITIDAS:
                continue
            destino = PASTA_DATA / nome_seguro
            destino.write_bytes(arquivo_enviado.getvalue())
            arquivos_salvos.append(nome_seguro)
        if arquivos_salvos:
            st.success(f"{len(arquivos_salvos)} arquivo(s) salvo(s) em data/.")
            st.rerun()

    arquivos_data = listar_arquivos_data()
    st.markdown(f"### Documentos disponíveis · {len(arquivos_data)}")
    if not arquivos_data:
        st.warning("A pasta data/ ainda não possui arquivos PDF ou Markdown.")
    else:
        nomes_arquivos = [arquivo.name for arquivo in arquivos_data]
        arquivo_selecionado = st.selectbox("Visualizar arquivo", nomes_arquivos)
        caminho_selecionado = PASTA_DATA / arquivo_selecionado

        for arquivo in arquivos_data:
            coluna_info, coluna_acao = st.columns([5, 1])
            with coluna_info:
                tamanho_kb = arquivo.stat().st_size / 1024
                st.markdown(
                    f'<div class="file-card"><div class="file-name">{arquivo.name}</div>'
                    f'<div class="file-meta">{arquivo.suffix.upper()[1:]} · {tamanho_kb:.1f} KB</div></div>',
                    unsafe_allow_html=True
                )
            with coluna_acao:
                st.write("")
                if st.button("Remover", key=f"remover_{arquivo.name}", use_container_width=True):
                    arquivo.unlink()
                    st.rerun()

        st.markdown(f"#### Visualização · {arquivo_selecionado}")
        try:
            if caminho_selecionado.suffix.lower() == ".md":
                conteudo = caminho_selecionado.read_text(encoding="utf-8")
                st.markdown(conteudo or "_Arquivo vazio._")
            else:
                conteudo_pdf = extrair_visualizacao_pdf(caminho_selecionado)
                if conteudo_pdf:
                    st.markdown(conteudo_pdf)
                else:
                    st.caption("Não foi possível extrair texto deste PDF. Use o botão abaixo para baixar o arquivo original.")
            st.download_button(
                "Baixar arquivo original",
                data=caminho_selecionado.read_bytes(),
                file_name=caminho_selecionado.name,
                mime="application/pdf" if caminho_selecionado.suffix.lower() == ".pdf" else "text/markdown",
                key=f"baixar_{caminho_selecionado.name}"
            )
        except Exception as erro:
            st.error(f"Não foi possível visualizar este arquivo: {erro}")