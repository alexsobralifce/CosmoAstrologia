"""
Serviço RAG (Retrieval-Augmented Generation) para consulta de documentos astrológicos.
Processa PDFs e cria um banco vetorial para consultas semânticas.
"""

import os
import pickle
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    np = None

try:
    from fastembed import TextEmbedding
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


def cosine_similarity(a, b):
    """
    Implementação própria de similaridade de cosseno para evitar dependências
    que exigem compilação em alguns ambientes (ex.: scikit-learn).
    """
    if not HAS_NUMPY:
        raise ImportError("numpy is required for cosine_similarity. Please install numpy.")
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
            # Carregar modelo de embeddings usando FastEmbed (multilíngue, inclui português)
            # Usando BGE-small que é leve, rápido e tem boa qualidade multilíngue
            try:
                # FastEmbed suporta modelos multilíngues do HuggingFace
                # Usamos um modelo multilíngue que funciona bem com português
                self.model = TextEmbedding(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
                print("[RAG] Modelo FastEmbed carregado: paraphrase-multilingual-MiniLM-L12-v2")
            except Exception as e:
                print(f"[WARNING] Erro ao carregar modelo multilíngue: {e}")
                print("Tentando modelo alternativo BGE-small...")
                try:
                    # Fallback para modelo BGE (inglês mas funciona para português também)
                    self.model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
                    print("[RAG] Modelo FastEmbed carregado: BAAI/bge-small-en-v1.5")
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
    
    def _clean_text(self, text: str) -> str:
        """Remove ruído comum de PDFs (URLs, headers repetidos, etc.)."""
        if not text:
            return ""
        
        # Remover URLs
        text = re.sub(r'https?://[^\s]+', '', text)
        text = re.sub(r'www\.[^\s]+', '', text)
        
        # Remover padrões comuns de lixo de PDFs baixados da web
        noise_patterns = [
            r'Privacy\s*',
            r'\d{2}/\d{2}/\d{2},?\s*\d{2}:\d{2}',  # Timestamps
            r'vebuka\.com[^\n]*',
            r'pdfcoffee\.com[^\n]*',
            r'\| V\s*ebuka\.com',
            r'Past_Life_Astrology[^a-zA-Z]*Use[^a-zA-Z]*Y\s*our[^a-zA-Z]*Birthchart[^a-zA-Z]*to[^a-zA-Z]*Understand[^a-zA-Z]*Y\s*our[^a-zA-Z]*Karma',
            r'Past Life Astrology - Use Y our Birthchart to Understand Y our Karma[^\n]*',
            r'rt to Understand Y our Karma[^\n]*',
            r'IndirectObject\([^)]+\)',
            r'unknown widths\s*:',
            r'incorrect startxref pointer\(\d+\)',
            r'\d{1,4}/\d{2,3}',  # Page numbers like 7/162
            r'^\s*\d+\s*$',  # Lines with only numbers
            r'11311-97edb49441f73951004f36555620cc64[^\n]*',  # Hash específico
            r'1071[^\n]*11311[^\n]*',  # Padrão específico do PDF problemático
        ]
        
        for pattern in noise_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.MULTILINE)
        
        # Remover linhas que são apenas números ou muito curtas
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            # Ignorar linhas que são apenas números, muito curtas, ou repetitivas
            if len(line) < 15:
                continue
            if re.match(r'^[\d\s\-\./]+$', line):
                continue
            if line.lower() in ['privacy', 'copyright', 'all rights reserved', 'y our']:
                continue
            # Ignorar linhas que são apenas repetições de títulos
            if 'Past Life Astrology' in line and len(line) < 100:
                continue
            cleaned_lines.append(line)
        
        text = '\n'.join(cleaned_lines)
        
        # Remover múltiplos espaços e quebras de linha
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()

    def extract_text_from_pdf(self, pdf_path: Path) -> List[Dict[str, any]]:
        """Extrai texto de um PDF e retorna lista de chunks com metadados."""
        chunks = []
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                
                # Acumular texto do documento inteiro para melhor contexto
                full_text = ""
                page_boundaries = []  # Guardar onde cada página começa
                
                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    
                    if text.strip():
                        # Limpar texto antes de adicionar
                        clean_text = self._clean_text(text)
                        if clean_text and len(clean_text) > 50:
                            page_boundaries.append((len(full_text), page_num + 1))
                            full_text += clean_text + "\n\n"
                
                if full_text.strip():
                    # Chunks maiores para melhor contexto semântico (1000 chars com 200 overlap)
                    chunk_size = 1000
                    chunk_overlap = 200
                    
                    # Tentar quebrar em sentenças/parágrafos para não cortar ideias
                    paragraphs = re.split(r'\n\s*\n', full_text)
                    current_chunk = ""
                    current_page = 1
                    
                    for para in paragraphs:
                        para = para.strip()
                        if not para or len(para) < 50:  # Ignorar parágrafos muito curtos
                            continue
                        
                        # Encontrar página deste parágrafo
                        for boundary_pos, page_num in reversed(page_boundaries):
                            if full_text.find(para) >= boundary_pos:
                                current_page = page_num
                                break
                        
                        # Se adicionar o parágrafo excede o tamanho, salvar chunk atual
                        if len(current_chunk) + len(para) > chunk_size and current_chunk:
                            clean_chunk = current_chunk.strip()
                            if len(clean_chunk) > 100:  # Só salvar chunks substanciais
                                chunks.append({
                                    'text': clean_chunk,
                                    'source': pdf_path.name,
                                    'page': current_page,
                                    'chunk_index': len(chunks)
                                })
                            # Manter overlap do final do chunk anterior
                            overlap_start = max(0, len(current_chunk) - chunk_overlap)
                            current_chunk = current_chunk[overlap_start:] + "\n\n" + para
                        else:
                            current_chunk = (current_chunk + "\n\n" + para).strip()
                    
                    # Salvar último chunk
                    if current_chunk and len(current_chunk.strip()) > 100:
                        chunks.append({
                            'text': current_chunk.strip(),
                            'source': pdf_path.name,
                            'page': current_page,
                            'chunk_index': len(chunks)
                        })
                        
        except Exception as e:
            print(f"[ERROR] Erro ao processar {pdf_path.name}: {e}")
        
        return chunks
    
    def extract_text_from_markdown(self, md_path: Path) -> List[Dict[str, any]]:
        """Extrai texto de um arquivo Markdown e retorna lista de chunks com metadados."""
        chunks = []
        
        try:
            with open(md_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            if content.strip():
                # Dividir por seções (##, ###, etc.)
                sections = re.split(r'\n(?=#{1,3}\s)', content)
                
                for i, section in enumerate(sections):
                    section = section.strip()
                    if section and len(section) > 50:  # Ignorar seções muito curtas
                        # Remover marcações excessivas de formatação
                        clean_section = section
                        # Manter headers mas limpar formatação excessiva
                        clean_section = re.sub(r'\*\*([^*]+)\*\*', r'\1', clean_section)  # Remove bold
                        clean_section = re.sub(r'\*([^*]+)\*', r'\1', clean_section)  # Remove italic
                        clean_section = re.sub(r'`([^`]+)`', r'\1', clean_section)  # Remove code
                        clean_section = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', clean_section)  # Remove links
                        
                        chunks.append({
                            'text': clean_section,
                            'source': md_path.name,
                            'page': i + 1,  # Usar número da seção como "página"
                            'chunk_index': len(chunks)
                        })
        except Exception as e:
            print(f"[ERROR] Erro ao processar {md_path.name}: {e}")
        
        return chunks

    def process_all_pdfs(self) -> int:
        """Processa todos os PDFs e Markdowns na pasta docs e cria o índice."""
        if not HAS_DEPENDENCIES:
            raise RuntimeError("Dependências RAG não disponíveis. Instale: pip install fastembed PyPDF2")
        if not self.model:
            raise RuntimeError("Modelo de embeddings não carregado. Verifique as dependências.")
        
        if not self.docs_path.exists():
            raise FileNotFoundError(f"Pasta de documentos não encontrada: {self.docs_path}")
        
        print(f"[RAG] Processando documentos em {self.docs_path}...")
        
        all_chunks = []
        
        # Processar PDFs
        pdf_files = list(self.docs_path.glob("*.pdf"))
        print(f"[RAG] Encontrados {len(pdf_files)} arquivos PDF")
        
        for pdf_path in pdf_files:
            print(f"[RAG] Processando PDF: {pdf_path.name}...")
            chunks = self.extract_text_from_pdf(pdf_path)
            all_chunks.extend(chunks)
            print(f"  → {len(chunks)} chunks extraídos")
        
        # Processar Markdowns
        md_files = list(self.docs_path.glob("*.md"))
        print(f"[RAG] Encontrados {len(md_files)} arquivos Markdown")
        
        for md_path in md_files:
            print(f"[RAG] Processando MD: {md_path.name}...")
            chunks = self.extract_text_from_markdown(md_path)
            all_chunks.extend(chunks)
            print(f"  → {len(chunks)} chunks extraídos")
        
        if not all_chunks:
            print("[WARNING] Nenhum texto extraído dos documentos")
            return 0
        
        print(f"[RAG] Total de chunks de todos os documentos: {len(all_chunks)}")
        print(f"[RAG] Criando embeddings com FastEmbed...")
        
        # Extrair textos para embeddings
        texts = [chunk['text'] for chunk in all_chunks]
        
        # Criar embeddings usando FastEmbed
        # FastEmbed retorna um generator, convertemos para lista de numpy arrays
        embeddings_list = list(self.model.embed(texts))
        # Converter lista de arrays em matriz numpy
        self.embeddings = np.array(embeddings_list)
        
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
    
    def search(self, query: str, top_k: int = 5, expand_query: bool = False) -> List[Dict[str, any]]:
        """
        Busca documentos relevantes para a query.
        
        Args:
            query: Texto da consulta
            top_k: Número de resultados a retornar
            expand_query: Se True, faz múltiplas buscas com variações da query
        
        Returns:
            Lista de documentos relevantes com metadados e score de similaridade
        """
        if not HAS_DEPENDENCIES:
            raise RuntimeError("Dependências RAG não disponíveis. Instale: pip install fastembed PyPDF2")
        
        if not self.model:
            raise RuntimeError("Modelo de embeddings não carregado. Verifique as dependências.")
        
        if self.embeddings is None or len(self.documents) == 0:
            raise ValueError("Índice não carregado. Execute load_index() ou process_all_pdfs() primeiro.")
        
        all_results = {}
        
        # Busca principal
        queries = [query]
        
        # Expandir query se solicitado
        if expand_query:
            # Criar variações da query
            query_lower = query.lower()
            
            # Adicionar termos relacionados
            if 'sinastria' in query_lower or 'compatibilidade' in query_lower:
                # Para sinastria, buscar por cada signo individualmente
                signos = ['Áries', 'Touro', 'Gêmeos', 'Câncer', 'Leão', 'Virgem', 
                         'Libra', 'Escorpião', 'Sagitário', 'Capricórnio', 'Aquário', 'Peixes']
                for signo in signos:
                    if signo.lower() in query_lower:
                        queries.append(f"{signo} características personalidade relacionamento")
                        queries.append(f"{signo} em relacionamentos compatibilidade")
            
            # Adicionar termos genéricos relacionados
            if 'planeta' in query_lower or any(p in query_lower for p in ['sol', 'lua', 'marte', 'venus', 'jupiter', 'saturno']):
                queries.append(f"{query} significado astrologia")
                queries.append(f"{query} interpretação mapa astral")
            
            if 'casa' in query_lower:
                queries.append(f"{query} área vida significado")
                queries.append(f"{query} interpretação astrológica")
            
            if 'aspecto' in query_lower:
                queries.append(f"{query} relação planetas")
                queries.append(f"{query} dinâmica astrológica")
        
        # Buscar com cada variação da query
        for q in queries:
            try:
                # Criar embedding da query usando FastEmbed
                query_embeddings_list = list(self.model.embed([q]))
                query_embedding = np.array(query_embeddings_list)
                
                # Calcular similaridade de cosseno
                similarities = cosine_similarity(query_embedding, self.embeddings)[0]
                
                # Obter top_k resultados para esta query
                top_indices = np.argsort(similarities)[::-1][:top_k * 2]  # Buscar mais para depois filtrar
                
                for idx in top_indices:
                    score = float(similarities[idx])
                    # Usar índice como chave única
                    result_key = idx
                    
                    # Manter o melhor score para cada documento
                    if result_key not in all_results or score > all_results[result_key]['score']:
                        all_results[result_key] = {
                            'text': self.documents[idx],
                            'score': score,
                            'source': self.metadata[idx]['source'],
                            'page': self.metadata[idx]['page'],
                            'chunk_index': self.metadata[idx]['chunk_index']
                        }
            except Exception as e:
                print(f"[RAG] Erro ao buscar com query '{q}': {e}")
                continue
        
        # Ordenar por score e retornar top_k
        sorted_results = sorted(all_results.values(), key=lambda x: x['score'], reverse=True)
        
        # Remover duplicatas muito similares (mesmo texto)
        unique_results = []
        seen_texts = set()
        for result in sorted_results:
            # Normalizar texto para comparação
            text_normalized = result['text'][:200].lower().strip()
            if text_normalized not in seen_texts:
                seen_texts.add(text_normalized)
                unique_results.append(result)
                if len(unique_results) >= top_k:
                    break
        
        return unique_results[:top_k]
    
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
        
        # Preparar contexto dos documentos (sem informações de fonte)
        context_text = "\n\n".join([
            doc.get('text', '')
            for doc in context_documents
            if doc.get('text')
        ])
        
        # Se não há contexto, criar contexto mínimo para sinastria
        if not context_text or len(context_text.strip()) < 50:
            if is_synastry_query:
                # Extrair signos da query
                sign1_match = None
                sign2_match = None
                query_lower_for_context = query.lower()
                for sign_name in ['Áries', 'Touro', 'Gêmeos', 'Câncer', 'Leão', 'Virgem', 
                                 'Libra', 'Escorpião', 'Sagitário', 'Capricórnio', 'Aquário', 'Peixes']:
                    if sign_name.lower() in query_lower_for_context:
                        if not sign1_match:
                            sign1_match = sign_name
                        elif not sign2_match and sign_name != sign1_match:
                            sign2_match = sign_name
                            break
                
                if sign1_match and sign2_match:
                    context_text = f"""
Análise de compatibilidade astrológica entre {sign1_match} e {sign2_match}.

{sign1_match} e {sign2_match} são signos do zodíaco com características distintas. A sinastria analisa como essas características interagem em relacionamentos, revelando pontos de conexão, desafios e potencial de crescimento conjunto.

Cada signo traz suas próprias necessidades, valores e formas de expressão. A compatibilidade depende de como esses elementos se complementam ou se desafiam mutuamente.
"""
                else:
                    context_text = "Análise de compatibilidade astrológica entre signos do zodíaco, focando em dinâmicas de relacionamento, comunicação, valores e objetivos de vida."
        
        # Detectar se é consulta sobre regente do mapa
        is_chart_ruler_query = any(phrase in query.lower() for phrase in [
            'regente do mapa', 'regente do ascendente', 'planeta regente', 
            'chart ruler', 'ruler of', 'ascendant ruler'
        ])
        
        # Detectar se é consulta sobre sinastria/compatibilidade
        is_synastry_query = any(phrase in query.lower() for phrase in [
            'sinastria', 'synastry', 'compatibilidade', 'compatibility', 
            'relacionamento', 'relationship', 'casal', 'couple'
        ])
        
        # Prompt específico para sinastria/compatibilidade
        if is_synastry_query:
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
            
            # Extrair signos da query para contexto
            sign1_match = None
            sign2_match = None
            query_lower_for_signs = query.lower()
            for sign_name in ['Áries', 'Touro', 'Gêmeos', 'Câncer', 'Leão', 'Virgem', 
                             'Libra', 'Escorpião', 'Sagitário', 'Capricórnio', 'Aquário', 'Peixes']:
                if sign_name.lower() in query_lower_for_signs:
                    if not sign1_match:
                        sign1_match = sign_name
                    elif not sign2_match and sign_name != sign1_match:
                        sign2_match = sign_name
                        break
            
            # Se não há contexto do RAG, criar contexto mínimo baseado nos signos
            if not context_snippet or len(context_snippet.strip()) < 100:
                if sign1_match and sign2_match:
                    context_snippet = f"""
Informações sobre os signos {sign1_match} e {sign2_match}:

{sign1_match} é um signo do zodíaco com características específicas que influenciam a personalidade e o comportamento em relacionamentos.

{sign2_match} é outro signo do zodíaco com suas próprias características e necessidades em relacionamentos.

A compatibilidade entre signos analisa como essas características interagem, criando dinâmicas únicas de atração, complementaridade e desafios.
"""
                else:
                    context_snippet = "Informações gerais sobre compatibilidade astrológica e análise de relacionamentos entre signos do zodíaco."
            
            user_prompt = f"""SINASTRIA / COMPATIBILIDADE:

Consulta: {query}
{f"Signos analisados: {sign1_match} + {sign2_match}" if (sign1_match and sign2_match) else ""}

CONHECIMENTO ASTROLÓGICO DE REFERÊNCIA:
{context_snippet}

---

INSTRUÇÕES:
Crie uma interpretação COMPLETA, PRÁTICA e DIDÁTICA sobre a compatibilidade entre os signos mencionados na consulta. A interpretação DEVE ser útil para pessoas em relacionamentos reais.

Estruture a interpretação explicando:

1. **Dinâmica Geral do Relacionamento** (1 parágrafo):
   - Como os signos interagem entre si
   - Energia geral da combinação
   - Potencial de conexão e atração

2. **Pontos Fortes e Complementaridade** (1 parágrafo):
   - O que cada signo traz de positivo para o relacionamento
   - Como se complementam
   - Áreas onde há harmonia natural

3. **Desafios e Áreas de Atenção** (1 parágrafo):
   - Diferenças que podem gerar tensão
   - Estilos de comunicação que podem conflitar
   - Valores ou prioridades que podem diferir

4. **Orientações Práticas** (1 parágrafo):
   - Como melhorar a comunicação
   - Dicas para navegar diferenças
   - Formas de fortalecer o relacionamento

IMPORTANTE:
- Escreva NO MÍNIMO 4 parágrafos completos e práticos
- Use linguagem didática, atual e aplicável ao dia a dia
- Foque em dinâmicas reais de relacionamento
- Seja específico sobre comunicação, valores, intimidade e objetivos
- Use títulos em negrito quando apropriado (formato markdown **texto**)
- Baseie-se no conhecimento astrológico geral sobre os signos mencionados
- Seja criativo e prático, mesmo sem documentos específicos de referência

Formate a resposta de forma didática, usando quebras de linha e estruturação adequada para facilitar a leitura."""
        
        # Prompt específico para regente do mapa (mais detalhado)
        elif is_chart_ruler_query:
            system_prompt = """Você é um astrólogo experiente especializado em interpretação de regentes do mapa astral. 
Sua função é criar interpretações PROFUNDAS, DETALHADAS e DIDÁTICAS sobre o planeta regente do mapa, explicando sua importância fundamental para o autoconhecimento.

REGRAS DE FORMATAÇÃO:
- Sempre escreva NO MÍNIMO 2 parágrafos completos e densos sobre o regente
- Use estrutura didática com títulos em negrito quando apropriado (formato: **TÍTULO:**)
- Explique termos astrológicos de forma simples
- Conecte as informações de forma narrativa, não apenas listas
- Foque na importância do regente para autoconhecimento e desenvolvimento pessoal
- Explique como o regente influencia personalidade, energia vital e comportamento
- Conecte o regente com o signo ascendente e sua posição no mapa

ESTRUTURA RECOMENDADA:
1. Explicação sobre o que significa ter esse planeta como regente (1-2 parágrafos)
2. Como o regente influencia a personalidade e energia vital (1-2 parágrafos)
3. A importância do regente para autoconhecimento e desenvolvimento (1 parágrafo)
4. Como o regente revela forças naturais e áreas de atenção (1 parágrafo)

IMPORTANTE: O texto deve ter NO MÍNIMO 2 parágrafos completos e densos."""
            
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
5. A relação entre o regente e o signo ascendente

IMPORTANTE:
- Escreva NO MÍNIMO 2 parágrafos completos e densos
- Use linguagem didática e acessível
- Conecte as informações de forma narrativa
- Explique a importância fundamental do regente para o autoconhecimento
- Baseie-se nos documentos de referência fornecidos acima
- Use títulos em negrito quando apropriado (formato markdown **texto**)

Formate a resposta de forma didática, usando quebras de linha e estruturação adequada para facilitar a leitura."""
        else:
            # Prompt padrão para outras consultas
            system_prompt = """Você é um astrólogo especialista com profundo conhecimento em astrologia tradicional, cármica e preditiva.

MISSÃO: Criar interpretações astrológicas PRECISAS, COMPLETAS e DIDÁTICAS baseadas nos documentos fornecidos.

ESTRUTURA OBRIGATÓRIA da interpretação (formatação didática):
1. **PASSADO/KARMA**: 
   - O que essa configuração indica sobre padrões herdados, vidas passadas, condicionamentos e lições que a alma traz
   - Use parágrafos claros e separados por quebras de linha duplas (\n\n)
   - Se houver múltiplos pontos, use listas com marcadores (- ou •)

2. **PRESENTE/ESSÊNCIA**: 
   - Como essa energia se manifesta AGORA na personalidade, comportamentos, talentos e desafios atuais
   - Seja específico sobre características pessoais e padrões de comportamento
   - Use exemplos práticos quando possível

3. **FUTURO/EVOLUÇÃO**: 
   - Para onde os astros estão inclinando - tendências, oportunidades de crescimento, direcionamentos e potenciais a desenvolver
   - Inclua orientações práticas e direcionamentos claros

FORMATAÇÃO DIDÁTICA OBRIGATÓRIA:
- Use títulos em negrito para seções principais (formato: **TÍTULO:**)
- Separe parágrafos com quebras de linha duplas (\n\n)
- Use listas com marcadores (- ou •) para múltiplos pontos
- Títulos de seções devem terminar com dois pontos (:)
- Cada seção deve ter pelo menos um parágrafo completo
- Use linguagem clara, profunda e acessível
- Evite jargões técnicos sem explicação

REGRAS:
- Use APENAS os documentos como base factual
- Conecte passado → presente → futuro de forma fluida
- Seja específico e prático, não genérico
- NÃO mencione fontes, páginas ou referências aos documentos
- NÃO repita a query ou o tema da consulta no início da resposta
- Mínimo 3 parágrafos principais (um para cada dimensão temporal)
- Formate o texto de forma organizada e fácil de ler"""
            
            user_prompt = f"""TEMA DA CONSULTA: {query}

CONHECIMENTO ASTROLÓGICO DISPONÍVEL:
{context_text}

INSTRUÇÕES:
1. Crie uma interpretação astrológica completa seguindo a estrutura PASSADO → PRESENTE → FUTURO
2. Formate o texto de forma DIDÁTICA e ORGANIZADA:
   - Use títulos em negrito para cada seção principal (formato: **PASSADO/KARMA:**)
   - Separe parágrafos com quebras de linha duplas
   - Use listas com marcadores (- ou •) para múltiplos pontos
   - Cada seção deve ter pelo menos um parágrafo completo
3. Seja preciso, profundo e útil para quem busca autoconhecimento e orientação
4. NÃO repita o tema da consulta no início da resposta
5. Comece diretamente com a interpretação do PASSADO/KARMA

IMPORTANTE: O texto deve ser formatado de forma clara e didática, usando quebras de linha e estruturação adequada para facilitar a leitura."""
        
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
                model="llama-3.1-8b-instant",  # Modelo rápido e disponível
                temperature=0.7,  # Balanceado entre criatividade e precisão
                max_tokens=2500 if (is_chart_ruler_query or is_synastry_query) else 2000,  # Mais tokens para regente do mapa e sinastria
                top_p=0.9,
            )
            
            interpretation = chat_completion.choices[0].message.content
            
            # Log da interpretação original para debug
            print(f"[RAG] Interpretação original do Groq (tamanho: {len(interpretation) if interpretation else 0} chars)")
            if interpretation:
                print(f"[RAG] Primeiros 500 chars da interpretação original: {interpretation[:500]}")
            
            # Verificar se a interpretação não está vazia ou é apenas a query
            if not interpretation:
                print(f"[RAG] Aviso: Groq retornou interpretação vazia")
                raise ValueError("Interpretação vazia retornada pelo Groq")
            
            # Remover possíveis referências à query no início da resposta
            interpretation_clean = interpretation.strip()
            
            # Limpeza menos agressiva: remover apenas linhas específicas que são claramente cabeçalhos
            lines = interpretation_clean.split('\n')
            filtered_lines = []
            skip_next = False
            
            for i, line in enumerate(lines):
                line_lower = line.lower().strip()
                
                # Ignorar apenas linhas que são claramente cabeçalhos ou referências
                if any(phrase in line_lower for phrase in [
                    'contexto da consulta:',
                    'documentos de referência:',
                    'query:',
                    'consulta:'
                ]):
                    # Se a linha é apenas um cabeçalho, pular ela e a próxima linha se for vazia ou a query
                    skip_next = True
                    continue
                
                # Se estamos pulando e a linha é vazia ou é exatamente a query, pular
                if skip_next:
                    if not line.strip() or line.strip() == query.strip():
                        skip_next = False
                        continue
                    skip_next = False
                
                filtered_lines.append(line)
            
            interpretation_clean = '\n'.join(filtered_lines).strip()
            
            print(f"[RAG] Interpretação após primeira limpeza (tamanho: {len(interpretation_clean)} chars)")
            
            # Se após limpeza ficou muito curta, usar a versão original com limpeza mínima
            if len(interpretation_clean) < 100:
                print(f"[RAG] Aviso: Interpretação muito curta após limpeza ({len(interpretation_clean)} chars), usando versão original com limpeza mínima")
                # Limpeza mínima: apenas remover referências explícitas a fontes
                interpretation_clean = interpretation.strip()
                # Remover apenas padrões muito específicos
                interpretation_clean = interpretation_clean.replace('[Fonte:', '')
                interpretation_clean = re.sub(r'Página \d+', '', interpretation_clean)
                interpretation_clean = interpretation_clean.strip()
            
            # Verificar se ainda há conteúdo válido após limpeza mínima
            if not interpretation_clean or len(interpretation_clean) < 50:
                print(f"[RAG] ERRO: Interpretação ainda muito curta após limpeza mínima: {len(interpretation_clean)} chars")
                print(f"[RAG] Conteúdo original completo: {interpretation}")
                raise ValueError(f"Interpretação muito curta após limpeza: {len(interpretation_clean)} chars")
            
            # Verificar se não é apenas a query (validação mais flexível)
            query_words = set(query.lower().split())
            interpretation_words = set(interpretation_clean.lower().split())
            # Se mais de 80% das palavras da query estão na interpretação E a interpretação é muito curta
            if len(query_words) > 0:
                matching_words = query_words.intersection(interpretation_words)
                similarity = len(matching_words) / len(query_words)
                if similarity > 0.8 and len(interpretation_clean) < 150:
                    print(f"[RAG] Aviso: Interpretação parece ser apenas a query (similaridade: {similarity:.2f})")
                    # Mesmo assim, se tiver algum conteúdo, usar
                    if len(interpretation_clean) < 50:
                        raise ValueError("Interpretação muito similar à query retornada pelo Groq")
            
            print(f"[RAG] Interpretação final gerada pelo Groq (tamanho: {len(interpretation_clean)} chars, primeiros 200 chars): {interpretation_clean[:200]}...")
            return interpretation_clean
            
        except Exception as e:
            print(f"[ERROR] Erro ao gerar interpretação com Groq: {e}")
            import traceback
            print(f"[ERROR] Traceback completo: {traceback.format_exc()}")
            # Fallback: retornar documentos sem processamento
            raise
    
    def get_interpretation(
        self,
        planet: Optional[str] = None,
        sign: Optional[str] = None,
        house: Optional[int] = None,
        aspect: Optional[str] = None,
        custom_query: Optional[str] = None,
        use_groq: bool = True,
        top_k: int = 8  # Adicionar parâmetro para controlar número de documentos
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
        # Construir query enriquecida baseada nos parâmetros
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
        
        # Identificar se é uma consulta sobre temas específicos para buscar mais contexto
        query_lower = query.lower()
        is_karma_query = any(word in query_lower for word in ['nodo', 'karma', 'carma', 'passado', 'vidas passadas', 'retrógrado'])
        is_transit_query = any(word in query_lower for word in ['trânsito', 'transito', 'futuro', 'previsão', 'tendência'])
        is_aspect_query = any(word in query_lower for word in ['aspecto', 'conjunção', 'oposição', 'trígono', 'quadratura', 'sextil'])
        
        # Buscar mais documentos para ter contexto suficiente
        # Queries mais complexas precisam de mais contexto
        if is_karma_query or is_transit_query:
            top_k = 20  # Mais contexto para temas de karma e trânsitos
        elif is_aspect_query:
            top_k = 15
        elif is_synastry_query:
            top_k = 18  # Mais contexto para sinastria
        else:
            top_k = 12  # Aumentado de 8 para 12
        
        results: List[Dict[str, any]] = []
        try:
            # Usar busca expandida para coletar mais informações
            results = self.search(query, top_k=top_k, expand_query=True)
            print(f"[RAG] Busca expandida retornou {len(results)} resultados para query: {query[:100]}")
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
        
        # Para sinastria, mesmo sem resultados do RAG, tentar gerar com Groq usando conhecimento geral
        if is_synastry_query and not results and use_groq and self.groq_client:
            print(f"[RAG] Sinastria sem resultados do RAG, tentando gerar com Groq usando conhecimento geral")
            try:
                # Criar contexto mínimo baseado nos signos mencionados
                sign1_match = None
                sign2_match = None
                for sign_name in ['Áries', 'Touro', 'Gêmeos', 'Câncer', 'Leão', 'Virgem', 
                                 'Libra', 'Escorpião', 'Sagitário', 'Capricórnio', 'Aquário', 'Peixes']:
                    if sign_name.lower() in query_lower:
                        if not sign1_match:
                            sign1_match = sign_name
                        elif not sign2_match and sign_name != sign1_match:
                            sign2_match = sign_name
                            break
                
                # Buscar informações sobre os signos individualmente
                sign_contexts = []
                if sign1_match:
                    sign1_context = _local_knowledge_base.get_context(sign=sign1_match, query=query)
                    if sign1_context:
                        sign_contexts.extend(sign1_context)
                if sign2_match:
                    sign2_context = _local_knowledge_base.get_context(sign=sign2_match, query=query)
                    if sign2_context:
                        sign_contexts.extend(sign2_context)
                
                if sign_contexts:
                    results = sign_contexts
                    print(f"[RAG] Usando contexto dos signos individuais para sinastria")
            except Exception as e:
                print(f"[RAG] Erro ao buscar contexto dos signos para sinastria: {e}")
        
        # Tentar usar Groq mesmo sem resultados do RAG (para sinastria e outras consultas)
        if use_groq:
            if not HAS_GROQ:
                # Silenciosamente usar fallback se Groq não estiver instalado
                pass
            elif not self.groq_client:
                # Silenciosamente usar fallback se Groq não estiver configurado
                pass
            else:
                try:
                    # Para sinastria, mesmo sem resultados do RAG, gerar com Groq
                    if is_synastry_query and not results:
                        print(f"[RAG] Gerando sinastria com Groq sem contexto do RAG")
                        # Criar contexto mínimo para o Groq
                        minimal_context = [{
                            'text': f"Informações sobre compatibilidade astrológica entre signos. {query}",
                            'source': 'knowledge_base',
                            'page': 1,
                            'score': 0.5
                        }]
                        interpretation_text = self._generate_with_groq(query, minimal_context)
                    else:
                        interpretation_text = self._generate_with_groq(query, results)
                    
                    return {
                        'interpretation': interpretation_text,
                        'sources': [
                            {
                                'source': r.get('source', 'knowledge_base'),
                                'page': r.get('page', 1),
                                'relevance': r.get('score', 0.5)
                            }
                            for r in (results if results else [])
                        ],
                        'query_used': query,
                        'generated_by': 'groq'
                    }
                except Exception as e:
                    # Log do erro para debug
                    print(f"[RAG] Erro ao gerar interpretação com Groq: {e}")
                    print(f"[RAG] Tipo do erro: {type(e).__name__}")
                    import traceback
                    print(f"[RAG] Traceback: {traceback.format_exc()}")
                    # Continuar para o fallback: retornar documentos sem processamento
                    # Não passar silenciosamente, vamos tentar o fallback
        
        # Fallback: Combinar textos dos resultados sem processamento LLM
        # Remover informações de fonte do texto para manter consistência
        interpretation_text = "\n\n".join([
            r['text'].strip()
            for r in results
            if r.get('text') and len(r['text'].strip()) > 10  # Filtrar textos muito curtos
        ])
        
        # Se não há texto suficiente, tentar fallback específico para sinastria
        if not interpretation_text or len(interpretation_text.strip()) < 50:
            if is_synastry_query:
                # Extrair signos da query
                sign1_match = None
                sign2_match = None
                for sign_name in ['Áries', 'Touro', 'Gêmeos', 'Câncer', 'Leão', 'Virgem', 
                                 'Libra', 'Escorpião', 'Sagitário', 'Capricórnio', 'Aquário', 'Peixes']:
                    if sign_name.lower() in query_lower:
                        if not sign1_match:
                            sign1_match = sign_name
                        elif not sign2_match and sign_name != sign1_match:
                            sign2_match = sign_name
                            break
                
                if sign1_match and sign2_match:
                    # Gerar interpretação básica de sinastria usando Groq mesmo sem RAG
                    if self.groq_client:
                        try:
                            print(f"[RAG] Tentando gerar sinastria {sign1_match} + {sign2_match} com Groq sem RAG")
                            minimal_context = [{
                                'text': f"Compatibilidade astrológica entre signos. {sign1_match} e {sign2_match} são signos do zodíaco com características distintas que podem criar dinâmicas interessantes em relacionamentos.",
                                'source': 'knowledge_base',
                                'page': 1,
                                'score': 0.5
                            }]
                            interpretation_text = self._generate_with_groq(query, minimal_context)
                            if interpretation_text and len(interpretation_text.strip()) > 50:
                                return {
                                    'interpretation': interpretation_text,
                                    'sources': [],
                                    'query_used': query,
                                    'generated_by': 'groq'
                                }
                        except Exception as e:
                            print(f"[RAG] Erro ao gerar sinastria com Groq sem RAG: {e}")
            
            # Se ainda não há interpretação, retornar mensagem
            if not interpretation_text or len(interpretation_text.strip()) < 50:
                return {
                    'interpretation': "Não foi possível encontrar informações suficientes sobre este tema na base de conhecimento. Por favor, tente uma consulta diferente.",
                    'sources': [],
                    'query_used': query,
                    'generated_by': 'none'
                }
        
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

