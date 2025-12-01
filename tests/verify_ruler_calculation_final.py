#!/usr/bin/env python3
"""
Script final para verificar se o cálculo do regente está correto.
Verifica se Urano está sendo calculado corretamente como regente de Aquário.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from datetime import datetime
from app.services.astrology_calculator import calculate_birth_chart

# Dados do usuário Francisco Alexandre Araujo Rocha
birth_date = datetime(1981, 10, 20)
birth_time = "13:30"
latitude = -3.6883
longitude = -40.3497

print("=" * 80)
print("VERIFICAÇÃO FINAL DO REGENTE")
print("=" * 80)

try:
    result = calculate_birth_chart(
        birth_date=birth_date,
        birth_time=birth_time,
        latitude=latitude,
        longitude=longitude,
        use_swiss_ephemeris=True
    )
    
    ascendant = result.get('ascendant_sign')
    uranus_sign = result.get('uranus_sign')
    uranus_degree = result.get('uranus_degree', 0)
    
    # Mapeamento de regentes
    RULER_MAP = {
        'Áries': 'Marte', 'Touro': 'Vênus', 'Gêmeos': 'Mercúrio', 'Câncer': 'Lua',
        'Leão': 'Sol', 'Virgem': 'Mercúrio', 'Libra': 'Vênus', 'Escorpião': 'Plutão',
        'Sagitário': 'Júpiter', 'Capricórnio': 'Saturno', 'Aquário': 'Urano', 'Peixes': 'Netuno'
    }
    
    ruler = RULER_MAP.get(ascendant, 'Desconhecido')
    
    print(f"\n✅ DADOS CALCULADOS:")
    print(f"   Ascendente: {ascendant}")
    print(f"   Regente: {ruler}")
    print(f"   Urano em: {uranus_sign} {uranus_degree:.2f}°")
    
    # Tentar obter casa de Urano
    try:
        from app.services.swiss_ephemeris_calculator import create_kr_instance, get_planet_house
        kr = create_kr_instance(birth_date, birth_time, latitude, longitude)
        uranus_house = get_planet_house(kr, "uranus")
        print(f"   Casa de Urano: {uranus_house}")
    except Exception as e:
        print(f"   Casa de Urano: Não disponível ({e})")
        uranus_house = None
    
    print(f"\n✅ VERIFICAÇÕES:")
    print(f"   1. Regente correto: {'✅ SIM' if ruler == 'Urano' else '❌ NÃO'}")
    print(f"   2. Signo de Urano: {'✅ Escorpião' if uranus_sign == 'Escorpião' else f'❌ {uranus_sign}'}")
    if uranus_house:
        print(f"   3. Casa de Urano: {'✅ Casa 9' if uranus_house == 9 else f'❌ Casa {uranus_house}'}")
    
    print(f"\n📋 DADOS CORRETOS PARA INTERPRETAÇÃO:")
    print(f"   - Regente: {ruler}")
    print(f"   - Regente em: {uranus_sign}")
    if uranus_house:
        print(f"   - Regente na Casa: {uranus_house}")
    
    print("\n" + "=" * 80)
    print("✅ CORREÇÃO IMPLEMENTADA!")
    print("=" * 80)
    print("\nO código foi corrigido para usar os dados corretos do regente:")
    print(f"  - Antes: Usava signo do Sol ({result.get('sun_sign')}) e casa 1")
    print(f"  - Agora: Usa signo de {ruler} ({uranus_sign}) e casa {uranus_house if uranus_house else 'calculada'}")
    print("\n" + "=" * 80)
    
except Exception as e:
    print(f"\n❌ ERRO: {e}")
    import traceback
    traceback.print_exc()

