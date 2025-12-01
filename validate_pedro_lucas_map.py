#!/usr/bin/env python3
"""
Script de Validação do Mapa Astral de Pedro Lucas Ribeiro Rocha
Valida todos os dados fornecidos contra os cálculos do sistema.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from datetime import datetime
from app.services.astrology_calculator import calculate_birth_chart
from app.services.precomputed_chart_engine import (
    calculate_temperament_from_chart,
    get_planet_dignity,
    get_chart_ruler,
    PLANET_DIGNITIES
)

# Dados de nascimento fornecidos
BIRTH_DATA = {
    'date': datetime(2011, 7, 19),
    'time': '22:45',
    'place': 'Sobral, Ceará, Brasil',
    'latitude': -3.6883,  # Latitude aproximada de Sobral
    'longitude': -40.3489  # Longitude aproximada de Sobral
}

# Dados fornecidos pelo usuário (para comparação)
PROVIDED_DATA = {
    'temperament': {
        'Água': 8,
        'Fogo': 0,  # Dados dizem que Fogo não está presente
        'Terra': 2,
        'Ar': 2
    },
    'temperament_dominant': 'Água',
    'ruler': 'Marte',
    'ruler_sign': 'Gêmeos',
    'dignities': {
        'Sol': ('Câncer', 'PEREGRINO'),
        'Lua': ('Peixes', 'PEREGRINO'),
        'Mercúrio': ('Leão', 'PEREGRINO'),
        'Vênus': ('Câncer', 'PEREGRINO'),
        'Marte': ('Gêmeos', 'PEREGRINO'),
        'Júpiter': ('Touro', 'PEREGRINO'),
        'Saturno': ('Libra', 'EXALTAÇÃO'),
        'Urano': ('Áries', 'PEREGRINO'),
        'Netuno': ('Peixes', 'DOMICÍLIO'),
        'Plutão': ('Capricórnio', 'PEREGRINO'),
    },
    'positions': {
        'Sol': 'Câncer',
        'Lua': 'Peixes',
        'Mercúrio': 'Leão',
        'Vênus': 'Câncer',
        'Marte': 'Gêmeos',
        'Júpiter': 'Touro',
        'Saturno': 'Libra',
        'Urano': 'Áries',
        'Netuno': 'Peixes',
        'Plutão': 'Capricórnio',
    }
}

def dignity_to_portuguese(dignity: str) -> str:
    """Converte dignidade em inglês para português."""
    mapping = {
        'domicile': 'DOMICÍLIO',
        'exaltation': 'EXALTAÇÃO',
        'detriment': 'DETRIMENTO',
        'fall': 'QUEDA',
        'peregrine': 'PEREGRINO'
    }
    return mapping.get(dignity, dignity.upper())


def validate_map():
    """Valida o mapa completo de Pedro Lucas."""
    print("=" * 80)
    print("VALIDAÇÃO DO MAPA ASTRAL - PEDRO LUCAS RIBEIRO ROCHA")
    print("=" * 80)
    print(f"\n📅 Data: {BIRTH_DATA['date'].strftime('%d/%m/%Y')}")
    print(f"🕐 Hora: {BIRTH_DATA['time']}")
    print(f"📍 Local: {BIRTH_DATA['place']}")
    print(f"🌍 Coordenadas: {BIRTH_DATA['latitude']}, {BIRTH_DATA['longitude']}")
    print("\n" + "=" * 80)
    
    # Calcular mapa astral
    print("\n📊 CALCULANDO MAPA ASTRAL...")
    chart_data = calculate_birth_chart(
        birth_date=BIRTH_DATA['date'],
        birth_time=BIRTH_DATA['time'],
        latitude=BIRTH_DATA['latitude'],
        longitude=BIRTH_DATA['longitude'],
        use_swiss_ephemeris=True
    )
    
    # Exibir posições calculadas
    print("\n🔍 POSIÇÕES CALCULADAS:")
    print(f"  • Sol: {chart_data.get('sun_sign')} ({chart_data.get('sun_degree', 0):.1f}°)")
    print(f"  • Lua: {chart_data.get('moon_sign')} ({chart_data.get('moon_degree', 0):.1f}°)")
    print(f"  • Ascendente: {chart_data.get('ascendant_sign')} ({chart_data.get('ascendant_degree', 0):.1f}°)")
    print(f"  • Mercúrio: {chart_data.get('mercury_sign')} ({chart_data.get('mercury_degree', 0):.1f}°)")
    print(f"  • Vênus: {chart_data.get('venus_sign')} ({chart_data.get('venus_degree', 0):.1f}°)")
    print(f"  • Marte: {chart_data.get('mars_sign')} ({chart_data.get('mars_degree', 0):.1f}°)")
    print(f"  • Júpiter: {chart_data.get('jupiter_sign')} ({chart_data.get('jupiter_degree', 0):.1f}°)")
    print(f"  • Saturno: {chart_data.get('saturn_sign')} ({chart_data.get('saturn_degree', 0):.1f}°)")
    print(f"  • Urano: {chart_data.get('uranus_sign')} ({chart_data.get('uranus_degree', 0):.1f}°)")
    print(f"  • Netuno: {chart_data.get('neptune_sign')} ({chart_data.get('neptune_degree', 0):.1f}°)")
    print(f"  • Plutão: {chart_data.get('pluto_sign')} ({chart_data.get('pluto_degree', 0):.1f}°)")
    
    # Validar posições planetárias
    print("\n" + "=" * 80)
    print("✅ VALIDAÇÃO DE POSIÇÕES PLANETÁRIAS:")
    print("=" * 80)
    position_errors = []
    for planet, expected_sign in PROVIDED_DATA['positions'].items():
        chart_key = {
            'Sol': 'sun_sign',
            'Lua': 'moon_sign',
            'Mercúrio': 'mercury_sign',
            'Vênus': 'venus_sign',
            'Marte': 'mars_sign',
            'Júpiter': 'jupiter_sign',
            'Saturno': 'saturn_sign',
            'Urano': 'uranus_sign',
            'Netuno': 'neptune_sign',
            'Plutão': 'pluto_sign',
        }.get(planet)
        
        calculated_sign = chart_data.get(chart_key)
        if calculated_sign == expected_sign:
            print(f"  ✅ {planet}: {calculated_sign} (CORRETO)")
        else:
            print(f"  ❌ {planet}: Esperado {expected_sign}, Calculado {calculated_sign}")
            position_errors.append((planet, expected_sign, calculated_sign))
    
    # Validar temperamento
    print("\n" + "=" * 80)
    print("🌊 VALIDAÇÃO DE TEMPERAMENTO:")
    print("=" * 80)
    temperament = calculate_temperament_from_chart(chart_data, 'pt')
    calculated_points = temperament['points']
    
    print("\n📊 PONTUAÇÃO CALCULADA:")
    for element in ['Fogo', 'Terra', 'Ar', 'Água']:
        calculated = calculated_points.get(element, 0)
        provided = PROVIDED_DATA['temperament'].get(element, 0)
        status = "✅" if calculated == provided else "❌"
        print(f"  {status} {element}: Calculado={calculated}, Fornecido={provided}")
    
    print(f"\n🎯 ELEMENTO DOMINANTE:")
    print(f"  Calculado: {temperament['dominant']}")
    print(f"  Fornecido: {PROVIDED_DATA['temperament_dominant']}")
    if temperament['dominant'] == PROVIDED_DATA['temperament_dominant']:
        print("  ✅ CORRETO")
    else:
        print("  ❌ ERRO")
    
    print(f"\n📋 CONTRIBUIÇÕES:")
    for contribution in temperament['contributions']:
        print(f"  • {contribution}")
    
    # Validar regente
    print("\n" + "=" * 80)
    print("👑 VALIDAÇÃO DO REGENTE DO MAPA:")
    print("=" * 80)
    ascendant = chart_data.get('ascendant_sign')
    ruler_info = get_chart_ruler(ascendant, chart_data)
    
    print(f"\nAscendente: {ascendant}")
    print(f"Regente Calculado: {ruler_info['planet']} em {ruler_info['sign']}")
    print(f"Regente Fornecido: {PROVIDED_DATA['ruler']} em {PROVIDED_DATA['ruler_sign']}")
    
    if ruler_info['planet'] == PROVIDED_DATA['ruler'] and ruler_info['sign'] == PROVIDED_DATA['ruler_sign']:
        print("  ✅ CORRETO")
    else:
        print("  ❌ ERRO")
        if ruler_info['planet'] != PROVIDED_DATA['ruler']:
            print(f"    - Planeta: Esperado {PROVIDED_DATA['ruler']}, Calculado {ruler_info['planet']}")
        if ruler_info['sign'] != PROVIDED_DATA['ruler_sign']:
            print(f"    - Signo: Esperado {PROVIDED_DATA['ruler_sign']}, Calculado {ruler_info['sign']}")
    
    # Validar dignidades
    print("\n" + "=" * 80)
    print("🏛️ VALIDAÇÃO DE DIGNIDADES PLANETÁRIAS:")
    print("=" * 80)
    dignity_errors = []
    for planet, (expected_sign, expected_dignity_pt) in PROVIDED_DATA['dignities'].items():
        chart_key = {
            'Sol': 'sun_sign',
            'Lua': 'moon_sign',
            'Mercúrio': 'mercury_sign',
            'Vênus': 'venus_sign',
            'Marte': 'mars_sign',
            'Júpiter': 'jupiter_sign',
            'Saturno': 'saturn_sign',
            'Urano': 'uranus_sign',
            'Netuno': 'neptune_sign',
            'Plutão': 'pluto_sign',
        }.get(planet)
        
        calculated_sign = chart_data.get(chart_key)
        if calculated_sign:
            calculated_dignity = get_planet_dignity(planet, calculated_sign)
            calculated_dignity_pt = dignity_to_portuguese(calculated_dignity)
            
            if calculated_sign == expected_sign and calculated_dignity_pt == expected_dignity_pt:
                print(f"  ✅ {planet} em {calculated_sign}: {calculated_dignity_pt}")
            else:
                print(f"  ❌ {planet}:")
                if calculated_sign != expected_sign:
                    print(f"      Signo: Esperado {expected_sign}, Calculado {calculated_sign}")
                if calculated_dignity_pt != expected_dignity_pt:
                    print(f"      Dignidade: Esperado {expected_dignity_pt}, Calculado {calculated_dignity_pt}")
                dignity_errors.append((planet, expected_sign, expected_dignity_pt, calculated_sign, calculated_dignity_pt))
    
    # Resumo final
    print("\n" + "=" * 80)
    print("📋 RESUMO DA VALIDAÇÃO:")
    print("=" * 80)
    
    errors_count = len(position_errors) + len(dignity_errors)
    
    if errors_count == 0:
        print("✅ TODOS OS DADOS ESTÃO CORRETOS!")
    else:
        print(f"❌ ENCONTRADOS {errors_count} ERRO(S):")
        if position_errors:
            print(f"\n  • {len(position_errors)} erro(s) em posições planetárias")
        if dignity_errors:
            print(f"  • {len(dignity_errors)} erro(s) em dignidades")
    
    print("\n" + "=" * 80)
    return errors_count == 0


if __name__ == '__main__':
    try:
        success = validate_map()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

