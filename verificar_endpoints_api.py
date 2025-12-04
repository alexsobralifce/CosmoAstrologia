#!/usr/bin/env python3
"""
Script para verificar todos os endpoints da API e se estão funcionais.
"""

import os
import re
from pathlib import Path

# Mapeamento de métodos do frontend para endpoints do backend
FRONTEND_METHODS = {
    # Autenticação
    'registerUser': '/api/auth/register',
    'verifyEmail': '/api/auth/verify-email',
    'resendVerificationCode': '/api/auth/resend-verification',
    'loginUser': '/api/auth/login',
    'getCurrentUser': '/api/auth/me',
    'getUserBirthChart': '/api/auth/birth-chart',
    'updateUser': '/api/auth/me',
    'verifyGoogleToken': '/api/auth/google/verify',
    'googleAuth': '/api/auth/google',
    'completeOnboarding': '/api/auth/complete-onboarding',
    
    # Interpretações
    'getInterpretation': '/api/interpretation',
    'searchDocuments': '/api/interpretation/search',
    'getRAGStatus': '/api/interpretation/status',
    'getPlanetInterpretation': '/api/interpretation/planet',
    'getChartRulerInterpretation': '/api/interpretation/chart-ruler',
    'getPlanetHouseInterpretation': '/api/interpretation/planet-house',
    'getAspectInterpretation': '/api/interpretation/aspect',
    'getDailyAdvice': '/api/interpretation/daily-advice',
    
    # Mapa Astral Completo
    'getCompleteChart': '/api/interpretation/complete-chart',
    'generateBirthChartSection': '/api/full-birth-chart/section',
    'generateFullBirthChart': '/api/full-birth-chart/all',
    
    # Trânsitos
    'getFutureTransits': '/api/transits/future',
    
    # Revolução Solar
    'calculateSolarReturn': '/api/solar-return/calculate',
    'getSolarReturnInterpretation': '/api/solar-return/interpretation',
    
    # Numerologia
    'getNumerologyMap': '/api/numerology/map',
    'getNumerologyInterpretation': '/api/numerology/interpretation',
    'getBirthGridQuantitiesInterpretation': '/api/numerology/birth-grid-quantities',
}

def find_endpoint_in_backend(endpoint_path: str) -> tuple[bool, str]:
    """Verifica se o endpoint existe no backend."""
    backend_path = Path('backend/app/api')
    
    # Remover /api do início
    route_path = endpoint_path.replace('/api/', '')
    
    # Procurar em todos os arquivos Python do backend
    for py_file in backend_path.rglob('*.py'):
        if py_file.name.endswith('.bak'):
            continue
            
        try:
            content = py_file.read_text(encoding='utf-8')
            
            # Procurar por definições de router
            # Padrões: @router.get("/path"), @router.post("/path"), etc.
            patterns = [
                rf'@router\.(get|post|put|delete)\("{re.escape(route_path)}"',
                rf'@router\.(get|post|put|delete)\("{re.escape(route_path)}"',
                rf'@router\.(get|post|put|delete)\("{re.escape(route_path.split("/")[-1])}"',  # Apenas última parte
            ]
            
            for pattern in patterns:
                if re.search(pattern, content):
                    return True, str(py_file.relative_to(Path('backend')))
        except Exception as e:
            continue
    
    return False, ""

def check_ai_provider_usage(endpoint_path: str) -> tuple[bool, str]:
    """Verifica se o endpoint usa a IA correta."""
    backend_path = Path('backend/app/api')
    route_path = endpoint_path.replace('/api/', '')
    
    for py_file in backend_path.rglob('*.py'):
        if py_file.name.endswith('.bak'):
            continue
            
        try:
            content = py_file.read_text(encoding='utf-8')
            
            # Verificar se menciona o endpoint
            if route_path.split('/')[-1] in content or route_path in content:
                # Verificar uso de IA
                has_groq = 'groq' in content.lower() or 'get_ai_provider' in content
                has_deepseek = 'deepseek' in content.lower()
                has_ai = has_groq or has_deepseek or 'ai_provider' in content
                
                if has_ai:
                    if has_groq:
                        return True, "Groq"
                    elif has_deepseek:
                        return True, "DeepSeek"
                    else:
                        return True, "AI Provider Service"
                else:
                    return False, "Não usa IA"
        except Exception:
            continue
    
    return False, "Endpoint não encontrado"

def main():
    print("=" * 80)
    print("VERIFICAÇÃO DE ENDPOINTS DA API")
    print("=" * 80)
    print()
    
    results = []
    
    for method_name, endpoint in FRONTEND_METHODS.items():
        exists, file_path = find_endpoint_in_backend(endpoint)
        uses_ai, ai_info = check_ai_provider_usage(endpoint)
        
        results.append({
            'method': method_name,
            'endpoint': endpoint,
            'exists': exists,
            'file': file_path,
            'uses_ai': uses_ai,
            'ai_info': ai_info
        })
    
    # Agrupar por status
    existing = [r for r in results if r['exists']]
    missing = [r for r in results if not r['exists']]
    using_ai = [r for r in results if r['uses_ai']]
    not_using_ai = [r for r in results if not r['uses_ai'] and r['exists']]
    
    print(f"📊 RESUMO:")
    print(f"   Total de endpoints: {len(results)}")
    print(f"   ✅ Existentes: {len(existing)}")
    print(f"   ❌ Faltando: {len(missing)}")
    print(f"   🤖 Usando IA: {len(using_ai)}")
    print(f"   ⚠️  Não usando IA (mas deveria?): {len(not_using_ai)}")
    print()
    
    # Endpoints faltando
    if missing:
        print("=" * 80)
        print("❌ ENDPOINTS FALTANDO NO BACKEND:")
        print("=" * 80)
        for r in missing:
            print(f"\n  Método: {r['method']}")
            print(f"  Endpoint: {r['endpoint']}")
        print()
    
    # Endpoints existentes mas não usando IA quando deveriam
    interpretation_endpoints = [r for r in not_using_ai if 'interpretation' in r['endpoint']]
    if interpretation_endpoints:
        print("=" * 80)
        print("⚠️  ENDPOINTS DE INTERPRETAÇÃO QUE NÃO USAM IA:")
        print("=" * 80)
        for r in interpretation_endpoints:
            print(f"\n  Método: {r['method']}")
            print(f"  Endpoint: {r['endpoint']}")
            print(f"  Arquivo: {r['file']}")
        print()
    
    # Todos os endpoints
    print("=" * 80)
    print("📋 TODOS OS ENDPOINTS:")
    print("=" * 80)
    for r in results:
        status = "✅" if r['exists'] else "❌"
        ai_status = f"🤖 {r['ai_info']}" if r['uses_ai'] else "⚪ Sem IA"
        print(f"\n{status} {r['method']}")
        print(f"   Endpoint: {r['endpoint']}")
        if r['exists']:
            print(f"   Arquivo: {r['file']}")
        print(f"   IA: {ai_status}")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()

