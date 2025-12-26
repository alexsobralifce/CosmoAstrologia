"""
Validação completa para 6 de Dezembro de 2025
Ação: pedir_aumento
Score reportado: 28
Aspectos reportados:
- Sol em sextil com Casa 2
- Vênus em sextil com Casa 2
- Sol em sextil com Casa 10
- Vênus em sextil com Casa 10
"""

from datetime import datetime
from app.services.best_timing_calculator import calculate_best_timing
from app.services.best_timing_calculator import calculate_planet_position_swiss, calculate_house_cusp
from app.services.transits_calculator import calculate_aspect_angle, get_aspect_type
import ephem

# Dados do usuário
birth_date = datetime(1981, 10, 20)
birth_time = "13:30"
latitude = -23.5505
longitude = -46.6333

# Data a validar
target_date = datetime(2025, 12, 6)

print("=" * 80)
print("VALIDAÇÃO COMPLETA: 6 de Dezembro de 2025 - Pedir Aumento")
print("=" * 80)
print(f"Data de nascimento: {birth_date.strftime('%d/%m/%Y')} às {birth_time}")
print(f"Data a validar: {target_date.strftime('%d/%m/%Y')}")
print()

# Calcular melhores momentos
result = calculate_best_timing(
    birth_date=birth_date,
    birth_time=birth_time,
    latitude=latitude,
    longitude=longitude,
    action_type='pedir_aumento',
    days_ahead=30
)

# Filtrar momentos do dia 6/12/2025
dec_6_moments = [
    m for m in result.get('best_moments', [])
    if m['date'].startswith('2025-12-06')
]

print(f"Momentos encontrados para 6/12/2025: {len(dec_6_moments)}")
print()

if dec_6_moments:
    # Verificar cada momento
    for moment in dec_6_moments:
        print(f"\n{'='*60}")
        print(f"Momento: {moment['date']}")
        print(f"Score: {moment['score']}")
        print(f"Aspectos ({len(moment.get('aspects', []))}):")
        
        # Calcular cúspides das casas
        birth_observer = ephem.Observer()
        birth_observer.lat = str(latitude)
        birth_observer.lon = str(longitude)
        time_parts = birth_time.split(":")
        hour = int(time_parts[0]) if len(time_parts) > 0 else 0
        minute = int(time_parts[1]) if len(time_parts) > 1 else 0
        birth_datetime = birth_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
        birth_observer.date = birth_datetime.strftime('%Y/%m/%d %H:%M:%S')
        
        casa_2_cusp = calculate_house_cusp(birth_observer, 2, birth_date, birth_time, latitude, longitude)
        casa_10_cusp = calculate_house_cusp(birth_observer, 10, birth_date, birth_time, latitude, longitude)
        
        print(f"\nCúspides das casas:")
        print(f"  Casa 2: {casa_2_cusp:.2f}°")
        print(f"  Casa 10: {casa_10_cusp:.2f}°")
        
        # Validar cada aspecto
        for aspect in moment.get('aspects', []):
            planet = aspect['planet']
            house = aspect['house']
            aspect_type = aspect['aspect_type']
            
            # Calcular posição do planeta
            check_datetime = datetime.fromisoformat(moment['date'].replace('Z', '+00:00'))
            planet_key = {
                'Sol': 'sun',
                'Vênus': 'venus',
                'Mercúrio': 'mercury',
                'Marte': 'mars',
                'Júpiter': 'jupiter',
                'Saturno': 'saturn',
                'Urano': 'uranus',
                'Netuno': 'neptune',
                'Plutão': 'pluto',
                'Lua': 'moon'
            }.get(planet, planet.lower())
            
            try:
                planet_longitude = calculate_planet_position_swiss(
                    check_datetime, latitude, longitude, planet_key
                )
                
                # Obter cúspide da casa
                house_cusp = casa_2_cusp if house == 2 else casa_10_cusp
                
                # Calcular ângulo
                angle = calculate_aspect_angle(planet_longitude, house_cusp)
                detected_aspect = get_aspect_type(angle, orb=8.0)
                
                # Validar
                is_valid = detected_aspect == aspect_type
                status = "✅ VÁLIDO" if is_valid else f"❌ INVÁLIDO (detectado: {detected_aspect})"
                
                print(f"\n  {status}: {planet} em {aspect_type} com Casa {house}")
                print(f"    Planeta: {planet_longitude:.2f}°")
                print(f"    Casa: {house_cusp:.2f}°")
                print(f"    Ângulo: {angle:.2f}°")
                print(f"    Aspecto detectado: {detected_aspect}")
                
                # Verificar se está dentro do orbe
                aspect_targets = {
                    'conjunção': 0,
                    'sextil': 60,
                    'quadratura': 90,
                    'trígono': 120,
                    'oposição': 180
                }
                target_angle = aspect_targets.get(aspect_type)
                if target_angle is not None:
                    angle_diff = abs(angle - target_angle)
                    in_orb = angle_diff <= 8.0
                    print(f"    Diferença para {aspect_type} ({target_angle}°): {angle_diff:.2f}°")
                    print(f"    Dentro do orbe (8°): {'✅ SIM' if in_orb else '❌ NÃO'}")
                
            except Exception as e:
                print(f"  ❌ ERRO ao validar: {e}")
        
        # Calcular score esperado
        expected_score = 0
        for aspect in moment.get('aspects', []):
            if aspect['aspect_type'] == 'sextil' and aspect.get('is_primary', False):
                expected_score += 7
            elif aspect['aspect_type'] == 'trígono' and aspect.get('is_primary', False):
                expected_score += 10
            elif aspect['aspect_type'] == 'conjunção' and aspect.get('is_primary', False):
                expected_score += 8
        
        print(f"\nScore calculado: {moment['score']}")
        print(f"Score esperado: {expected_score}")
        if moment['score'] == expected_score:
            print("✅ Score correto!")
        else:
            print(f"❌ Score incorreto! Diferença: {abs(moment['score'] - expected_score)}")
else:
    print("❌ NENHUM MOMENTO ENCONTRADO PARA 6/12/2025")

print()
print("=" * 80)

