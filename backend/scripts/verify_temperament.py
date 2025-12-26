
import sys
import os
from datetime import datetime

# Adicionar o diretório pai ao path para importar os módulos
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Importar do CALCULADOR PRINCIPAL que tem fallback
from app.services.astrology_calculator import calculate_birth_chart
from app.services.precomputed_chart_engine import calculate_temperament_from_chart

def verify_temperament():
    print("=== VERIFICAÇÃO DE TEMPERAMENTO ===")
    print("Dados: Francisco Alexandre Araujo Rocha")
    print("Data: 20/10/1981 13:30")
    print("Local: Sobral, CE (Lat: -3.686, Lon: -40.349)")
    
    # Dados de nascimento
    birth_date = datetime(1981, 10, 20)
    birth_time = "13:30"
    lat = -3.686111
    lon = -40.349722
    
    # 1. Calcular Mapa Astral
    print("\nCalculando posições planetárias (usando motor disponível)...")
    # calculate_birth_chart no astrology_calculator tenta usar swiss e faz fallback para ephem
    chart = calculate_birth_chart(
        birth_date=birth_date,
        birth_time=birth_time,
        latitude=lat,
        longitude=lon
    )
    
    # Imprimir posições relevantes para temperamento
    print("\n--- POSIÇÕES CALCULADAS ---")
    
    print(f"Sol: {chart['sun_sign']} (Grau: {chart['sun_degree']:.2f})")
    print(f"Lua: {chart['moon_sign']} (Grau: {chart['moon_degree']:.2f})")
    print(f"Ascendente: {chart['ascendant_sign']} (Grau: {chart['ascendant_degree']:.2f})")
    print("-" * 20)
    print(f"Mercúrio: {chart['mercury_sign']}")
    print(f"Vênus: {chart['venus_sign']}")
    print(f"Marte: {chart['mars_sign']}")
    print(f"Júpiter: {chart['jupiter_sign']}")
    print(f"Saturno: {chart['saturn_sign']}")
    print(f"Urano: {chart['uranus_sign']}")
    print(f"Netuno: {chart['neptune_sign']}")
    print(f"Plutão: {chart['pluto_sign']}")
    
    # 2. Calcular Temperamento
    print("\n--- CÁLCULO DE PONTOS DE TEMPERAMENTO ---")
    temperament = calculate_temperament_from_chart(chart, language='pt')
    
    print("\nContribuição detalhada:")
    for item in temperament['contributions']:
        print(f"  - {item}")
        
    print("\n--- RESULTADO FINAL ---")
    points = temperament['points']
    print(f"Fogo: {points.get('Fogo', 0)} pontos")
    print(f"Terra: {points.get('Terra', 0)} pontos")
    print(f"Ar: {points.get('Ar', 0)} pontos")
    print(f"Água: {points.get('Água', 0)} pontos")
    
    # Comparação com dados do usuário
    user_fogo = 6
    user_terra = 0
    user_ar = 10
    user_agua = 1
    
    print("\n--- COMPARAÇÃO ---")
    print(f"Fogo:  Calculado={points.get('Fogo')} vs Usuário={user_fogo} -> {'OK' if points.get('Fogo')==user_fogo else 'DIFERENTE'}")
    print(f"Terra: Calculado={points.get('Terra')} vs Usuário={user_terra} -> {'OK' if points.get('Terra')==user_terra else 'DIFERENTE'}")
    print(f"Ar:    Calculado={points.get('Ar')} vs Usuário={user_ar} -> {'OK' if points.get('Ar')==user_ar else 'DIFERENTE'}")
    print(f"Água:  Calculado={points.get('Água')} vs Usuário={user_agua} -> {'OK' if points.get('Água')==user_agua else 'DIFERENTE'}")

if __name__ == "__main__":
    verify_temperament()
