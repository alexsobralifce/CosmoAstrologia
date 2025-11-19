#!/usr/bin/env python3
"""
Script para encontrar o horário que resulta em Ascendente em Aquário
para uma data específica (Libra).
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from datetime import datetime
from app.services.astrology_calculator import calculate_birth_chart

# Data de teste (Libra)
birth_date = datetime(1990, 10, 15)
latitude = -23.5505  # São Paulo
longitude = -46.6333

print("=" * 60)
print("PROCURANDO HORÁRIO PARA ASCENDENTE EM AQUÁRIO")
print("=" * 60)
print(f"Data: {birth_date.strftime('%d/%m/%Y')}")
print(f"Local: São Paulo (Lat: {latitude}, Lon: {longitude})")
print("=" * 60)

# Testar cada hora do dia
found_aquarius = False
for hour in range(24):
    for minute in [0, 30]:
        birth_time = f"{hour:02d}:{minute:02d}"
        
        try:
            result = calculate_birth_chart(
                birth_date=birth_date,
                birth_time=birth_time,
                latitude=latitude,
                longitude=longitude
            )
            
            if result['ascendant_sign'] == 'Aquário':
                print(f"\n✓ ENCONTRADO: {birth_time}")
                print(f"  Sol: {result['sun_sign']} {result['sun_degree']:.2f}°")
                print(f"  Ascendente: {result['ascendant_sign']} {result['ascendant_degree']:.2f}°")
                found_aquarius = True
        except Exception as e:
            print(f"Erro em {birth_time}: {e}")

if not found_aquarius:
    print("\nNão encontrado Ascendente em Aquário para esta data/local.")
    print("Tente uma data diferente ou outro local.")

print("\n" + "=" * 60)

