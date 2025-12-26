#!/usr/bin/env python3
"""
Script para validar o mapa astral de Francisco Alexandre Araujo Rocha
Compara os dados do relatório fornecido com os cálculos reais do sistema.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from datetime import datetime
from app.services.astrology_calculator import calculate_birth_chart
from app.services.swiss_ephemeris_calculator import create_kr_instance, get_planet_house, get_planet_position
from app.services.local_knowledge_base import SIGN_TRAITS

# Dados de nascimento de Francisco
BIRTH_DATE = datetime(1981, 10, 20)
BIRTH_TIME = "13:30"
LATITUDE = -3.6883  # Sobral, Ceará
LONGITUDE = -40.3497

# Dados do relatório fornecido
REPORT_DATA = {
    "temperamento": {
        "ar": 10,
        "fogo": 6,
        "terra": 0,
        "agua": None  # Não mencionado
    },
    "planets": {
        "sol": {"sign": "Libra", "house": 1},
        "lua": {"sign": "Leão", "house": 4},
        "mercury": {"sign": "Libra", "house": 1},
        "venus": {"sign": "Sagitário", "house": 2},
        "mars": {"sign": "Leão", "house": 5},
        "jupiter": {"sign": "Libra", "house": 9},
        "saturn": {"sign": "Libra", "house": 10},
        "uranus": {"sign": "Escorpião", "house": 11},
        "neptune": {"sign": "Sagitário", "house": 12},
        "pluto": {"sign": "Libra", "house": 8},
    },
    "ascendant": "Aquário",
    "midheaven": "Escorpião",
    "north_node": "Câncer",
    "south_node": "Capricórnio",
    "chiron": "Touro",
    "ruler": "Urano",
    "ruler_sign": "Escorpião",
    "ruler_house": 11
}

def calculate_temperament(chart_data):
    """Calcula o temperamento baseado nos signos dos planetas."""
    elements = {"Fogo": 0, "Terra": 0, "Ar": 0, "Água": 0}
    
    planets_to_check = [
        "sun", "moon", "mercury", "venus", "mars",
        "jupiter", "saturn", "uranus", "neptune", "pluto"
    ]
    
    for planet in planets_to_check:
        sign_key = f"{planet}_sign"
        sign = chart_data.get(sign_key)
        if sign and sign in SIGN_TRAITS:
            element = SIGN_TRAITS[sign]["element"]
            elements[element] = elements.get(element, 0) + 1
    
    return elements

def get_house_ruler(house_number, ascendant_sign, chart_data):
    """Determina o regente de uma casa baseado no signo da cúspide."""
    # Mapeamento de signos para regentes
    RULER_MAP = {
        'Áries': 'Marte',
        'Touro': 'Vênus',
        'Gêmeos': 'Mercúrio',
        'Câncer': 'Lua',
        'Leão': 'Sol',
        'Virgem': 'Mercúrio',
        'Libra': 'Vênus',
        'Escorpião': 'Plutão',  # Moderno
        'Sagitário': 'Júpiter',
        'Capricórnio': 'Saturno',
        'Aquário': 'Urano',  # Moderno
        'Peixes': 'Netuno'  # Moderno
    }
    
    # Signos em ordem zodiacal
    SIGNS = ["Áries", "Touro", "Gêmeos", "Câncer", "Leão", "Virgem",
             "Libra", "Escorpião", "Sagitário", "Capricórnio", "Aquário", "Peixes"]
    
    # Encontrar índice do ascendente
    asc_index = SIGNS.index(ascendant_sign)
    
    # Calcular signo da casa (casa 1 = ascendente, casa 2 = próximo signo, etc.)
    house_sign_index = (asc_index + house_number - 1) % 12
    house_sign = SIGNS[house_sign_index]
    
    ruler = RULER_MAP.get(house_sign)
    
    # Encontrar onde está o regente
    ruler_planet_key = None
    ruler_sign = None
    ruler_house = None
    
    for planet_key, planet_name in [
        ("sun", "Sol"), ("moon", "Lua"), ("mercury", "Mercúrio"),
        ("venus", "Vênus"), ("mars", "Marte"), ("jupiter", "Júpiter"),
        ("saturn", "Saturno"), ("uranus", "Urano"), ("neptune", "Netuno"),
        ("pluto", "Plutão")
    ]:
        if planet_name == ruler:
            ruler_planet_key = planet_key
            ruler_sign = chart_data.get(f"{planet_key}_sign")
            break
    
    return {
        "house": house_number,
        "house_sign": house_sign,
        "ruler": ruler,
        "ruler_planet": ruler_planet_key,
        "ruler_sign": ruler_sign,
        "ruler_house": ruler_house
    }

print("=" * 80)
print("VALIDAÇÃO DO MAPA ASTRAL DE FRANCISCO ALEXANDRE ARAUJO ROCHA")
print("=" * 80)

try:
    # Calcular mapa astral
    print("\n📊 Calculando mapa astral...")
    chart_data = calculate_birth_chart(
        birth_date=BIRTH_DATE,
        birth_time=BIRTH_TIME,
        latitude=LATITUDE,
        longitude=LONGITUDE,
        use_swiss_ephemeris=True
    )
    
    # Criar instância kerykeion para obter casas
    print("📊 Calculando casas astrológicas...")
    kr = create_kr_instance(BIRTH_DATE, BIRTH_TIME, LATITUDE, LONGITUDE)
    
    # Obter casas dos planetas
    planet_houses = {}
    for planet in ["sun", "moon", "mercury", "venus", "mars", 
                   "jupiter", "saturn", "uranus", "neptune", "pluto"]:
        try:
            house = get_planet_house(kr, planet)
            planet_houses[planet] = house
        except Exception as e:
            print(f"  ⚠️  Erro ao obter casa de {planet}: {e}")
            planet_houses[planet] = None
    
    # Calcular temperamento
    temperament = calculate_temperament(chart_data)
    
    print("\n" + "=" * 80)
    print("RESULTADOS DO CÁLCULO")
    print("=" * 80)
    
    # Verificar planetas
    print("\n📌 POSIÇÕES PLANETÁRIAS:")
    print("-" * 80)
    for planet_key, planet_name in [
        ("sun", "Sol"), ("moon", "Lua"), ("mercury", "Mercúrio"),
        ("venus", "Vênus"), ("mars", "Marte"), ("jupiter", "Júpiter"),
        ("saturn", "Saturno"), ("uranus", "Urano"), ("neptune", "Netuno"),
        ("pluto", "Plutão")
    ]:
        sign = chart_data.get(f"{planet_key}_sign")
        degree = chart_data.get(f"{planet_key}_degree", 0)
        house = planet_houses.get(planet_key)
        
        report_planet = REPORT_DATA["planets"].get(planet_key, {})
        report_sign = report_planet.get("sign")
        report_house = report_planet.get("house")
        
        sign_ok = "✅" if sign == report_sign else "❌"
        house_ok = "✅" if house == report_house else "❌"
        
        print(f"{planet_name:12} | {sign_ok} Signo: {sign:12} (Esperado: {report_sign:12}) | "
              f"{house_ok} Casa: {house:2} (Esperado: {report_house:2}) | Grau: {degree:5.2f}°")
    
    # Verificar pontos especiais
    print("\n📌 PONTOS ESPECIAIS:")
    print("-" * 80)
    
    ascendant = chart_data.get("ascendant_sign")
    midheaven = chart_data.get("midheaven_sign")
    north_node = chart_data.get("north_node_sign")
    south_node = chart_data.get("south_node_sign")
    chiron = chart_data.get("chiron_sign")
    
    print(f"Ascendente:  {ascendant:12} {'✅' if ascendant == REPORT_DATA['ascendant'] else '❌'} (Esperado: {REPORT_DATA['ascendant']})")
    print(f"Meio do Céu: {midheaven:12} {'✅' if midheaven == REPORT_DATA['midheaven'] else '❌'} (Esperado: {REPORT_DATA['midheaven']})")
    print(f"Nodo Norte:  {north_node:12} {'✅' if north_node == REPORT_DATA['north_node'] else '❌'} (Esperado: {REPORT_DATA['north_node']})")
    print(f"Nodo Sul:    {south_node:12} {'✅' if south_node == REPORT_DATA['south_node'] else '❌'} (Esperado: {REPORT_DATA['south_node']})")
    print(f"Quíron:      {chiron:12} {'✅' if chiron == REPORT_DATA['chiron'] else '❌'} (Esperado: {REPORT_DATA['chiron']})")
    
    # Verificar temperamento
    print("\n📌 TEMPERAMENTO (ELEMENTOS):")
    print("-" * 80)
    print(f"Ar:    {temperament.get('Ar', 0):2} pontos {'✅' if temperament.get('Ar', 0) == REPORT_DATA['temperamento']['ar'] else '❌'} (Esperado: {REPORT_DATA['temperamento']['ar']})")
    print(f"Fogo:  {temperament.get('Fogo', 0):2} pontos {'✅' if temperament.get('Fogo', 0) == REPORT_DATA['temperamento']['fogo'] else '❌'} (Esperado: {REPORT_DATA['temperamento']['fogo']})")
    print(f"Terra: {temperament.get('Terra', 0):2} pontos {'✅' if temperament.get('Terra', 0) == REPORT_DATA['temperamento']['terra'] else '❌'} (Esperado: {REPORT_DATA['temperamento']['terra']})")
    print(f"Água:  {temperament.get('Água', 0):2} pontos")
    
    # Verificar regente do mapa
    print("\n📌 REGENTE DO MAPA:")
    print("-" * 80)
    uranus_sign = chart_data.get("uranus_sign")
    uranus_house = planet_houses.get("uranus")
    
    print(f"Regente: Urano")
    print(f"Urano em: {uranus_sign:12} {'✅' if uranus_sign == REPORT_DATA['ruler_sign'] else '❌'} (Esperado: {REPORT_DATA['ruler_sign']})")
    print(f"Urano na Casa: {uranus_house:2} {'✅' if uranus_house == REPORT_DATA['ruler_house'] else '❌'} (Esperado: {REPORT_DATA['ruler_house']})")
    
    # Verificar regências das casas
    print("\n📌 REGÊNCIAS DAS CASAS:")
    print("-" * 80)
    for house_num in range(1, 13):
        house_info = get_house_ruler(house_num, ascendant, chart_data)
        ruler_house = None
        if house_info["ruler_planet"]:
            ruler_house = planet_houses.get(house_info["ruler_planet"])
        
        print(f"Casa {house_num:2} ({house_info['house_sign']:12}) | "
              f"Regente: {house_info['ruler']:10} em {house_info['ruler_sign']:12} "
              f"na Casa {ruler_house if ruler_house else 'N/A':2}")
    
    # Resumo de erros
    print("\n" + "=" * 80)
    print("RESUMO DE VALIDAÇÃO")
    print("=" * 80)
    
    errors = []
    
    # Verificar planetas
    for planet_key, planet_name in [
        ("sun", "Sol"), ("moon", "Lua"), ("mercury", "Mercúrio"),
        ("venus", "Vênus"), ("mars", "Marte"), ("jupiter", "Júpiter"),
        ("saturn", "Saturno"), ("uranus", "Urano"), ("neptune", "Netuno"),
        ("pluto", "Plutão")
    ]:
        sign = chart_data.get(f"{planet_key}_sign")
        house = planet_houses.get(planet_key)
        report_planet = REPORT_DATA["planets"].get(planet_key, {})
        
        if sign != report_planet.get("sign"):
            errors.append(f"{planet_name}: Signo calculado ({sign}) != esperado ({report_planet.get('sign')})")
        if house != report_planet.get("house"):
            errors.append(f"{planet_name}: Casa calculada ({house}) != esperada ({report_planet.get('house')})")
    
    # Verificar pontos especiais
    if ascendant != REPORT_DATA['ascendant']:
        errors.append(f"Ascendente: {ascendant} != {REPORT_DATA['ascendant']}")
    if midheaven != REPORT_DATA['midheaven']:
        errors.append(f"Meio do Céu: {midheaven} != {REPORT_DATA['midheaven']}")
    if north_node != REPORT_DATA['north_node']:
        errors.append(f"Nodo Norte: {north_node} != {REPORT_DATA['north_node']}")
    if south_node != REPORT_DATA['south_node']:
        errors.append(f"Nodo Sul: {south_node} != {REPORT_DATA['south_node']}")
    if chiron != REPORT_DATA['chiron']:
        errors.append(f"Quíron: {chiron} != {REPORT_DATA['chiron']}")
    
    # Verificar temperamento
    if temperament.get('Ar', 0) != REPORT_DATA['temperamento']['ar']:
        errors.append(f"Temperamento Ar: {temperament.get('Ar', 0)} != {REPORT_DATA['temperamento']['ar']}")
    if temperament.get('Fogo', 0) != REPORT_DATA['temperamento']['fogo']:
        errors.append(f"Temperamento Fogo: {temperament.get('Fogo', 0)} != {REPORT_DATA['temperamento']['fogo']}")
    if temperament.get('Terra', 0) != REPORT_DATA['temperamento']['terra']:
        errors.append(f"Temperamento Terra: {temperament.get('Terra', 0)} != {REPORT_DATA['temperamento']['terra']}")
    
    # Verificar regente
    if uranus_sign != REPORT_DATA['ruler_sign']:
        errors.append(f"Regente (Urano) em: {uranus_sign} != {REPORT_DATA['ruler_sign']}")
    if uranus_house != REPORT_DATA['ruler_house']:
        errors.append(f"Regente (Urano) na Casa: {uranus_house} != {REPORT_DATA['ruler_house']}")
    
    if errors:
        print(f"\n❌ ENCONTRADOS {len(errors)} ERROS:")
        for i, error in enumerate(errors, 1):
            print(f"  {i}. {error}")
    else:
        print("\n✅ TODOS OS DADOS ESTÃO CORRETOS!")
    
    print("\n" + "=" * 80)
    
except Exception as e:
    print(f"\n❌ ERRO: {e}")
    import traceback
    traceback.print_exc()

