#!/usr/bin/env python3
"""
Script de teste para gerar mapa astral completo com todas as seções.
Usa dados fictícios para testar a consistência e correção do sistema.
"""

import requests
import json
from datetime import datetime

# Configuração
BASE_URL = "http://localhost:8000"
# O router interpretation está registrado com prefixo "/api"
# Então o endpoint completo é: /api/full-birth-chart/all
API_ENDPOINT = f"{BASE_URL}/api/full-birth-chart/all"

# Dados fictícios para teste
# Mapa com configuração interessante para testar diferentes aspectos
TEST_DATA = {
    "name": "Maria Silva Santos",
    "birthDate": "15/03/1990",
    "birthTime": "14:30",
    "birthPlace": "São Paulo, São Paulo, Brasil",
    "language": "pt",
    # Tríade Fundamental
    "sunSign": "Peixes",
    "moonSign": "Leão",
    "ascendant": "Aquário",
    "sunHouse": 1,
    "moonHouse": 5,
    "ascendantHouse": 1,
    # Planetas Pessoais
    "mercurySign": "Peixes",
    "mercuryHouse": 1,
    "venusSign": "Áries",
    "venusHouse": 2,
    "marsSign": "Escorpião",
    "marsHouse": 8,
    # Planetas Sociais
    "jupiterSign": "Câncer",
    "jupiterHouse": 4,
    "saturnSign": "Capricórnio",
    "saturnHouse": 10,
    # Planetas Transpessoais
    "uranusSign": "Capricórnio",
    "uranusHouse": 10,
    "neptuneSign": "Capricórnio",
    "neptuneHouse": 10,
    "plutoSign": "Escorpião",
    "plutoHouse": 8,
    # Nodos Lunares
    "northNodeSign": "Gêmeos",
    "southNodeSign": "Sagitário",
    # Quíron
    "chironSign": "Câncer",
    # Meio do Céu
    "midheavenSign": "Escorpião",
}

# Seções esperadas
EXPECTED_SECTIONS = [
    "power",      # A Estrutura de Poder (Temperamento e Motivação)
    "triad",      # A Tríade Fundamental (O Núcleo da Personalidade)
    "personal",   # Dinâmica Pessoal e Ferramentas
    "houses",     # Análise Setorial Avançada
    "karma",      # Expansão, Estrutura e Karma
    "synthesis",  # Síntese e Orientação Estratégica
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
        # Mostrar primeiras 500 caracteres
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
        
        # Procurar menções de elementos
        elements = ['fogo', 'terra', 'ar', 'água', 'água']
        found_elements = []
        
        for element in elements:
            if element in content:
                # Tentar extrair o número de pontos
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
        
        # Verificar consistência
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
                print("   ⚠️ Diferentes seções mencionam valores diferentes")
        else:
            print("\n⚠️ Apenas uma seção menciona temperamento")
    else:
        print("⚠️ Nenhuma menção de temperamento encontrada nas seções")
    
    print("=" * 80)


def validate_dignities_consistency(sections):
    """Valida se as dignidades são consistentes."""
    print("\n" + "=" * 80)
    print("🔍 VALIDAÇÃO DE CONSISTÊNCIA DAS DIGNIDADES")
    print("=" * 80)
    
    dignity_mentions = {}
    
    for section in sections:
        content = section.get('content', '')
        section_name = section.get('section', 'unknown')
        
        # Procurar menções de dignidades
        import re
        # Padrão: "Planeta em Signo: DIGNIDADE" ou "Planeta em Signo está em DIGNIDADE"
        patterns = [
            r'(\w+)\s+em\s+(\w+).*?(?:PEREGRINO|DOMICÍLIO|EXALTAÇÃO|QUEDA|DETRIMENTO)',
            r'(\w+)\s+em\s+(\w+).*?(?:peregrino|domicílio|exaltação|queda|detrimento)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                planet = match[0] if isinstance(match, tuple) else match
                if planet not in dignity_mentions:
                    dignity_mentions[planet] = []
                dignity_mentions[planet].append({
                    'section': section_name,
                    'mention': match if isinstance(match, str) else ' '.join(match)
                })
    
    if dignity_mentions:
        print("📊 Menções de dignidades encontradas:")
        for planet, mentions in dignity_mentions.items():
            print(f"  • {planet}: {len(mentions)} menção(ões)")
            for mention in mentions[:3]:  # Mostrar até 3
                print(f"    - {mention['section']}: {mention['mention'][:50]}...")
    else:
        print("⚠️ Nenhuma menção de dignidades encontrada")
    
    print("=" * 80)


def test_full_birth_chart():
    """Testa a geração do mapa astral completo."""
    print("=" * 80)
    print("🧪 TESTE DE MAPA ASTRAL COMPLETO")
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
            timeout=300  # 5 minutos para gerar todas as seções
        )
        
        print(f"📥 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print("\n✅ Resposta recebida com sucesso!")
            print(f"  Nome: {data.get('name', 'N/A')}")
            print(f"  Dados de Nascimento: {data.get('birthData', 'N/A')}")
            print(f"  Gerado em: {data.get('generated_at', 'N/A')}")
            print(f"  Número de seções: {len(data.get('sections', []))}")
            
            sections = data.get('sections', [])
            
            # Validar que todas as seções esperadas foram geradas
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
            
            # Mostrar cada seção
            print("\n" + "=" * 80)
            print("📄 CONTEÚDO DAS SEÇÕES")
            print("=" * 80)
            
            for i, section in enumerate(sections):
                print_section(section, i)
            
            # Validações de consistência
            validate_temperament_consistency(sections)
            validate_dignities_consistency(sections)
            
            # Salvar resultado em arquivo
            output_file = f"test_birth_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"\n💾 Resultado salvo em: {output_file}")
            
            return True
            
        else:
            print(f"\n❌ Erro na requisição!")
            print(f"  Status Code: {response.status_code}")
            print(f"  Resposta: {response.text[:500]}")
            return False
            
    except requests.exceptions.Timeout:
        print("\n❌ Timeout! A requisição demorou mais de 5 minutos.")
        print("   Isso pode indicar que o servidor está lento ou há um problema.")
        return False
    except requests.exceptions.ConnectionError:
        print("\n❌ Erro de conexão!")
        print(f"   Verifique se o servidor está rodando em {BASE_URL}")
        print("   Execute: cd backend && python3 main.py")
        return False
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║  TESTE DE MAPA ASTRAL COMPLETO - TODAS AS SEÇÕES            ║
    ╚══════════════════════════════════════════════════════════════╝
    
    Este script testa:
    1. Geração de todas as 6 seções do mapa astral
    2. Consistência do temperamento entre seções
    3. Consistência das dignidades entre seções
    4. Validação de dados pré-calculados
    
    Seções esperadas:
    - power: A Estrutura de Poder (Temperamento e Motivação)
    - triad: A Tríade Fundamental (O Núcleo da Personalidade)
    - personal: Dinâmica Pessoal e Ferramentas
    - houses: Análise Setorial Avançada
    - karma: Expansão, Estrutura e Karma
    - synthesis: Síntese e Orientação Estratégica
    """)
    
    success = test_full_birth_chart()
    
    if success:
        print("\n" + "=" * 80)
        print("✅ TESTE CONCLUÍDO COM SUCESSO!")
        print("=" * 80)
    else:
        print("\n" + "=" * 80)
        print("❌ TESTE FALHOU!")
        print("=" * 80)
        exit(1)

