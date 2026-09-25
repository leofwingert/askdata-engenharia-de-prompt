import os
import sys
import time
import json
import streamlit as st
from collections import defaultdict

try:
    from rag_engine import RAGEngine
except ImportError:
    from src.rag_engine import RAGEngine

# 1. Configuração da Página e Identidade Visual
st.set_page_config(
    page_title="AskData | Enterprise Knowledge Hub",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS personalizada (Tema Dark Enterprise Minimalista)
st.markdown("""
<style>
    /* Tipografia e espaçamentos gerais */
    .block-container { padding-top: 2rem; padding-bottom: 3rem; }
    
    /* Pílula de Telemetria e FinOps */
    .finops-badge {
        display: inline-flex;
        align-items: center;
        gap: 12px;
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 6px 14px;
        font-size: 0.82rem;
        color: #94a3b8;
        margin-top: 8px;
        margin-bottom: 8px;
    }
    .finops-badge strong { color: #f8fafc; }
    .finops-highlight { color: #38bdf8; font-weight: 600; }
    
    /* Card de Confiança Semântica */
    .confidence-tag {
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.78rem;
        text-transform: uppercase;
    }
    .conf-alta { background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.4); }
    .conf-media { background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.4); }
    .conf-baixa { background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.4); }
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

# 4. Barra Lateral (Sidebar)
with st.sidebar:
    st.title("⚡ Painel de Controle")
    st.caption("AskData Enterprise • DataLakers & Navi Hub")
    st.markdown("---")

    st.subheader("Profundidade de Busca (Top-K)")
    top_k = st.slider(
        label="Chunks recuperados por consulta:",
        min_value=2,
        max_value=6,
        value=4,
        help="Quantidade de fragmentos semânticos resgatados do ChromaDB via similaridade de cosseno."
    )

    st.markdown("---")
    st.subheader("💡 Casos Rápidos para o Pitch")
    perguntas_demo = [
        "O que significa a matriz PACIF e suas 5 letras?",
        "Quais módulos compõem o ecossistema ANIA.core do TCESP?",
        "O que é a técnica Chain of Verification (CoVe)?",
        "Qual foi a escalação do Brasil na Copa de 2002?"
    ]

    for p in perguntas_demo:
        if st.button(p, key=f"btn_{p}", use_container_width=True):
            pergunta_para_processar = p

    st.markdown("---")
    col_limpar, col_exportar = st.columns(2)
    with col_limpar:
        if st.button("🧹 Limpar Chat", use_container_width=True):
            st.session_state.mensagens = [st.session_state.mensagens[0]]
            st.rerun()

    if len(st.session_state.mensagens) > 1:
        dados_json = json.dumps(st.session_state.mensagens, indent=2, ensure_ascii=False)
        st.download_button(
            label="📥 Baixar JSON",
            data=dados_json,
            file_name="historico_askdata.json",
            mime="application/json",
            use_container_width=True
        )

    st.markdown("---")
    st.caption("🔒 **Guardrails Operacionais:** Grounding Estrito • Citações por Página • FinOps Telemetry")

# 5. Navegação em Abas (Clean & Estruturada)
aba_chat, aba_auditoria = st.tabs(["💬 Chat Corporativo com IA", "📊 Auditoria da Base Vetorial (ChromaDB)"])

# ==============================================================================
# ABA 1: CHAT CORPORATIVO & TELEMETRIA
# ==============================================================================
with aba_chat:
    st.title("AskData: Assistente de Documentação Técnica")
    st.caption("Respostas sintetizadas a partir de base vetorial local com citações auditáveis e métricas FinOps.")

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
    st.title("Auditoria Interna da Base Vetorial (ChromaDB)")
    st.caption("Visão técnica de volumetria, metadados persistidos e simulação de busca por cosseno.")

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