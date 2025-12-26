#!/usr/bin/env python3
"""
Script de teste para verificar se as interpretações de planetas variam corretamente
entre diferentes planetas e casas.

Este script testa:
1. Mesmo planeta em diferentes casas
2. Diferentes planetas na mesma casa
3. Diferentes planetas em diferentes casas

Uso:
    python3 test_planet_house_rotation.py
"""

import sys
import os
from pathlib import Path
import requests
import json
from typing import Dict, List, Tuple

# Adicionar o diretório backend ao path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

print("=" * 80)
print("🧪 TESTE: ROTAÇÃO DE PLANETAS NAS 12 CASAS")
print("=" * 80)
print()

# Configuração
BASE_URL = os.getenv("API_URL", "http://localhost:8000")
TEST_TOKEN = os.getenv("TEST_TOKEN", "")

# Lista de planetas para testar
PLANETS = ["Sol", "Lua", "Mercúrio", "Vênus", "Marte", "Júpiter", "Saturno"]
HOUSES = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
SIGNS = ["Áries", "Touro", "Gêmeos", "Câncer", "Leão", "Virgem", 
         "Libra", "Escorpião", "Sagitário", "Capricórnio", "Aquário", "Peixes"]

def get_planet_interpretation(planet: str, sign: str, house: int, token: str = "") -> Dict:
    """Busca interpretação de um planeta via API"""
    url = f"{BASE_URL}/api/interpretation/planet"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    payload = {
        "planet": planet,
        "sign": sign,
        "house": house,
        "sunSign": "Áries",
        "moonSign": "Touro",
        "ascendant": "Leão",
        "userName": "Teste"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e), "interpretation": None}

def extract_key_phrases(text: str) -> List[str]:
    """Extrai frases-chave da interpretação para comparação"""
    if not text:
        return []
    
    # Dividir em parágrafos
    paragraphs = text.split('\n\n')
    key_phrases = []
    
    for para in paragraphs:
        para = para.strip()
        if len(para) > 50:  # Ignorar parágrafos muito curtos
            # Pegar primeira frase de cada parágrafo
            first_sentence = para.split('.')[0] if '.' in para else para[:100]
            key_phrases.append(first_sentence.strip())
    
    return key_phrases[:3]  # Retornar até 3 frases-chave

def compare_interpretations(interpretations: List[Dict]) -> Dict:
    """Compara interpretações para verificar se são diferentes"""
    results = {
        "total": len(interpretations),
        "unique": 0,
        "similar": 0,
        "identical": 0,
        "details": []
    }
    
    texts = [i.get("interpretation", "") for i in interpretations]
    
    # Remover interpretações vazias ou com erro
    valid_texts = [(idx, text) for idx, text in enumerate(texts) if text and "error" not in text.lower()]
    
    if len(valid_texts) < 2:
        results["error"] = "Não há interpretações suficientes para comparar"
        return results
    
    # Comparar cada par de interpretações
    for i, (idx1, text1) in enumerate(valid_texts):
        for j, (idx2, text2) in enumerate(valid_texts[i+1:], start=i+1):
            # Calcular similaridade simples (porcentagem de palavras em comum)
            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())
            
            if len(words1) == 0 or len(words2) == 0:
                continue
            
            common_words = words1.intersection(words2)
            similarity = len(common_words) / max(len(words1), len(words2))
            
            # Extrair frases-chave
            phrases1 = extract_key_phrases(text1)
            phrases2 = extract_key_phrases(text2)
            
            # Verificar se são idênticas
            if text1.strip() == text2.strip():
                results["identical"] += 1
                results["details"].append({
                    "type": "identical",
                    "indices": [idx1, idx2],
                    "similarity": 1.0
                })
            # Verificar se são muito similares (>80% de palavras em comum)
            elif similarity > 0.8:
                results["similar"] += 1
                results["details"].append({
                    "type": "similar",
                    "indices": [idx1, idx2],
                    "similarity": similarity,
                    "phrases1": phrases1,
                    "phrases2": phrases2
                })
            else:
                results["unique"] += 1
    
    return results

def test_same_planet_different_houses():
    """Testa o mesmo planeta em diferentes casas"""
    print("=" * 80)
    print("TESTE 1: Mesmo planeta em diferentes casas")
    print("=" * 80)
    print()
    
    planet = "Sol"
    sign = "Leão"
    houses_to_test = [1, 5, 9, 12]  # Testar algumas casas
    
    interpretations = []
    
    for house in houses_to_test:
        print(f"📊 Buscando interpretação: {planet} em {sign} na Casa {house}...")
        result = get_planet_interpretation(planet, sign, house, TEST_TOKEN)
        
        if "error" in result:
            print(f"   ❌ Erro: {result['error']}")
        else:
            interpretation = result.get("interpretation", "")
            if interpretation:
                print(f"   ✅ Recebido ({len(interpretation)} caracteres)")
                print(f"   📝 Preview: {interpretation[:150]}...")
                interpretations.append({
                    "planet": planet,
                    "sign": sign,
                    "house": house,
                    "interpretation": interpretation,
                    "queries_used": result.get("queries_used", [])
                })
            else:
                print(f"   ⚠️  Interpretação vazia")
        
        print()
    
    # Comparar interpretações
    if len(interpretations) > 1:
        print("🔍 Comparando interpretações...")
        comparison = compare_interpretations(interpretations)
        
        print(f"\n📊 Resultados da comparação:")
        print(f"   Total de comparações: {comparison['total']}")
        print(f"   Interpretações únicas: {comparison['unique']}")
        print(f"   Interpretações similares: {comparison['similar']}")
        print(f"   Interpretações idênticas: {comparison['identical']}")
        
        if comparison.get("details"):
            print(f"\n📋 Detalhes:")
            for detail in comparison["details"][:3]:  # Mostrar até 3 detalhes
                if detail["type"] == "identical":
                    idx1, idx2 = detail["indices"]
                    print(f"   ⚠️  Interpretações {idx1} e {idx2} são IDÊNTICAS")
                elif detail["type"] == "similar":
                    idx1, idx2 = detail["indices"]
                    print(f"   ⚠️  Interpretações {idx1} e {idx2} são muito similares ({detail['similarity']*100:.1f}%)")
                    print(f"      Frases-chave 1: {detail['phrases1'][0] if detail['phrases1'] else 'N/A'}")
                    print(f"      Frases-chave 2: {detail['phrases2'][0] if detail['phrases2'] else 'N/A'}")
    
    print()
    return interpretations

def test_different_planets_same_house():
    """Testa diferentes planetas na mesma casa"""
    print("=" * 80)
    print("TESTE 2: Diferentes planetas na mesma casa")
    print("=" * 80)
    print()
    
    house = 5
    sign = "Leão"
    planets_to_test = ["Sol", "Lua", "Mercúrio", "Vênus"]
    
    interpretations = []
    
    for planet in planets_to_test:
        print(f"📊 Buscando interpretação: {planet} em {sign} na Casa {house}...")
        result = get_planet_interpretation(planet, sign, house, TEST_TOKEN)
        
        if "error" in result:
            print(f"   ❌ Erro: {result['error']}")
        else:
            interpretation = result.get("interpretation", "")
            if interpretation:
                print(f"   ✅ Recebido ({len(interpretation)} caracteres)")
                print(f"   📝 Preview: {interpretation[:150]}...")
                interpretations.append({
                    "planet": planet,
                    "sign": sign,
                    "house": house,
                    "interpretation": interpretation,
                    "queries_used": result.get("queries_used", [])
                })
            else:
                print(f"   ⚠️  Interpretação vazia")
        
        print()
    
    # Comparar interpretações
    if len(interpretations) > 1:
        print("🔍 Comparando interpretações...")
        comparison = compare_interpretations(interpretations)
        
        print(f"\n📊 Resultados da comparação:")
        print(f"   Total de comparações: {comparison['total']}")
        print(f"   Interpretações únicas: {comparison['unique']}")
        print(f"   Interpretações similares: {comparison['similar']}")
        print(f"   Interpretações idênticas: {comparison['identical']}")
        
        if comparison.get("details"):
            print(f"\n📋 Detalhes:")
            for detail in comparison["details"][:3]:
                if detail["type"] == "identical":
                    idx1, idx2 = detail["indices"]
                    planet1 = interpretations[idx1]["planet"]
                    planet2 = interpretations[idx2]["planet"]
                    print(f"   ⚠️  {planet1} e {planet2} têm interpretações IDÊNTICAS")
                elif detail["type"] == "similar":
                    idx1, idx2 = detail["indices"]
                    planet1 = interpretations[idx1]["planet"]
                    planet2 = interpretations[idx2]["planet"]
                    print(f"   ⚠️  {planet1} e {planet2} têm interpretações muito similares ({detail['similarity']*100:.1f}%)")
    
    print()
    return interpretations

def test_different_combinations():
    """Testa diferentes combinações de planeta + casa"""
    print("=" * 80)
    print("TESTE 3: Diferentes combinações de planeta + casa")
    print("=" * 80)
    print()
    
    test_cases = [
        ("Sol", "Leão", 1),
        ("Lua", "Câncer", 4),
        ("Mercúrio", "Gêmeos", 3),
        ("Vênus", "Libra", 7),
        ("Marte", "Áries", 1),
    ]
    
    interpretations = []
    
    for planet, sign, house in test_cases:
        print(f"📊 Buscando interpretação: {planet} em {sign} na Casa {house}...")
        result = get_planet_interpretation(planet, sign, house, TEST_TOKEN)
        
        if "error" in result:
            print(f"   ❌ Erro: {result['error']}")
        else:
            interpretation = result.get("interpretation", "")
            queries_used = result.get("queries_used", [])
            
            if interpretation:
                print(f"   ✅ Recebido ({len(interpretation)} caracteres)")
                print(f"   📝 Preview: {interpretation[:150]}...")
                print(f"   🔍 Queries usadas: {len(queries_used)} queries")
                if queries_used:
                    print(f"      - {queries_used[0]}")
                    if len(queries_used) > 1:
                        print(f"      - {queries_used[1]}")
                
                interpretations.append({
                    "planet": planet,
                    "sign": sign,
                    "house": house,
                    "interpretation": interpretation,
                    "queries_used": queries_used
                })
            else:
                print(f"   ⚠️  Interpretação vazia")
        
        print()
    
    # Comparar interpretações
    if len(interpretations) > 1:
        print("🔍 Comparando interpretações...")
        comparison = compare_interpretations(interpretations)
        
        print(f"\n📊 Resultados da comparação:")
        print(f"   Total de comparações: {comparison['total']}")
        print(f"   Interpretações únicas: {comparison['unique']}")
        print(f"   Interpretações similares: {comparison['similar']}")
        print(f"   Interpretações idênticas: {comparison['identical']}")
        
        if comparison["identical"] > 0 or comparison["similar"] > comparison["unique"]:
            print(f"\n⚠️  ATENÇÃO: Muitas interpretações similares ou idênticas!")
            print(f"   Isso indica que o sistema pode não estar variando corretamente.")
        else:
            print(f"\n✅ SUCESSO: As interpretações são diferentes!")
    
    print()
    return interpretations

def main():
    """Executa todos os testes"""
    print(f"🌐 URL da API: {BASE_URL}")
    print(f"🔑 Token: {'Configurado' if TEST_TOKEN else 'Não configurado (opcional)'}")
    print()
    
    # Teste 1: Mesmo planeta em diferentes casas
    test1_results = test_same_planet_different_houses()
    
    # Teste 2: Diferentes planetas na mesma casa
    test2_results = test_different_planets_same_house()
    
    # Teste 3: Diferentes combinações
    test3_results = test_different_combinations()
    
    # Resumo final
    print("=" * 80)
    print("📊 RESUMO FINAL")
    print("=" * 80)
    print()
    
    total_tests = len(test1_results) + len(test2_results) + len(test3_results)
    print(f"✅ Total de interpretações obtidas: {total_tests}")
    print()
    
    if total_tests == 0:
        print("❌ Nenhuma interpretação foi obtida. Verifique:")
        print("   1. Se o servidor está rodando")
        print("   2. Se a URL da API está correta")
        print("   3. Se há erros nos logs do servidor")
    else:
        print("✅ Testes concluídos! Verifique os resultados acima para confirmar")
        print("   se as interpretações estão variando corretamente.")
    
    print()

if __name__ == "__main__":
    main()

