"""
Teste para validar a correção do bug de validação de ângulos.
Verifica se a correção trata corretamente ângulos próximos de 0° e 180°.
"""

from app.services.astrology_calculator import shortest_angular_distance

def test_angle_validation():
    """Testa a validação de ângulos com geometria circular."""
    
    print("=" * 80)
    print("TESTE: Validação de Ângulos com Geometria Circular")
    print("=" * 80)
    print()
    
    # Casos de teste
    test_cases = [
        # (angle, target_angle, expected_diff, description)
        (179.0, 180.0, 1.0, "Oposição: 179° vs 180° (deve ser 1°)"),
        (181.0, 180.0, 1.0, "Oposição: 181° vs 180° (deve ser 1°)"),
        (1.0, 0.0, 1.0, "Conjunção: 1° vs 0° (deve ser 1°)"),
        (359.0, 0.0, 1.0, "Conjunção: 359° vs 0° (deve ser 1°)"),
        (59.0, 60.0, 1.0, "Sextil: 59° vs 60° (deve ser 1°)"),
        (61.0, 60.0, 1.0, "Sextil: 61° vs 60° (deve ser 1°)"),
        (119.0, 120.0, 1.0, "Trígono: 119° vs 120° (deve ser 1°)"),
        (121.0, 120.0, 1.0, "Trígono: 121° vs 120° (deve ser 1°)"),
        (89.0, 90.0, 1.0, "Quadratura: 89° vs 90° (deve ser 1°)"),
        (91.0, 90.0, 1.0, "Quadratura: 91° vs 90° (deve ser 1°)"),
        (0.0, 0.0, 0.0, "Conjunção exata: 0° vs 0° (deve ser 0°)"),
        (180.0, 180.0, 0.0, "Oposição exata: 180° vs 180° (deve ser 0°)"),
        (10.0, 0.0, 10.0, "Conjunção: 10° vs 0° (fora do orbe de 8°)"),
        (170.0, 180.0, 10.0, "Oposição: 170° vs 180° (fora do orbe de 8°)"),
    ]
    
    print("Testando shortest_angular_distance:")
    print()
    
    all_passed = True
    for angle, target, expected, description in test_cases:
        # Normalizar angle para 0-180° (como calculate_aspect_angle faz)
        if angle > 180:
            angle_normalized = 360 - angle
        else:
            angle_normalized = angle
        
        # Calcular diferença usando shortest_angular_distance
        diff = shortest_angular_distance(angle_normalized, target)
        
        # Verificar se está correto (com tolerância de 0.01°)
        passed = abs(diff - expected) < 0.01
        status = "✅ PASSOU" if passed else "❌ FALHOU"
        
        if not passed:
            all_passed = False
        
        print(f"{status}: {description}")
        print(f"  angle={angle}° (normalizado={angle_normalized}°), target={target}°")
        print(f"  diff calculado: {diff:.2f}°, esperado: {expected:.2f}°")
        print()
    
    print("=" * 80)
    if all_passed:
        print("✅ TODOS OS TESTES PASSARAM!")
    else:
        print("❌ ALGUNS TESTES FALHARAM!")
    print("=" * 80)
    
    return all_passed

if __name__ == "__main__":
    test_angle_validation()

