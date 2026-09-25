# 🤖 AskData Enterprise: Base de Conhecimento RAG Auditável

Assistente corporativo de alta fidelidade factual baseado em **Retrieval-Augmented Generation (RAG Local)** para consulta, análise e explicabilidade de documentações técnicas de Engenharia de Prompt e diretrizes institucionais do TCESP.

Projeto desenvolvido para a **Sprint 1** da parceria **DataLakers & Navi Hub (Tecnopuc)**.

---

## 👥 Equipe
* **Leonardo**
* **Marcos Vinícius**

---

## 🏗️ Arquitetura do Sistema

```mermaid
flowchart TD
    subgraph INGESTÃO [Pipeline Offline de Ingestão]
        A[PDFs Técnicos /data] --> B[pypdf: Extração por Página]
        B --> C[Regex Chunking: Sentenças e Tail-Merging]
        C --> D[gemini-embedding-001]
        D --> E[(ChromaDB: Espaço Cosseno)]
    end

    subgraph INFERÊNCIA [Motor Online de Recuperação e Síntese]
        F[Pergunta do Usuário] --> G[Embedding da Query]
        G --> H[Busca Top-K no ChromaDB]
        E -. Similaridade .-> H
        H --> I[Prompt Blindado + Contexto XML]
        I --> J[gemini-3.5-flash-lite: Temp 0.1]
        J --> K[Resposta com Citação de Página]
    end

    subgraph INTERFACE [Streamlit Enterprise Frontend]
        K --> L[Chat Reativo + Streaming]
        H --> M[Explicabilidade & Telemetria Vetorial]
        J --> N[Tracker FinOps: Tokens e Custo USD]
        E --> O[Dashboard de Auditoria da Base]
    end