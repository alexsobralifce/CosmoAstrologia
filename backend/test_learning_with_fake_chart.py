#!/usr/bin/env python3
"""
Teste completo do sistema de aprendizado contínuo usando mapa fictício.
Este script testa se as interpretações geradas estão sendo aprendidas pelo RAG.
"""

import sys
import os
from pathlib import Path
import requests
import json
import time

# Adicionar backend ao path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

print("=" * 80)
print("🧪 TESTE COMPLETO: APRENDIZADO CONTÍNUO COM MAPA FICTÍCIO")
print("=" * 80)
print()

# Configuração
BASE_URL = os.getenv("API_URL", "http://localhost:8000")

# Dados fictícios do mapa
TEST_CHART = {
    "name": "João Teste Aprendizado",
    "birthDate": "20/05/1985",
    "birthTime": "10:15",
    "birthPlace": "Rio de Janeiro, RJ, Brasil",
    "sunSign": "Touro",
    "moonSign": "Escorpião",
    "ascendant": "Virgem"
}

# Planetas e casas para testar
TEST_CASES = [
    {"planet": "Sol", "sign": "Touro", "house": 2},
    {"planet": "Lua", "sign": "Escorpião", "house": 8},
    {"planet": "Mercúrio", "sign": "Gêmeos", "house": 3},
    {"planet": "Vênus", "sign": "Libra", "house": 7},
    {"planet": "Marte", "sign": "Áries", "house": 1},
]

def get_initial_learning_stats():
    """Obtém estatísticas iniciais do aprendizado."""
    try:
        from app.services.rag_learning_service import get_learning_service
        ls = get_learning_service()
        return ls.get_statistics()
    except Exception as e:
        print(f"⚠️  Erro ao obter estatísticas: {e}")
        return None

def get_planet_interpretation(planet, sign, house):
    """Busca interpretação de um planeta."""
    url = f"{BASE_URL}/api/interpretation/planet"
    
    payload = {
        "planet": planet,
        "sign": sign,
        "house": house,
        "sunSign": TEST_CHART["sunSign"],
        "moonSign": TEST_CHART["moonSign"],
        "ascendant": TEST_CHART["ascendant"],
        "userName": TEST_CHART["name"]
    }
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def main():
    """Executa teste completo."""
    print(f"🌐 URL da API: {BASE_URL}")
    print(f"📋 Mapa fictício: {TEST_CHART['name']}")
    print(f"   Sol: {TEST_CHART['sunSign']} | Lua: {TEST_CHART['moonSign']} | Asc: {TEST_CHART['ascendant']}")
    print()
    
    # Estatísticas iniciais
    print("📊 Obtendo estatísticas iniciais do aprendizado...")
    initial_stats = get_initial_learning_stats()
    if initial_stats:
        print(f"   Total aprendido antes: {initial_stats['total_learned']}")
        print(f"   Total validado antes: {initial_stats['total_validated']}")
        print(f"   Total rejeitado antes: {initial_stats['total_rejected']}")
    print()
    
    # Testar interpretações
    print("=" * 80)
    print("🔍 TESTANDO INTERPRETAÇÕES DE PLANETAS")
    print("=" * 80)
    print()
    
    successful_tests = 0
    groq_generated = 0
    rag_only = 0
    
    for i, test_case in enumerate(TEST_CASES, 1):
        planet = test_case["planet"]
        sign = test_case["sign"]
        house = test_case["house"]
        
        print(f"[{i}/{len(TEST_CASES)}] Testando: {planet} em {sign} na Casa {house}...")
        
        result = get_planet_interpretation(planet, sign, house)
        
        if "error" in result:
            print(f"   ❌ Erro: {result['error']}")
            continue
        
        interpretation = result.get("interpretation", "")
        generated_by = result.get("generated_by", "unknown")
        
        if interpretation:
            print(f"   ✅ Interpretação recebida ({len(interpretation)} chars)")
            print(f"   📊 Gerado por: {generated_by}")
            
            if generated_by == "groq":
                groq_generated += 1
                print(f"   🎓 Esta interpretação DEVE ser aprendida pelo sistema")
            else:
                rag_only += 1
                print(f"   ⚠️  Gerado por RAG apenas (não será aprendido)")
            
            successful_tests += 1
        else:
            print(f"   ⚠️  Interpretação vazia")
        
        print()
        
        # Pequena pausa entre requisições
        time.sleep(1)
    
    # Aguardar um pouco para processamento assíncrono
    print("⏳ Aguardando processamento assíncrono do aprendizado...")
    time.sleep(3)
    
    # Estatísticas finais
    print()
    print("=" * 80)
    print("📊 ESTATÍSTICAS FINAIS DO APRENDIZADO")
    print("=" * 80)
    
    final_stats = get_initial_learning_stats()
    if final_stats and initial_stats:
        learned_before = initial_stats['total_learned']
        learned_after = final_stats['total_learned']
        learned_new = learned_after - learned_before
        
        print(f"   Total aprendido antes: {learned_before}")
        print(f"   Total aprendido depois: {learned_after}")
        print(f"   Novos aprendidos neste teste: {learned_new}")
        print()
        print(f"   Total validado: {final_stats['total_validated']}")
        print(f"   Total rejeitado: {final_stats['total_rejected']}")
        print(f"   Por categoria: {final_stats['by_category']}")
        print()
        
        if learned_new > 0:
            print(f"✅ SUCESSO: {learned_new} nova(s) interpretação(ões) foram aprendidas!")
        else:
            print(f"⚠️  Nenhuma nova interpretação foi aprendida.")
            print(f"   Possíveis razões:")
            print(f"   - Interpretações foram geradas por RAG apenas (não Groq)")
            print(f"   - Interpretações foram rejeitadas pela validação")
            print(f"   - Interpretações eram duplicadas")
    
    # Resumo
    print()
    print("=" * 80)
    print("📋 RESUMO DO TESTE")
    print("=" * 80)
    print(f"   Testes executados: {len(TEST_CASES)}")
    print(f"   Testes bem-sucedidos: {successful_tests}")
    print(f"   Gerados pelo Groq: {groq_generated}")
    print(f"   Gerados por RAG apenas: {rag_only}")
    print()
    
    if successful_tests == len(TEST_CASES):
        print("✅ TODOS OS TESTES PASSARAM!")
    else:
        print(f"⚠️  {len(TEST_CASES) - successful_tests} teste(s) falharam")
    
    print("=" * 80)

if __name__ == "__main__":
    main()

