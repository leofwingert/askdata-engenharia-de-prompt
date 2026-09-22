import os
import glob
import time
import re
from pathlib import Path
from pypdf import PdfReader
import chromadb
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY não encontrada no arquivo .env!")

client = genai.Client(api_key=api_key)

# Modelo gratuito de embeddings do Google AI Studio
EMBEDDING_MODEL = "gemini-embedding-001"

def extrair_texto_pdf(caminho_pdf: str) -> list[dict]:
    """Le um arquivo PDF e extrai o texto pagina a pagina com metadados."""
    reader = PdfReader(caminho_pdf)
    paginas = []
    nome_arquivo = Path(caminho_pdf).name
    
    for idx, pagina in enumerate(reader.pages):
        texto = pagina.extract_text() or ""
        if texto.strip():
            paginas.append({
                "texto": texto.strip(),
                "arquivo": nome_arquivo,
                "pagina": idx + 1
            })
    return paginas

def extrair_texto_markdown(caminho_md: str) -> list[dict]:
    """Le um arquivo Markdown e extrai o texto com metadados."""
    nome_arquivo = Path(caminho_md).name
    with open(caminho_md, "r", encoding="utf-8") as f:
        texto = f.read().strip()
    
    if texto:
        return [{
            "texto": texto,
            "arquivo": nome_arquivo,
            "pagina": 1
        }]
    return []

def criar_chunks(documentos_paginas: list[dict], chunk_size: int = 1000, chunk_overlap: int = 200) -> list[dict]:
    """Divide os textos em blocos, priorizando o fim de frases."""
    chunks = []

    for item in documentos_paginas:
        texto = item["texto"]
        frases = [parte.strip() for parte in re.split(r"(?<=[.!?])\s+", texto) if parte.strip()]
        inicio_frase = 0
        chunk_idx = 1

        while inicio_frase < len(frases):
            fim_frase = inicio_frase
            tamanho = 0
            while fim_frase < len(frases):
                tamanho_adicional = len(frases[fim_frase]) + (1 if fim_frase > inicio_frase else 0)
                if fim_frase > inicio_frase and tamanho + tamanho_adicional > chunk_size:
                    break
                tamanho += tamanho_adicional
                fim_frase += 1

            trecho = " ".join(frases[inicio_frase:fim_frase])
            
            chunk_id = f"{item['arquivo']}_p{item['pagina']}_c{chunk_idx}"
            chunks.append({
                "id": chunk_id,
                "texto": trecho,
                "arquivo": item["arquivo"],
                "pagina": item["pagina"],
                "chunk_idx": chunk_idx
            })

            proxima_frase = fim_frase
            tamanho_overlap = 0
            while proxima_frase > inicio_frase and tamanho_overlap < chunk_overlap:
                proxima_frase -= 1
                tamanho_overlap += len(frases[proxima_frase]) + 1

            inicio_frase = proxima_frase if proxima_frase > inicio_frase else fim_frase
            chunk_idx += 1

    return chunks

def indexar_no_chromadb(chunks: list[dict], path_db: str = "./chroma_db", collection_name: str = "askdata_knowledge"):
    """Gera embeddings e salva os chunks no ChromaDB com controle de fluxo para evitar erro 429."""
    chroma_client = chromadb.PersistentClient(path=path_db)
    collection = chroma_client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )
    
    # 1. Recupera os IDs ja persistidos no banco local
    dados_banco = collection.get()
    ids_existentes = set(dados_banco["ids"]) if dados_banco and "ids" in dados_banco else set()
    
    print(f"Total de chunks a processar: {len(chunks)}")
    print(f"Chunks ja salvos no ChromaDB: {len(ids_existentes)}")
    
    for i, ch in enumerate(chunks, 1):
        # Pula itens ja indexados na execucao anterior para poupar cota
        if ch["id"] in ids_existentes:
            continue
            
        tentativas = 3
        while tentativas > 0:
            try:
                res = client.models.embed_content(
                    model=EMBEDDING_MODEL,
                    contents=ch["texto"]
                )
                vetor = res.embeddings[0].values
                
                collection.upsert(
                    ids=[ch["id"]],
                    embeddings=[vetor],
                    documents=[ch["texto"]],
                    metadatas={
                        "arquivo": ch["arquivo"],
                        "pagina": ch["pagina"],
                        "chunk_idx": ch["chunk_idx"]
                    }
                )
                
                # Pausa de 0.7s por chunk: mantem ~85 req/min (abaixo do teto gratuito de 100/min)
                time.sleep(0.2)
                break
                
            except Exception as e:
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    print(f"\n[Aviso Cota] Teto atingido no chunk {i}. Aguardando 35 segundos para liberar...")
                    time.sleep(35)
                    tentativas -= 1
                else:
                    print(f"\n[Erro fatal no chunk {ch['id']}]: {e}")
                    raise e

        if i % 5 == 0 or i == len(chunks):
            print(f"  -> Progresso: {i}/{len(chunks)} chunks analisados (Total salvo: {collection.count()})...")
            
    print(f"\nIngestao concluida com sucesso! Total definitivo no ChromaDB: {collection.count()} chunks.")

if __name__ == "__main__":
    pasta_dados = "./data"
    todos_documentos = []
    
    # 1. Carregar PDFs da pasta data
    for pdf_path in glob.glob(f"{pasta_dados}/*.pdf"):
        print(f"Processando PDF: {pdf_path}")
        todos_documentos.extend(extrair_texto_pdf(pdf_path))
        
    # 2. Carregar Markdowns da pasta data
    for md_path in glob.glob(f"{pasta_dados}/*.md"):
        print(f"Processando Markdown: {md_path}")
        todos_documentos.extend(extrair_texto_markdown(md_path))
        
    if not todos_documentos:
        print("Nenhum arquivo PDF ou Markdown encontrado em ./data! Adicione arquivos na pasta para testar.")
    else:
        # 3. Gerar Chunks
        lista_chunks = criar_chunks(todos_documentos, chunk_size=1000, chunk_overlap=200)
        # 4. Indexar no ChromaDB
        indexar_no_chromadb(lista_chunks)