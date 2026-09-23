# AskData

Assistente de perguntas e respostas baseado em RAG, desenvolvido para o tema
**Engenharia de Prompt**.

## Integrantes

- Leonardo
- Marcos

## Domínio dos dados indexados

A base de conhecimento reúne documentos técnicos sobre engenharia de prompt,
incluindo:

- a matriz PACIF (Papel, Ação, Contexto, Intenção e Formato);
- o projeto ANIA.core e seus módulos do TCESP;
- técnicas como Chain of Thought e Few-Shot Prompting;
- elementos para estruturar prompts eficazes.

Os documentos são carregados da pasta `data/`, transformados em chunks e
indexados no ChromaDB com embeddings do modelo `gemini-embedding-001`.

## Execução rápida

Execute os comandos a partir da raiz do projeto.

### 1. Criar e ativar o ambiente virtual

```bash
python3 -m venv .venv
source .venv/bin/activate
```

No Windows, use:

```powershell
.venv\Scripts\activate
```

### 2. Instalar as dependências

```bash
pip install -r requirements.txt
```

Crie um arquivo `.env` na raiz do projeto e informe sua chave da API do
Gemini:

```env
GEMINI_API_KEY=sua_chave_aqui
```

### 3. Executar a ingestão

Coloque os arquivos PDF ou Markdown na pasta `data/` e execute:

```bash
python src/ingestion.py
```

Esse comando extrai o texto, cria os chunks e persiste os embeddings em
`chroma_db/`.

### 4. Iniciar a aplicação Streamlit

```bash
streamlit run src/app.py
```

Depois, abra no navegador o endereço local exibido pelo Streamlit.
