"""
Teste direto da API para 8 de Dezembro de 2025
"""

import requests
import json
from datetime import datetime

# URL da API
API_URL = "http://localhost:8000/api/best-timing/calculate"

# Dados do usuário
payload = {
    "action_type": "pedir_aumento",
    "days_ahead": 30
}

# Headers (precisa de token de autenticação)
# Por enquanto, vamos testar sem autenticação para ver o erro
headers = {
    "Content-Type": "application/json"
}

print("=" * 80)
print("TESTE DA API: 8 de Dezembro de 2025 - Pedir Aumento")
print("=" * 80)
print(f"URL: {API_URL}")
print(f"Payload: {json.dumps(payload, indent=2)}")
print()

try:
    response = requests.post(API_URL, json=payload, headers=headers, timeout=30)
    print(f"Status Code: {response.status_code}")
    print()
    
    if response.status_code == 200:
        data = response.json()
        print(f"Total de momentos: {len(data.get('best_moments', []))}")
        print()
        
        # Filtrar momentos de 8/12/2025
        dec_8_moments = [
            m for m in data.get('best_moments', [])
            if m['date'].startswith('2025-12-08')
        ]
        
        print(f"Momentos de 8/12/2025: {len(dec_8_moments)}")
        print()
        
        if dec_8_moments:
            max_score = max(m['score'] for m in dec_8_moments)
            print(f"Score máximo: {max_score}")
            print()
            
            # Coletar aspectos únicos
            all_aspects = []
            for moment in dec_8_moments:
                if moment['score'] > 0:
                    for aspect in moment.get('aspects', []):
                        aspect_str = f"{aspect['planet']} em {aspect['aspect_type']} com Casa {aspect['house']}"
                        if aspect_str not in all_aspects:
                            all_aspects.append(aspect_str)
            
            print("Aspectos únicos do dia:")
            for aspect in all_aspects:
                print(f"  - {aspect}")
            print()
            
            # Mostrar detalhes
            for moment in dec_8_moments:
                if moment['score'] > 0:
                    print(f"Data/Hora: {moment['date']}")
                    print(f"Score: {moment['score']}")
                    print(f"Aspectos ({len(moment.get('aspects', []))}):")
                    for aspect in moment.get('aspects', []):
                        print(f"  - {aspect['planet']} em {aspect['aspect_type']} com Casa {aspect['house']}")
                    print()
        else:
            print("Nenhum momento encontrado para 8/12/2025")
            print()
            print("Primeiros 5 momentos retornados:")
            for m in data.get('best_moments', [])[:5]:
                print(f"  - {m['date']}: score {m['score']}")
    else:
        print(f"Erro: {response.text}")
        
except Exception as e:
    print(f"Erro ao fazer requisição: {e}")
    import traceback
    traceback.print_exc()

print("=" * 80)

