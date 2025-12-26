"""
Serviço RAG (Retrieval-Augmented Generation) usando FastEmbed e modelo BGE (Hugging Face).
Versão otimizada - mais leve e rápida que LlamaIndex.
"""

import os
import json
import pickle
from pathlib import Path
from typing import List, Dict, Optional, Any
import re
import numpy as np

try:
    from fastembed import TextEmbedding
    HAS_FASTEMBED = True
except ImportError as e:
    HAS_FASTEMBED = False
    print(f"[DEBUG] ImportError ao carregar FastEmbed: {e}")

try:
    import PyPDF2
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False
    print("[WARNING] PyPDF2 não instalado. PDFs não poderão ser processados.")

try:
    from groq import Groq
    HAS_GROQ = True
except ImportError:
    HAS_GROQ = False

from app.services.local_knowledge_base import LocalKnowledgeBase


def _chunk_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
    """
    Divide texto em chunks com overlap.
    
    Args:
        text: Texto a dividir
        chunk_size: Tamanho do chunk
        chunk_overlap: Overlap entre chunks
    
    Returns:
        Lista de chunks
    """
    if not text or len(text) < chunk_size:
        return [text] if text else []
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        
        # Tentar quebrar em parágrafo ou frase
        if end < len(text):
            # Procurar última quebra de linha ou ponto
            last_newline = chunk.rfind('\n')
            last_period = chunk.rfind('. ')
            
            if last_newline > chunk_size * 0.5:
                chunk = chunk[:last_newline + 1]
                end = start + last_newline + 1
            elif last_period > chunk_size * 0.5:
                chunk = chunk[:last_period + 1]
                end = start + last_period + 1
        
        chunks.append(chunk.strip())
        start = end - chunk_overlap
    
    return chunks


class RAGServiceFastEmbed:
    """Serviço RAG usando FastEmbed e modelo BGE do Hugging Face."""
    
    def __init__(
        self,
        docs_path: str = "docs",
        index_path: str = "rag_index_fastembed",
        groq_api_key: Optional[str] = None,
        bge_model_name: str = "BAAI/bge-small-en-v1.5"
    ):
        """
        Inicializa o serviço RAG com FastEmbed.
        
        Args:
            docs_path: Caminho para pasta de documentos
            index_path: Caminho para salvar/carregar o índice
            groq_api_key: Chave API do Groq para geração
            bge_model_name: Nome do modelo BGE do Hugging Face
        """
        self.docs_path = Path(docs_path)
        self.index_path = Path(index_path)
        self.embedding_model = None
        self.groq_client = None
        self.bge_model_name = bge_model_name
        
        # Dados do índice
        self.documents: List[Dict[str, Any]] = []  # Lista de documentos com embeddings
        self.embeddings_matrix: Optional[np.ndarray] = None  # Matriz de embeddings
        
        if not HAS_FASTEMBED:
            print("[WARNING] FastEmbed não instalado. Instale com: pip install fastembed")
            return
        
        # Configurar modelo de embeddings BGE
        try:
            print(f"[RAG-FastEmbed] Carregando modelo BGE: {bge_model_name}")
            self.embedding_model = TextEmbedding(model_name=bge_model_name)
            print(f"[RAG-FastEmbed] Modelo BGE carregado com sucesso")
        except Exception as e:
            print(f"[ERROR] Erro ao carregar modelo BGE: {e}")
            print(f"[RAG-FastEmbed] Tentando modelo alternativo...")
            try:
                # Fallback para modelo multilíngue
                self.embedding_model = TextEmbedding(
                    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
                )
                self.bge_model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
                print(f"[RAG-FastEmbed] Modelo alternativo carregado")
            except Exception as e2:
                print(f"[ERROR] Não foi possível carregar modelo: {e2}")
                raise
        
        # Inicializar cliente Groq se disponível
        if HAS_GROQ:
            if groq_api_key and groq_api_key.strip():
                try:
                    self.groq_client = Groq(api_key=groq_api_key.strip())
                    print("[RAG-FastEmbed] Cliente Groq inicializado com sucesso")
                except Exception as e:
                    print(f"[WARNING] Erro ao inicializar Groq: {e}")
                    self.groq_client = None
            else:
                print("[WARNING] GROQ_API_KEY não configurada. Funcionalidades com Groq estarão desabilitadas.")
                self.groq_client = None
    
    def _clean_text(self, text: str) -> str:
        """Remove ruído comum de PDFs."""
        if not text:
            return ""
        
        # Remover URLs
        text = re.sub(r'https?://[^\s]+', '', text)
        text = re.sub(r'www\.[^\s]+', '', text)
        
        # Remover padrões comuns de lixo de PDFs
        noise_patterns = [
            r'Privacy\s*',
            r'\d{2}/\d{2}/\d{2},?\s*\d{2}:\d{2}',
            r'vebuka\.com[^\n]*',
            r'pdfcoffee\.com[^\n]*',
            r'Past_Life_Astrology[^\n]*',
            r'IndirectObject\([^)]+\)',
            r'unknown widths\s*:',
            r'incorrect startxref pointer\(\d+\)',
            r'\d{1,4}/\d{2,3}',
            r'^\s*\d+\s*$',
        ]
        
        for pattern in noise_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.MULTILINE)
        
        # Remover linhas muito curtas
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if len(line) < 15:
                continue
            if re.match(r'^[\d\s\-\./]+$', line):
                continue
            cleaned_lines.append(line)
        
        text = '\n'.join(cleaned_lines)
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()
    
    def _detect_category(self, filename: str, folder_path: Path) -> str:
        """Detecta a categoria do documento."""
        filename_lower = filename.lower()
        folder_str = str(folder_path).lower()
        
        if filename_lower.startswith('num_'):
            return 'numerology'
        elif filename_lower.startswith('ast_'):
            return 'astrology'
        
        if 'numerologia' in folder_str:
            return 'numerology'
        
        return 'astrology'
    
    def _extract_text_from_pdf(self, pdf_path: Path) -> str:
        """Extrai texto de um PDF."""
        if not HAS_PYPDF2:
            return ""
        
        try:
            text = ""
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text
        except Exception as e:
            print(f"[ERROR] Erro ao extrair texto de {pdf_path.name}: {e}")
            return ""
    
    def _process_folder(self, folder_path: Path) -> List[Dict[str, Any]]:
        """Processa todos os documentos de uma pasta."""
        if not folder_path.exists():
            print(f"[RAG-FastEmbed] Pasta não encontrada: {folder_path}")
            return []
        
        folder_name = folder_path.name
        print(f"[RAG-FastEmbed] Processando pasta: {folder_name}...")
        
        documents = []
        
        # Processar PDFs
        pdf_files = list(folder_path.glob("*.pdf"))
        print(f"[RAG-FastEmbed] Encontrados {len(pdf_files)} arquivos PDF em {folder_name}")
        
        for pdf_path in pdf_files:
            print(f"[RAG-FastEmbed] Processando PDF: {pdf_path.name}...")
            try:
                category = self._detect_category(pdf_path.name, folder_path)
                text = self._extract_text_from_pdf(pdf_path)
                cleaned_text = self._clean_text(text)
                
                if cleaned_text:
                    # Dividir em chunks
                    chunks = _chunk_text(cleaned_text, chunk_size=1000, chunk_overlap=200)
                    
                    for i, chunk in enumerate(chunks):
                        if len(chunk.strip()) > 50:  # Ignorar chunks muito pequenos
                            documents.append({
                                'text': chunk,
                                'source': pdf_path.name,
                                'file_type': 'pdf',
                                'category': category,
                                'page': i + 1,  # Aproximação
                                'metadata': {
                                    'source': pdf_path.name,
                                    'file_type': 'pdf',
                                    'category': category
                                }
                            })
                    
                    print(f"  → {len(chunks)} chunks extraídos (categoria: {category})")
            except Exception as e:
                print(f"[ERROR] Erro ao processar {pdf_path.name}: {e}")
        
        # Processar Markdowns
        md_files = list(folder_path.glob("*.md"))
        print(f"[RAG-FastEmbed] Encontrados {len(md_files)} arquivos Markdown em {folder_name}")
        
        for md_path in md_files:
            print(f"[RAG-FastEmbed] Processando MD: {md_path.name}...")
            try:
                with open(md_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if content.strip():
                    category = self._detect_category(md_path.name, folder_path)
                    
                    # Dividir em chunks
                    chunks = _chunk_text(content, chunk_size=1000, chunk_overlap=200)
                    
                    for i, chunk in enumerate(chunks):
                        if len(chunk.strip()) > 50:
                            documents.append({
                                'text': chunk,
                                'source': md_path.name,
                                'file_type': 'markdown',
                                'category': category,
                                'page': i + 1,
                                'metadata': {
                                    'source': md_path.name,
                                    'file_type': 'markdown',
                                    'category': category
                                }
                            })
                    
                    print(f"  → {len(chunks)} chunks extraídos (categoria: {category})")
            except Exception as e:
                print(f"[ERROR] Erro ao processar {md_path.name}: {e}")
        
        return documents
    
    def process_all_documents(self) -> int:
        """
        Processa todos os documentos e cria o índice.
        
        Returns:
            Número de chunks processados
        """
        if not HAS_FASTEMBED:
            raise RuntimeError("FastEmbed não disponível. Instale: pip install fastembed")
        
        if not self.docs_path.exists():
            raise FileNotFoundError(f"Pasta de documentos não encontrada: {self.docs_path}")
        
        # Definir pastas
        docs_path = Path(self.docs_path)
        numerologia_path = docs_path.parent / "numerologia"
        
        print(f"[RAG-FastEmbed] Processando documentos em {docs_path} e {numerologia_path}...")
        
        # Processar documentos
        documents = []
        documents.extend(self._process_folder(docs_path))
        
        if numerologia_path.exists():
            documents.extend(self._process_folder(numerologia_path))
        else:
            print(f"[RAG-FastEmbed] Pasta numerologia não encontrada: {numerologia_path}")
        
        if not documents:
            print("[WARNING] Nenhum documento processado")
            return 0
        
        # Estatísticas por categoria
        categories_count = {}
        for doc in documents:
            category = doc.get('category', 'astrology')
            categories_count[category] = categories_count.get(category, 0) + 1
        
        print(f"[RAG-FastEmbed] Total de chunks: {len(documents)}")
        for cat, count in categories_count.items():
            print(f"  → {cat}: {count} chunks")
        
        print(f"[RAG-FastEmbed] Gerando embeddings com FastEmbed...")
        
        # Gerar embeddings para todos os documentos
        texts = [doc['text'] for doc in documents]
        embeddings_list = list(self.embedding_model.embed(texts))
        
        # Converter para numpy array
        self.embeddings_matrix = np.array(embeddings_list)
        
        # Adicionar embeddings aos documentos
        for i, doc in enumerate(documents):
            doc['embedding'] = embeddings_list[i]
        
        self.documents = documents
        
        print(f"[RAG-FastEmbed] Índice criado com sucesso!")
        print(f"  → {len(documents)} chunks indexados")
        print(f"  → Dimensão dos embeddings: {self.embeddings_matrix.shape[1]}")
        
        return len(documents)
    
    def save_index(self):
        """Salva o índice em disco."""
        if not self.documents or self.embeddings_matrix is None:
            raise ValueError("Nenhum índice para salvar. Execute process_all_documents() primeiro.")
        
        # Criar diretório se não existir
        self.index_path.mkdir(parents=True, exist_ok=True)
        
        # Salvar documentos (sem embeddings para economizar espaço)
        documents_to_save = []
        for doc in self.documents:
            doc_copy = doc.copy()
            doc_copy.pop('embedding', None)  # Remover embedding (será recalculado se necessário)
            documents_to_save.append(doc_copy)
        
        # Salvar documentos
        with open(self.index_path / "documents.json", 'w', encoding='utf-8') as f:
            json.dump(documents_to_save, f, ensure_ascii=False, indent=2)
        
        # Salvar embeddings como numpy array (mais eficiente)
        np.save(self.index_path / "embeddings.npy", self.embeddings_matrix)
        
        # Salvar metadados
        metadata = {
            'model_name': self.bge_model_name,
            'num_documents': len(self.documents),
            'embedding_dim': self.embeddings_matrix.shape[1]
        }
        with open(self.index_path / "metadata.json", 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"[RAG-FastEmbed] Índice salvo em {self.index_path}")
    
    def load_index(self) -> bool:
        """Carrega o índice do disco."""
        if not HAS_FASTEMBED:
            return False
        
        if not self.index_path.exists():
            return False
        
        try:
            # Carregar metadados
            metadata_path = self.index_path / "metadata.json"
            if not metadata_path.exists():
                return False
            
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # Verificar se o modelo é compatível
            if metadata.get('model_name') != self.bge_model_name:
                print(f"[WARNING] Modelo do índice ({metadata.get('model_name')}) diferente do configurado ({self.bge_model_name})")
                print("[WARNING] Reconstruindo índice...")
                return False
            
            # Carregar documentos
            documents_path = self.index_path / "documents.json"
            if not documents_path.exists():
                return False
            
            with open(documents_path, 'r', encoding='utf-8') as f:
                documents = json.load(f)
            
            # Carregar embeddings
            embeddings_path = self.index_path / "embeddings.npy"
            if not embeddings_path.exists():
                return False
            
            self.embeddings_matrix = np.load(embeddings_path)
            
            # Reconstruir documentos com embeddings
            self.documents = []
            for i, doc in enumerate(documents):
                doc['embedding'] = self.embeddings_matrix[i].tolist()
                self.documents.append(doc)
            
            print(f"[RAG-FastEmbed] Índice carregado de {self.index_path}")
            print(f"  → {len(self.documents)} documentos carregados")
            return True
        except Exception as e:
            print(f"[ERROR] Erro ao carregar índice: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calcula similaridade cosseno entre dois vetores."""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return float(dot_product / (norm1 * norm2))
    
    def search(
        self, 
        query: str, 
        top_k: int = 5, 
        expand_query: bool = False,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Busca documentos relevantes para a query.
        
        Args:
            query: Texto da consulta
            top_k: Número de resultados a retornar
            expand_query: Se True, faz múltiplas buscas com variações da query
            category: Filtrar por categoria ('astrology' ou 'numerology')
        
        Returns:
            Lista de documentos relevantes com metadados e score
        """
        if not HAS_FASTEMBED or self.embedding_model is None:
            # Fallback para base de conhecimento local
            local_kb = LocalKnowledgeBase()
            import re
            
            # Tentar extrair planetas e signos da query
            planet = None
            sign = None
            house = None
            
            planets_list = ['Sol', 'Lua', 'Mercúrio', 'Vênus', 'Marte', 'Júpiter', 'Saturno', 'Urano', 'Netuno', 'Plutão']
            signs_list = ['Áries', 'Touro', 'Gêmeos', 'Câncer', 'Leão', 'Virgem', 'Libra', 'Escorpião', 'Sagitário', 'Capricórnio', 'Aquário', 'Peixes']
            
            query_lower = query.lower()
            
            for p in planets_list:
                if p.lower() in query_lower or local_kb.normalize_planet(p).lower() in query_lower:
                    planet = p
                    break
            
            for s in signs_list:
                if s.lower() in query_lower or local_kb.normalize_sign(s).lower() in query_lower:
                    sign = s
                    break
            
            house_match = re.search(r'casa\s+(\d+)', query_lower)
            if house_match:
                house = int(house_match.group(1))
            
            context = local_kb.get_context(
                planet=planet,
                sign=sign,
                house=house,
                query=query if not planet and not sign else None
            )
            
            results = []
            for i, ctx in enumerate(context[:top_k]):
                results.append({
                    'text': ctx.get('text', ''),
                    'source': ctx.get('source', 'local_kb'),
                    'page': ctx.get('page', 1),
                    'score': 0.8 - (i * 0.1)
                })
            
            if not results:
                results.append({
                    'text': f"Informações sobre: {query}. Para interpretações completas, instale o FastEmbed e construa o índice RAG.",
                    'source': 'local_kb',
                    'page': 1,
                    'score': 0.5
                })
            
            return results
        
        if not self.documents or self.embeddings_matrix is None:
            raise ValueError("Índice não carregado. Execute load_index() ou process_all_documents() primeiro.")
        
        try:
            # Gerar embedding da query
            query_embedding = np.array(list(self.embedding_model.embed([query]))[0])
            
            # Buscar mais resultados se houver filtro de categoria (otimizado: reduzido de *3 para *1.5)
            search_top_k = int(top_k * 1.5) if category else (int(top_k * 1.2) if expand_query else top_k)
            
            # Calcular similaridade com todos os documentos
            similarities = []
            for i, doc in enumerate(self.documents):
                # Filtrar por categoria se especificada
                if category and doc.get('category') != category:
                    continue
                
                doc_embedding = np.array(doc.get('embedding', []))
                if len(doc_embedding) == 0:
                    continue
                
                similarity = self._cosine_similarity(query_embedding, doc_embedding)
                similarities.append((similarity, i))
            
            # Ordenar por similaridade e pegar top_k
            similarities.sort(reverse=True, key=lambda x: x[0])
            top_indices = [idx for _, idx in similarities[:search_top_k]]
            
            # Converter para formato esperado
            results = []
            for idx in top_indices:
                doc = self.documents[idx]
                similarity_score = similarities[top_indices.index(idx)][0] if top_indices else 0.0
                
                results.append({
                    'text': doc.get('text', ''),
                    'score': float(similarity_score),
                    'source': doc.get('source', 'unknown'),
                    'page': doc.get('page', 1),
                    'category': doc.get('category', 'astrology'),
                    'metadata': doc.get('metadata', {})
                })
                
                if len(results) >= top_k:
                    break
            
            if category:
                print(f"[RAG-FastEmbed] Busca filtrada por categoria '{category}': {len(results)} resultados")
            
            return results
        except Exception as e:
            print(f"[RAG-FastEmbed] Erro ao buscar: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _generate_with_groq(
        self,
        query: str,
        context_documents: List[Dict[str, Any]],
        category: Optional[str] = None
    ) -> str:
        """Gera interpretação usando Groq baseada nos documentos recuperados."""
        if not self.groq_client:
            raise ValueError("Cliente Groq não disponível")
        
        # Determinar categoria se não especificada
        if category is None:
            doc_categories = [doc.get('category', 'astrology') for doc in context_documents if doc.get('category')]
            if doc_categories:
                category = doc_categories[0]
            else:
                query_lower = query.lower()
                if any(word in query_lower for word in ['numerologia', 'numerology', 'número', 'numero', 'caminho de vida', 'life path']):
                    category = 'numerology'
                else:
                    category = 'astrology'
        
        # Preparar contexto
        filtered_docs = [
            doc for doc in context_documents 
            if doc.get('category', 'astrology') == category
        ]
        
        if not filtered_docs:
            print(f"[WARNING] Nenhum documento da categoria '{category}' encontrado. Usando todos os documentos.")
            filtered_docs = context_documents
        
        context_text = "\n\n".join([
            doc.get('text', '')
            for doc in filtered_docs
            if doc.get('text')
        ])
        
        # Detectar tipo de consulta
        is_synastry_query = False
        is_chart_ruler_query = False
        
        if category == 'astrology':
            is_synastry_query = any(phrase in query.lower() for phrase in [
                'sinastria', 'synastry', 'compatibilidade', 'compatibility',
                'relacionamento', 'relationship', 'casal', 'couple'
            ])
            
            is_chart_ruler_query = any(phrase in query.lower() for phrase in [
                'regente do mapa', 'regente do ascendente', 'planeta regente',
                'chart ruler', 'ruler of', 'ascendant ruler'
            ])
        
        # Ajustar prompts baseado na categoria (mesmo código do original)
        if category == 'numerology':
            system_prompt = """Você é um Numerólogo Pitagórico experiente e também Astrólogo. Sua abordagem sintetiza as melhores referências mundiais: a precisão técnica e síntese de Matthew Oliver Goodwin, a profundidade psicológica e terapêutica de Hans Decoz, a visão holística de saúde de David A. Phillips e a geometria sagrada/ciclos de vida de Faith Javane & Dusty Bunker.

IMPORTANTE CRÍTICO:
- Use APENAS conhecimento NUMEROLÓGICO fornecido no contexto
- NÃO mencione planetas, signos, casas ou qualquer conceito astrológico (exceto quando explicitamente solicitado para conexão com Tarot/Planetas)
- Foque em números, cálculos numerológicos, significados dos números e ciclos numerológicos
- Se o contexto não contiver informações numerológicas suficientes, informe isso claramente
- Linguagem simples, prática e esclarecedora (evite "numerologês" excessivo)
- Tom de empoderamento e autoconhecimento
- Os números são ferramentas de livre arbítrio, não sentença imutável
- PRIORIZE as informações do contexto fornecido - use-as como base principal da interpretação

MISSÃO: Criar interpretações numerológicas PRECISAS, COMPLETAS e DIDÁTICAS baseadas nos documentos fornecidos."""
            
            user_prompt = f"""NUMEROLOGIA:

Consulta: {query}

CONHECIMENTO NUMEROLÓGICO DE REFERÊNCIA (Use estas informações como base principal):
{context_text}

---

INSTRUÇÕES:
Crie uma interpretação COMPLETA e DETALHADA sobre numerologia baseada nos documentos fornecidos acima.

IMPORTANTE:
- PRIORIZE e USE as informações do contexto fornecido - elas são a base da sua interpretação
- Se o contexto mencionar informações específicas sobre os números, USE-AS na sua resposta
- Se o contexto não tiver informações sobre algum número específico, use conhecimento geral, mas sempre mencione quando estiver usando conhecimento geral vs. informações do contexto
- NÃO mencione astrologia, planetas ou signos (exceto conexões Tarot/Planetas quando solicitado)
- Foque em números, significados numerológicos e ciclos pessoais
- Seja específico e prático
- Formate com títulos em negrito quando apropriado (formato: **TÍTULO:**)
- Use parágrafos claros e separados por quebras de linha duplas
- Incorpore naturalmente as informações do contexto na interpretação"""
        
        elif is_synastry_query:
            system_prompt = """Você é um astrólogo experiente especializado em sinastria e análise de compatibilidade entre signos. 
Sua função é criar interpretações práticas, didáticas e atuais sobre relacionamentos, focando em dinâmicas reais e aplicáveis.

REGRAS DE FORMATAÇÃO:
- Sempre escreva interpretações práticas e aplicáveis ao dia a dia
- Use estrutura didática com títulos em negrito quando apropriado (formato: **TÍTULO:**)
- Explique termos astrológicos de forma simples
- Foque em dinâmicas práticas do relacionamento
- Inclua pontos fortes, desafios e orientações práticas
- Seja específico sobre comunicação, valores, intimidade e objetivos de vida
- Use linguagem atual e relevante para relacionamentos modernos"""
            
            user_prompt = f"""SINASTRIA / COMPATIBILIDADE:

Consulta: {query}

CONHECIMENTO ASTROLÓGICO DE REFERÊNCIA:
{context_text}

---

INSTRUÇÕES:
Crie uma interpretação COMPLETA, PRÁTICA e DIDÁTICA sobre a compatibilidade entre os signos mencionados na consulta. A interpretação DEVE ser útil para pessoas em relacionamentos reais.

Estruture a interpretação explicando:

1. **Dinâmica Geral do Relacionamento** (1 parágrafo)
2. **Pontos Fortes e Complementaridade** (1 parágrafo)
3. **Desafios e Áreas de Atenção** (1 parágrafo)
4. **Orientações Práticas** (1 parágrafo)
5. **Exemplos Práticos** (OBRIGATÓRIO - pelo menos 3 exemplos)

IMPORTANTE:
- Escreva NO MÍNIMO 4 parágrafos completos e práticos
- SEMPRE inclua uma seção "**Exemplos Práticos:**" com pelo menos 3 exemplos concretos
- Use linguagem didática, atual e aplicável ao dia a dia
- Foque em dinâmicas reais de relacionamento"""
        
        elif is_chart_ruler_query:
            system_prompt = """Você é um astrólogo experiente especializado em interpretação de regentes do mapa astral. 
Sua função é criar interpretações PROFUNDAS, DETALHADAS e DIDÁTICAS sobre o planeta regente do mapa, explicando sua importância fundamental para o autoconhecimento.

IMPORTANTE CRÍTICO:
- Use APENAS conhecimento ASTROLÓGICO fornecido no contexto
- NÃO mencione numerologia, números ou cálculos numerológicos
- Foque em planetas, signos, casas e aspectos astrológicos

REGRAS DE FORMATAÇÃO:
- Sempre escreva NO MÍNIMO 2 parágrafos completos e densos sobre o regente
- Use estrutura didática com títulos em negrito quando apropriado (formato: **TÍTULO:**)
- Explique termos astrológicos de forma simples
- Conecte as informações de forma narrativa, não apenas listas
- Foque na importância do regente para autoconhecimento e desenvolvimento pessoal"""
            
            user_prompt = f"""REGENTE DO MAPA ASTRAL:

Consulta: {query}

CONHECIMENTO ASTROLÓGICO DE REFERÊNCIA:
{context_text}

---

INSTRUÇÕES:
Crie uma interpretação COMPLETA e DETALHADA sobre o regente do mapa astral, explicando:

1. O que significa ter esse planeta como regente do mapa (pelo menos 1 parágrafo completo e denso)
2. Como o regente influencia a personalidade, energia vital e comportamento (pelo menos 1 parágrafo completo e denso)
3. A importância do regente para o autoconhecimento e desenvolvimento pessoal
4. Como o regente revela forças naturais e áreas de atenção

IMPORTANTE:
- Escreva NO MÍNIMO 2 parágrafos completos e densos
- Use linguagem didática e acessível
- Conecte as informações de forma narrativa"""
        
        else:
            system_prompt = """Você é um astrólogo especialista com profundo conhecimento em astrologia tradicional, cármica e preditiva.

MISSÃO: Criar interpretações astrológicas PRECISAS, COMPLETAS e DIDÁTICAS baseadas nos documentos fornecidos.

ESTRUTURA OBRIGATÓRIA da interpretação (formatação didática):
1. **PASSADO/KARMA**: 
   - O que essa configuração indica sobre padrões herdados, vidas passadas, condicionamentos e lições que a alma traz
   - Use parágrafos claros e separados por quebras de linha duplas (\n\n)

2. **PRESENTE/ESSÊNCIA**: 
   - Como essa energia se manifesta AGORA na personalidade, comportamentos, talentos e desafios atuais
   - Seja específico sobre características pessoais e padrões de comportamento

3. **FUTURO/EVOLUÇÃO**: 
   - Para onde os astros estão inclinando - tendências, oportunidades de crescimento, direcionamentos e potenciais a desenvolver

REGRAS:
- Use APENAS os documentos como base factual
- Conecte passado → presente → futuro de forma fluida
- Seja específico e prático, não genérico
- NÃO mencione fontes, páginas ou referências aos documentos
- NÃO repita a query ou o tema da consulta no início da resposta
- Mínimo 3 parágrafos principais (um para cada dimensão temporal)"""
            
            user_prompt = f"""TEMA DA CONSULTA: {query}

CONHECIMENTO ASTROLÓGICO DISPONÍVEL:
{context_text}

INSTRUÇÕES:
1. Crie uma interpretação astrológica completa seguindo a estrutura PASSADO → PRESENTE → FUTURO
2. Use APENAS informações ASTROLÓGICAS do contexto fornecido
3. NÃO mencione numerologia, números pessoais ou cálculos numerológicos
4. Formate o texto de forma DIDÁTICA e ORGANIZADA:
   - Use títulos em negrito para cada seção principal (formato: **PASSADO/KARMA:**)
   - Separe parágrafos com quebras de linha duplas
   - Use listas com marcadores (- ou •) para múltiplos pontos
   - Cada seção deve ter pelo menos um parágrafo completo
5. Seja preciso, profundo e útil para quem busca autoconhecimento e orientação
6. NÃO repita o tema da consulta no início da resposta
7. Comece diretamente com a interpretação do PASSADO/KARMA"""
        
        try:
            chat_completion = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model="llama-3.1-8b-instant",
                temperature=0.7,
                max_tokens=2500 if (is_chart_ruler_query or is_synastry_query) else 2000,
                top_p=0.9,
            )
            
            interpretation = chat_completion.choices[0].message.content
            
            if interpretation:
                interpretation = interpretation.strip()
                interpretation = re.sub(r'\[Fonte:[^\]]+\]', '', interpretation)
                interpretation = re.sub(r'Página \d+', '', interpretation)
            
            return interpretation if interpretation else ""
        except Exception as e:
            print(f"[ERROR] Erro ao gerar interpretação com Groq: {e}")
            raise
    
    def get_interpretation(
        self,
        planet: Optional[str] = None,
        sign: Optional[str] = None,
        house: Optional[int] = None,
        aspect: Optional[str] = None,
        custom_query: Optional[str] = None,
        use_groq: bool = True,
        top_k: int = 8,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """Obtém interpretação astrológica ou numerológica."""
        if not HAS_FASTEMBED:
            local_kb = LocalKnowledgeBase()
            
            if custom_query:
                query = custom_query
            else:
                query_parts = []
                if planet and sign:
                    query_parts.append(f"{planet} em {sign}")
                elif planet:
                    query_parts.append(planet)
                elif sign:
                    query_parts.append(sign)
                if house:
                    query_parts.append(f"casa {house}")
                query = " ".join(query_parts) if query_parts else "interpretação astrológica"
            
            context = local_kb.get_context(
                planet=planet,
                sign=sign,
                house=house,
                query=query
            )
            
            if context and len(context) > 0:
                context_text = "\n\n".join([ctx.get('text', '') for ctx in context[:3] if ctx.get('text')])
                return {
                    'interpretation': context_text[:1000] if context_text else "Interpretação não disponível sem FastEmbed.",
                    'sources': [],
                    'query_used': query,
                    'generated_by': 'local_kb'
                }
            else:
                return {
                    'interpretation': f"Interpretação básica: {query}. Para interpretações completas, instale o FastEmbed.",
                    'sources': [],
                    'query_used': query,
                    'generated_by': 'fallback'
                }
        
        # Construir query
        if custom_query:
            query = custom_query
        else:
            query_parts = []
            if planet and sign:
                query_parts.append(f"{planet} em {sign} significado interpretação karma evolução")
            elif planet:
                query_parts.append(f"{planet} planeta astrologia significado personalidade")
            elif sign:
                query_parts.append(f"signo {sign} características personalidade")
            if house:
                query_parts.append(f"casa {house} área vida significado")
            if aspect:
                query_parts.append(f"aspecto {aspect} relação planetas")
            query = " ".join(query_parts) if query_parts else "interpretação mapa astral completa"
        
        # Identificar tipo de consulta para ajustar top_k (otimizado: valores reduzidos)
        query_lower = query.lower()
        is_karma_query = any(word in query_lower for word in ['nodo', 'karma', 'carma', 'passado', 'vidas passadas', 'retrógrado'])
        is_transit_query = any(word in query_lower for word in ['trânsito', 'transito', 'futuro', 'previsão', 'tendência'])
        is_aspect_query = any(word in query_lower for word in ['aspecto', 'conjunção', 'oposição', 'trígono', 'quadratura', 'sextil'])
        is_synastry_query = any(phrase in query_lower for phrase in [
            'sinastria', 'synastry', 'compatibilidade', 'compatibility',
            'relacionamento', 'relationship', 'casal', 'couple'
        ])
        
        # Ajustar top_k baseado no tipo de consulta (valores reduzidos)
        if is_karma_query or is_transit_query:
            top_k = 12  # Era 20
        elif is_aspect_query:
            top_k = 10  # Era 15
        elif is_synastry_query:
            top_k = 12  # Era 18
        else:
            top_k = 8  # Era 12
        
        # Determinar categoria se não especificada
        if category is None:
            query_lower = query.lower()
            if any(word in query_lower for word in ['numerologia', 'numerology', 'número', 'numero', 'caminho de vida', 'life path']):
                category = 'numerology'
            else:
                category = 'astrology'
        
        # Buscar documentos relevantes
        results = []
        try:
            results = self.search(query, top_k=top_k, expand_query=True, category=category)
            print(f"[RAG-FastEmbed] Busca retornou {len(results)} resultados para query: {query[:100]} (categoria: {category})")
        except Exception as e:
            print(f"[RAG-FastEmbed] Erro na busca: {e}")
        
        # Fallback para base local se não houver resultados
        if not results:
            local_kb = LocalKnowledgeBase()
            results = local_kb.get_context(
                planet=planet,
                sign=sign,
                house=house,
                aspect=aspect,
                query=query
            )
        
        # Gerar interpretação com Groq se disponível
        if use_groq and self.groq_client and results:
            try:
                interpretation_text = self._generate_with_groq(query, results, category=category)
                if interpretation_text and len(interpretation_text.strip()) > 50:
                    return {
                        'interpretation': interpretation_text,
                        'sources': [
                            {
                                'source': r.get('source', 'knowledge_base'),
                                'page': r.get('page', 1),
                                'relevance': r.get('score', 0.5)
                            }
                            for r in results
                        ],
                        'query_used': query,
                        'generated_by': 'groq'
                    }
            except Exception as e:
                print(f"[RAG-FastEmbed] Erro ao gerar com Groq: {e}")
        
        # Fallback: retornar documentos sem processamento
        interpretation_text = "\n\n".join([
            r.get('text', '').strip()
            for r in results
            if r.get('text') and len(r.get('text', '').strip()) > 10
        ])
        
        if not interpretation_text or len(interpretation_text.strip()) < 50:
            return {
                'interpretation': "Não foi possível encontrar informações suficientes sobre este tema na base de conhecimento.",
                'sources': [],
                'query_used': query,
                'generated_by': 'none'
            }
        
        return {
            'interpretation': interpretation_text,
            'sources': [
                {
                    'source': r.get('source', 'unknown'),
                    'page': r.get('page', 1),
                    'relevance': r.get('score', 0.5)
                }
                for r in results
            ],
            'query_used': query,
            'generated_by': 'rag_only'
        }


# Instância global
_rag_service_instance: Optional[RAGServiceFastEmbed] = None


def get_rag_service() -> RAGServiceFastEmbed:
    """Obtém instância singleton do serviço RAG com FastEmbed."""
    global _rag_service_instance
    
    if _rag_service_instance is None:
        from app.core.config import settings
        
        service_path = Path(__file__).parent.parent.parent
        docs_path = service_path / settings.DOCS_PATH
        index_path = service_path / settings.INDEX_PATH
        
        groq_api_key = settings.GROQ_API_KEY if settings.GROQ_API_KEY else None
        
        _rag_service_instance = RAGServiceFastEmbed(
            docs_path=str(docs_path),
            index_path=str(index_path),
            groq_api_key=groq_api_key,
            bge_model_name=settings.BGE_MODEL_NAME
        )
        
        # Tentar carregar índice existente
        if not _rag_service_instance.load_index():
            print("[RAG-Service] Índice não encontrado. Execute o script de build do índice para criar.")
    
    return _rag_service_instance
