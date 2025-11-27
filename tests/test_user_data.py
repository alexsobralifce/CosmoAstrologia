#!/usr/bin/env python3
"""
Script para testar cálculos astrológicos com dados específicos do usuário.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from datetime import datetime
from app.services.astrology_calculator import calculate_birth_chart

print("=" * 60)
print("TESTE COM DADOS ESPECÍFICOS DO USUÁRIO")
print("=" * 60)
print("\nPor favor, forneça os seguintes dados:")
print("1. Data de nascimento (formato: DD/MM/AAAA)")
print("2. Hora de nascimento (formato: HH:MM)")
print("3. Local de nascimento (cidade, estado/país)")
print("\nOu edite este script diretamente com os dados.")
print("=" * 60)

# ==========================================
# INSIRA OS DADOS AQUI:
# ==========================================
# Exemplo:
# birth_date = datetime(1990, 10, 15)  # 15/10/1990
# birth_time = "10:00"  # 10:00
# birth_place = "São Paulo, SP, Brasil"
# latitude = -23.5505  # Latitude de São Paulo
# longitude = -46.6333  # Longitude de São Paulo

# Descomente e preencha com os dados reais:
# birth_date = datetime(ANO, MES, DIA)
# birth_time = "HH:MM"
# latitude = XX.XXXX  # Use Google Maps ou similar para encontrar
# longitude = XX.XXXX
# birth_place = "Cidade, Estado, País"

# ==========================================
# DADOS DE TESTE (substitua pelos dados reais)
# ==========================================
birth_date = datetime(1990, 10, 15)  # ALTERE AQUI
birth_time = "10:00"  # ALTERE AQUI
birth_place = "São Paulo, SP, Brasil"  # ALTERE AQUI
latitude = -23.5505  # ALTERE AQUI
longitude = -46.6333  # ALTERE AQUI

# ==========================================
# EXECUÇÃO DO TESTE
# ==========================================
print(f"\nDados inseridos:")
print(f"  Data: {birth_date.strftime('%d/%m/%Y')}")
print(f"  Hora: {birth_time}")
print(f"  Local: {birth_place}")
print(f"  Coordenadas: Lat {latitude}, Lon {longitude}")
print("\nCalculando mapa astral...")
print("-" * 60)

try:
    result = calculate_birth_chart(
        birth_date=birth_date,
        birth_time=birth_time,
        latitude=latitude,
        longitude=longitude
    )
    
    print("\nRESULTADOS:")
    print("=" * 60)
    print(f"  Sol: {result['sun_sign']} {result['sun_degree']:.2f}°")
    print(f"  Lua: {result['moon_sign']} {result['moon_degree']:.2f}°")
    print(f"  Ascendente: {result['ascendant_sign']} {result['ascendant_degree']:.2f}°")
    print("=" * 60)
    
    # Verificações
    print("\nVERIFICAÇÕES:")
    print("-" * 60)
    
    expected_sun = "Libra"
    expected_asc = "Aquário"
    
    if result['sun_sign'] == expected_sun:
        print(f"  ✓ Sol correto: {result['sun_sign']}")
    else:
        print(f"  ✗ Sol incorreto: esperado {expected_sun}, obtido {result['sun_sign']}")
        print(f"    (Sol em {result['sun_sign']} {result['sun_degree']:.2f}°)")
    
    if result['ascendant_sign'] == expected_asc:
        print(f"  ✓ Ascendente correto: {result['ascendant_sign']}")
    else:
        print(f"  ✗ Ascendente incorreto: esperado {expected_asc}, obtido {result['ascendant_sign']}")
        print(f"    (Ascendente em {result['ascendant_sign']} {result['ascendant_degree']:.2f}°)")
        print(f"\n  Dica: O ascendente muda aproximadamente a cada 2 horas.")
        print(f"        Tente ajustar a hora de nascimento para encontrar Aquário.")
        
except Exception as e:
    print(f"\n✗ ERRO: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)

