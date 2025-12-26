"""
Script para validar os dados do best timing via API.
Testa os casos reportados pelo usuário.
"""
import sys
import os
import requests
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

API_URL = "http://localhost:8000"

print("="*80)
print("VALIDAÇÃO DA API - BEST TIMING")
print("="*80)
print()

# Primeiro, criar um usuário de teste
print("1. Criando usuário de teste...")
register_data = {
    "email": "test_validation@example.com",
    "password": "Test123456!",
    "name": "Test User"
}

try:
    register_response = requests.post(f"{API_URL}/api/auth/register", json=register_data, timeout=5)
    if register_response.status_code == 201:
        print("   ✅ Usuário criado com sucesso")
    elif register_response.status_code == 400 and "já existe" in register_response.text.lower():
        print("   ⚠️ Usuário já existe, continuando...")
    else:
        print(f"   ⚠️ Status: {register_response.status_code}")
except Exception as e:
    print(f"   ⚠️ Erro ao criar usuário: {e}")

# Fazer login
print("\n2. Fazendo login...")
login_data = {
    "email": "test_validation@example.com",
    "password": "Test123456!"
}

try:
    login_response = requests.post(f"{API_URL}/api/auth/login", json=login_data, timeout=5)
    if login_response.status_code == 200:
        token = login_response.json().get("access_token")
        print("   ✅ Login realizado com sucesso")
    else:
        print(f"   ❌ Erro no login: {login_response.status_code}")
        print(f"   Resposta: {login_response.text}")
        sys.exit(1)
except Exception as e:
    print(f"   ❌ Erro ao fazer login: {e}")
    sys.exit(1)

# Registrar mapa astral
print("\n3. Registrando mapa astral...")
birth_chart_data = {
    "birth_date": "20/10/1981",
    "birth_time": "13:30",
    "latitude": -23.5505,
    "longitude": -46.6333,
    "birth_place": "São Paulo, SP",
    "name": "Test User"
}

headers = {"Authorization": f"Bearer {token}"}

try:
    chart_response = requests.post(
        f"{API_URL}/api/birth-chart/complete",
        json=birth_chart_data,
        headers=headers,
        timeout=10
    )
    if chart_response.status_code in [200, 201]:
        print("   ✅ Mapa astral registrado com sucesso")
    else:
        print(f"   ⚠️ Status: {chart_response.status_code}")
        print(f"   Resposta: {chart_response.text[:200]}")
except Exception as e:
    print(f"   ⚠️ Erro ao registrar mapa: {e}")

# Testar best timing para diferentes ações e datas
print("\n4. Testando Best Timing...")
print("="*80)

test_cases = [
    {
        "action": "pedir_aumento",
        "date": "2025-12-06",
        "expected_aspects": [
            "Sol em sextil com Casa 2",
            "Vênus em sextil com Casa 2",
            "Sol em sextil com Casa 10",
            "Vênus em sextil com Casa 10"
        ],
        "expected_score": 28
    },
    {
        "action": "primeiro_encontro",
        "date": "2025-12-28",
        "expected_aspects": [
            "Lua em conjunção com Casa 5",
            "Vênus em trígono com Casa 5",
            "Lua em sextil com Casa 7",
            "Lua em trígono com Casa 1",
            "Vênus em conjunção com Casa 1",
            "Vênus em sextil com Casa 11"
        ],
        "expected_score": 32
    }
]

for test_case in test_cases:
    print(f"\n📅 Testando: {test_case['action']} para {test_case['date']}")
    print("-" * 80)
    
    try:
        timing_response = requests.post(
            f"{API_URL}/api/best-timing/calculate",
            json={
                "action_type": test_case["action"],
                "days_ahead": 30
            },
            headers=headers,
            timeout=30
        )
        
        if timing_response.status_code == 200:
            data = timing_response.json()
            best_moments = data.get("best_moments", [])
            
            # Filtrar momentos da data específica
            target_moments = [
                m for m in best_moments
                if m['date'].startswith(test_case['date'])
            ]
            
            print(f"   Total de momentos retornados: {len(best_moments)}")
            print(f"   Momentos em {test_case['date']}: {len(target_moments)}")
            
            if target_moments:
                print(f"\n   Momentos encontrados:")
                for moment in target_moments:
                    print(f"     📅 {moment['date']}")
                    print(f"        Score: {moment['score']}")
                    print(f"        Aspectos estruturados: {len(moment.get('aspects', []))}")
                    print(f"        Reasons: {len(moment.get('reasons', []))}")
                    
                    if 'aspects' in moment:
                        print(f"        Aspectos calculados:")
                        for aspect in moment['aspects']:
                            print(f"          - {aspect.get('planet')} em {aspect.get('aspect_type')} com Casa {aspect.get('house')}")
                    
                    if 'reasons' in moment:
                        print(f"        Reasons reportados:")
                        for reason in moment['reasons'][:5]:
                            print(f"          - {reason}")
            else:
                print(f"   ⚠️ Nenhum momento encontrado para {test_case['date']}")
                print(f"   Isso está CORRETO se não houver aspectos válidos!")
        else:
            print(f"   ❌ Erro: {timing_response.status_code}")
            print(f"   Resposta: {timing_response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Erro ao testar: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "="*80)
print("VALIDAÇÃO COMPLETA")
print("="*80)

