"""
Serviço RAG para gerar interpretações astrológicas baseadas nos documentos PDF
"""
import os
from typing import List, Dict, Optional
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from app.core.config import settings

class RAGService:
    def __init__(self):
        self.embeddings = None
        self.vectorstore = None
        self.qa_chain = None
        self.initialized = False
        
        if settings.OPENAI_API_KEY:
            self.embeddings = OpenAIEmbeddings(
                openai_api_key=settings.OPENAI_API_KEY,
                model=settings.EMBEDDING_MODEL
            )
    
    def initialize(self):
        """Initialize RAG service with documents"""
        if not settings.OPENAI_API_KEY:
            print("Warning: OpenAI API key not set. RAG will use fallback responses.")
            self.initialized = True
            return
        
        try:
            pdfs_path = settings.PDFS_PATH
            if not os.path.exists(pdfs_path):
                pdfs_path = os.path.join(os.path.dirname(__file__), "../../../pdf")
            
            # Load documents
            documents = []
            
            # Load PDF files
            for filename in os.listdir(pdfs_path):
                if filename.endswith('.pdf'):
                    try:
                        filepath = os.path.join(pdfs_path, filename)
                        loader = PyPDFLoader(filepath)
                        docs = loader.load()
                        documents.extend(docs)
                    except Exception as e:
                        print(f"Error loading {filename}: {e}")
                
                # Load markdown files
                elif filename.endswith('.md'):
                    try:
                        filepath = os.path.join(pdfs_path, filename)
                        loader = TextLoader(filepath, encoding='utf-8')
                        docs = loader.load()
                        documents.extend(docs)
                    except Exception as e:
                        print(f"Error loading {filename}: {e}")
            
            if not documents:
                print("No documents found to load")
                self.initialized = True
                return
            
            # Split documents
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=settings.CHUNK_SIZE,
                chunk_overlap=settings.CHUNK_OVERLAP
            )
            splits = text_splitter.split_documents(documents)
            
            # Create vector store
            persist_directory = "./chroma_db"
            self.vectorstore = Chroma.from_documents(
                documents=splits,
                embedding=self.embeddings,
                persist_directory=persist_directory
            )
            
            # Create QA chain
            llm = ChatOpenAI(
                model=settings.RAG_MODEL,
                temperature=0.7,
                openai_api_key=settings.OPENAI_API_KEY
            )
            
            prompt_template = """Você é um astrólogo experiente e especializado em interpretação de mapas astrológicos. 
Use os documentos fornecidos para criar interpretações precisas e detalhadas.

Contexto dos documentos astrológicos:
{context}

Pergunta do usuário: {question}

Instruções:
- Responda em português brasileiro
- Use apenas informações dos documentos fornecidos
- Seja detalhado e específico
- Use termos técnicos astrológicos corretos
- Estruture a resposta de forma clara e organizada
- Inclua informações sobre significado psicológico e prático

Resposta:"""
            
            PROMPT = PromptTemplate(
                template=prompt_template,
                input_variables=["context", "question"]
            )
            
            # Create retriever
            retriever = self.vectorstore.as_retriever(search_kwargs={"k": 5})
            
            # Create QA chain using LCEL
            def format_docs(docs):
                return "\n\n".join(doc.page_content for doc in docs)
            
            self.qa_chain = (
                {"context": retriever | format_docs, "question": RunnablePassthrough()}
                | PROMPT
                | llm
                | StrOutputParser()
            )
            
            self.initialized = True
            print(f"RAG service initialized with {len(documents)} documents")
            
        except Exception as e:
            print(f"Error initializing RAG service: {e}")
            self.initialized = True  # Mark as initialized to prevent repeated attempts
    
    def get_interpretation(self, query: str, context: Dict = None) -> str:
        """Get interpretation using RAG"""
        if not self.initialized:
            self.initialize()
        
        if not self.qa_chain:
            return self._get_fallback_interpretation(query, context)
        
        try:
            # Add context to query if provided
            if context:
                context_str = f"\nContexto do mapa astral: {self._format_context(context)}"
                full_query = query + context_str
            else:
                full_query = query
            
            result = self.qa_chain.invoke({"question": full_query})
            return result
        except Exception as e:
            print(f"Error getting interpretation: {e}")
            return self._get_fallback_interpretation(query, context)
    
    def get_planet_interpretation(self, planet: str, sign: str, house: int, chart_context: Dict) -> Dict:
        """Get interpretation for a planet in a sign and house"""
        query_in_sign = f"Interpretação de {planet} em {sign}. Explique o significado psicológico, características e influências."
        query_in_house = f"Interpretação de planetas na Casa {house}. Explique o significado e influência desta casa astrológica."
        
        context = {
            "planet": planet,
            "sign": sign,
            "house": house,
            "big_three": chart_context.get("big_three", {}),
            "ascendant": chart_context.get("big_three", {}).get("ascendant", "")
        }
        
        in_sign = self.get_interpretation(query_in_sign, context)
        in_house = self.get_interpretation(query_in_house, context)
        
        return {
            "in_sign": in_sign,
            "in_house": in_house
        }
    
    def get_house_interpretation(self, house_number: int, cusp_sign: str, planets: List[str], chart_context: Dict) -> str:
        """Get interpretation for a house"""
        planets_str = ", ".join(planets) if planets else "nenhum planeta"
        query = f"Interpretação da Casa {house_number} com cúspide em {cusp_sign}. Planetas nesta casa: {planets_str}. Explique o tema desta casa e como os planetas influenciam."
        
        context = {
            "house": house_number,
            "cusp_sign": cusp_sign,
            "planets": planets,
            "big_three": chart_context.get("big_three", {})
        }
        
        return self.get_interpretation(query, context)
    
    def get_aspect_interpretation(self, planet1: str, planet2: str, aspect_type: str, orb: float, chart_context: Dict) -> Dict:
        """Get interpretation for an aspect"""
        # Map aspect types to Portuguese
        aspect_names = {
            "conjunction": "Conjunção",
            "opposition": "Oposição",
            "square": "Quadratura",
            "trine": "Trígono",
            "sextile": "Sextil"
        }
        
        aspect_name_pt = aspect_names.get(aspect_type, aspect_type)
        
        query = f"Interpretação do aspecto {aspect_name_pt} entre {planet1} e {planet2} com orbe de {orb:.1f} graus. Explique o significado, influências psicológicas e práticas deste aspecto."
        
        context = {
            "planet1": planet1,
            "planet2": planet2,
            "aspect": aspect_type,
            "aspect_name": aspect_name_pt,
            "orb": orb,
            "big_three": chart_context.get("big_three", {})
        }
        
        interpretation = self.get_interpretation(query, context)
        
        # Determine tags based on aspect type
        tags = []
        if aspect_type in ["trine", "sextile", "conjunction"]:
            tags.extend(["Harmonia", "Equilíbrio"])
        if aspect_type in ["square", "opposition"]:
            tags.extend(["Desafio", "Crescimento"])
        if planet1 in ["Vênus", "Júpiter"] or planet2 in ["Vênus", "Júpiter"]:
            tags.append("Relacionamentos")
        if planet1 in ["Marte", "Plutão"] or planet2 in ["Marte", "Plutão"]:
            tags.append("Energia")
        if aspect_type == "square":
            tags.append("Tensão")
        
        return {
            "interpretation": interpretation,
            "tags": list(set(tags))  # Remove duplicates
        }
    
    def get_chart_ruler_interpretation(self, ascendant: str, ruler: str, ruler_sign: str, ruler_house: int, chart_context: Dict) -> Dict:
        """Get interpretation for chart ruler"""
        query = f"Interpretação do planeta regente do mapa. Ascendente em {ascendant}, regente é {ruler} em {ruler_sign} na Casa {ruler_house}. Explique o significado do planeta regente e como ele guia a jornada de vida."
        
        context = {
            "ascendant": ascendant,
            "ruler": ruler,
            "ruler_sign": ruler_sign,
            "ruler_house": ruler_house,
            "big_three": chart_context.get("big_three", {})
        }
        
        interpretation = self.get_interpretation(query, context)
        
        return {
            "concept": f"Seu Ascendente é {ascendant}, portanto, seu planeta regente é {ruler}.",
            "positioning": f"No seu mapa, {ruler} está em {ruler_sign} na sua Casa {ruler_house}.",
            "influence": interpretation
        }
    
    def _format_context(self, context: Dict) -> str:
        """Format chart context for query"""
        parts = []
        if "planet" in context:
            parts.append(f"Planeta: {context['planet']}")
        if "sign" in context:
            parts.append(f"Signo: {context['sign']}")
        if "house" in context:
            parts.append(f"Casa: {context['house']}")
        if "big_three" in context:
            bt = context["big_three"]
            parts.append(f"Sol: {bt.get('sun', '')}, Lua: {bt.get('moon', '')}, Ascendente: {bt.get('ascendant', '')}")
        return ". ".join(parts)
    
    def _get_fallback_interpretation(self, query: str, context: Dict = None) -> str:
        """Fallback interpretation when RAG is not available"""
        # Simple rule-based fallback
        if "Sol" in query and "Casa 5" in query:
            return """O Sol na Casa 5 é uma posição extremamente favorável para a autoexpressão criativa e o prazer. Esta casa rege a criatividade, o romance, os hobbies, os filhos e tudo aquilo que nos traz alegria genuína. Quando o Sol, que representa nossa essência e vitalidade, está posicionado aqui, ele ilumina todas essas áreas da vida.

Você tem uma necessidade inata de se expressar criativamente. Seja através da arte, da música, da escrita ou de qualquer outra forma de expressão, você brilha quando está criando algo que vem do coração. Sua identidade está intimamente ligada à sua capacidade de criar e compartilhar sua visão única com o mundo."""
        
        return f"Interpretação baseada em conhecimentos astrológicos clássicos. {query} Esta é uma interpretação geral e seria beneficiada pela análise dos documentos especializados."

# Global instance
rag_service = RAGService()

