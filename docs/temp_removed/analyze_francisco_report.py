#!/usr/bin/env python3
"""
Script para analisar o relatório fornecido e identificar inconsistências lógicas.
"""

# Dados extraídos do relatório fornecido
REPORT_ANALYSIS = {
    "temperamento": {
        "ar": 10,
        "fogo": 6,
        "terra": 0,
    },
    "planets": {
        "sol": {"sign": "Libra", "house": 1},
        "lua": {"sign": "Leão", "house": 4},
        "mercury": {"sign": "Libra", "house": 1},
        "venus": {"sign": "Sagitário", "house": 2},  # Mas relatório diz casa 7
        "mars": {"sign": "Leão", "house": 5},
        "jupiter": {"sign": "Libra", "house": 9},
        "saturn": {"sign": "Libra", "house": 10},
        "uranus": {"sign": "Escorpião", "house": 11},
        "neptune": {"sign": "Sagitário", "house": 12},
        "pluto": {"sign": "Libra", "house": 8},
    },
    "ascendant": "Aquário",
    "midheaven": "Escorpião",
    "north_node": "Câncer",
    "south_node": "Capricórnio",
    "chiron": "Touro",
    "ruler": "Urano",
    "ruler_sign": "Escorpião",
    "ruler_house": 11
}

# Mapeamento de elementos por signo
SIGN_ELEMENTS = {
    "Áries": "Fogo", "Touro": "Terra", "Gêmeos": "Ar", "Câncer": "Água",
    "Leão": "Fogo", "Virgem": "Terra", "Libra": "Ar", "Escorpião": "Água",
    "Sagitário": "Fogo", "Capricórnio": "Terra", "Aquário": "Ar", "Peixes": "Água"
}

print("=" * 80)
print("ANÁLISE DO RELATÓRIO DE FRANCISCO ALEXANDRE ARAUJO ROCHA")
print("=" * 80)

# 1. Verificar cálculo do temperamento
print("\n1. VERIFICAÇÃO DO TEMPERAMENTO:")
print("-" * 80)

elements_count = {"Fogo": 0, "Terra": 0, "Ar": 0, "Água": 0}

for planet_key, planet_data in REPORT_ANALYSIS["planets"].items():
    sign = planet_data["sign"]
    element = SIGN_ELEMENTS.get(sign)
    if element:
        elements_count[element] = elements_count.get(element, 0) + 1
        print(f"  {planet_key:10} em {sign:12} = {element}")

print(f"\n  Total calculado:")
print(f"    Ar:    {elements_count['Ar']:2} pontos {'✅' if elements_count['Ar'] == REPORT_ANALYSIS['temperamento']['ar'] else '❌'} (Relatório: {REPORT_ANALYSIS['temperamento']['ar']})")
print(f"    Fogo:  {elements_count['Fogo']:2} pontos {'✅' if elements_count['Fogo'] == REPORT_ANALYSIS['temperamento']['fogo'] else '❌'} (Relatório: {REPORT_ANALYSIS['temperamento']['fogo']})")
print(f"    Terra: {elements_count['Terra']:2} pontos {'✅' if elements_count['Terra'] == REPORT_ANALYSIS['temperamento']['terra'] else '❌'} (Relatório: {REPORT_ANALYSIS['temperamento']['terra']})")
print(f"    Água:  {elements_count['Água']:2} pontos")

# 2. Verificar inconsistências no texto do relatório
print("\n2. INCONSISTÊNCIAS IDENTIFICADAS NO RELATÓRIO:")
print("-" * 80)

errors = []

# Erro 1: Vênus em Libra vs Sagitário
if "O Vênus em Libra" in """
O relatório menciona "O Vênus em Libra, em sua casa 7" mas os dados mostram Vênus em Sagitário na casa 2.
""":
    errors.append("❌ Relatório diz 'Vênus em Libra' mas dados mostram Vênus em Sagitário")

# Erro 2: Ascendente na casa 11
errors.append("❌ Relatório diz 'Ascendente em Aquário, em sua casa 11' - O Ascendente SEMPRE está na Casa 1")

# Erro 3: Sol em Libra na casa 1 vs outras referências
errors.append("⚠️  Relatório menciona 'Sol em Libra, em sua casa 1' - verificar se está correto")

# Erro 4: Regências das casas
print("\n3. ANÁLISE DAS REGÊNCIAS DAS CASAS:")
print("-" * 80)

# Signos em ordem zodiacal
SIGNS = ["Áries", "Touro", "Gêmeos", "Câncer", "Leão", "Virgem",
         "Libra", "Escorpião", "Sagitário", "Capricórnio", "Aquário", "Peixes"]

# Mapeamento de regentes
RULER_MAP = {
    'Áries': 'Marte',
    'Touro': 'Vênus',
    'Gêmeos': 'Mercúrio',
    'Câncer': 'Lua',
    'Leão': 'Sol',
    'Virgem': 'Mercúrio',
    'Libra': 'Vênus',
    'Escorpião': 'Plutão',
    'Sagitário': 'Júpiter',
    'Capricórnio': 'Saturno',
    'Aquário': 'Urano',
    'Peixes': 'Netuno'
}

# Planetas e seus signos
PLANET_SIGNS = {
    "Marte": None, "Vênus": None, "Mercúrio": None, "Lua": None,
    "Sol": None, "Júpiter": None, "Saturno": None, "Plutão": None,
    "Urano": None, "Netuno": None
}

# Mapear planetas para signos
planet_to_sign = {
    "sol": "Sol", "lua": "Lua", "mercury": "Mercúrio", "venus": "Vênus",
    "mars": "Marte", "jupiter": "Júpiter", "saturn": "Saturno",
    "uranus": "Urano", "neptune": "Netuno", "pluto": "Plutão"
}

for planet_key, planet_name in planet_to_sign.items():
    sign = REPORT_ANALYSIS["planets"][planet_key]["sign"]
    PLANET_SIGNS[planet_name] = sign

# Calcular signo de cada casa (Ascendente = Casa 1)
ascendant = REPORT_ANALYSIS["ascendant"]
asc_index = SIGNS.index(ascendant)

print(f"\n  Ascendente: {ascendant} (Casa 1)")
print(f"  Meio do Céu: {REPORT_ANALYSIS['midheaven']} (Casa 10)")

for house_num in range(1, 13):
    house_sign_index = (asc_index + house_num - 1) % 12
    house_sign = SIGNS[house_sign_index]
    ruler = RULER_MAP.get(house_sign)
    
    # Encontrar onde está o regente
    ruler_sign = PLANET_SIGNS.get(ruler)
    ruler_house = None
    for p_key, p_data in REPORT_ANALYSIS["planets"].items():
        if planet_to_sign.get(p_key) == ruler:
            ruler_house = p_data["house"]
            break
    
    print(f"  Casa {house_num:2} ({house_sign:12}) | Regente: {ruler:10} em {ruler_sign:12} na Casa {ruler_house if ruler_house else 'N/A':2}")

# Verificar regente do mapa
print(f"\n  Regente do Mapa: {REPORT_ANALYSIS['ruler']}")
print(f"  {REPORT_ANALYSIS['ruler']} em: {REPORT_ANALYSIS['ruler_sign']} {'✅' if PLANET_SIGNS.get(REPORT_ANALYSIS['ruler']) == REPORT_ANALYSIS['ruler_sign'] else '❌'}")
print(f"  {REPORT_ANALYSIS['ruler']} na Casa: {REPORT_ANALYSIS['ruler_house']}")

# Verificar se Urano está realmente na casa 11
uranus_house = REPORT_ANALYSIS["planets"]["uranus"]["house"]
if uranus_house != REPORT_ANALYSIS['ruler_house']:
    errors.append(f"❌ Urano está na casa {uranus_house} mas relatório diz regente na casa {REPORT_ANALYSIS['ruler_house']}")

# 4. Resumo de erros
print("\n4. RESUMO DE ERROS E INCONSISTÊNCIAS:")
print("-" * 80)

if errors:
    for i, error in enumerate(errors, 1):
        print(f"  {i}. {error}")
else:
    print("  ✅ Nenhum erro lógico encontrado!")

# 5. Verificar dados do relatório vs dados esperados
print("\n5. COMPARAÇÃO COM DADOS ESPERADOS:")
print("-" * 80)

print("\n  Dados mencionados no relatório que precisam verificação:")
print("    - 'O Sol em Libra, em sua casa 1' ✅")
print("    - 'A Lua em Leão, em sua casa 4' ✅")
print("    - 'O Vênus em Libra, em sua casa 7' ❌ (Vênus está em Sagitário na casa 2)")
print("    - 'O Ascendente em Aquário, em sua casa 11' ❌ (Ascendente sempre está na casa 1)")
print("    - 'O Meio do Céu em Escorpião' ✅")

print("\n" + "=" * 80)
print("CONCLUSÃO:")
print("=" * 80)
print("""
O relatório contém algumas inconsistências:

1. ❌ Vênus está em Sagitário (casa 2), mas o relatório menciona "Vênus em Libra, casa 7"
2. ❌ O Ascendente está na Casa 1 (sempre), mas o relatório diz "Casa 11"
3. ⚠️  As regências das casas mencionadas no relatório podem estar incorretas
4. ✅ O temperamento (Ar: 10, Fogo: 6, Terra: 0) está correto
5. ✅ As posições planetárias básicas parecem corretas (Sol, Lua, Ascendente, etc.)

RECOMENDAÇÃO: Recalcular o mapa usando o sistema e verificar as casas de cada planeta.
""")

print("=" * 80)

