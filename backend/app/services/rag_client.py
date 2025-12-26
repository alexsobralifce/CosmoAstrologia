"""
Cliente HTTP para o RAG Service (microsserviço).
"""
import httpx
import os
from typing import Optional, List, Dict, Any
from app.core.config import settings


class RAGClient:
    """Cliente HTTP para comunicação com o RAG Service."""
    
    def __init__(self, base_url: Optional[str] = None):
        """
        Inicializa o cliente RAG.
        
        Args:
            base_url: URL base do RAG service. Se None, usa RAG_SERVICE_URL das settings.
        """
        self.base_url = base_url or getattr(settings, 'RAG_SERVICE_URL', 'http://localhost:8001')
        self.timeout = 60.0  # 60 segundos de timeout
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Faz uma requisição HTTP para o RAG service.
        
        Args:
            method: Método HTTP (GET, POST, etc)
            endpoint: Endpoint relativo (ex: '/api/rag/interpretation')
            json_data: Dados JSON para o body (POST)
            params: Parâmetros de query (GET)
        
        Returns:
            Resposta JSON do serviço
        
        Raises:
            Exception: Se a requisição falhar
        """
        url = f"{self.base_url.rstrip('/')}{endpoint}"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                if method.upper() == "GET":
                    response = await client.get(url, params=params)
                elif method.upper() == "POST":
                    response = await client.post(url, json=json_data)
                else:
                    raise ValueError(f"Método HTTP não suportado: {method}")
                
                response.raise_for_status()
                return response.json()
        except httpx.TimeoutException:
            raise Exception(f"Timeout ao conectar com RAG service em {url}")
        except httpx.ConnectError:
            raise Exception(f"Não foi possível conectar com RAG service em {url}. Verifique se o serviço está rodando.")
        except httpx.HTTPStatusError as e:
            error_detail = "Erro desconhecido"
            try:
                error_data = e.response.json()
                error_detail = error_data.get('detail', str(e))
            except:
                error_detail = e.response.text or str(e)
            raise Exception(f"Erro do RAG service: {error_detail}")
        except Exception as e:
            raise Exception(f"Erro ao comunicar com RAG service: {str(e)}")
    
    async def get_interpretation(
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
            planet: Nome do planeta
            sign: Nome do signo
            house: Número da casa
            aspect: Tipo de aspecto
            custom_query: Query customizada
            use_groq: Se deve usar Groq para gerar interpretação
            top_k: Número de resultados a buscar
            category: Categoria ('astrology' ou 'numerology')
        
        Returns:
            Dicionário com interpretação, fontes, etc.
        """
        payload = {
            "use_groq": use_groq,
            "top_k": top_k
        }
        
        if planet:
            payload["planet"] = planet
        if sign:
            payload["sign"] = sign
        if house:
            payload["house"] = house
        if aspect:
            payload["aspect"] = aspect
        if custom_query:
            payload["custom_query"] = custom_query
        if category:
            payload["category"] = category
        
        return await self._request("POST", "/api/rag/interpretation", json_data=payload)
    
    async def search(
        self,
        query: str,
        top_k: int = 5,
        expand_query: bool = False,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Busca documentos relevantes na base de conhecimento.
        
        Args:
            query: Texto da consulta
            top_k: Número de resultados
            expand_query: Se deve expandir a query
            category: Categoria para filtrar
        
        Returns:
            Lista de documentos relevantes
        """
        payload = {
            "query": query,
            "top_k": top_k,
            "expand_query": expand_query
        }
        
        if category:
            payload["category"] = category
        
        response = await self._request("POST", "/api/rag/search", json_data=payload)
        return response.get("results", [])
    
    async def get_status(self) -> Dict[str, Any]:
        """
        Obtém o status do RAG service.
        
        Returns:
            Dicionário com informações de status
        """
        return await self._request("GET", "/api/rag/status")
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Verifica se o RAG service está saudável.
        
        Returns:
            Dicionário com status de saúde
        """
        return await self._request("GET", "/health")


# Instância global do cliente
_rag_client: Optional[RAGClient] = None


def get_rag_client() -> Optional[RAGClient]:
    """
    Obtém instância singleton do cliente RAG.
    Retorna None se RAG_SERVICE_URL não estiver configurado.
    """
    global _rag_client
    
    if _rag_client is None:
        rag_service_url = getattr(settings, 'RAG_SERVICE_URL', None)
        if not rag_service_url:
            print("[RAG-Client] RAG_SERVICE_URL não configurado. RAG service não estará disponível.")
            return None
        
        # Verificar se está usando localhost em produção
        is_production = (
            os.getenv("RAILWAY_ENVIRONMENT") is not None or
            os.getenv("VERCEL") is not None or
            os.getenv("PRODUCTION") == "true" or
            "postgresql" in str(getattr(settings, 'DATABASE_URL', '')).lower()
        )
        
        if is_production and "localhost" in rag_service_url:
            print("=" * 80)
            print("🚨 ERRO CRÍTICO: RAG_SERVICE_URL está usando localhost em produção!")
            print(f"   URL atual: {rag_service_url}")
            print("   Configure RAG_SERVICE_URL no Railway com a URL do RAG service")
            print("   Exemplo: https://rag-service-production.up.railway.app")
            print("=" * 80)
        
        print(f"[RAG-Client] Inicializando cliente RAG com URL: {rag_service_url}")
        _rag_client = RAGClient(base_url=rag_service_url)
    
    return _rag_client

