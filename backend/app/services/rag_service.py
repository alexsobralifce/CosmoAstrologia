"""
Serviço RAG (Retrieval-Augmented Generation) para consulta de documentos astrológicos.
Processa PDFs e cria um banco vetorial para consultas semânticas.
"""

import os
import pickle
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
    import PyPDF2
    HAS_DEPENDENCIES = True
except ImportError:
    HAS_DEPENDENCIES = False

try:
    from groq import Groq
    HAS_GROQ = True
except ImportError:
    HAS_GROQ = False

from app.services.local_knowledge_base import LocalKnowledgeBase


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """
    Implementação própria de similaridade de cosseno para evitar dependências
    que exigem compilação em alguns ambientes (ex.: scikit-learn).
    """
    a_norm = a / (np.linalg.norm(a, axis=1, keepdims=True) + 1e-9)
    b_norm = b / (np.linalg.norm(b, axis=1, keepdims=True) + 1e-9)
    return np.dot(a_norm, b_norm.T)


class RAGService:
    """Serviço RAG para consulta de documentos astrológicos."""
    
    def __init__(self, docs_path: str = "docs", index_path: str = "rag_index.pkl", groq_api_key: Optional[str] = None):
        self.docs_path = Path(docs_path)
        self.index_path = Path(index_path)
        self.model = None
        self.documents = []  # Lista de textos extraídos
        self.embeddings = None  # Matriz de embeddings
        self.metadata = []  # Metadados dos documentos (título, página, etc.)
        self.groq_client = None
        
        if HAS_DEPENDENCIES:
            # Carregar modelo de embeddings (português)
            try:
                self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            except Exception as e:
                print(f"[WARNING] Erro ao carregar modelo de embeddings: {e}")
                print("Tentando modelo alternativo...")
                try:
                    self.model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
                except Exception as e2:
                    print(f"[ERROR] Não foi possível carregar modelo: {e2}")
                    self.model = None
        else:
            # Só avisar se tentar usar funcionalidades que requerem dependências
            pass
        
        # Inicializar cliente Groq se disponível
        if HAS_GROQ and groq_api_key:
            try:
                self.groq_client = Groq(api_key=groq_api_key)
            except Exception as e:
                print(f"[WARNING] Erro ao inicializar Groq: {e}")
                self.groq_client = None
        elif HAS_GROQ and not groq_api_key:
            # Só avisar se tentar usar Groq sem chave
            pass
    
    def extract_text_from_pdf(self, pdf_path: Path) -> List[Dict[str, any]]:
        """Extrai texto de um PDF e retorna lista de chunks com metadados."""
        chunks = []
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                
                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    
                    if text.strip():
                        # Dividir texto em chunks menores (aproximadamente 500 caracteres)
                        chunk_size = 500
                        chunk_overlap = 100
                        
                        for i in range(0, len(text), chunk_size - chunk_overlap):
                            chunk_text = text[i:i + chunk_size].strip()
                            if chunk_text:
                                chunks.append({
                                    'text': chunk_text,
                                    'source': pdf_path.name,
                                    'page': page_num + 1,
                                    'chunk_index': len(chunks)
                                })
        except Exception as e:
            print(f"[ERROR] Erro ao processar {pdf_path.name}: {e}")
        
        return chunks
    
    def process_all_pdfs(self) -> int:
        """Processa todos os PDFs na pasta docs e cria o índice."""
        if not HAS_DEPENDENCIES:
            raise RuntimeError("Dependências RAG não disponíveis. Instale: pip install sentence-transformers PyPDF2")
        if not self.model:
            raise RuntimeError("Modelo de embeddings não carregado. Verifique as dependências.")
        
        if not self.docs_path.exists():
            raise FileNotFoundError(f"Pasta de documentos não encontrada: {self.docs_path}")
        
        print(f"[RAG] Processando PDFs em {self.docs_path}...")
        
        all_chunks = []
        pdf_files = list(self.docs_path.glob("*.pdf"))
        
        if not pdf_files:
            print(f"[WARNING] Nenhum PDF encontrado em {self.docs_path}")
            return 0
        
        print(f"[RAG] Encontrados {len(pdf_files)} arquivos PDF")
        
        for pdf_path in pdf_files:
            print(f"[RAG] Processando: {pdf_path.name}...")
            chunks = self.extract_text_from_pdf(pdf_path)
            all_chunks.extend(chunks)
            print(f"  → {len(chunks)} chunks extraídos")
        
        if not all_chunks:
            print("[WARNING] Nenhum texto extraído dos PDFs")
            return 0
        
        print(f"[RAG] Total de chunks: {len(all_chunks)}")
        print(f"[RAG] Criando embeddings...")
        
        # Extrair textos para embeddings
        texts = [chunk['text'] for chunk in all_chunks]
        
        # Criar embeddings
        self.embeddings = self.model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
        
        # Armazenar documentos e metadados
        self.documents = texts
        self.metadata = [
            {
                'source': chunk['source'],
                'page': chunk['page'],
                'chunk_index': chunk['chunk_index']
            }
            for chunk in all_chunks
        ]
        
        print(f"[RAG] Índice criado com sucesso!")
        print(f"  → {len(self.documents)} documentos")
        print(f"  → {self.embeddings.shape[0]} embeddings")
        
        return len(all_chunks)
    
    def save_index(self):
        """Salva o índice em arquivo."""
        if self.embeddings is None:
            raise ValueError("Nenhum índice para salvar. Execute process_all_pdfs() primeiro.")
        
        index_data = {
            'documents': self.documents,
            'embeddings': self.embeddings,
            'metadata': self.metadata
        }
        
        with open(self.index_path, 'wb') as f:
            pickle.dump(index_data, f)
        
        print(f"[RAG] Índice salvo em {self.index_path}")
    
    def load_index(self) -> bool:
        """Carrega o índice do arquivo."""
        if not self.index_path.exists():
            return False
        
        try:
            with open(self.index_path, 'rb') as f:
                index_data = pickle.load(f)
            
            self.documents = index_data['documents']
            self.embeddings = index_data['embeddings']
            self.metadata = index_data['metadata']
            
            print(f"[RAG] Índice carregado: {len(self.documents)} documentos")
            return True
        except Exception as e:
            print(f"[ERROR] Erro ao carregar índice: {e}")
            return False
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, any]]:
        """
        Busca documentos relevantes para a query.
        
        Args:
            query: Texto da consulta
            top_k: Número de resultados a retornar
        
        Returns:
            Lista de documentos relevantes com metadados e score de similaridade
        """
        if not HAS_DEPENDENCIES:
            raise RuntimeError("Dependências RAG não disponíveis. Instale: pip install sentence-transformers PyPDF2")
        
        if not self.model:
            raise RuntimeError("Modelo de embeddings não carregado. Verifique as dependências.")
        
        if self.embeddings is None or len(self.documents) == 0:
            raise ValueError("Índice não carregado. Execute load_index() ou process_all_pdfs() primeiro.")
        
        # Criar embedding da query
        query_embedding = self.model.encode([query], convert_to_numpy=True)
        
        # Calcular similaridade de cosseno
        similarities = cosine_similarity(query_embedding, self.embeddings)[0]
        
        # Obter top_k resultados
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            results.append({
                'text': self.documents[idx],
                'score': float(similarities[idx]),
                'source': self.metadata[idx]['source'],
                'page': self.metadata[idx]['page'],
                'chunk_index': self.metadata[idx]['chunk_index']
            })
        
        return results
    
    def _generate_with_groq(
        self,
        query: str,
        context_documents: List[Dict[str, any]]
    ) -> str:
        """
        Gera interpretação usando Groq baseada nos documentos recuperados.
        
        Args:
            query: Query original
            context_documents: Lista de documentos relevantes
        
        Returns:
            Interpretação gerada pelo LLM
        """
        if not self.groq_client:
            raise ValueError("Cliente Groq não disponível")
        
        # Preparar contexto dos documentos
        context_text = "\n\n".join([
            f"--- Documento {i+1} (Fonte: {doc['source']}, Página {doc['page']}) ---\n{doc['text']}"
            for i, doc in enumerate(context_documents)
        ])
        
        # Criar prompt para o Groq
        system_prompt = """Você é um astrólogo experiente e especializado em interpretação de mapas astrais. 
Sua tarefa é criar interpretações astrológicas precisas, profundas e úteis baseadas nos documentos fornecidos.

Diretrizes:
- Use APENAS as informações dos documentos fornecidos como base
- Seja claro, objetivo e prático
- Mantenha o tom profissional mas acessível
- Estruture a interpretação de forma organizada
- Cite aspectos específicos mencionados nos documentos
- Se os documentos não contiverem informações suficientes, indique isso claramente"""
        
        user_prompt = f"""Com base nos seguintes documentos sobre astrologia, crie uma interpretação detalhada e útil sobre: {query}

Documentos de referência:
{context_text}

Por favor, crie uma interpretação estruturada que:
1. Explique o significado astrológico do tema consultado
2. Descreva as características e influências
3. Forneça insights práticos e aplicáveis
4. Seja baseada exclusivamente nas informações dos documentos fornecidos

Interpretação:"""
        
        try:
            # Chamar Groq API
            chat_completion = self.groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ],
                model="llama-3.1-70b-versatile",  # Modelo rápido e eficiente do Groq
                temperature=0.7,
                max_tokens=2000,
                top_p=1,
            )
            
            interpretation = chat_completion.choices[0].message.content
            return interpretation.strip()
            
        except Exception as e:
            print(f"[ERROR] Erro ao gerar interpretação com Groq: {e}")
            # Fallback: retornar documentos sem processamento
            raise
    
    def get_interpretation(
        self,
        planet: Optional[str] = None,
        sign: Optional[str] = None,
        house: Optional[int] = None,
        aspect: Optional[str] = None,
        custom_query: Optional[str] = None,
        use_groq: bool = True
    ) -> Dict[str, any]:
        """
        Obtém interpretação astrológica baseada nos parâmetros do mapa.
        
        Args:
            planet: Nome do planeta (ex: "Sol", "Lua", "Mercúrio")
            sign: Signo (ex: "Áries", "Libra")
            house: Número da casa (1-12)
            aspect: Aspecto (ex: "conjunção", "oposição", "trígono")
            custom_query: Query customizada
            use_groq: Se True, usa Groq para gerar interpretação (padrão: True)
        
        Returns:
            Dicionário com interpretação e referências
        """
        # Construir query baseada nos parâmetros
        if custom_query:
            query = custom_query
        else:
            query_parts = []
            
            if planet and sign:
                query_parts.append(f"{planet} em {sign}")
            elif planet:
                query_parts.append(planet)
            elif sign:
                query_parts.append(f"signo {sign}")
            
            if house:
                query_parts.append(f"casa {house}")
            
            if aspect:
                query_parts.append(f"aspecto {aspect}")
            
            query = " ".join(query_parts) if query_parts else "interpretação mapa astral"
        
        # Buscar documentos relevantes (RAG ou base local)
        results: List[Dict[str, any]] = []
        try:
            results = self.search(query, top_k=5)
        except Exception as e:
            print(f"[RAG] Falha ao consultar índice vetorial ({e}). Usando base local.")
        
        if not results:
            results = _local_knowledge_base.get_context(
                planet=planet,
                sign=sign,
                house=house,
                aspect=aspect,
                query=query
            )
        
        if not results:
            return {
                'interpretation': "Nenhum documento relevante encontrado para esta consulta.",
                'sources': [],
                'query_used': query,
                'generated_by': 'none'
            }
        
        # Tentar usar Groq se disponível e solicitado
        if use_groq:
            if not HAS_GROQ:
                # Silenciosamente usar fallback se Groq não estiver instalado
                pass
            elif not self.groq_client:
                # Silenciosamente usar fallback se Groq não estiver configurado
                pass
            else:
                try:
                    interpretation_text = self._generate_with_groq(query, results)
                    return {
                        'interpretation': interpretation_text,
                        'sources': [
                            {
                                'source': r['source'],
                                'page': r['page'],
                                'relevance': r['score']
                            }
                            for r in results
                        ],
                        'query_used': query,
                        'generated_by': 'groq'
                    }
                except Exception as e:
                    # Fallback silencioso: retornar documentos sem processamento
                    pass
        
        # Fallback: Combinar textos dos resultados sem processamento LLM
        interpretation_text = "\n\n".join([
            f"[Fonte: {r['source']}, Página {r['page']}]\n{r['text']}"
            for r in results
        ])
        
        # Criar resposta estruturada
        return {
            'interpretation': interpretation_text,
            'sources': [
                {
                    'source': r['source'],
                    'page': r['page'],
                    'relevance': r['score']
                }
                for r in results
            ],
            'query_used': query,
            'generated_by': 'rag_only'
        }


# Instâncias globais
_rag_service: Optional[RAGService] = None
_local_knowledge_base = LocalKnowledgeBase()


def get_rag_service() -> RAGService:
    """Obtém instância singleton do serviço RAG."""
    global _rag_service
    
    if _rag_service is None:
        # Importar configurações
        from app.core.config import settings
        
        # Determinar caminho da pasta docs (relativo ao backend)
        backend_path = Path(__file__).parent.parent.parent
        docs_path = backend_path / "docs"
        index_path = backend_path / "rag_index.pkl"
        
        # Obter chave do Groq das configurações
        groq_api_key = settings.GROQ_API_KEY if hasattr(settings, 'GROQ_API_KEY') else None
        
        _rag_service = RAGService(
            docs_path=str(docs_path),
            index_path=str(index_path),
            groq_api_key=groq_api_key
        )
        
        # Tentar carregar índice existente
        if not _rag_service.load_index():
            print("[RAG] Índice não encontrado. Execute build_rag_index.py para criar.")
    
    return _rag_service

