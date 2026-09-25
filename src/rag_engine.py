import os
from typing import List, Dict, Any
import chromadb
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY não encontrada no arquivo .env!")

EMBEDDING_MODEL = "gemini-embedding-001"
MODELO_GERACAO = "gemini-3.5-flash-lite"

class RAGEngine:
    def __init__(self, path_db: str = "./chroma_db", collection_name: str = "askdata_knowledge"):
        """Inicializa a conexão local persistente com o ChromaDB e o cliente Gemini."""
        self.client = genai.Client(api_key=api_key)
        self.chroma_client = chromadb.PersistentClient(path=path_db)
        self.collection = self.chroma_client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def _gerar_embedding(self, texto: str) -> List[float]:
        """Gera o embedding numérico da pergunta do usuário."""
        res = self.client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=texto
        )
        return res.embeddings[0].values

    def recuperar_contexto(self, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
        """Recupera os top_k trechos mais próximos via similaridade de cosseno."""
        vetor_query = self._gerar_embedding(query)
        
        resultados = self.collection.query(
            query_embeddings=[vetor_query],
            n_results=top_k
        )
        
        chunks_recuperados = []
        if resultados and resultados.get("documents") and resultados["documents"][0]:
            for doc, meta, dist in zip(
                resultados["documents"][0],
                resultados["metadatas"][0],
                resultados["distances"][0]
            ):
                chunks_recuperados.append({
                    "texto": doc,
                    "arquivo": meta.get("arquivo", "documento_desconhecido"),
                    "pagina": meta.get("pagina", 1),
                    "distancia": dist,
                    "similaridade": round(1.0 - dist, 4)
                })
        return chunks_recuperados

    def responder_pergunta(self, query: str, top_k: int = 4) -> Dict[str, Any]:
        """Executa o pipeline RAG: Recuperação -> Montagem de Contexto -> Síntese Blindada."""
        chunks = self.recuperar_contexto(query, top_k=top_k)
        
        if not chunks:
            return {
                "resposta": "Desculpe, não encontrei informações sobre isso nos documentos fornecidos.",
                "fontes": []
            }

        contexto_formatado = ""
        for idx, ch in enumerate(chunks, 1):
            contexto_formatado += f"\n--- [FONTE {idx} | Arquivo: {ch['arquivo']} | Página: {ch['pagina']}] ---\n"
            contexto_formatado += ch["texto"] + "\n"

        system_instruction = """
Você é o 'AskData', assistente de base de conhecimento da DataLakers.
Sua missão é responder à pergunta do usuário EXCLUSIVAMENTE com base nos trechos fornecidos em <contexto_recuperado>.

REGRAS OBRIGATÓRIAS DE OPERAÇÃO:
1. Responda apenas com fatos descritos no <contexto_recuperado>. Se a pergunta comparar conceitos e eles estiverem descritos nos trechos, você pode sintetizar e contrastar com base nas definições fornecidas.
2. Se o tema principal da pergunta NÃO constar nos trechos fornecidos, você DEVE responder exatamente a seguinte frase:
"Desculpe, não encontrei informações sobre isso nos documentos fornecidos."
3. NUNCA tente inventar, deduzir sem respaldo ou utilizar conhecimentos externos de pré-treino.
4. Para cada ponto abordado, cite explicitamente o nome do arquivo e a página de onde o fato foi extraído (ex: "[Manual_TCESP.pdf, p. 6]").
5. Responda de forma direta, técnica, profissional e em bom português.
"""

        prompt_final = f"""
<contexto_recuperado>
{contexto_formatado}
</contexto_recuperado>

<pergunta_do_usuario>
{query}
</pergunta_do_usuario>
"""

        response = self.client.models.generate_content(
            model=MODELO_GERACAO,
            contents=prompt_final,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.1
            )
        )

        return {
            "resposta": response.text.strip(),
            "fontes": chunks
        }