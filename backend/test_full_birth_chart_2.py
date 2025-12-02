#!/usr/bin/env python3
"""
Script de teste 2 para gerar mapa astral completo com todas as seções.
Dados fictícios: João Pedro Oliveira - Mapa com predominância de Terra
"""

import requests
import json
from datetime import datetime

# Configuração
BASE_URL = "http://localhost:8000"
API_ENDPOINT = f"{BASE_URL}/api/full-birth-chart/all"

# Dados fictícios para teste - Mapa com predominância de Terra
TEST_DATA = {
    "name": "João Pedro Oliveira",
    "birthDate": "22/08/1985",
    "birthTime": "08:15",
    "birthPlace": "Rio de Janeiro, Rio de Janeiro, Brasil",
    "language": "pt",
    # Tríade Fundamental - Terra dominante
    "sunSign": "Virgem",
    "moonSign": "Touro",
    "ascendant": "Capricórnio",
    "sunHouse": 6,
    "moonHouse": 2,
    "ascendantHouse": 1,
    # Planetas Pessoais
    "mercurySign": "Virgem",
    "mercuryHouse": 6,
    "venusSign": "Libra",
    "venusHouse": 7,
    "marsSign": "Câncer",
    "marsHouse": 4,
    # Planetas Sociais
    "jupiterSign": "Libra",
    "jupiterHouse": 7,
    "saturnSign": "Libra",
    "saturnHouse": 7,
    # Planetas Transpessoais
    "uranusSign": "Escorpião",
    "uranusHouse": 8,
    "neptuneSign": "Sagitário",
    "neptuneHouse": 9,
    "plutoSign": "Libra",
    "plutoHouse": 7,
    # Nodos Lunares
    "northNodeSign": "Leão",
    "southNodeSign": "Aquário",
    # Quíron
    "chironSign": "Touro",
    # Meio do Céu
    "midheavenSign": "Gêmeos",
}

EXPECTED_SECTIONS = [
    "power", "triad", "personal", "houses", "karma", "synthesis",
]


def print_section(section_data, index):
    """Imprime uma seção formatada."""
    print("\n" + "=" * 80)
    print(f"SEÇÃO {index + 1}/{len(EXPECTED_SECTIONS)}: {section_data.get('section', 'unknown').upper()}")
    print("=" * 80)
    print(f"Título: {section_data.get('title', 'N/A')}")
    print(f"Gerado por: {section_data.get('generated_by', 'N/A')}")
    print("-" * 80)
    content = section_data.get('content', '')
    if content:
        preview = content[:500] + "..." if len(content) > 500 else content
        print(preview)
    else:
        print("⚠️ Conteúdo vazio ou não disponível")
    print("=" * 80)


def validate_temperament_consistency(sections):
    """Valida se o temperamento é consistente em todas as seções."""
    print("\n" + "=" * 80)
    print("🔍 VALIDAÇÃO DE CONSISTÊNCIA DO TEMPERAMENTO")
    print("=" * 80)
    
    temperament_mentions = []
    
    for section in sections:
        content = section.get('content', '').lower()
        section_name = section.get('section', 'unknown')
        
        elements = ['fogo', 'terra', 'ar', 'água']
        found_elements = []
        
        for element in elements:
            if element in content:
                import re
                pattern = rf'{element}.*?(\d+)\s*ponto'
                matches = re.findall(pattern, content)
                if matches:
                    found_elements.append(f"{element}: {matches[0]} pontos")
        
        if found_elements:
            temperament_mentions.append({
                'section': section_name,
                'elements': found_elements
            })
    
    if temperament_mentions:
        print("📊 Menções de temperamento encontradas:")
        for mention in temperament_mentions:
            print(f"  • {mention['section']}: {', '.join(mention['elements'])}")
        
        if len(temperament_mentions) > 1:
            first = temperament_mentions[0]['elements']
            all_consistent = all(
                mention['elements'] == first 
                for mention in temperament_mentions[1:]
            )
            
            if all_consistent:
                print("\n✅ Temperamento CONSISTENTE em todas as seções!")
            else:
                print("\n❌ Temperamento INCONSISTENTE entre seções!")
        else:
            print("\n⚠️ Apenas uma seção menciona temperamento")
    else:
        print("⚠️ Nenhuma menção de temperamento encontrada nas seções")
    
    print("=" * 80)


def test_full_birth_chart():
    """Testa a geração do mapa astral completo."""
    print("=" * 80)
    print("🧪 TESTE 2: MAPA ASTRAL COMPLETO - JOÃO PEDRO OLIVEIRA")
    print("=" * 80)
    print(f"URL: {API_ENDPOINT}")
    print(f"Data de Teste: {datetime.now().isoformat()}")
    print(f"Dados Fictícios:")
    print(f"  Nome: {TEST_DATA['name']}")
    print(f"  Data: {TEST_DATA['birthDate']} às {TEST_DATA['birthTime']}")
    print(f"  Local: {TEST_DATA['birthPlace']}")
    print(f"  Sol: {TEST_DATA['sunSign']} | Lua: {TEST_DATA['moonSign']} | Asc: {TEST_DATA['ascendant']}")
    print("=" * 80)
    
    try:
        print("\n📤 Enviando requisição...")
        response = requests.post(
            API_ENDPOINT,
            json=TEST_DATA,
            headers={"Content-Type": "application/json"},
            timeout=300
        )
        
        print(f"📥 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print("\n✅ Resposta recebida com sucesso!")
            print(f"  Nome: {data.get('name', 'N/A')}")
            print(f"  Gerado em: {data.get('generated_at', 'N/A')}")
            print(f"  Número de seções: {len(data.get('sections', []))}")
            
            sections = data.get('sections', [])
            
            print("\n" + "=" * 80)
            print("📋 VALIDAÇÃO DE SEÇÕES")
            print("=" * 80)
            
            found_sections = {s.get('section') for s in sections}
            missing_sections = set(EXPECTED_SECTIONS) - found_sections
            
            if missing_sections:
                print(f"❌ Seções faltando: {', '.join(missing_sections)}")
            else:
                print("✅ Todas as seções esperadas foram geradas!")
            
            print(f"\nSeções encontradas: {', '.join(sorted(found_sections))}")
            
            validate_temperament_consistency(sections)
            
            # Salvar resultado
            output_file = f"test_birth_chart_2_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"\n💾 Resultado salvo em: {output_file}")
            
            return True
            
        else:
            print(f"\n❌ Erro na requisição!")
            print(f"  Status Code: {response.status_code}")
            print(f"  Resposta: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_full_birth_chart()
    
    if success:
        print("\n" + "=" * 80)
        print("✅ TESTE 2 CONCLUÍDO COM SUCESSO!")
        print("=" * 80)
    else:
        print("\n" + "=" * 80)
        print("❌ TESTE 2 FALHOU!")
        print("=" * 80)
        exit(1)

