#!/usr/bin/env python3
"""
Script completo de validação do sistema de interpretação astrológica.
Testa cálculos, interpretações e referências do RAG e numerologia.
"""

import sys
import os
import json
from datetime import datetime
from pathlib import Path

# Adicionar o diretório backend ao path
sys.path.insert(0, os.path.dirname(__file__))

from app.services.astrology_calculator import calculate_birth_chart
from app.services.precomputed_chart_engine import (
    calculate_temperament_from_chart,
    get_planet_dignity,
    get_chart_ruler
)
from app.services.rag_service_fastembed import get_rag_service
from app.services.local_knowledge_base import LocalKnowledgeBase

# Dados de teste - pessoa fictícia
TEST_DATA = {
    "name": "Maria Silva",
    "birthDate": "1990-05-15",
    "birthTime": "14:30",
    "birthPlace": "São Paulo, SP, Brasil",
    "latitude": -23.5505,
    "longitude": -46.6333,
    "language": "pt"
}

def print_section(title):
    """Imprime um título de seção formatado."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def validate_calculations(chart_data):
    """Valida os cálculos astronômicos."""
    print_section("1. VALIDAÇÃO DOS CÁLCULOS ASTRONÔMICOS")
    
    errors = []
    warnings = []
    
    # Verificar se todos os planetas principais foram calculados
    required_planets = ['sun', 'moon', 'mercury', 'venus', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune', 'pluto']
    for planet in required_planets:
        sign_key = f"{planet}_sign"
        degree_key = f"{planet}_degree"
        
        if sign_key not in chart_data or not chart_data[sign_key]:
            errors.append(f"❌ {planet.capitalize()}: signo não calculado")
        elif degree_key not in chart_data or chart_data[degree_key] is None:
            warnings.append(f"⚠️ {planet.capitalize()}: grau não calculado")
        else:
            print(f"✅ {planet.capitalize()}: {chart_data[sign_key]} ({chart_data[degree_key]:.2f}°)")
    
    # Verificar ascendente
    if 'ascendant_sign' not in chart_data or not chart_data['ascendant_sign']:
        errors.append("❌ Ascendente: não calculado")
    else:
        print(f"✅ Ascendente: {chart_data['ascendant_sign']} ({chart_data.get('ascendant_degree', 0):.2f}°)")
    
    # Verificar casas
    required_houses = ['sun_house', 'moon_house', 'mercury_house', 'venus_house', 'mars_house']
    for house_key in required_houses:
        planet = house_key.replace('_house', '').replace('_', ' ').title()
        if house_key not in chart_data or chart_data[house_key] is None:
            warnings.append(f"⚠️ Casa de {planet}: não calculada")
        else:
            print(f"✅ Casa de {planet}: Casa {chart_data[house_key]}")
    
    if errors:
        print("\n❌ ERROS ENCONTRADOS:")
        for error in errors:
            print(f"  {error}")
    
    if warnings:
        print("\n⚠️ AVISOS:")
        for warning in warnings:
            print(f"  {warning}")
    
    return len(errors) == 0

def validate_temperament(chart_data):
    """Valida o cálculo do temperamento."""
    print_section("2. VALIDAÇÃO DO TEMPERAMENTO (FILTRO DE ARROYO)")
    
    try:
        temperament = calculate_temperament_from_chart(chart_data, 'pt')
        
        # A função retorna {'points': {...}, 'dominant': ..., 'lacking': ...}
        points = temperament.get('points', {})
        dominant = temperament.get('dominant', 'Nenhum')
        lacking = temperament.get('lacking')
        
        print(f"📊 Pontos por Elemento:")
        print(f"  🔥 Fogo: {points.get('Fogo', 0)} pontos")
        print(f"  🌍 Terra: {points.get('Terra', 0)} pontos")
        print(f"  💨 Ar: {points.get('Ar', 0)} pontos")
        print(f"  💧 Água: {points.get('Água', 0)} pontos")
        
        print(f"\n🎯 Elemento Dominante: {dominant}")
        print(f"🎯 Elemento Ausente: {lacking if lacking else 'Nenhum'}")
        
        # Validar lógica do elemento ausente
        if lacking:
            lacking_points = points.get(lacking, -1)
            if lacking_points != 0:
                print(f"\n❌ ERRO: Elemento ausente '{lacking}' tem {lacking_points} pontos, deveria ter 0!")
                return False
            else:
                print(f"✅ Validação: Elemento ausente '{lacking}' tem 0 pontos (correto)")
        
        # Verificar se há outros elementos com 0 pontos não identificados
        for element, pts in points.items():
            if pts == 0 and element != lacking:
                print(f"⚠️ AVISO: Elemento '{element}' também tem 0 pontos mas não foi identificado como ausente")
        
        # Mostrar contribuições dos planetas
        contributions = temperament.get('contributions', [])
        if contributions:
            print(f"\n📋 Contribuições dos Planetas:")
            for contrib in contributions[:10]:  # Mostrar apenas os primeiros 10
                print(f"  - {contrib}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao calcular temperamento: {e}")
        import traceback
        traceback.print_exc()
        return False

def validate_dignities(chart_data):
    """Valida o cálculo das dignidades."""
    print_section("3. VALIDAÇÃO DAS DIGNIDADES")
    
    try:
        planets_to_check = ['sun', 'moon', 'mercury', 'venus', 'mars', 'jupiter', 'saturn']
        
        for planet in planets_to_check:
            planet_name = planet.capitalize()
            sign_key = f"{planet}_sign"
            
            if sign_key not in chart_data or not chart_data[sign_key]:
                continue
            
            sign = chart_data[sign_key]
            dignity_type = get_planet_dignity(planet, sign)
            
            print(f"✅ {planet_name} em {sign}: {dignity_type}")
            
            # Validar lógica básica
            if sign == 'Leão' and planet == 'sun' and dignity_type != 'DOMICÍLIO':
                print(f"  ⚠️ AVISO: Sol em Leão deveria estar em Domicílio, mas está como {dignity_type}")
            elif sign == 'Câncer' and planet == 'moon' and dignity_type != 'DOMICÍLIO':
                print(f"  ⚠️ AVISO: Lua em Câncer deveria estar em Domicílio, mas está como {dignity_type}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao calcular dignidades: {e}")
        import traceback
        traceback.print_exc()
        return False

def validate_chart_ruler(chart_data):
    """Valida o cálculo do regente do mapa."""
    print_section("4. VALIDAÇÃO DO REGENTE DO MAPA")
    
    try:
        ascendant = chart_data.get('ascendant_sign', 'N/A')
        
        if not ascendant or ascendant == 'N/A':
            print("❌ Ascendente não disponível")
            return False
        
        # A função get_chart_ruler espera (ascendant_sign, chart_data)
        ruler_info = get_chart_ruler(ascendant, chart_data)
        
        if not ruler_info:
            print("❌ Regente do mapa não calculado")
            return False
        
        ruler_planet = ruler_info.get('planet', 'N/A')
        ruler_sign = ruler_info.get('sign', 'N/A')
        
        print(f"✅ Ascendente: {ascendant}")
        print(f"✅ Regente: {ruler_planet}")
        print(f"✅ Regente em: {ruler_sign}")
        
        # Validar mapeamento básico
        expected_rulers = {
            'Áries': 'Marte',
            'Touro': 'Vênus',
            'Gêmeos': 'Mercúrio',
            'Câncer': 'Lua',
            'Leão': 'Sol',
            'Virgem': 'Mercúrio',
            'Libra': 'Vênus',
            'Escorpião': 'Marte',
            'Sagitário': 'Júpiter',
            'Capricórnio': 'Saturno',
            'Aquário': 'Urano',
            'Peixes': 'Netuno'
        }
        
        expected = expected_rulers.get(ascendant)
        if expected and ruler_planet != expected:
            print(f"❌ ERRO: Regente esperado para {ascendant} é {expected}, mas foi calculado {ruler_planet}")
            return False
        else:
            print(f"✅ Validação: Regente correto para {ascendant}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao calcular regente: {e}")
        import traceback
        traceback.print_exc()
        return False

def validate_rag_references():
    """Valida se o RAG está funcionando e tem referências."""
    print_section("5. VALIDAÇÃO DO RAG (BASE DE CONHECIMENTO)")
    
    try:
        rag_service = get_rag_service()
        
        if not rag_service:
            print("❌ Serviço RAG não disponível")
            return False
        
        # Testar busca por elementos
        test_queries = [
            "elemento fogo predominante",
            "elemento terra ausente",
            "temperamento astrológico",
            "dignidades planetárias"
        ]
        
        print("🔍 Testando buscas no RAG:")
        for query in test_queries:
            try:
                results = rag_service.search(query, top_k=3)
                if results and len(results) > 0:
                    print(f"  ✅ '{query}': {len(results)} resultados encontrados")
                else:
                    print(f"  ⚠️ '{query}': Nenhum resultado encontrado")
            except Exception as e:
                print(f"  ❌ '{query}': Erro - {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao validar RAG: {e}")
        import traceback
        traceback.print_exc()
        return False

def validate_local_knowledge_base():
    """Valida a base de conhecimento local."""
    print_section("6. VALIDAÇÃO DA BASE DE CONHECIMENTO LOCAL")
    
    try:
        kb = LocalKnowledgeBase()
        
        # Testar busca por elementos
        test_queries = [
            "elemento fogo predominante",
            "elemento terra ausente",
            "elemento ar predominante",
            "elemento água ausente"
        ]
        
        print("🔍 Testando base de conhecimento local:")
        for query in test_queries:
            try:
                result = kb.get_context(query=query)
                if result and len(result) > 0:
                    print(f"  ✅ '{query}': {len(result)} resultados encontrados")
                else:
                    print(f"  ⚠️ '{query}': Nenhum resultado encontrado")
            except Exception as e:
                print(f"  ❌ '{query}': Erro - {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao validar base de conhecimento local: {e}")
        import traceback
        traceback.print_exc()
        return False

def validate_numerology_references():
    """Valida se os arquivos de numerologia existem."""
    print_section("7. VALIDAÇÃO DOS ARQUIVOS DE NUMEROLOGIA")
    
    numerology_dir = Path(__file__).parent / "numerologia"
    
    if not numerology_dir.exists():
        print(f"❌ Diretório de numerologia não encontrado: {numerology_dir}")
        return False
    
    pdf_files = list(numerology_dir.glob("*.pdf"))
    
    if not pdf_files:
        print(f"⚠️ Nenhum arquivo PDF encontrado em {numerology_dir}")
        return False
    
    print(f"✅ {len(pdf_files)} arquivos PDF encontrados:")
    for pdf_file in pdf_files[:5]:  # Mostrar apenas os primeiros 5
        print(f"  - {pdf_file.name}")
    
    if len(pdf_files) > 5:
        print(f"  ... e mais {len(pdf_files) - 5} arquivos")
    
    return True

def validate_validation_files():
    """Valida os arquivos de validação."""
    print_section("8. VALIDAÇÃO DOS ARQUIVOS DE VALIDAÇÃO")
    
    validation_dir = Path(__file__).parent.parent / "docs" / "validation"
    
    if not validation_dir.exists():
        print(f"❌ Diretório de validação não encontrado: {validation_dir}")
        return False
    
    required_files = [
        "power_pt.txt",
        "triad_pt.txt",
        "personal_pt.txt",
        "houses_pt.txt",
        "karma_pt.txt",
        "synthesis_pt.txt"
    ]
    
    print("📄 Verificando arquivos de validação:")
    all_exist = True
    
    for file_name in required_files:
        file_path = validation_dir / file_name
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"  ✅ {file_name}: {size} bytes")
        else:
            print(f"  ❌ {file_name}: Não encontrado")
            all_exist = False
    
    return all_exist

def main():
    """Função principal de validação."""
    print("\n" + "=" * 80)
    print("  VALIDAÇÃO COMPLETA DO SISTEMA DE INTERPRETAÇÃO ASTROLÓGICA")
    print("=" * 80)
    
    print(f"\n📋 Dados de Teste:")
    print(f"  Nome: {TEST_DATA['name']}")
    print(f"  Data: {TEST_DATA['birthDate']}")
    print(f"  Hora: {TEST_DATA['birthTime']}")
    print(f"  Local: {TEST_DATA['birthPlace']}")
    
    # Calcular mapa astral
    print_section("CALCULANDO MAPA ASTRAL")
    
    try:
        birth_date = datetime.strptime(TEST_DATA['birthDate'], '%Y-%m-%d')
        chart_data = calculate_birth_chart(
            birth_date=birth_date,
            birth_time=TEST_DATA['birthTime'],
            latitude=TEST_DATA['latitude'],
            longitude=TEST_DATA['longitude']
        )
        
        print("✅ Mapa astral calculado com sucesso!")
        
        # Salvar dados calculados para referência
        output_file = Path(__file__).parent / "test_chart_data.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(chart_data, f, indent=2, ensure_ascii=False, default=str)
        print(f"💾 Dados salvos em: {output_file}")
        
    except Exception as e:
        print(f"❌ Erro ao calcular mapa astral: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Executar todas as validações
    results = {}
    
    results['calculations'] = validate_calculations(chart_data)
    results['temperament'] = validate_temperament(chart_data)
    results['dignities'] = validate_dignities(chart_data)
    results['chart_ruler'] = validate_chart_ruler(chart_data)
    results['rag'] = validate_rag_references()
    results['local_kb'] = validate_local_knowledge_base()
    results['numerology'] = validate_numerology_references()
    results['validation_files'] = validate_validation_files()
    
    # Resumo final
    print_section("RESUMO DA VALIDAÇÃO")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    failed = total - passed
    
    print(f"✅ Testes Passados: {passed}/{total}")
    print(f"❌ Testes Falhados: {failed}/{total}")
    
    print("\n📊 Detalhes:")
    for test_name, result in results.items():
        status = "✅" if result else "❌"
        print(f"  {status} {test_name.replace('_', ' ').title()}")
    
    if failed == 0:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
    else:
        print(f"\n⚠️ {failed} TESTE(S) FALHARAM - Verifique os erros acima")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

