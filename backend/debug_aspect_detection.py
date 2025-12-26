"""
Script para debugar a detecção de aspectos.
Verifica por que aspectos incorretos estão sendo detectados.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.transits_calculator import calculate_aspect_angle, get_aspect_type

# Valores do exemplo
sol_longitude = 272.93  # Sol em 24/12/2025 12:00
house_1_cusp = 284.08
house_9_cusp = 164.08

print("="*70)
print("DEBUG: DETECÇÃO DE ASPECTOS")
print("="*70)
print()

# Verificar aspecto com Casa 1
angle_1 = calculate_aspect_angle(sol_longitude, house_1_cusp)
print(f"Sol: {sol_longitude:.2f}°")
print(f"Casa 1: {house_1_cusp:.2f}°")
print(f"Ângulo calculado: {angle_1:.2f}°")
print(f"Diferença absoluta: {abs(sol_longitude - house_1_cusp):.2f}°")
print(f"Diferença circular: {min(abs(sol_longitude - house_1_cusp), 360 - abs(sol_longitude - house_1_cusp)):.2f}°")
print()

aspect_1_orb8 = get_aspect_type(angle_1, orb=8.0)
aspect_1_orb10 = get_aspect_type(angle_1, orb=10.0)
aspect_1_orb12 = get_aspect_type(angle_1, orb=12.0)
aspect_1_orb15 = get_aspect_type(angle_1, orb=15.0)

print(f"Aspecto detectado (orbe 8°): {aspect_1_orb8}")
print(f"Aspecto detectado (orbe 10°): {aspect_1_orb10}")
print(f"Aspecto detectado (orbe 12°): {aspect_1_orb12}")
print(f"Aspecto detectado (orbe 15°): {aspect_1_orb15}")
print()

# Verificar aspecto com Casa 9
angle_9 = calculate_aspect_angle(sol_longitude, house_9_cusp)
print(f"Sol: {sol_longitude:.2f}°")
print(f"Casa 9: {house_9_cusp:.2f}°")
print(f"Ângulo calculado: {angle_9:.2f}°")
print(f"Diferença absoluta: {abs(sol_longitude - house_9_cusp):.2f}°")
print(f"Diferença circular: {min(abs(sol_longitude - house_9_cusp), 360 - abs(sol_longitude - house_9_cusp)):.2f}°")
print()

aspect_9_orb8 = get_aspect_type(angle_9, orb=8.0)
aspect_9_orb10 = get_aspect_type(angle_9, orb=10.0)
aspect_9_orb12 = get_aspect_type(angle_9, orb=12.0)
aspect_9_orb15 = get_aspect_type(angle_9, orb=15.0)

print(f"Aspecto detectado (orbe 8°): {aspect_9_orb8}")
print(f"Aspecto detectado (orbe 10°): {aspect_9_orb10}")
print(f"Aspecto detectado (orbe 12°): {aspect_9_orb12}")
print(f"Aspecto detectado (orbe 15°): {aspect_9_orb15}")
print()

# Verificar se há algum problema com o cálculo do ângulo
print("="*70)
print("VERIFICAÇÃO DE CÁLCULO DE ÂNGULO")
print("="*70)
print()

# Para conjunção: ângulo deve estar próximo de 0° ou 360°
conjunction_target = 0
conjunction_diff_1 = min(abs(angle_1 - conjunction_target), abs(angle_1 - 360))
print(f"Diferença para conjunção (Casa 1): {conjunction_diff_1:.2f}°")
print(f"Está dentro do orbe de 8°? {conjunction_diff_1 <= 8.0}")
print()

# Para trígono: ângulo deve estar próximo de 120°
trine_target = 120
trine_diff_9 = abs(angle_9 - trine_target)
print(f"Diferença para trígono (Casa 9): {trine_diff_9:.2f}°")
print(f"Está dentro do orbe de 8°? {trine_diff_9 <= 8.0}")
print()

print("="*70)
print("CONCLUSÃO")
print("="*70)
print()
print("Se os aspectos estão sendo detectados incorretamente, pode ser:")
print("  1. Orbe muito grande sendo usado")
print("  2. Bug no cálculo de ângulo")
print("  3. Problema na função get_aspect_type")
print("  4. Cúspides das casas sendo calculadas incorretamente")

