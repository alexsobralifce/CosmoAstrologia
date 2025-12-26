#!/usr/bin/env python3
"""
Script para recalcular o mapa astral completo de Francisco Alexandre Araujo Rocha
usando Swiss Ephemeris e validar todos os dados.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from datetime import datetime
from app.services.chart_validator import validate_complete_chart, ChartValidationError
from app.services.precomputed_chart_engine import calculate_temperament_from_chart, SIGN_TO_ELEMENT

# Dados de nascimento de Francisco
BIRTH_DATE = datetime(1981, 10, 20)
BIRTH_TIME = "13:30"
LATITUDE = -3.6883  # Sobral, Ceará
LONGITUDE = -40.3497

print("=" * 80)
print("RECÁLCULO E VALIDAÇÃO DO MAPA ASTRAL")
print("FRANCISCO ALEXANDRE ARAUJO ROCHA")
print("=" * 80)

try:
    # Recalcular e validar mapa completo
    print("\n📊 Recalculando mapa completo usando Swiss Ephemeris...")
    chart_data = validate_complete_chart(
        birth_date=BIRTH_DATE,
        birth_time=BIRTH_TIME,
        latitude=LATITUDE,
        longitude=LONGITUDE
    )
    
    print("✅ Mapa recalculado e validado com sucesso!")
    
    # Exibir resultados
    print("\n" + "=" * 80)
    print("POSIÇÕES PLANETÁRIAS (CALCULADAS)")
    print("=" * 80)
    
    planets = [
        ('sun', 'Sol'),
        ('moon', 'Lua'),
        ('mercury', 'Mercúrio'),
        ('venus', 'Vênus'),
        ('mars', 'Marte'),
        ('jupiter', 'Júpiter'),
        ('saturn', 'Saturno'),
        ('uranus', 'Urano'),
        ('neptune', 'Netuno'),
        ('pluto', 'Plutão'),
    ]
    
    for planet_key, planet_name in planets:
        sign_key = f"{planet_key}_sign"
        degree_key = f"{planet_key}_degree"
        house_key = f"{planet_key}_house"
        
        sign = chart_data.get(sign_key)
        degree = chart_data.get(degree_key, 0)
        house = chart_data.get(house_key)
        
        print(f"{planet_name:12} | {sign:12} | {degree:5.2f}° | Casa {house:2}")
    
    print("\n" + "=" * 80)
    print("PONTOS ESPECIAIS")
    print("=" * 80)
    
    print(f"Ascendente:  {chart_data.get('ascendant_sign'):12} | {chart_data.get('ascendant_degree', 0):5.2f}° | Casa 1")
    print(f"Meio do Céu: {chart_data.get('midheaven_sign'):12} | {chart_data.get('midheaven_degree', 0):5.2f}°")
    print(f"Nodo Norte:  {chart_data.get('north_node_sign'):12} | {chart_data.get('north_node_degree', 0):5.2f}°")
    print(f"Nodo Sul:    {chart_data.get('south_node_sign'):12} | {chart_data.get('south_node_degree', 0):5.2f}°")
    print(f"Quíron:      {chart_data.get('chiron_sign'):12} | {chart_data.get('chiron_degree', 0):5.2f}°")
    
    # Temperamento validado
    print("\n" + "=" * 80)
    print("TEMPERAMENTO (CALCULADO E VALIDADO)")
    print("=" * 80)
    
    temperament = chart_data.get('_validated_temperament', {})
    points = temperament.get('points', {})
    
    print(f"\nPontuação por elemento:")
    print(f"  Fogo:  {points.get('Fogo', 0):2} pontos")
    print(f"  Terra: {points.get('Terra', 0):2} pontos")
    print(f"  Ar:    {points.get('Ar', 0):2} pontos")
    print(f"  Água:  {points.get('Água', 0):2} pontos")
    
    print(f"\nElemento Dominante: {temperament.get('dominant', 'N/A')}")
    print(f"Elemento Ausente:   {temperament.get('lacking', 'Nenhum') if temperament.get('lacking') else 'Nenhum (todos presentes)'}")
    
    print(f"\nContribuições detalhadas:")
    for contribution in temperament.get('contributions', []):
        print(f"  • {contribution}")
    
    # Regente validado
    print("\n" + "=" * 80)
    print("REGENTE DO MAPA (VALIDADO)")
    print("=" * 80)
    
    ruler_info = chart_data.get('_validated_ruler', {})
    print(f"Ascendente: {chart_data.get('ascendant_sign')}")
    print(f"Regente:    {ruler_info.get('planet', 'N/A')}")
    print(f"Regente em: {ruler_info.get('sign', 'N/A')}")
    
    # Verificar casa do regente
    if ruler_info.get('planet') == 'Urano':
        uranus_house = chart_data.get('uranus_house')
        print(f"Regente na Casa: {uranus_house}")
    
    # Resumo de validação
    print("\n" + "=" * 80)
    print("RESUMO DE VALIDAÇÃO")
    print("=" * 80)
    
    print(f"✅ Mapa validado: {chart_data.get('_validated', False)}")
    print(f"✅ Temperamento calculado: {bool(temperament)}")
    print(f"✅ Regente identificado: {bool(ruler_info)}")
    print(f"✅ Todas as casas calculadas: {all(chart_data.get(f'{p[0]}_house') for p in planets)}")
    
    # Salvar dados validados em arquivo JSON
    import json
    output_file = "francisco_chart_validated.json"
    
    # Preparar dados para JSON (remover objetos não serializáveis)
    json_data = {
        'name': 'Francisco Alexandre Araujo Rocha',
        'birth_date': BIRTH_DATE.isoformat(),
        'birth_time': BIRTH_TIME,
        'latitude': LATITUDE,
        'longitude': LONGITUDE,
        'planets': {},
        'special_points': {},
        'temperament': {
            'points': points,
            'dominant': temperament.get('dominant'),
            'lacking': temperament.get('lacking'),
            'contributions': temperament.get('contributions', [])
        },
        'ruler': ruler_info,
        'validated': True
    }
    
    for planet_key, planet_name in planets:
        sign_key = f"{planet_key}_sign"
        degree_key = f"{planet_key}_degree"
        house_key = f"{planet_key}_house"
        
        json_data['planets'][planet_key] = {
            'name': planet_name,
            'sign': chart_data.get(sign_key),
            'degree': chart_data.get(degree_key, 0),
            'house': chart_data.get(house_key)
        }
    
    json_data['special_points'] = {
        'ascendant': {
            'sign': chart_data.get('ascendant_sign'),
            'degree': chart_data.get('ascendant_degree', 0),
            'house': 1
        },
        'midheaven': {
            'sign': chart_data.get('midheaven_sign'),
            'degree': chart_data.get('midheaven_degree', 0)
        },
        'north_node': {
            'sign': chart_data.get('north_node_sign'),
            'degree': chart_data.get('north_node_degree', 0)
        },
        'south_node': {
            'sign': chart_data.get('south_node_sign'),
            'degree': chart_data.get('south_node_degree', 0)
        },
        'chiron': {
            'sign': chart_data.get('chiron_sign'),
            'degree': chart_data.get('chiron_degree', 0)
        }
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Dados validados salvos em: {output_file}")
    
    print("\n" + "=" * 80)
    print("✅ RECÁLCULO E VALIDAÇÃO CONCLUÍDOS COM SUCESSO!")
    print("=" * 80)
    
except ChartValidationError as e:
    print(f"\n❌ ERRO DE VALIDAÇÃO: {e}")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ ERRO: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

