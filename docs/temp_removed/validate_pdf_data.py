#!/usr/bin/env python3
"""
Script para validar os dados do PDF do mapa astral de Francisco.
Compara os dados apresentados no PDF com a lógica astrológica.
"""

# Dados do PDF fornecido
PDF_DATA = {
    "planets": {
        "sol": {"sign": "Libra", "degree": "27° 11' 30\"", "house": 8},
        "lua": {"sign": "Leão", "degree": "3° 53' 53\"", "house": 6},
        "mercury": {"sign": "Libra", "degree": "22° 17' 43\"", "house": 8},
        "venus": {"sign": "Sagitário", "degree": "13° 01' 46\"", "house": 10},
        "mars": {"sign": "Leão", "degree": "29° 46' 11\"", "house": 7},
        "jupiter": {"sign": "Libra", "degree": "22° 09' 38\"", "house": 8},
        "saturn": {"sign": "Libra", "degree": "14° 36' 24\"", "house": 8},
        "uranus": {"sign": "Escorpião", "degree": "28° 24' 56\"", "house": 9},
        "neptune": {"sign": "Sagitário", "degree": "22° 40' 57\"", "house": 10},
        "pluto": {"sign": "Libra", "degree": "24° 23' 19\"", "house": 8},
    },
    "points": {
        "ascendant": {"sign": "Aquário", "degree": "24° 46' 43\"", "house": 1},
        "midheaven": {"sign": "Escorpião", "degree": "28° 26' 23\"", "house": 10},
        "north_node": {"sign": "Câncer", "degree": "27° 15' 30\"", "house": 6},
        "south_node": {"sign": "Capricórnio", "degree": "27° 15' 30\"", "house": 12},
        "chiron": {"sign": "Touro", "degree": "21° 31' 01\"", "house": 3},
    }
}

# Mapeamento de signos para elementos
SIGN_ELEMENTS = {
    "Áries": "Fogo", "Touro": "Terra", "Gêmeos": "Ar", "Câncer": "Água",
    "Leão": "Fogo", "Virgem": "Terra", "Libra": "Ar", "Escorpião": "Água",
    "Sagitário": "Fogo", "Capricórnio": "Terra", "Aquário": "Ar", "Peixes": "Água"
}

# Mapeamento de signos para regentes
SIGN_RULERS = {
    "Áries": "Marte", "Touro": "Vênus", "Gêmeos": "Mercúrio", "Câncer": "Lua",
    "Leão": "Sol", "Virgem": "Mercúrio", "Libra": "Vênus", "Escorpião": "Plutão",
    "Sagitário": "Júpiter", "Capricórnio": "Saturno", "Aquário": "Urano", "Peixes": "Netuno"
}

def parse_degree(degree_str):
    """Converte grau em formato string para decimal."""
    try:
        parts = degree_str.replace('"', '').replace("'", " ").split()
        degrees = float(parts[0].replace('°', ''))
        minutes = float(parts[1]) if len(parts) > 1 else 0
        seconds = float(parts[2]) if len(parts) > 2 else 0
        return degrees + minutes/60 + seconds/3600
    except:
        return None

def calculate_temperament():
    """Calcula o temperamento baseado nos planetas."""
    elements = {"Fogo": 0, "Terra": 0, "Ar": 0, "Água": 0}
    
    for planet_key, planet_data in PDF_DATA["planets"].items():
        sign = planet_data["sign"]
        element = SIGN_ELEMENTS.get(sign)
        if element:
            elements[element] = elements.get(element, 0) + 1
    
    return elements

def check_ascendant_house():
    """Verifica se o Ascendente está na Casa 1 (sempre deve estar)."""
    asc_house = PDF_DATA["points"]["ascendant"]["house"]
    if asc_house != 1:
        return False, f"Ascendente está na Casa {asc_house}, mas SEMPRE deve estar na Casa 1"
    return True, "Ascendente corretamente na Casa 1"

def check_node_opposition():
    """Verifica se Nodo Norte e Sul estão opostos (devem estar 180° aparte)."""
    north_deg = parse_degree(PDF_DATA["points"]["north_node"]["degree"])
    south_deg = parse_degree(PDF_DATA["points"]["south_node"]["degree"])
    
    if north_deg is None or south_deg is None:
        return None, "Não foi possível calcular graus dos nodos"
    
    # Nodos devem estar em signos opostos
    north_sign = PDF_DATA["points"]["north_node"]["sign"]
    south_sign = PDF_DATA["points"]["south_node"]["sign"]
    
    signs = ["Áries", "Touro", "Gêmeos", "Câncer", "Leão", "Virgem",
             "Libra", "Escorpião", "Sagitário", "Capricórnio", "Aquário", "Peixes"]
    
    north_idx = signs.index(north_sign)
    south_idx = signs.index(south_sign)
    expected_south_idx = (north_idx + 6) % 12
    
    if south_idx == expected_south_idx:
        return True, f"Nodos em signos opostos: {north_sign} ↔ {south_sign}"
    else:
        return False, f"Nodos NÃO estão opostos: {north_sign} vs {south_sign} (esperado oposto de {north_sign})"

def check_midheaven_house():
    """Verifica se MC está na Casa 10 (sempre deve estar)."""
    mc_house = PDF_DATA["points"]["midheaven"]["house"]
    if mc_house != 10:
        return False, f"MC está na Casa {mc_house}, mas SEMPRE deve estar na Casa 10"
    return True, "MC corretamente na Casa 10"

def check_chart_ruler():
    """Verifica o regente do mapa (deve ser o regente do Ascendente)."""
    asc_sign = PDF_DATA["points"]["ascendant"]["sign"]
    expected_ruler = SIGN_RULERS.get(asc_sign)
    
    # Verificar onde está o regente
    ruler_planet_map = {
        "Sol": "sol", "Lua": "lua", "Mercúrio": "mercury", "Vênus": "venus",
        "Marte": "mars", "Júpiter": "jupiter", "Saturno": "saturn",
        "Urano": "uranus", "Netuno": "neptune", "Plutão": "pluto"
    }
    
    ruler_key = ruler_planet_map.get(expected_ruler)
    if ruler_key and ruler_key in PDF_DATA["planets"]:
        ruler_data = PDF_DATA["planets"][ruler_key]
        return True, f"Regente do mapa: {expected_ruler} em {ruler_data['sign']} na Casa {ruler_data['house']}"
    
    return None, f"Regente esperado: {expected_ruler} (não encontrado nos planetas)"

def check_planets_in_same_sign():
    """Verifica se há planetas no mesmo signo e se faz sentido."""
    sign_counts = {}
    for planet_key, planet_data in PDF_DATA["planets"].items():
        sign = planet_data["sign"]
        if sign not in sign_counts:
            sign_counts[sign] = []
        sign_counts[sign].append(planet_key)
    
    # Verificar agrupamentos
    issues = []
    for sign, planets in sign_counts.items():
        if len(planets) > 3:
            issues.append(f"⚠️  {len(planets)} planetas em {sign}: {', '.join(planets)}")
    
    if issues:
        return False, "\n".join(issues)
    return True, "Distribuição de planetas parece razoável"

print("=" * 80)
print("VALIDAÇÃO DOS DADOS DO PDF - FRANCISCO ALEXANDRE ARAUJO ROCHA")
print("=" * 80)

# 1. Verificar Ascendente
print("\n1. VERIFICAÇÃO DO ASCENDENTE:")
print("-" * 80)
asc_ok, asc_msg = check_ascendant_house()
print(f"{'✅' if asc_ok else '❌'} {asc_msg}")

# 2. Verificar MC
print("\n2. VERIFICAÇÃO DO MEIO DO CÉU:")
print("-" * 80)
mc_ok, mc_msg = check_midheaven_house()
print(f"{'✅' if mc_ok else '❌'} {mc_msg}")

# 3. Verificar Nodos
print("\n3. VERIFICAÇÃO DOS NODOS LUNARES:")
print("-" * 80)
node_ok, node_msg = check_node_opposition()
if node_ok is not None:
    print(f"{'✅' if node_ok else '❌'} {node_msg}")
else:
    print(f"⚠️  {node_msg}")

# 4. Verificar Regente do Mapa
print("\n4. VERIFICAÇÃO DO REGENTE DO MAPA:")
print("-" * 80)
ruler_ok, ruler_msg = check_chart_ruler()
if ruler_ok is not None:
    print(f"{'✅' if ruler_ok else '❌'} {ruler_msg}")
else:
    print(f"⚠️  {ruler_msg}")

# 5. Calcular Temperamento
print("\n5. CÁLCULO DO TEMPERAMENTO (Elementos):")
print("-" * 80)
temperament = calculate_temperament()
for element, count in temperament.items():
    print(f"{element:8}: {count:2} pontos")

# 6. Verificar Agrupamentos de Planetas
print("\n6. VERIFICAÇÃO DE AGRUPAMENTOS:")
print("-" * 80)
group_ok, group_msg = check_planets_in_same_sign()
if group_ok:
    print(f"✅ {group_msg}")
else:
    print(f"⚠️  {group_msg}")

# 7. Resumo de Posições
print("\n7. RESUMO DE POSIÇÕES PLANETÁRIAS:")
print("-" * 80)
print(f"{'Planeta':<12} | {'Signo':<12} | {'Grau':<15} | {'Casa':<5}")
print("-" * 80)
for planet_key, planet_data in PDF_DATA["planets"].items():
    planet_name = planet_key.capitalize()
    print(f"{planet_name:<12} | {planet_data['sign']:<12} | {planet_data['degree']:<15} | {planet_data['house']:<5}")

print("\n8. RESUMO DE PONTOS ESPECIAIS:")
print("-" * 80)
print(f"{'Ponto':<15} | {'Signo':<12} | {'Grau':<15} | {'Casa':<5}")
print("-" * 80)
for point_key, point_data in PDF_DATA["points"].items():
    point_name = point_key.capitalize()
    print(f"{point_name:<15} | {point_data['sign']:<12} | {point_data['degree']:<15} | {point_data['house']:<5}")

# 8. Verificações de Consistência
print("\n9. VERIFICAÇÕES DE CONSISTÊNCIA:")
print("-" * 80)

issues = []

# Verificar se há muitos planetas na Casa 8 (Stellium)
planets_in_house_8 = [p for p, d in PDF_DATA["planets"].items() if d["house"] == 8]
if len(planets_in_house_8) >= 4:
    issues.append(f"⚠️  STELLIUM na Casa 8: {len(planets_in_house_8)} planetas ({', '.join(planets_in_house_8)})")

# Verificar se há muitos planetas em Libra
planets_in_libra = [p for p, d in PDF_DATA["planets"].items() if d["sign"] == "Libra"]
if len(planets_in_libra) >= 5:
    issues.append(f"⚠️  STELLIUM em Libra: {len(planets_in_libra)} planetas ({', '.join(planets_in_libra)})")

# Verificar se Vênus está realmente em Sagitário (não Libra)
if PDF_DATA["planets"]["venus"]["sign"] != "Sagitário":
    issues.append(f"❌ Vênus está em {PDF_DATA['planets']['venus']['sign']}, mas deveria estar em Sagitário")

if issues:
    for issue in issues:
        print(issue)
else:
    print("✅ Nenhuma inconsistência grave encontrada")

print("\n" + "=" * 80)
print("CONCLUSÃO")
print("=" * 80)

all_ok = asc_ok and mc_ok and (node_ok is None or node_ok)

if all_ok:
    print("✅ Os dados básicos do PDF parecem estar corretos estruturalmente.")
    print("⚠️  Para validação completa, é necessário verificar os cálculos com Swiss Ephemeris.")
else:
    print("❌ Foram encontrados erros nos dados do PDF.")
    print("⚠️  Recomenda-se recalcular o mapa usando Swiss Ephemeris.")

print("\n" + "=" * 80)

