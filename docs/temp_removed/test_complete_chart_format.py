#!/usr/bin/env python3
"""
Script para testar o formato do endpoint /api/interpretation/complete-chart
e verificar se o formato está correto (com degree_dms).
"""

import requests
import json
import sys
from datetime import datetime

# Configuração
API_BASE_URL = "http://localhost:8000"

def test_complete_chart_format():
    """Testa o formato do endpoint complete-chart"""
    
    print("=" * 80)
    print("🧪 TESTE DO FORMATO DO MAPA ASTRAL COMPLETO")
    print("=" * 80)
    print(f"API URL: {API_BASE_URL}")
    print(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Dados de teste (mesmos dados das imagens)
    test_data = {
        "birth_date": "20/10/1981",
        "birth_time": "13:30",
        "latitude": -3.6883,  # Sobral, CE
        "longitude": -40.3497,
        "birth_place": "Sobral, Ceará, Brasil",
        "name": "Teste Usuário"
    }
    
    endpoint = f"{API_BASE_URL}/api/interpretation/complete-chart"
    
    print(f"📋 DADOS DE TESTE:")
    print(f"   Nome: {test_data['name']}")
    print(f"   Data: {test_data['birth_date']} às {test_data['birth_time']}")
    print(f"   Local: {test_data['birth_place']}")
    print(f"   Coordenadas: ({test_data['latitude']}, {test_data['longitude']})")
    print()
    
    try:
        print(f"🔗 Endpoint: {endpoint}")
        print(f"📤 Enviando requisição...")
        
        response = requests.post(
            endpoint,
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📥 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCESSO!")
            print()
            
            # Verificar formato de planets_in_signs
            print(f"📊 PLANETAS EM SIGNOS ({len(data.get('planets_in_signs', []))} planetas):")
            print("-" * 80)
            
            for planet in data.get('planets_in_signs', [])[:5]:  # Mostrar primeiros 5
                planet_name = planet.get('planet', 'N/A')
                sign = planet.get('sign', 'N/A')
                degree_dms = planet.get('degree_dms', 'N/A')
                house = planet.get('house', 'N/A')
                
                # Formato esperado: "Planeta em Signo 27° 11' 30'' • Casa"
                formatted = f"{planet_name} em {sign} {degree_dms} • {get_house_name(house)}"
                
                print(f"   ✅ {formatted}")
                print(f"      - degree_dms: {degree_dms}")
                print(f"      - degree: {planet.get('degree', 'N/A')}")
                print(f"      - house: {house}")
                print()
            
            # Verificar formato de special_points
            print(f"📊 PONTOS ESPECIAIS ({len(data.get('special_points', []))} pontos):")
            print("-" * 80)
            
            for point in data.get('special_points', []):
                point_name = point.get('point', 'N/A')
                sign = point.get('sign', 'N/A')
                degree_dms = point.get('degree_dms', 'N/A')
                house = point.get('house', 'N/A')
                
                # Formato esperado: "Ponto em Signo 27° 11' 30'' • Casa"
                formatted = f"{point_name} em {sign} {degree_dms} • {get_house_name(house)}"
                
                print(f"   ✅ {formatted}")
                print(f"      - degree_dms: {degree_dms}")
                print(f"      - degree: {point.get('degree', 'N/A')}")
                print(f"      - house: {house}")
                print()
            
            # Verificar se todos têm degree_dms
            all_planets = data.get('planets_in_signs', [])
            all_points = data.get('special_points', [])
            
            missing_dms_planets = [p.get('planet') for p in all_planets if not p.get('degree_dms')]
            missing_dms_points = [p.get('point') for p in all_points if not p.get('degree_dms')]
            
            if missing_dms_planets or missing_dms_points:
                print(f"⚠️  PROBLEMAS ENCONTRADOS:")
                if missing_dms_planets:
                    print(f"   ❌ Planetas sem degree_dms: {', '.join(missing_dms_planets)}")
                if missing_dms_points:
                    print(f"   ❌ Pontos sem degree_dms: {', '.join(missing_dms_points)}")
            else:
                print(f"✅ TODOS OS ITENS TÊM degree_dms FORMATADO CORRETAMENTE!")
            
            # Verificar formato do degree_dms
            print()
            print(f"🔍 VALIDAÇÃO DO FORMATO degree_dms:")
            print("-" * 80)
            
            all_items = all_planets + all_points
            format_errors = []
            
            for item in all_items:
                degree_dms = item.get('degree_dms', '')
                if degree_dms:
                    # Verificar se está no formato "X° Y' Z''"
                    import re
                    pattern = r'^\d+°\s+\d{2}\'\s+\d{2}"$'
                    if not re.match(pattern, degree_dms):
                        item_name = item.get('planet') or item.get('point', 'Desconhecido')
                        format_errors.append(f"{item_name}: '{degree_dms}' (formato incorreto)")
            
            if format_errors:
                print(f"   ❌ Erros de formato encontrados:")
                for error in format_errors:
                    print(f"      - {error}")
            else:
                print(f"   ✅ Todos os degree_dms estão no formato correto: 'X° Y' Z\"'")
            
            # Exemplo de formato esperado no frontend
            print()
            print(f"📋 EXEMPLO DE FORMATO ESPERADO NO FRONTEND:")
            print("-" * 80)
            if all_planets:
                example = all_planets[0]
                example_formatted = f"{example.get('planet')} em {example.get('sign')} {example.get('degree_dms')} • {get_house_name(example.get('house'))}"
                print(f"   {example_formatted}")
            
            return 0
        else:
            print(f"❌ ERRO!")
            print(f"   Status: {response.status_code}")
            print(f"   Resposta: {response.text[:500]}")
            return 1
            
    except requests.exceptions.ConnectionError:
        print(f"❌ ERRO: Não foi possível conectar ao servidor")
        print(f"   Verifique se o backend está rodando em {API_BASE_URL}")
        return 1
    except Exception as e:
        print(f"❌ ERRO: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

def get_house_name(house_num: int) -> str:
    """Retorna o nome da casa em português"""
    house_names = {
        1: 'Primeira Casa',
        2: 'Segunda Casa',
        3: 'Terceira Casa',
        4: 'Quarta Casa',
        5: 'Quinta Casa',
        6: 'Sexta Casa',
        7: 'Sétima Casa',
        8: 'Oitava Casa',
        9: 'Nona Casa',
        10: 'Décima Casa',
        11: 'Décima Primeira Casa',
        12: 'Décima Segunda Casa',
    }
    return house_names.get(house_num, f'Casa {house_num}')

if __name__ == "__main__":
    try:
        exit_code = test_complete_chart_format()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Teste interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

