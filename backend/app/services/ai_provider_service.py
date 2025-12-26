"""
Serviço abstrato para múltiplos provedores de IA.
Permite trocar facilmente entre Groq, OpenAI, Anthropic, Google Gemini, etc.
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from enum import Enum
import os
from app.core.config import settings


class AIProvider(str, Enum):
    """Provedores de IA disponíveis."""
    DEEPSEEK = "deepseek"
    GROQ = "groq"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    OLLAMA = "ollama"  # Para modelos locais


class AIProviderService(ABC):
    """Interface abstrata para provedores de IA."""
    
    @abstractmethod
    def generate_text(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        """Gera texto usando o provedor de IA."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Verifica se o provedor está disponível e configurado."""
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Retorna o nome do provedor."""
        pass


class DeepSeekProvider(AIProviderService):
    """Implementação do provedor DeepSeek (compatível com OpenAI API)."""
    
    def __init__(self):
        self.client = None
        self._initialize()
    
    def _initialize(self):
        """Inicializa o cliente DeepSeek."""
        try:
            api_key = getattr(settings, "DEEPSEEK_API_KEY", None) or os.getenv("DEEPSEEK_API_KEY")
            if not api_key or not api_key.strip():
                return
            
            self.api_key = api_key.strip()
            
            # DeepSeek usa API compatível com OpenAI
            try:
                from openai import OpenAI
                # Timeout configurável - padrão 180 segundos para respostas longas
                # Mas tentar otimizar para ser mais rápido
                timeout_seconds = int(os.getenv("DEEPSEEK_TIMEOUT", "180"))
                self.client = OpenAI(
                    api_key=self.api_key,
                    base_url="https://api.deepseek.com",
                    timeout=timeout_seconds,
                    max_retries=2  # Limitar retries para não demorar muito
                )
                self.timeout = timeout_seconds
            except ImportError:
                # Se openai não estiver instalado, usar requests diretamente
                self.client = None  # Será None, mas api_key está armazenado
                self.timeout = int(os.getenv("DEEPSEEK_TIMEOUT", "180"))
        except Exception as e:
            print(f"[AI Provider] Erro ao inicializar DeepSeek: {e}")
            self.client = None
            self.api_key = None
            self.timeout = 180
    
    def is_available(self) -> bool:
        """Verifica se DeepSeek está disponível."""
        return hasattr(self, 'api_key') and self.api_key is not None
    
    def get_provider_name(self) -> str:
        return "deepseek"
    
    def generate_text(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        model: str = "deepseek-chat",
        **kwargs
    ) -> str:
        """Gera texto usando DeepSeek."""
        if not self.is_available():
            raise ValueError("DeepSeek não está disponível")
        
        try:
            # Se tem cliente OpenAI (preferido)
            if self.client is not None and hasattr(self.client, 'chat'):
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens,
                    top_p=kwargs.get("top_p", 0.9),
                    frequency_penalty=kwargs.get("frequency_penalty", 0.1),
                    presence_penalty=kwargs.get("presence_penalty", 0.1)
                )
                return response.choices[0].message.content
            else:
                # Usar requests diretamente (fallback se openai não estiver instalado)
                import requests
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                data = {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "top_p": kwargs.get("top_p", 0.9),
                    "frequency_penalty": kwargs.get("frequency_penalty", 0.1),
                    "presence_penalty": kwargs.get("presence_penalty", 0.1)
                }
                # Usar timeout configurável (padrão 180 segundos)
                timeout_seconds = getattr(self, 'timeout', 180) if hasattr(self, 'timeout') else int(os.getenv("DEEPSEEK_TIMEOUT", "180"))
                response = requests.post(
                    "https://api.deepseek.com/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=timeout_seconds
                )
                response.raise_for_status()
                return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            raise Exception(f"Erro ao gerar texto com DeepSeek: {str(e)}")


class GroqProvider(AIProviderService):
    """Implementação do provedor Groq."""
    
    def __init__(self):
        self.client = None
        self._initialize()
    
    def _initialize(self):
        """Inicializa o cliente Groq."""
        try:
            api_key = settings.GROQ_API_KEY
            if not api_key or not api_key.strip():
                return
            
            from groq import Groq
            self.client = Groq(api_key=api_key.strip())
        except Exception as e:
            print(f"[AI Provider] Erro ao inicializar Groq: {e}")
            self.client = None
    
    def is_available(self) -> bool:
        """Verifica se Groq está disponível."""
        return self.client is not None
    
    def get_provider_name(self) -> str:
        return "groq"
    
    def generate_text(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        model: str = "llama-3.1-8b-instant",  # Modelo rápido e profissional (8B - sempre disponível)
        **kwargs
    ) -> str:
        """Gera texto usando Groq."""
        if not self.is_available():
            raise ValueError("Groq não está disponível")
        
        try:
            chat_completion = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=kwargs.get("top_p", 0.9),
                frequency_penalty=kwargs.get("frequency_penalty", 0.1),
                presence_penalty=kwargs.get("presence_penalty", 0.1)
            )
            
            return chat_completion.choices[0].message.content
        except Exception as e:
            raise Exception(f"Erro ao gerar texto com Groq: {str(e)}")


class OpenAIProvider(AIProviderService):
    """Implementação do provedor OpenAI."""
    
    def __init__(self):
        self.client = None
        self._initialize()
    
    def _initialize(self):
        """Inicializa o cliente OpenAI."""
        try:
            api_key = getattr(settings, "OPENAI_API_KEY", None) or os.getenv("OPENAI_API_KEY")
            if not api_key or not api_key.strip():
                return
            
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key.strip())
        except Exception as e:
            print(f"[AI Provider] Erro ao inicializar OpenAI: {e}")
            self.client = None
    
    def is_available(self) -> bool:
        """Verifica se OpenAI está disponível."""
        return self.client is not None
    
    def get_provider_name(self) -> str:
        return "openai"
    
    def generate_text(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        model: str = "gpt-4o-mini",
        **kwargs
    ) -> str:
        """Gera texto usando OpenAI."""
        if not self.is_available():
            raise ValueError("OpenAI não está disponível")
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=kwargs.get("top_p", 0.9),
                frequency_penalty=kwargs.get("frequency_penalty", 0.1),
                presence_penalty=kwargs.get("presence_penalty", 0.1)
            )
            
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Erro ao gerar texto com OpenAI: {str(e)}")


class AnthropicProvider(AIProviderService):
    """Implementação do provedor Anthropic (Claude)."""
    
    def __init__(self):
        self.client = None
        self._initialize()
    
    def _initialize(self):
        """Inicializa o cliente Anthropic."""
        try:
            api_key = getattr(settings, "ANTHROPIC_API_KEY", None) or os.getenv("ANTHROPIC_API_KEY")
            if not api_key or not api_key.strip():
                return
            
            from anthropic import Anthropic
            self.client = Anthropic(api_key=api_key.strip())
        except Exception as e:
            print(f"[AI Provider] Erro ao inicializar Anthropic: {e}")
            self.client = None
    
    def is_available(self) -> bool:
        """Verifica se Anthropic está disponível."""
        return self.client is not None
    
    def get_provider_name(self) -> str:
        return "anthropic"
    
    def generate_text(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        model: str = "claude-3-5-sonnet-20241022",
        **kwargs
    ) -> str:
        """Gera texto usando Anthropic Claude."""
        if not self.is_available():
            raise ValueError("Anthropic não está disponível")
        
        try:
            message = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            return message.content[0].text
        except Exception as e:
            raise Exception(f"Erro ao gerar texto com Anthropic: {str(e)}")


class GeminiProvider(AIProviderService):
    """Implementação do provedor Google Gemini."""
    
    def __init__(self):
        self.client = None
        self._initialize()
    
    def _initialize(self):
        """Inicializa o cliente Gemini."""
        try:
            api_key = getattr(settings, "GEMINI_API_KEY", None) or os.getenv("GEMINI_API_KEY")
            if not api_key or not api_key.strip():
                return
            
            import google.generativeai as genai
            genai.configure(api_key=api_key.strip())
            self.client = genai.GenerativeModel('gemini-pro')
        except Exception as e:
            print(f"[AI Provider] Erro ao inicializar Gemini: {e}")
            self.client = None
    
    def is_available(self) -> bool:
        """Verifica se Gemini está disponível."""
        return self.client is not None
    
    def get_provider_name(self) -> str:
        return "gemini"
    
    def generate_text(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        model: str = "gemini-pro",
        **kwargs
    ) -> str:
        """Gera texto usando Google Gemini."""
        if not self.is_available():
            raise ValueError("Gemini não está disponível")
        
        try:
            # Gemini combina system e user prompt
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            generation_config = {
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            }
            
            response = self.client.generate_content(
                full_prompt,
                generation_config=generation_config
            )
            
            return response.text
        except Exception as e:
            raise Exception(f"Erro ao gerar texto com Gemini: {str(e)}")


def get_ai_provider(provider_name: Optional[str] = None) -> Optional[AIProviderService]:
    """
    Retorna o provedor de IA configurado.
    Ordem de prioridade: Groq (padrão) -> DeepSeek (fallback) -> outros
    
    Args:
        provider_name: Nome do provedor (groq, deepseek, openai, anthropic, gemini).
                      Se None, usa Groq como padrão, com DeepSeek como fallback.
    
    Returns:
        Instância do provedor de IA ou None se nenhum estiver disponível.
    """
    # Ordem de prioridade: Groq primeiro, depois DeepSeek, depois outros
    priority_order = [
        ("groq", GroqProvider),
        ("deepseek", DeepSeekProvider),
        ("openai", OpenAIProvider),
        ("anthropic", AnthropicProvider),
        ("gemini", GeminiProvider),
    ]
    
    # Se um provedor específico foi solicitado, tentar apenas ele primeiro
    if provider_name:
        provider_name = provider_name.lower()
        # Reordenar para tentar o solicitado primeiro
        priority_order = [
            (name, cls) for name, cls in priority_order if name == provider_name
        ] + [
            (name, cls) for name, cls in priority_order if name != provider_name
        ]
    else:
        # Padrão: Groq primeiro, DeepSeek como fallback
        # Verificar se Groq está disponível
        try:
            groq = GroqProvider()
            if groq.is_available():
                print(f"[AI Provider] Usando provedor padrão: Groq")
                return groq
        except Exception as e:
            print(f"[AI Provider] Erro ao inicializar Groq: {e}")
        
        # Se Groq não estiver disponível, tentar DeepSeek
        try:
            deepseek = DeepSeekProvider()
            if deepseek.is_available():
                print(f"[AI Provider] Groq não disponível, usando fallback: DeepSeek")
                return deepseek
        except Exception as e:
            print(f"[AI Provider] Erro ao inicializar DeepSeek: {e}")
    
    # Tentar todos os provedores na ordem de prioridade
    for name, provider_class in priority_order:
        try:
            provider = provider_class()
            if provider.is_available():
                print(f"[AI Provider] Usando provedor: {provider.get_provider_name()}")
                return provider
        except Exception as e:
            print(f"[AI Provider] Erro ao inicializar {name}: {e}")
            continue
    
    print("[AI Provider] ⚠️ Nenhum provedor de IA disponível")
    return None


def get_available_providers() -> Dict[str, bool]:
    """Retorna um dicionário com os provedores disponíveis."""
    providers = {
        "deepseek": DeepSeekProvider(),
        "groq": GroqProvider(),
        "openai": OpenAIProvider(),
        "anthropic": AnthropicProvider(),
        "gemini": GeminiProvider(),
    }
    
    return {
        name: provider.is_available()
        for name, provider in providers.items()
    }

