#!/usr/bin/env python3
"""
Script para verificar se Urano é o regente do mapa para Francisco Alexandre Araujo Rocha.
Dados:
- Nome: Francisco Alexandre Araujo Rocha
- Data: 20/10/1981
- Hora: 13:30
- Local: Sobral, Ceará
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from datetime import datetime
from app.services.astrology_calculator import calculate_birth_chart

# Tentar usar Swiss Ephemeris se disponível
try:
    from app.services.swiss_ephemeris_calculator import calculate_birth_chart as calculate_swiss
    from app.services.swiss_ephemeris_calculator import get_planet_house, create_kr_instance
    SWISS_AVAILABLE = True
except ImportError:
    SWISS_AVAILABLE = False
    print("[INFO] Swiss Ephemeris não disponível, usando cálculo básico")

# Dados do usuário
birth_date = datetime(1981, 10, 20)  # 20/10/1981
birth_time = "13:30"  # 13:30
birth_place = "Sobral, CE, Brasil"

# Coordenadas de Sobral, Ceará
# Fonte: https://www.google.com/maps/place/Sobral,+CE
latitude = -3.6883
longitude = -40.3497

# Mapeamento de signos para regentes (moderno)
RULER_MAP = {
    'Áries': 'Marte',
    'Touro': 'Vênus',
    'Gêmeos': 'Mercúrio',
    'Câncer': 'Lua',
    'Leão': 'Sol',
    'Virgem': 'Mercúrio',
    'Libra': 'Vênus',
    'Escorpião': 'Plutão',
    'Sagitário': 'Júpiter',
    'Capricórnio': 'Saturno',
    'Aquário': 'Urano',
    'Peixes': 'Netuno',
}

print("=" * 80)
print("VERIFICAÇÃO DO REGENTE DO MAPA")
print("=" * 80)
print(f"\nDados do usuário:")
print(f"  Nome: Francisco Alexandre Araujo Rocha")
print(f"  Data: {birth_date.strftime('%d/%m/%Y')}")
print(f"  Hora: {birth_time}")
print(f"  Local: {birth_place}")
print(f"  Coordenadas: Lat {latitude}, Lon {longitude}")
print("\nCalculando mapa astral...")
print("-" * 80)

try:
    result = calculate_birth_chart(
        birth_date=birth_date,
        birth_time=birth_time,
        latitude=latitude,
        longitude=longitude,
        use_swiss_ephemeris=True
    )
    
    print("\nRESULTADOS DO MAPA ASTRAL:")
    print("-" * 80)
    print(f"Sol: {result.get('sun_sign')} {result.get('sun_degree', 0):.2f}°")
    print(f"Lua: {result.get('moon_sign')} {result.get('moon_degree', 0):.2f}°")
    print(f"Ascendente: {result.get('ascendant_sign')} {result.get('ascendant_degree', 0):.2f}°")
    print(f"Mercúrio: {result.get('mercury_sign')} {result.get('mercury_degree', 0):.2f}°")
    print(f"Vênus: {result.get('venus_sign')} {result.get('venus_degree', 0):.2f}°")
    print(f"Marte: {result.get('mars_sign')} {result.get('mars_degree', 0):.2f}°")
    print(f"Júpiter: {result.get('jupiter_sign')} {result.get('jupiter_degree', 0):.2f}°")
    print(f"Saturno: {result.get('saturn_sign')} {result.get('saturn_degree', 0):.2f}°")
    print(f"Urano: {result.get('uranus_sign')} {result.get('uranus_degree', 0):.2f}°")
    print(f"Netuno: {result.get('neptune_sign')} {result.get('neptune_degree', 0):.2f}°")
    print(f"Plutão: {result.get('pluto_sign')} {result.get('pluto_degree', 0):.2f}°")
    
    # Tentar obter casa de Urano se Swiss Ephemeris estiver disponível
    uranus_house = None
    if SWISS_AVAILABLE:
        try:
            kr = create_kr_instance(birth_date, birth_time, latitude, longitude)
            uranus_house = get_planet_house(kr, "uranus")
        except Exception as e:
            print(f"[INFO] Não foi possível calcular casa de Urano: {e}")
    
    # Verificar regente
    ascendant_sign = result.get('ascendant_sign')
    if ascendant_sign:
        ruler = RULER_MAP.get(ascendant_sign, 'Desconhecido')
        
        print("\n" + "=" * 80)
        print("VERIFICAÇÃO DO REGENTE:")
        print("=" * 80)
        print(f"Ascendente: {ascendant_sign}")
        print(f"Regente calculado: {ruler}")
        print(f"Regente esperado: Urano")
        print(f"\n{'✅ CORRETO!' if ruler == 'Urano' else '❌ INCORRETO!'}")
        
        if ruler == 'Urano':
            print("\n✓ Urano é realmente o regente do mapa!")
            print("✓ O ascendente é Aquário, que tem Urano como regente (sistema moderno)")
            
            # Verificar posição de Urano
            uranus_sign = result.get('uranus_sign')
            uranus_degree = result.get('uranus_degree', 0)
            print(f"\nPosição de Urano (regente): {uranus_sign} {uranus_degree:.2f}°")
            
            if uranus_house:
                print(f"Casa de Urano: Casa {uranus_house}")
            
            # Verificar se a informação fornecida está correta
            print("\n" + "-" * 80)
            print("VERIFICAÇÃO DOS DADOS FORNECIDOS:")
            print("-" * 80)
            print(f"Informação fornecida: 'Urano em Libra na casa 1'")
            print(f"Urano calculado: {uranus_sign} {uranus_degree:.2f}°")
            if uranus_house:
                print(f"Casa calculada: Casa {uranus_house}")
            
            if uranus_sign == 'Libra':
                print("✓ Signo de Urano está CORRETO (Libra)")
            else:
                print(f"✗ Signo de Urano está INCORRETO. Calculado: {uranus_sign}, Esperado: Libra")
            
            if uranus_house == 1:
                print("✓ Casa de Urano está CORRETO (Casa 1)")
            elif uranus_house:
                print(f"✗ Casa de Urano está INCORRETO. Calculado: Casa {uranus_house}, Esperado: Casa 1")
            else:
                print("⚠ Não foi possível verificar a casa de Urano (Swiss Ephemeris não disponível)")
        else:
            print(f"\n✗ O regente calculado é {ruler}, não Urano.")
            print(f"✗ O ascendente é {ascendant_sign}, que tem {ruler} como regente.")
    else:
        print("\n❌ ERRO: Não foi possível determinar o ascendente!")
        
except Exception as e:
    print(f"\n❌ ERRO ao calcular mapa astral: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)

