"""
Serviço RAG (Retrieval-Augmented Generation) usando LlamaIndex e BGE (Hugging Face).
Nova implementação que substituirá a estrutura antiga após validação.
"""

import os
from pathlib import Path
from typing import List, Dict, Optional, Any, TYPE_CHECKING
import re

if TYPE_CHECKING:
    from llama_index.core.node_parser import SentenceSplitter
    from llama_index.core.schema import Document

try:
    from llama_index.core import (
        VectorStoreIndex,
        SimpleDirectoryReader,
        StorageContext,
        load_index_from_storage,
        Settings,
    )
    from llama_index.core.schema import Document
    from llama_index.core.node_parser import SentenceSplitter
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding
    HAS_LLAMAINDEX = True
except ImportError as e:
    HAS_LLAMAINDEX = False
    SentenceSplitter = None  # Define como None quando não disponível
    print(f"[DEBUG] ImportError ao carregar LlamaIndex: {e}")

try:
    from groq import Groq
    HAS_GROQ = True
except ImportError:
    HAS_GROQ = False

from app.services.local_knowledge_base import LocalKnowledgeBase


class RAGServiceLlamaIndex:
    """Serviço RAG usando LlamaIndex e modelo BGE do Hugging Face."""
    
    def __init__(
        self,
        docs_path: str = "docs",
        index_path: str = "rag_index_llamaindex",
        groq_api_key: Optional[str] = None,
        bge_model_name: str = "BAAI/bge-small-en-v1.5"
    ):
        """
        Inicializa o serviço RAG com LlamaIndex.
        
        Args:
            docs_path: Caminho para pasta de documentos
            index_path: Caminho para salvar/carregar o índice
            groq_api_key: Chave API do Groq para geração
            bge_model_name: Nome do modelo BGE do Hugging Face
        """
        self.docs_path = Path(docs_path)
        self.index_path = Path(index_path)
        self.index = None
        self.groq_client = None
        self.bge_model_name = bge_model_name
        
        if not HAS_LLAMAINDEX:
            print("[WARNING] LlamaIndex não instalado. Instale com: pip install llama-index llama-index-embeddings-huggingface")
            return
        
        # Configurar modelo de embeddings BGE
        try:
            print(f"[RAG-LlamaIndex] Carregando modelo BGE: {bge_model_name}")
            embed_model = HuggingFaceEmbedding(
                model_name=bge_model_name,
                trust_remote_code=True
            )
            Settings.embed_model = embed_model
            print(f"[RAG-LlamaIndex] Modelo BGE carregado com sucesso")
        except Exception as e:
            print(f"[ERROR] Erro ao carregar modelo BGE: {e}")
            print(f"[RAG-LlamaIndex] Tentando modelo alternativo...")
            try:
                # Fallback para modelo multilíngue
                embed_model = HuggingFaceEmbedding(
                    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
                    trust_remote_code=True
                )
                Settings.embed_model = embed_model
                self.bge_model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
                print(f"[RAG-LlamaIndex] Modelo alternativo carregado")
            except Exception as e2:
                print(f"[ERROR] Não foi possível carregar modelo: {e2}")
                raise
        
        # Inicializar cliente Groq se disponível
        if HAS_GROQ:
            if groq_api_key and groq_api_key.strip():
                try:
                    self.groq_client = Groq(api_key=groq_api_key.strip())
                    print("[RAG-LlamaIndex] Cliente Groq inicializado com sucesso")
                except Exception as e:
                    print(f"[WARNING] Erro ao inicializar Groq: {e}")
                    self.groq_client = None
            else:
                print("[WARNING] GROQ_API_KEY não configurada. Funcionalidades com Groq estarão desabilitadas.")
                self.groq_client = None
    
    def _clean_text(self, text: str) -> str:
        """Remove ruído comum de PDFs (mesma lógica da implementação antiga)."""
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
        """
        Detecta a categoria do documento pelo prefixo do arquivo ou pela pasta.
        
        Args:
            filename: Nome do arquivo
            folder_path: Caminho da pasta onde o arquivo está
            
        Returns:
            'astrology' ou 'numerology'
        """
        filename_lower = filename.lower()
        folder_str = str(folder_path).lower()
        
        # Prioridade 1: Verificar prefixo do arquivo
        if filename_lower.startswith('num_'):
            return 'numerology'
        elif filename_lower.startswith('ast_'):
            return 'astrology'
        
        # Prioridade 2: Verificar se está na pasta numerologia
        if 'numerologia' in folder_str:
            return 'numerology'
        
        # Default: astrologia (pasta docs)
        return 'astrology'
    
    def _process_folder(
        self, 
        folder_path: Path, 
        node_parser: "SentenceSplitter",
        documents: List
    ) -> None:
        """
        Processa todos os documentos (PDFs e Markdowns) de uma pasta específica.
        
        Args:
            folder_path: Caminho da pasta a processar
            node_parser: Parser de nós para chunking
            documents: Lista de documentos para adicionar os processados
        """
        if not folder_path.exists():
            print(f"[RAG-LlamaIndex] Pasta não encontrada: {folder_path}")
            return
        
        folder_name = folder_path.name
        print(f"[RAG-LlamaIndex] Processando pasta: {folder_name}...")
        
        # Processar PDFs
        pdf_files = list(folder_path.glob("*.pdf"))
        print(f"[RAG-LlamaIndex] Encontrados {len(pdf_files)} arquivos PDF em {folder_name}")
        
        for pdf_path in pdf_files:
            print(f"[RAG-LlamaIndex] Processando PDF: {pdf_path.name}...")
            try:
                category = self._detect_category(pdf_path.name, folder_path)
                
                reader = SimpleDirectoryReader(
                    input_files=[str(pdf_path)],
                    file_metadata=lambda filename: {
                        'source': Path(filename).name,
                        'file_type': 'pdf',
                        'category': category
                    }
                )
                pdf_docs = reader.load_data()
                
                # Limpar texto e garantir categoria nos metadados
                # Criar novos documentos com texto limpo (Document.text é read-only)
                cleaned_docs = []
                for doc in pdf_docs:
                    cleaned_text = self._clean_text(doc.text if hasattr(doc, 'text') else str(doc))
                    
                    # Criar novo documento com texto limpo
                    new_doc = Document(
                        text=cleaned_text,
                        metadata={
                            'source': pdf_path.name,
                            'file_type': 'pdf',
                            'category': category,
                            **(doc.metadata if hasattr(doc, 'metadata') and doc.metadata else {})
                        }
                    )
                    cleaned_docs.append(new_doc)
                
                documents.extend(cleaned_docs)
                print(f"  → {len(pdf_docs)} documentos extraídos (categoria: {category})")
            except Exception as e:
                print(f"[ERROR] Erro ao processar {pdf_path.name}: {e}")
        
        # Processar Markdowns
        md_files = list(folder_path.glob("*.md"))
        print(f"[RAG-LlamaIndex] Encontrados {len(md_files)} arquivos Markdown em {folder_name}")
        
        for md_path in md_files:
            print(f"[RAG-LlamaIndex] Processando MD: {md_path.name}...")
            try:
                with open(md_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if content.strip():
                    category = self._detect_category(md_path.name, folder_path)
                    
                    doc = Document(
                        text=content,
                        metadata={
                            'source': md_path.name,
                            'file_type': 'markdown',
                            'category': category
                        }
                    )
                    documents.append(doc)
                    print(f"  → 1 documento extraído (categoria: {category})")
            except Exception as e:
                print(f"[ERROR] Erro ao processar {md_path.name}: {e}")
    
    def process_all_documents(self) -> int:
        """
        Processa todos os documentos (PDFs e Markdowns) de ambas as pastas
        (docs para astrologia e numerologia para numerologia) e cria o índice.
        
        Returns:
            Número de chunks processados
        """
        if not HAS_LLAMAINDEX:
            raise RuntimeError("LlamaIndex não disponível. Instale: pip install llama-index llama-index-embeddings-huggingface")
        
        if not self.docs_path.exists():
            raise FileNotFoundError(f"Pasta de documentos não encontrada: {self.docs_path}")
        
        # Definir pastas
        docs_path = Path(self.docs_path)  # Pasta docs (astrologia)
        numerologia_path = docs_path.parent / "numerologia"  # Pasta numerologia
        
        print(f"[RAG-LlamaIndex] Processando documentos em {docs_path} e {numerologia_path}...")
        
        # Configurar parser de nós com chunking otimizado
        node_parser = SentenceSplitter(
            chunk_size=1000,
            chunk_overlap=200,
        )
        
        # Ler documentos
        documents = []
        
        # Processar pasta docs (astrologia)
        self._process_folder(docs_path, node_parser, documents)
        
        # Processar pasta numerologia (se existir)
        if numerologia_path.exists():
            self._process_folder(numerologia_path, node_parser, documents)
        else:
            print(f"[RAG-LlamaIndex] Pasta numerologia não encontrada: {numerologia_path}")
        
        if not documents:
            print("[WARNING] Nenhum documento processado")
            return 0
        
        # Estatísticas por categoria
        categories_count = {}
        for doc in documents:
            category = doc.metadata.get('category', 'astrology') if hasattr(doc, 'metadata') and doc.metadata else 'astrology'
            categories_count[category] = categories_count.get(category, 0) + 1
        
        print(f"[RAG-LlamaIndex] Total de documentos: {len(documents)}")
        for cat, count in categories_count.items():
            print(f"  → {cat}: {count} documentos")
        
        print(f"[RAG-LlamaIndex] Criando índice vetorial com LlamaIndex...")
        
        # Criar nós dos documentos
        nodes = node_parser.get_nodes_from_documents(documents)
        print(f"[RAG-LlamaIndex] Criados {len(nodes)} nós (chunks)")
        
        # Criar índice vetorial
        self.index = VectorStoreIndex(nodes)
        
        print(f"[RAG-LlamaIndex] Índice criado com sucesso!")
        print(f"  → {len(nodes)} nós indexados")
        
        return len(nodes)
    
    def save_index(self):
        """Salva o índice em disco."""
        if self.index is None:
            raise ValueError("Nenhum índice para salvar. Execute process_all_documents() primeiro.")
        
        # Criar diretório se não existir
        self.index_path.mkdir(parents=True, exist_ok=True)
        
        # Salvar índice
        self.index.storage_context.persist(persist_dir=str(self.index_path))
        print(f"[RAG-LlamaIndex] Índice salvo em {self.index_path}")
    
    def load_index(self) -> bool:
        """Carrega o índice do disco."""
        if not HAS_LLAMAINDEX:
            return False
        
        if not self.index_path.exists():
            return False
        
        try:
            # Recriar embed_model para garantir que está configurado
            embed_model = HuggingFaceEmbedding(
                model_name=self.bge_model_name,
                trust_remote_code=True
            )
            Settings.embed_model = embed_model
            
            # Carregar índice
            storage_context = StorageContext.from_defaults(persist_dir=str(self.index_path))
            self.index = load_index_from_storage(storage_context)
            
            print(f"[RAG-LlamaIndex] Índice carregado de {self.index_path}")
            return True
        except Exception as e:
            print(f"[ERROR] Erro ao carregar índice: {e}")
            return False
    
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
            category: Filtrar por categoria ('astrology' ou 'numerology'). 
                     Se None, retorna resultados de todas as categorias.
        
        Returns:
            Lista de documentos relevantes com metadados e score
        """
        if not HAS_LLAMAINDEX:
            # Fallback para base de conhecimento local
            from app.services.local_knowledge_base import LocalKnowledgeBase
            import re
            
            local_kb = LocalKnowledgeBase()
            
            # Tentar extrair planetas e signos da query
            planet = None
            sign = None
            house = None
            
            # Lista de planetas
            planets_list = ['Sol', 'Lua', 'Mercúrio', 'Vênus', 'Marte', 'Júpiter', 'Saturno', 'Urano', 'Netuno', 'Plutão']
            signs_list = ['Áries', 'Touro', 'Gêmeos', 'Câncer', 'Leão', 'Virgem', 'Libra', 'Escorpião', 'Sagitário', 'Capricórnio', 'Aquário', 'Peixes']
            
            query_lower = query.lower()
            
            # Procurar planetas na query
            for p in planets_list:
                if p.lower() in query_lower or local_kb.normalize_planet(p).lower() in query_lower:
                    planet = p
                    break
            
            # Procurar signos na query
            for s in signs_list:
                if s.lower() in query_lower or local_kb.normalize_sign(s).lower() in query_lower:
                    sign = s
                    break
            
            # Procurar casas (casa 1, casa 2, etc.)
            house_match = re.search(r'casa\s+(\d+)', query_lower)
            if house_match:
                house = int(house_match.group(1))
            
            # Buscar contexto com informações extraídas
            context = local_kb.get_context(
                planet=planet,
                sign=sign,
                house=house,
                query=query if not planet and not sign else None
            )
            
            # Converter para formato esperado
            results = []
            for i, ctx in enumerate(context[:top_k]):
                results.append({
                    'text': ctx.get('text', ''),
                    'source': ctx.get('source', 'local_kb'),
                    'page': ctx.get('page', 1),
                    'score': 0.8 - (i * 0.1)  # Score decrescente
                })
            
            # Se não encontrou nada, retornar pelo menos um resultado genérico
            if not results:
                results.append({
                    'text': f"Informações sobre: {query}. Para interpretações completas, instale o LlamaIndex e construa o índice RAG.",
                    'source': 'local_kb',
                    'page': 1,
                    'score': 0.5
                })
            
            return results
        
        if self.index is None:
            raise ValueError("Índice não carregado. Execute load_index() ou process_all_documents() primeiro.")
        
        # Usar retriever para obter nós diretamente
        try:
            # Buscar mais resultados se houver filtro de categoria (para garantir top_k após filtro)
            search_top_k = top_k * 3 if category else (top_k * 2 if expand_query else top_k)
            retriever = self.index.as_retriever(similarity_top_k=search_top_k)
            nodes = retriever.retrieve(query)
            
            # Converter nós para formato esperado e filtrar por categoria
            results = []
            for node in nodes:
                # Extrair score (similarity score)
                score = node.score if hasattr(node, 'score') else 0.0
                
                # Extrair metadados
                metadata = node.metadata if hasattr(node, 'metadata') else {}
                source = metadata.get('source', 'unknown')
                page = metadata.get('page', 1)
                node_category = metadata.get('category', 'astrology')  # Default para astrologia
                
                # Filtrar por categoria se especificada
                if category and node_category != category:
                    continue
                
                results.append({
                    'text': node.text if hasattr(node, 'text') else str(node),
                    'score': float(score),
                    'source': source,
                    'page': page,
                    'category': node_category,
                    'metadata': metadata
                })
                
                # Limitar resultados após filtro
                if len(results) >= top_k:
                    break
            
            # Ordenar por score (caso não esteja ordenado) e limitar
            results = sorted(results, key=lambda x: x['score'], reverse=True)[:top_k]
            
            if category:
                print(f"[RAG-LlamaIndex] Busca filtrada por categoria '{category}': {len(results)} resultados")
            
            return results
        except Exception as e:
            print(f"[RAG-LlamaIndex] Erro ao buscar: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _generate_with_groq(
        self,
        query: str,
        context_documents: List[Dict[str, Any]],
        category: Optional[str] = None
    ) -> str:
        """
        Gera interpretação usando Groq baseada nos documentos recuperados.
        
        Args:
            query: Query de busca
            context_documents: Documentos recuperados do RAG
            category: 'astrology' ou 'numerology' para ajustar o prompt
        """
        if not self.groq_client:
            raise ValueError("Cliente Groq não disponível")
        
        # Determinar categoria se não especificada
        if category is None:
            # Detectar categoria pelos documentos ou pela query
            doc_categories = [doc.get('category', 'astrology') for doc in context_documents if doc.get('category')]
            if doc_categories:
                category = doc_categories[0]  # Usar categoria do primeiro documento
            else:
                query_lower = query.lower()
                if any(word in query_lower for word in ['numerologia', 'numerology', 'número', 'numero', 'caminho de vida', 'life path']):
                    category = 'numerology'
                else:
                    category = 'astrology'
        
        # Preparar contexto - garantir que todos os documentos sejam da mesma categoria
        filtered_docs = [
            doc for doc in context_documents 
            if doc.get('category', 'astrology') == category
        ]
        
        # Se não houver documentos filtrados, usar todos (mas avisar)
        if not filtered_docs:
            print(f"[WARNING] Nenhum documento da categoria '{category}' encontrado. Usando todos os documentos.")
            filtered_docs = context_documents
        
        context_text = "\n\n".join([
            doc.get('text', '')
            for doc in filtered_docs
            if doc.get('text')
        ])
        
        # Detectar tipo de consulta (apenas para astrologia)
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
        
        # Ajustar prompts baseado na categoria
        if category == 'numerology':
            # Prompt específico para numerologia
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
            # Prompt padrão para outras consultas
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
            
            # Limpeza básica
            if interpretation:
                interpretation = interpretation.strip()
                # Remover referências explícitas a fontes
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
        """
        Obtém interpretação astrológica ou numerológica.
        
        Args:
            category: 'astrology' ou 'numerology' para filtrar resultados.
                     Se None, assume 'astrology' por padrão.
        """
        # Verificar se LlamaIndex está disponível
        if not HAS_LLAMAINDEX:
            # Usar base de conhecimento local como fallback
            from app.services.local_knowledge_base import LocalKnowledgeBase
            local_kb = LocalKnowledgeBase()
            
            # Construir query
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
            
            # Buscar no conhecimento local
            context = local_kb.get_context(
                planet=planet,
                sign=sign,
                house=house,
                query=query
            )
            
            # Gerar interpretação básica
            if context and len(context) > 0:
                context_text = "\n\n".join([ctx.get('text', '') for ctx in context[:3] if ctx.get('text')])
                return {
                    'interpretation': context_text[:1000] if context_text else "Interpretação não disponível sem LlamaIndex.",
                    'sources': [],
                    'query_used': query,
                    'generated_by': 'local_kb'
                }
            else:
                return {
                    'interpretation': f"Interpretação básica: {query}. Para interpretações completas, instale o LlamaIndex.",
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
        
        # Identificar tipo de consulta para ajustar top_k
        query_lower = query.lower()
        is_karma_query = any(word in query_lower for word in ['nodo', 'karma', 'carma', 'passado', 'vidas passadas', 'retrógrado'])
        is_transit_query = any(word in query_lower for word in ['trânsito', 'transito', 'futuro', 'previsão', 'tendência'])
        is_aspect_query = any(word in query_lower for word in ['aspecto', 'conjunção', 'oposição', 'trígono', 'quadratura', 'sextil'])
        is_synastry_query = any(phrase in query_lower for phrase in [
            'sinastria', 'synastry', 'compatibilidade', 'compatibility',
            'relacionamento', 'relationship', 'casal', 'couple'
        ])
        
        # Ajustar top_k baseado no tipo de consulta
        if is_karma_query or is_transit_query:
            top_k = 20
        elif is_aspect_query:
            top_k = 15
        elif is_synastry_query:
            top_k = 18
        else:
            top_k = 12
        
        # Determinar categoria se não especificada
        if category is None:
            # Detectar categoria pela query (padrão: astrologia)
            query_lower = query.lower()
            if any(word in query_lower for word in ['numerologia', 'numerology', 'número', 'numero', 'caminho de vida', 'life path']):
                category = 'numerology'
            else:
                category = 'astrology'  # Default
        
        # Buscar documentos relevantes com filtro de categoria
        results = []
        try:
            results = self.search(query, top_k=top_k, expand_query=True, category=category)
            print(f"[RAG-LlamaIndex] Busca retornou {len(results)} resultados para query: {query[:100]} (categoria: {category})")
        except Exception as e:
            print(f"[RAG-LlamaIndex] Erro na busca: {e}")
        
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
                print(f"[RAG-LlamaIndex] Erro ao gerar com Groq: {e}")
        
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
_rag_service_llamaindex: Optional[RAGServiceLlamaIndex] = None


def get_rag_service_llamaindex() -> RAGServiceLlamaIndex:
    """Obtém instância singleton do serviço RAG com LlamaIndex."""
    global _rag_service_llamaindex
    
    if _rag_service_llamaindex is None:
        from app.core.config import settings
        
        backend_path = Path(__file__).parent.parent.parent
        docs_path = backend_path / "docs"
        index_path = backend_path / "rag_index_llamaindex"
        
        groq_api_key = settings.GROQ_API_KEY if hasattr(settings, 'GROQ_API_KEY') else None
        
        _rag_service_llamaindex = RAGServiceLlamaIndex(
            docs_path=str(docs_path),
            index_path=str(index_path),
            groq_api_key=groq_api_key
        )
        
        # Tentar carregar índice existente
        if not _rag_service_llamaindex.load_index():
            print("[RAG-LlamaIndex] Índice não encontrado. Execute build_rag_index_llamaindex.py para criar.")
    
    return _rag_service_llamaindex

