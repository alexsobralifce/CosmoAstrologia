"""
Testa especificamente o bug de detecção de aspecto Sol-Casa 10 para 6/12/2025.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
import ephem
from app.services.astrology_calculator import calculate_planet_position
from app.services.transits_calculator import calculate_aspect_angle, get_aspect_type

# Dados específicos do problema
sun_longitude = 254.617924  # Sol em 6/12/2025 12:00
house_10_cusp = 184.393240  # Casa 10

print("="*80)
print("TESTE ESPECÍFICO: SOL vs CASA 10 - 6/12/2025 12:00")
print("="*80)
print()
print(f"Sol: {sun_longitude:.6f}°")
print(f"Casa 10: {house_10_cusp:.6f}°")
print()

# Calcular ângulo
angle = calculate_aspect_angle(sun_longitude, house_10_cusp)
print(f"Ângulo calculado: {angle:.6f}°")
print()

# Testar detecção com diferentes orbes
print("Testando detecção de aspecto com diferentes orbes:")
for orb in [5.0, 8.0, 10.0, 12.0, 15.0]:
    aspect_type = get_aspect_type(angle, orb=orb)
    if aspect_type:
        print(f"  Orbe {orb:4.1f}°: {aspect_type:12s} ✓")
    else:
        print(f"  Orbe {orb:4.1f}°: {'Nenhum':12s}")

print()

# Verificar diferença para sextil (60°)
sextil_diff = abs(angle - 60)
print(f"Diferença para sextil (60°): {sextil_diff:.6f}°")
print(f"Está dentro do orbe de 8°? {sextil_diff <= 8.0}")
print()

# Verificar diferença para quadratura (90°)
quad_diff = abs(angle - 90)
print(f"Diferença para quadratura (90°): {quad_diff:.6f}°")
print(f"Está dentro do orbe de 8°? {quad_diff <= 8.0}")
print()

# Verificar diferença para trígono (120°)
trine_diff = abs(angle - 120)
print(f"Diferença para trígono (120°): {trine_diff:.6f}°")
print(f"Está dentro do orbe de 8°? {trine_diff <= 8.0}")
print()

print("="*80)
print("CONCLUSÃO:")
print("="*80)
print()
print(f"O ângulo de {angle:.6f}° está:")
print(f"  - {sextil_diff:.6f}° longe de sextil (60°)")
print(f"  - {quad_diff:.6f}° longe de quadratura (90°)")
print(f"  - {trine_diff:.6f}° longe de trígono (120°)")
print()
if sextil_diff <= 8.0:
    print("✅ Sol ESTÁ em sextil com Casa 10 (dentro do orbe de 8°)")
else:
    print("❌ Sol NÃO está em sextil com Casa 10 (fora do orbe de 8°)")
    print(f"   Diferença de {sextil_diff:.6f}° > 8.0°")

