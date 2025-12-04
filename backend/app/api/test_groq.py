from fastapi import APIRouter
from app.services.ai_provider_service import get_ai_provider

router = APIRouter()

@router.get("/test-groq")
async def test_groq():
    """Endpoint simples para testar se o Groq está funcionando."""
    try:
        provider = get_ai_provider()
        
        if not provider:
            return {"status": "error", "message": "Nenhum provedor de IA disponível"}
        
        provider_name = provider.get_provider_name()
        print(f"[TEST GROQ] Provedor obtido: {provider_name}")
        
        # Teste simples
        test_response = provider.generate_text(
            system_prompt="Você é um assistente útil.",
            user_prompt="Responda apenas com 'OK' se estiver funcionando.",
            temperature=0.7,
            max_tokens=10
        )
        
        return {
            "status": "success",
            "provider": provider_name,
            "response": test_response,
            "message": f"Groq está funcionando corretamente como provedor padrão"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erro ao testar Groq: {str(e)}",
            "provider": provider.get_provider_name() if provider else "none"
        }
