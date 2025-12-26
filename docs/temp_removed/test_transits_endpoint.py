#!/usr/bin/env python3
"""
Script para testar o endpoint de trânsitos.
"""

import requests
import json
import sys

# URL base do backend
BASE_URL = "http://localhost:8000"

def test_transits_endpoint(token=None):
    """Testa o endpoint de trânsitos."""
    
    url = f"{BASE_URL}/api/transits/future"
    params = {
        "months_ahead": 24,
        "max_transits": 10
    }
    
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    print("=" * 80)
    print("TESTE DO ENDPOINT DE TRÂNSITOS")
    print("=" * 80)
    print(f"\nURL: {url}")
    print(f"Parâmetros: {params}")
    print(f"Headers: {headers}")
    print("\n" + "-" * 80)
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=60)
        
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ SUCESSO!")
            print(f"Trânsitos encontrados: {data.get('count', 0)}")
            
            transits = data.get('transits', [])
            if transits:
                print("\n📊 TRÂNSITOS ENCONTRADOS:")
                print("-" * 80)
                for i, transit in enumerate(transits[:5], 1):  # Mostrar apenas os 5 primeiros
                    print(f"\n{i}. {transit.get('title', 'N/A')}")
                    print(f"   Planeta: {transit.get('planet', 'N/A')}")
                    print(f"   Aspecto: {transit.get('aspect_type_display', 'N/A')}")
                    print(f"   Ponto Natal: {transit.get('natal_point', 'N/A')}")
                    print(f"   Data Início: {transit.get('start_date', 'N/A')}")
                    print(f"   Data Fim: {transit.get('end_date', 'N/A')}")
                    print(f"   Ativo: {transit.get('isActive', False)}")
                    print(f"   Descrição: {transit.get('description', 'N/A')[:100]}...")
            else:
                print("\n⚠️  Nenhum trânsito encontrado no período.")
        else:
            print(f"\n❌ ERRO: {response.status_code}")
            print(f"Resposta: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("\n❌ ERRO: Não foi possível conectar ao servidor.")
        print("Certifique-se de que o backend está rodando em http://localhost:8000")
    except requests.exceptions.Timeout:
        print("\n❌ ERRO: Timeout ao aguardar resposta do servidor.")
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Se um token foi passado como argumento, usar ele
    token = sys.argv[1] if len(sys.argv) > 1 else None
    
    if not token:
        print("⚠️  AVISO: Nenhum token fornecido. O endpoint requer autenticação.")
        print("Use: python test_transits_endpoint.py <seu_token_jwt>")
        print("\nTentando sem token (pode falhar)...\n")
    
    test_transits_endpoint(token)

