#!/usr/bin/env python3
"""
Script para testar os cálculos astrológicos com dados conhecidos.
Testa se o cálculo retorna Libra (Sol) e Aquário (Ascendente).
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from datetime import datetime
from app.services.astrology_calculator import calculate_birth_chart

# Dados de teste - ajuste conforme necessário
# Para ter Sol em Libra, a data deve ser entre 23/09 e 22/10
# Para ter Ascendente em Aquário, depende da hora e local

print("=" * 60)
print("TESTE DE CÁLCULOS ASTROLÓGICOS")
print("=" * 60)

# Teste 1: Data típica de Libra (23 de setembro)
test_cases = [
    {
        "name": "Teste 1: 23/09/1990, 10:00, São Paulo",
        "birth_date": datetime(1990, 9, 23),
        "birth_time": "10:00",
        "latitude": -23.5505,  # São Paulo
        "longitude": -46.6333,
        "expected_sun": "Libra",
        "expected_asc": None  # Vamos ver o que calcula
    },
    {
        "name": "Teste 2: 15/10/1990, 14:30, São Paulo",
        "birth_date": datetime(1990, 10, 15),
        "birth_time": "14:30",
        "latitude": -23.5505,
        "longitude": -46.6333,
        "expected_sun": "Libra",
        "expected_asc": None
    },
    {
        "name": "Teste 3: 15/10/1990, 06:00, São Paulo (manhã cedo)",
        "birth_date": datetime(1990, 10, 15),
        "birth_time": "06:00",
        "latitude": -23.5505,
        "longitude": -46.6333,
        "expected_sun": "Libra",
        "expected_asc": None
    },
    {
        "name": "Teste 4: 15/10/1990, 22:00, São Paulo (noite)",
        "birth_date": datetime(1990, 10, 15),
        "birth_time": "22:00",
        "latitude": -23.5505,
        "longitude": -46.6333,
        "expected_sun": "Libra",
        "expected_asc": None
    },
]

for i, test in enumerate(test_cases, 1):
    print(f"\n{test['name']}")
    print("-" * 60)
    
    try:
        result = calculate_birth_chart(
            birth_date=test["birth_date"],
            birth_time=test["birth_time"],
            latitude=test["latitude"],
            longitude=test["longitude"]
        )
        
        print(f"Data/Hora: {test['birth_date'].strftime('%d/%m/%Y')} {test['birth_time']}")
        print(f"Local: Lat {test['latitude']}, Lon {test['longitude']}")
        print(f"\nResultados:")
        print(f"  Sol: {result['sun_sign']} {result['sun_degree']:.2f}°")
        print(f"  Lua: {result['moon_sign']} {result['moon_degree']:.2f}°")
        print(f"  Ascendente: {result['ascendant_sign']} {result['ascendant_degree']:.2f}°")
        
        # Verificar se o Sol está correto
        if result['sun_sign'] == test['expected_sun']:
            print(f"  ✓ Sol correto: {result['sun_sign']}")
        else:
            print(f"  ✗ Sol incorreto: esperado {test['expected_sun']}, obtido {result['sun_sign']}")
        
        # Verificar ascendente se especificado
        if test['expected_asc']:
            if result['ascendant_sign'] == test['expected_asc']:
                print(f"  ✓ Ascendente correto: {result['ascendant_sign']}")
            else:
                print(f"  ✗ Ascendente incorreto: esperado {test['expected_asc']}, obtido {result['ascendant_sign']}")
        else:
            print(f"  ? Ascendente calculado: {result['ascendant_sign']} (verificar manualmente)")
            
    except Exception as e:
        print(f"  ✗ ERRO: {str(e)}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 60)
print("TESTE CONCLUÍDO")
print("=" * 60)
print("\nPara obter Ascendente em Aquário, você precisa:")
print("- Ajustar a hora de nascimento")
print("- O ascendente muda aproximadamente a cada 2 horas")
print("- Para São Paulo, tente diferentes horários até encontrar Aquário")

