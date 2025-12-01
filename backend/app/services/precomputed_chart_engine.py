"""
Motor de Cálculos Pré-Computados para o Mapa Astral.
Este módulo calcula TODOS os dados antes de enviar ao prompt.
A IA NÃO pode calcular nada - apenas interpretar dados já calculados.

TRAVAS DE SEGURANÇA:
1. Todos os cálculos são feitos pelo código Python
2. Temperamento é calculado matematicamente
3. Dignidades são identificadas por tabela fixa
4. Regente é mapeado por tabela fixa (NUNCA Quíron)
5. Elementos são mapeados por tabela fixa (Libra = AR, Leão = FOGO, etc)
"""
from typing import Dict, List, Any, Optional
from app.services.astrology_calculator import get_zodiac_sign


# TABELA FIXA: Signos → Elementos (FONTE ÚNICA DE VERDADE)
SIGN_TO_ELEMENT = {
    'Áries': 'Fogo', 'Aries': 'Fire',
    'Touro': 'Terra', 'Taurus': 'Earth',
    'Gêmeos': 'Ar', 'Gemini': 'Air',
    'Câncer': 'Água', 'Cancer': 'Water',
    'Leão': 'Fogo', 'Leo': 'Fire',
    'Virgem': 'Terra', 'Virgo': 'Earth',
    'Libra': 'Ar', 'Libra': 'Air',  # ← LIBRA É AR, NÃO FOGO
    'Escorpião': 'Água', 'Scorpio': 'Water',
    'Sagitário': 'Fogo', 'Sagittarius': 'Fire',
    'Capricórnio': 'Terra', 'Capricorn': 'Earth',
    'Aquário': 'Ar', 'Aquarius': 'Air',
    'Peixes': 'Água', 'Pisces': 'Water',
}

# TABELA FIXA: Signos → Modalidades
SIGN_TO_MODALITY = {
    'Áries': 'Cardinal', 'Aries': 'Cardinal',
    'Touro': 'Fixo', 'Taurus': 'Fixed',
    'Gêmeos': 'Mutável', 'Gemini': 'Mutable',
    'Câncer': 'Cardinal', 'Cancer': 'Cardinal',
    'Leão': 'Fixo', 'Leo': 'Fixed',
    'Virgem': 'Mutável', 'Virgo': 'Mutable',
    'Libra': 'Cardinal', 'Libra': 'Cardinal',
    'Escorpião': 'Fixo', 'Scorpio': 'Fixed',
    'Sagitário': 'Mutável', 'Sagittarius': 'Mutable',
    'Capricórnio': 'Cardinal', 'Capricorn': 'Cardinal',
    'Aquário': 'Fixo', 'Aquarius': 'Fixed',
    'Peixes': 'Mutável', 'Pisces': 'Mutable',
}

# TABELA FIXA: Signos → Regentes (NUNCA QUÍRON)
SIGN_TO_RULER = {
    'Áries': 'Marte', 'Aries': 'Mars',
    'Touro': 'Vênus', 'Taurus': 'Venus',
    'Gêmeos': 'Mercúrio', 'Gemini': 'Mercury',
    'Câncer': 'Lua', 'Cancer': 'Moon',
    'Leão': 'Sol', 'Leo': 'Sun',
    'Virgem': 'Mercúrio', 'Virgo': 'Mercury',
    'Libra': 'Vênus', 'Libra': 'Venus',
    'Escorpião': 'Marte', 'Scorpio': 'Mars',  # Tradicional; moderno = Plutão
    'Sagitário': 'Júpiter', 'Sagittarius': 'Jupiter',
    'Capricórnio': 'Saturno', 'Capricorn': 'Saturn',
    'Aquário': 'Urano', 'Aquarius': 'Uranus',  # Tradicional = Saturno; moderno = Urano
    'Peixes': 'Netuno', 'Pisces': 'Neptune',  # Tradicional = Júpiter; moderno = Netuno
}

# TABELA FIXA: Dignidades Planetárias
PLANET_DIGNITIES = {
    'Sol': {'domicile': ['Leão', 'Leo'], 'exaltation': ['Áries', 'Aries'], 'detriment': ['Aquário', 'Aquarius'], 'fall': ['Libra', 'Libra']},
    'Sun': {'domicile': ['Leão', 'Leo'], 'exaltation': ['Áries', 'Aries'], 'detriment': ['Aquário', 'Aquarius'], 'fall': ['Libra', 'Libra']},
    'Lua': {'domicile': ['Câncer', 'Cancer'], 'exaltation': ['Touro', 'Taurus'], 'detriment': ['Capricórnio', 'Capricorn'], 'fall': ['Escorpião', 'Scorpio']},
    'Moon': {'domicile': ['Câncer', 'Cancer'], 'exaltation': ['Touro', 'Taurus'], 'detriment': ['Capricórnio', 'Capricorn'], 'fall': ['Escorpião', 'Scorpio']},
    'Mercúrio': {'domicile': ['Gêmeos', 'Gemini', 'Virgem', 'Virgo'], 'exaltation': ['Virgem', 'Virgo'], 'detriment': ['Sagitário', 'Sagittarius', 'Peixes', 'Pisces'], 'fall': ['Peixes', 'Pisces']},
    'Mercury': {'domicile': ['Gêmeos', 'Gemini', 'Virgem', 'Virgo'], 'exaltation': ['Virgem', 'Virgo'], 'detriment': ['Sagitário', 'Sagittarius', 'Peixes', 'Pisces'], 'fall': ['Peixes', 'Pisces']},
    'Vênus': {'domicile': ['Touro', 'Taurus', 'Libra', 'Libra'], 'exaltation': ['Peixes', 'Pisces'], 'detriment': ['Áries', 'Aries', 'Escorpião', 'Scorpio'], 'fall': ['Virgem', 'Virgo']},
    'Venus': {'domicile': ['Touro', 'Taurus', 'Libra', 'Libra'], 'exaltation': ['Peixes', 'Pisces'], 'detriment': ['Áries', 'Aries', 'Escorpião', 'Scorpio'], 'fall': ['Virgem', 'Virgo']},
    'Marte': {'domicile': ['Áries', 'Aries', 'Escorpião', 'Scorpio'], 'exaltation': ['Capricórnio', 'Capricorn'], 'detriment': ['Libra', 'Libra', 'Touro', 'Taurus'], 'fall': ['Câncer', 'Cancer']},
    'Mars': {'domicile': ['Áries', 'Aries', 'Escorpião', 'Scorpio'], 'exaltation': ['Capricórnio', 'Capricorn'], 'detriment': ['Libra', 'Libra', 'Touro', 'Taurus'], 'fall': ['Câncer', 'Cancer']},
    'Júpiter': {'domicile': ['Sagitário', 'Sagittarius', 'Peixes', 'Pisces'], 'exaltation': ['Câncer', 'Cancer'], 'detriment': ['Gêmeos', 'Gemini', 'Virgem', 'Virgo'], 'fall': ['Capricórnio', 'Capricorn']},
    'Jupiter': {'domicile': ['Sagitário', 'Sagittarius', 'Peixes', 'Pisces'], 'exaltation': ['Câncer', 'Cancer'], 'detriment': ['Gêmeos', 'Gemini', 'Virgem', 'Virgo'], 'fall': ['Capricórnio', 'Capricorn']},
    'Saturno': {'domicile': ['Capricórnio', 'Capricorn', 'Aquário', 'Aquarius'], 'exaltation': ['Libra', 'Libra'], 'detriment': ['Câncer', 'Cancer', 'Leão', 'Leo'], 'fall': ['Áries', 'Aries']},
    'Saturn': {'domicile': ['Capricórnio', 'Capricorn', 'Aquário', 'Aquarius'], 'exaltation': ['Libra', 'Libra'], 'detriment': ['Câncer', 'Cancer', 'Leão', 'Leo'], 'fall': ['Áries', 'Aries']},
    'Urano': {'domicile': ['Aquário', 'Aquarius'], 'exaltation': ['Escorpião', 'Scorpio'], 'detriment': ['Leão', 'Leo'], 'fall': ['Touro', 'Taurus']},
    'Uranus': {'domicile': ['Aquário', 'Aquarius'], 'exaltation': ['Escorpião', 'Scorpio'], 'detriment': ['Leão', 'Leo'], 'fall': ['Touro', 'Taurus']},
    'Netuno': {'domicile': ['Peixes', 'Pisces'], 'exaltation': ['Leão', 'Leo'], 'detriment': ['Virgem', 'Virgo'], 'fall': ['Aquário', 'Aquarius']},
    'Neptune': {'domicile': ['Peixes', 'Pisces'], 'exaltation': ['Leão', 'Leo'], 'detriment': ['Virgem', 'Virgo'], 'fall': ['Aquário', 'Aquarius']},
    'Plutão': {'domicile': ['Escorpião', 'Scorpio'], 'exaltation': ['Áries', 'Aries'], 'detriment': ['Touro', 'Taurus'], 'fall': ['Libra', 'Libra']},
    'Pluto': {'domicile': ['Escorpião', 'Scorpio'], 'exaltation': ['Áries', 'Aries'], 'detriment': ['Touro', 'Taurus'], 'fall': ['Libra', 'Libra']},
}


def calculate_temperament_from_chart(chart_data: Dict[str, Any], language: str = 'pt') -> Dict[str, Any]:
    """
    Calcula temperamento matematicamente usando APENAS signos.
    NÃO permite invenção - usa tabela fixa de elementos.
    
    Args:
        chart_data: Dados do mapa astral com signos
        language: 'pt' ou 'en'
    
    Returns:
        Dict com pontuação de elementos e análise
    """
    # Criar dicionário de pontos com chaves corretas
    if language == 'pt':
        points = {'Fogo': 0, 'Terra': 0, 'Ar': 0, 'Água': 0}
    else:
        points = {'Fire': 0, 'Earth': 0, 'Air': 0, 'Water': 0}
    
    # Planetas principais (3 pontos)
    major_planets = [
        ('sun_sign', 'Sol/Sun'),
        ('moon_sign', 'Lua/Moon'),
        ('ascendant_sign', 'Ascendente/Ascendant'),
    ]
    
    # Planetas secundários (1 ponto)
    minor_planets = [
        ('mercury_sign', 'Mercúrio/Mercury'),
        ('venus_sign', 'Vênus/Venus'),
        ('mars_sign', 'Marte/Mars'),
        ('jupiter_sign', 'Júpiter/Jupiter'),
        ('saturn_sign', 'Saturno/Saturn'),
        ('uranus_sign', 'Urano/Uranus'),
        ('neptune_sign', 'Netuno/Neptune'),
        ('pluto_sign', 'Plutão/Pluto'),
    ]
    
    planet_contributions = []
    
    # Processar planetas principais
    for sign_key, planet_name in major_planets:
        sign = chart_data.get(sign_key)
        if sign:
            # Obter elemento do signo (pode estar em PT ou EN)
            element = SIGN_TO_ELEMENT.get(sign, 'Unknown')
            if element != 'Unknown':
                # Se estiver em inglês e precisamos em português, ou vice-versa, normalizar
                if language == 'pt' and element in ['Fire', 'Earth', 'Air', 'Water']:
                    element_map = {'Fire': 'Fogo', 'Earth': 'Terra', 'Air': 'Ar', 'Water': 'Água'}
                    element = element_map.get(element, element)
                elif language == 'en' and element in ['Fogo', 'Terra', 'Ar', 'Água']:
                    element_map = {'Fogo': 'Fire', 'Terra': 'Earth', 'Ar': 'Air', 'Água': 'Water'}
                    element = element_map.get(element, element)
                
                if element in points:
                    points[element] += 3
                    planet_contributions.append(f"{planet_name} em {sign} ({element}): 3 pontos")
    
    # Processar planetas secundários
    for sign_key, planet_name in minor_planets:
        sign = chart_data.get(sign_key)
        if sign:
            element = SIGN_TO_ELEMENT.get(sign, 'Unknown')
            if element != 'Unknown':
                # Normalizar elemento para o idioma correto
                if language == 'pt' and element in ['Fire', 'Earth', 'Air', 'Water']:
                    element_map = {'Fire': 'Fogo', 'Earth': 'Terra', 'Air': 'Ar', 'Water': 'Água'}
                    element = element_map.get(element, element)
                elif language == 'en' and element in ['Fogo', 'Terra', 'Ar', 'Água']:
                    element_map = {'Fogo': 'Fire', 'Terra': 'Earth', 'Ar': 'Air', 'Água': 'Water'}
                    element = element_map.get(element, element)
                
                if element in points:
                    points[element] += 1
                    planet_contributions.append(f"{planet_name} em {sign} ({element}): 1 ponto")
    
    # Identificar excesso e falta
    max_element = max(points, key=points.get)
    min_element = min(points, key=points.get)
    
    return {
        'points': points,
        'contributions': planet_contributions,
        'dominant': max_element,
        'lacking': min_element if points[min_element] == 0 else None,
        'total_points': sum(points.values()),
    }


def get_planet_dignity(planet: str, sign: str) -> str:
    """
    Identifica dignidade de um planeta usando tabela fixa.
    
    Returns:
        'domicile', 'exaltation', 'detriment', 'fall', ou 'peregrine'
    """
    dignities = PLANET_DIGNITIES.get(planet, {})
    
    if sign in dignities.get('domicile', []):
        return 'domicile'
    elif sign in dignities.get('exaltation', []):
        return 'exaltation'
    elif sign in dignities.get('detriment', []):
        return 'detriment'
    elif sign in dignities.get('fall', []):
        return 'fall'
    else:
        return 'peregrine'


def get_chart_ruler(ascendant_sign: str, chart_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Identifica o regente do mapa usando tabela fixa.
    NUNCA retorna Quíron - apenas planetas clássicos.
    
    Returns:
        Dict com planeta regente, signo e grau
    """
    ruler_planet = SIGN_TO_RULER.get(ascendant_sign)
    
    if not ruler_planet:
        return {'error': f'Regente não encontrado para {ascendant_sign}'}
    
    # Mapear para chaves do chart_data
    planet_key_map = {
        'Sol': 'sun_sign', 'Sun': 'sun_sign',
        'Lua': 'moon_sign', 'Moon': 'moon_sign',
        'Mercúrio': 'mercury_sign', 'Mercury': 'mercury_sign',
        'Vênus': 'venus_sign', 'Venus': 'venus_sign',
        'Marte': 'mars_sign', 'Mars': 'mars_sign',
        'Júpiter': 'jupiter_sign', 'Jupiter': 'jupiter_sign',
        'Saturno': 'saturn_sign', 'Saturn': 'saturn_sign',
        'Urano': 'uranus_sign', 'Uranus': 'uranus_sign',
        'Netuno': 'neptune_sign', 'Neptune': 'neptune_sign',
        'Plutão': 'pluto_sign', 'Pluto': 'pluto_sign',
    }
    
    sign_key = planet_key_map.get(ruler_planet)
    ruler_sign = chart_data.get(sign_key) if sign_key else None
    
    return {
        'planet': ruler_planet,
        'sign': ruler_sign,
        'ascendant': ascendant_sign,
    }


def calculate_stelliums(chart_data: Dict[str, Any], language: str = 'pt') -> List[Dict[str, Any]]:
    """
    Calcula stelliums (3+ planetas no mesmo signo).
    
    Returns:
        Lista de dicts com signo e planetas no stellium
    """
    from collections import defaultdict
    
    # Mapear planetas para signos
    planet_sign_map = {
        'sun_sign': 'Sol',
        'moon_sign': 'Lua',
        'mercury_sign': 'Mercúrio',
        'venus_sign': 'Vênus',
        'mars_sign': 'Marte',
        'jupiter_sign': 'Júpiter',
        'saturn_sign': 'Saturno',
        'uranus_sign': 'Urano',
        'neptune_sign': 'Netuno',
        'pluto_sign': 'Plutão',
    }
    
    # Agrupar planetas por signo
    sign_planets = defaultdict(list)
    for sign_key, planet_name in planet_sign_map.items():
        sign = chart_data.get(sign_key)
        if sign:
            sign_planets[sign].append(planet_name)
    
    # Identificar stelliums (3+ planetas)
    stelliums = []
    for sign, planets in sign_planets.items():
        if len(planets) >= 3:
            stelliums.append({
                'sign': sign,
                'planets': planets,
                'count': len(planets)
            })
    
    return stelliums


def get_validated_aspects(chart_data: Dict[str, Any], language: str = 'pt') -> List[Dict[str, Any]]:
    """
    Obtém aspectos validados do chart_data (se disponíveis).
    
    Returns:
        Lista de aspectos validados
    """
    validated_aspects = chart_data.get('_validated_aspects', [])
    
    if not validated_aspects:
        return []
    
    # Mapear nomes de planetas
    planet_name_map_pt = {
        'sun': 'Sol', 'moon': 'Lua', 'mercury': 'Mercúrio', 'venus': 'Vênus',
        'mars': 'Marte', 'jupiter': 'Júpiter', 'saturn': 'Saturno',
        'uranus': 'Urano', 'neptune': 'Netuno', 'pluto': 'Plutão'
    }
    
    aspect_name_map_pt = {
        'conjunction': 'Conjunção',
        'sextile': 'Sextil',
        'square': 'Quadratura',
        'trine': 'Trígono',
        'opposition': 'Oposição',
        'quincunx': 'Quincúncio'
    }
    
    aspect_name_map_en = {
        'conjunction': 'Conjunction',
        'sextile': 'Sextile',
        'square': 'Square',
        'trine': 'Trine',
        'opposition': 'Opposition',
        'quincunx': 'Quincunx'
    }
    
    formatted_aspects = []
    for aspect in validated_aspects:
        planet1 = aspect.get('planet1', '')
        planet2 = aspect.get('planet2', '')
        aspect_type = aspect.get('aspect', '')
        
        if language == 'pt':
            planet1_name = planet_name_map_pt.get(planet1, planet1.capitalize())
            planet2_name = planet_name_map_pt.get(planet2, planet2.capitalize())
            aspect_name = aspect_name_map_pt.get(aspect_type, aspect_type)
        else:
            planet1_name = planet1.capitalize()
            planet2_name = planet2.capitalize()
            aspect_name = aspect_name_map_en.get(aspect_type, aspect_type)
        
        formatted_aspects.append({
            'planet1': planet1_name,
            'planet2': planet2_name,
            'aspect': aspect_name,
            'type': aspect_type,
            'distance': aspect.get('distance', 0)
        })
    
    return formatted_aspects


def create_precomputed_data_block(chart_data: Dict[str, Any], language: str = 'pt') -> str:
    """
    Cria bloco de dados PRÉ-CALCULADOS para o prompt.
    A IA NÃO pode calcular - apenas ler e interpretar estes dados.
    
    Args:
        chart_data: Dados do mapa astral
        language: 'pt' ou 'en'
    
    Returns:
        String formatada com TODOS os cálculos já feitos
    """
    if language == 'pt':
        # Calcular temperamento
        temperament = calculate_temperament_from_chart(chart_data, 'pt')
        
        # Calcular regente
        ascendant_sign = chart_data.get('ascendant_sign', 'Não informado')
        ruler_info = get_chart_ruler(ascendant_sign, chart_data)
        
        # Identificar dignidades de TODOS os planetas (incluindo transpessoais)
        planets_to_check = [
            ('sun_sign', 'Sol'),
            ('moon_sign', 'Lua'),
            ('mercury_sign', 'Mercúrio'),
            ('venus_sign', 'Vênus'),
            ('mars_sign', 'Marte'),
            ('jupiter_sign', 'Júpiter'),
            ('saturn_sign', 'Saturno'),
            ('uranus_sign', 'Urano'),
            ('neptune_sign', 'Netuno'),
            ('pluto_sign', 'Plutão'),
        ]
        
        dignities_list = []
        for sign_key, planet_name in planets_to_check:
            sign = chart_data.get(sign_key)
            if sign:
                dignity = get_planet_dignity(planet_name, sign)
                dignity_names = {
                    'domicile': 'DOMICÍLIO',
                    'exaltation': 'EXALTAÇÃO',
                    'detriment': 'DETRIMENTO',
                    'fall': 'QUEDA',
                    'peregrine': 'PEREGRINO',
                }
                dignities_list.append(f"  • {planet_name} em {sign}: {dignity_names[dignity]}")
        
        # Calcular stelliums
        stelliums = calculate_stelliums(chart_data, 'pt')
        stelliums_text = []
        if stelliums:
            for st in stelliums:
                planets_str = ', '.join(st['planets'])
                stelliums_text.append(f"  • STELLIUM em {st['sign']}: {planets_str} ({st['count']} planetas)")
        else:
            stelliums_text.append("  • Nenhum stellium identificado (3+ planetas no mesmo signo)")
        
        # Obter aspectos validados
        aspects = get_validated_aspects(chart_data, 'pt')
        aspects_text = []
        if aspects:
            for asp in aspects:
                aspects_text.append(f"  • {asp['planet1']} {asp['aspect']} {asp['planet2']} (distância: {asp['distance']:.1f}°)")
        else:
            aspects_text.append("  • Aspectos não calculados (requer longitudes precisas)")
        
        block = f"""
═══════════════════════════════════════════════════════════════
🔒 DADOS PRÉ-CALCULADOS (TRAVAS DE SEGURANÇA ATIVADAS)
═══════════════════════════════════════════════════════════════

⚠️ INSTRUÇÃO CRÍTICA PARA A IA:
Você NÃO deve calcular NADA. Todos os dados abaixo foram calculados
matematicamente pelo código Python usando Swiss Ephemeris.
Use APENAS estes dados. NÃO invente, NÃO estime, NÃO "adivinhe".

⚠️⚠️⚠️ VALIDAÇÃO OBRIGATÓRIA ⚠️⚠️⚠️
Antes de escrever sobre temperamento, você DEVE:
1. Ler os pontos EXATOS abaixo
2. Usar EXATAMENTE esses números
3. NÃO recalcular ou estimar
4. Se o bloco diz "Água: 8 pontos", você DEVE dizer "Água com 8 pontos"
5. Se o bloco diz "ELEMENTO DOMINANTE: Água", você DEVE dizer "Água é dominante"

───────────────────────────────────────────────────────────────
📊 TEMPERAMENTO (CALCULADO MATEMATICAMENTE) - USE APENAS ESTES DADOS
───────────────────────────────────────────────────────────────

🎯 PONTUAÇÃO DE ELEMENTOS (já calculada - USE EXATAMENTE ESTES NÚMEROS):
  • Fogo: {temperament['points'].get('Fogo', 0)} pontos
  • Terra: {temperament['points'].get('Terra', 0)} pontos
  • Ar: {temperament['points'].get('Ar', 0)} pontos
  • Água: {temperament['points'].get('Água', 0)} pontos

🎯 ELEMENTO DOMINANTE: {temperament['dominant']} (USE EXATAMENTE ESTE)
🎯 ELEMENTO AUSENTE: {temperament['lacking'] if temperament['lacking'] else 'Nenhum (todos presentes)'} (USE EXATAMENTE ESTE)

📋 CONTRIBUIÇÃO DE CADA PLANETA (para referência):
{chr(10).join(temperament['contributions'])}

⚠️ LEMBRE-SE: Se o bloco diz "Água: 8 pontos" e "ELEMENTO DOMINANTE: Água",
você NÃO PODE dizer "Fogo dominante" ou "Água ausente". Use EXATAMENTE os dados acima.

───────────────────────────────────────────────────────────────
👑 REGENTE DO MAPA (IDENTIFICADO POR TABELA FIXA)
───────────────────────────────────────────────────────────────

Ascendente: {ascendant_sign}
Regente: {ruler_info['planet']} (NUNCA Quíron - este é um asteroide)
Regente em: {ruler_info['sign'] or 'Não calculado'}

───────────────────────────────────────────────────────────────
🏛️ DIGNIDADES PLANETÁRIAS (IDENTIFICADAS POR TABELA FIXA)
───────────────────────────────────────────────────────────────

{chr(10).join(dignities_list)}

───────────────────────────────────────────────────────────────
⭐ STELLIUMS (3+ PLANETAS NO MESMO SIGNO)
───────────────────────────────────────────────────────────────

{chr(10).join(stelliums_text)}

⚠️ IMPORTANTE: Stelliums são identificados apenas quando há 3 ou mais planetas no mesmo signo.
Se não houver stellium listado acima, NÃO invente um.

───────────────────────────────────────────────────────────────
🔗 ASPECTOS VALIDADOS (CALCULADOS MATEMATICAMENTE)
───────────────────────────────────────────────────────────────

{chr(10).join(aspects_text)}

⚠️ CRÍTICO: Use APENAS os aspectos listados acima. NÃO invente aspectos.
Se não houver aspectos listados, NÃO mencione aspectos específicos na interpretação.

───────────────────────────────────────────────────────────────
🔍 MAPEAMENTO FIXO DE ELEMENTOS (NÃO PODE SER ALTERADO)
───────────────────────────────────────────────────────────────

FOGO: Áries, Leão, Sagitário
TERRA: Touro, Virgem, Capricórnio
AR: Gêmeos, LIBRA, Aquário  ← LIBRA É AR!
ÁGUA: Câncer, Escorpião, Peixes

⚠️ PROIBIDO dizer que Libra é Fogo ou Terra
⚠️ PROIBIDO dizer que Leão é Água
⚠️ PROIBIDO dizer que Quíron é regente

═══════════════════════════════════════════════════════════════
"""
        return block
    
    else:  # English
        # Calculate temperament
        temperament = calculate_temperament_from_chart(chart_data, 'en')
        
        # Calculate ruler
        ascendant_sign = chart_data.get('ascendant_sign', 'Not provided')
        ruler_info = get_chart_ruler(ascendant_sign, chart_data)
        
        # Identify dignities of ALL planets (including transpersonal)
        planets_to_check = [
            ('sun_sign', 'Sun'),
            ('moon_sign', 'Moon'),
            ('mercury_sign', 'Mercury'),
            ('venus_sign', 'Venus'),
            ('mars_sign', 'Mars'),
            ('jupiter_sign', 'Jupiter'),
            ('saturn_sign', 'Saturn'),
            ('uranus_sign', 'Uranus'),
            ('neptune_sign', 'Neptune'),
            ('pluto_sign', 'Pluto'),
        ]
        
        dignities_list = []
        for sign_key, planet_name in planets_to_check:
            sign = chart_data.get(sign_key)
            if sign:
                dignity = get_planet_dignity(planet_name, sign)
                dignity_names = {
                    'domicile': 'DOMICILE',
                    'exaltation': 'EXALTATION',
                    'detriment': 'DETRIMENT',
                    'fall': 'FALL',
                    'peregrine': 'PEREGRINE',
                }
                dignities_list.append(f"  • {planet_name} in {sign}: {dignity_names[dignity]}")
        
        # Calculate stelliums
        stelliums = calculate_stelliums(chart_data, 'en')
        stelliums_text = []
        if stelliums:
            for st in stelliums:
                planets_str = ', '.join(st['planets'])
                stelliums_text.append(f"  • STELLIUM in {st['sign']}: {planets_str} ({st['count']} planets)")
        else:
            stelliums_text.append("  • No stelliums identified (3+ planets in same sign)")
        
        # Get validated aspects
        aspects = get_validated_aspects(chart_data, 'en')
        aspects_text = []
        if aspects:
            for asp in aspects:
                aspects_text.append(f"  • {asp['planet1']} {asp['aspect']} {asp['planet2']} (distance: {asp['distance']:.1f}°)")
        else:
            aspects_text.append("  • Aspects not calculated (requires precise longitudes)")
        
        block = f"""
═══════════════════════════════════════════════════════════════
🔒 PRE-COMPUTED DATA (SAFETY LOCKS ACTIVATED)
═══════════════════════════════════════════════════════════════

⚠️ CRITICAL INSTRUCTION FOR AI:
You MUST NOT calculate ANYTHING. All data below was mathematically
calculated by Python code using Swiss Ephemeris.
Use ONLY this data. DO NOT invent, DO NOT estimate, DO NOT "guess".

⚠️⚠️⚠️ MANDATORY VALIDATION ⚠️⚠️⚠️
Before writing about temperament, you MUST:
1. Read the EXACT points below
2. Use EXACTLY these numbers
3. DO NOT recalculate or estimate
4. If the block says "Water: 8 points", you MUST say "Water with 8 points"
5. If the block says "DOMINANT ELEMENT: Water", you MUST say "Water is dominant"

───────────────────────────────────────────────────────────────
📊 TEMPERAMENT (MATHEMATICALLY CALCULATED) - USE ONLY THIS DATA
───────────────────────────────────────────────────────────────

🎯 ELEMENT SCORES (pre-calculated - USE EXACTLY THESE NUMBERS):
  • Fire: {temperament['points'].get('Fire', 0)} points
  • Earth: {temperament['points'].get('Earth', 0)} points
  • Air: {temperament['points'].get('Air', 0)} points
  • Water: {temperament['points'].get('Water', 0)} points

🎯 DOMINANT ELEMENT: {temperament['dominant']} (USE EXACTLY THIS)
🎯 LACKING ELEMENT: {temperament['lacking'] if temperament['lacking'] else 'None (all present)'} (USE EXACTLY THIS)

📋 PLANET CONTRIBUTIONS (for reference):
{chr(10).join(temperament['contributions'])}

⚠️ REMEMBER: If the block says "Water: 8 points" and "DOMINANT ELEMENT: Water",
you CANNOT say "Fire dominant" or "Water absent". Use EXACTLY the data above.

───────────────────────────────────────────────────────────────
👑 CHART RULER (IDENTIFIED BY FIXED TABLE)
───────────────────────────────────────────────────────────────

Ascendant: {ascendant_sign}
Ruler: {ruler_info['planet']} (NEVER Chiron - it's an asteroid)
Ruler in: {ruler_info['sign'] or 'Not calculated'}

───────────────────────────────────────────────────────────────
🏛️ PLANETARY DIGNITIES (IDENTIFIED BY FIXED TABLE)
───────────────────────────────────────────────────────────────

{chr(10).join(dignities_list)}

───────────────────────────────────────────────────────────────
⭐ STELLIUMS (3+ PLANETS IN SAME SIGN)
───────────────────────────────────────────────────────────────

{chr(10).join(stelliums_text)}

⚠️ IMPORTANT: Stelliums are identified only when there are 3 or more planets in the same sign.
If no stellium is listed above, DO NOT invent one.

───────────────────────────────────────────────────────────────
🔗 VALIDATED ASPECTS (MATHEMATICALLY CALCULATED)
───────────────────────────────────────────────────────────────

{chr(10).join(aspects_text)}

⚠️ CRITICAL: Use ONLY the aspects listed above. DO NOT invent aspects.
If no aspects are listed, DO NOT mention specific aspects in the interpretation.

───────────────────────────────────────────────────────────────
🔍 FIXED ELEMENT MAPPING (CANNOT BE CHANGED)
───────────────────────────────────────────────────────────────

FIRE: Aries, Leo, Sagittarius
EARTH: Taurus, Virgo, Capricorn
AIR: Gemini, LIBRA, Aquarius  ← LIBRA IS AIR!
WATER: Cancer, Scorpio, Pisces

⚠️ FORBIDDEN to say Libra is Fire or Earth
⚠️ FORBIDDEN to say Leo is Water
⚠️ FORBIDDEN to say Chiron is a ruler

═══════════════════════════════════════════════════════════════
"""
        return block


def create_planet_safety_block(planet: str, sign: str, house: Optional[int] = None, language: str = 'pt') -> str:
    """
    Cria bloco de segurança específico para interpretação de um planeta.
    Fornece elemento do signo e dignidade calculados.
    
    Args:
        planet: Nome do planeta
        sign: Signo onde o planeta está
        house: Casa onde o planeta está (opcional)
        language: 'pt' ou 'en'
    
    Returns:
        Bloco formatado com dados pré-calculados
    """
    element = SIGN_TO_ELEMENT.get(sign, 'Desconhecido' if language == 'pt' else 'Unknown')
    modality = SIGN_TO_MODALITY.get(sign, 'Desconhecida' if language == 'pt' else 'Unknown')
    dignity = get_planet_dignity(planet, sign)
    
    dignity_names_pt = {
        'domicile': 'DOMICÍLIO (planeta está em casa)',
        'exaltation': 'EXALTAÇÃO (planeta opera em sua melhor forma)',
        'detriment': 'DETRIMENTO (planeta está desconfortável)',
        'fall': 'QUEDA (planeta precisa de esforço extra)',
        'peregrine': 'PEREGRINO (planeta depende de aspectos)'
    }
    
    dignity_names_en = {
        'domicile': 'DOMICILE (planet is at home)',
        'exaltation': 'EXALTATION (planet operates at its best)',
        'detriment': 'DETRIMENT (planet is uncomfortable)',
        'fall': 'FALL (planet needs extra effort)',
        'peregrine': 'PEREGRINE (planet depends on aspects)'
    }
    
    if language == 'pt':
        house_str = f"na Casa {house}" if house else "sem casa especificada"
        return f"""
═══════════════════════════════════════════════════════════════
🔒 DADOS PRÉ-CALCULADOS PARA {planet.upper()}
═══════════════════════════════════════════════════════════════

⚠️ ATENÇÃO IA: Use APENAS estes dados calculados. NÃO invente.

PLANETA: {planet}
SIGNO: {sign}
ELEMENTO DO SIGNO: {element} (FIXO - não pode mudar)
MODALIDADE: {modality}
CASA: {house_str}
DIGNIDADE: {dignity_names_pt[dignity]}

REGRAS CRÍTICAS:
• {sign} é SEMPRE elemento {element}
• Dignidade de {planet} em {sign} é {dignity.upper()}
• NÃO calcule nada - interprete apenas
═══════════════════════════════════════════════════════════════
"""
    else:
        house_str = f"in House {house}" if house else "no house specified"
        return f"""
═══════════════════════════════════════════════════════════════
🔒 PRE-COMPUTED DATA FOR {planet.upper()}
═══════════════════════════════════════════════════════════════

⚠️ AI ATTENTION: Use ONLY this calculated data. DO NOT invent.

PLANET: {planet}
SIGN: {sign}
SIGN ELEMENT: {element} (FIXED - cannot change)
MODALITY: {modality}
HOUSE: {house_str}
DIGNITY: {dignity_names_en[dignity]}

CRITICAL RULES:
• {sign} is ALWAYS element {element}
• Dignity of {planet} in {sign} is {dignity.upper()}
• DO NOT calculate anything - only interpret
═══════════════════════════════════════════════════════════════
"""


def create_chart_ruler_safety_block(ascendant: str, ruler: str, ruler_sign: Optional[str] = None, 
                                     ruler_house: Optional[int] = None, language: str = 'pt') -> str:
    """
    Cria bloco de segurança para interpretação do regente do mapa.
    Valida que o regente está correto para o ascendente.
    
    Args:
        ascendant: Signo do Ascendente
        ruler: Planeta regente informado
        ruler_sign: Signo onde o regente está
        ruler_house: Casa onde o regente está
        language: 'pt' ou 'en'
    
    Returns:
        Bloco formatado com validação do regente
    """
    correct_ruler = SIGN_TO_RULER.get(ascendant, 'Desconhecido' if language == 'pt' else 'Unknown')
    is_correct = (ruler == correct_ruler)
    
    if language == 'pt':
        validation_status = "✅ CORRETO" if is_correct else f"❌ ERRO: Deveria ser {correct_ruler}"
        ruler_sign_str = f"em {ruler_sign}" if ruler_sign else "signo não especificado"
        ruler_house_str = f"na Casa {ruler_house}" if ruler_house else "casa não especificada"
        
        return f"""
═══════════════════════════════════════════════════════════════
🔒 DADOS PRÉ-CALCULADOS DO REGENTE DO MAPA
═══════════════════════════════════════════════════════════════

⚠️ ATENÇÃO IA: Use APENAS estes dados. NÃO calcule regentes.

ASCENDENTE: {ascendant}
REGENTE CORRETO: {correct_ruler} (por tabela fixa)
REGENTE INFORMADO: {ruler} {validation_status}
REGENTE ESTÁ: {ruler_sign_str}, {ruler_house_str}

REGRAS CRÍTICAS:
• Ascendente {ascendant} = Regente {correct_ruler} (SEMPRE)
• Quíron NÃO é regente de NENHUM signo
• Use APENAS o regente validado acima
• NÃO invente co-regentes sem mencionar o principal

TABELA COMPLETA DE REGENTES:
  Áries → Marte
  Touro → Vênus
  Gêmeos → Mercúrio
  Câncer → Lua
  Leão → Sol
  Virgem → Mercúrio
  Libra → Vênus
  Escorpião → Marte (moderno: Plutão)
  Sagitário → Júpiter
  Capricórnio → Saturno
  Aquário → Urano (tradicional: Saturno)
  Peixes → Netuno (tradicional: Júpiter)
═══════════════════════════════════════════════════════════════
"""
    else:
        validation_status = "✅ CORRECT" if is_correct else f"❌ ERROR: Should be {correct_ruler}"
        ruler_sign_str = f"in {ruler_sign}" if ruler_sign else "sign not specified"
        ruler_house_str = f"in House {ruler_house}" if ruler_house else "house not specified"
        
        return f"""
═══════════════════════════════════════════════════════════════
🔒 PRE-COMPUTED DATA FOR CHART RULER
═══════════════════════════════════════════════════════════════

⚠️ AI ATTENTION: Use ONLY this data. DO NOT calculate rulers.

ASCENDANT: {ascendant}
CORRECT RULER: {correct_ruler} (by fixed table)
PROVIDED RULER: {ruler} {validation_status}
RULER IS: {ruler_sign_str}, {ruler_house_str}

CRITICAL RULES:
• Ascendant {ascendant} = Ruler {correct_ruler} (ALWAYS)
• Chiron is NOT a ruler of ANY sign
• Use ONLY the validated ruler above
• DO NOT invent co-rulers without mentioning the primary

COMPLETE RULER TABLE:
  Aries → Mars
  Taurus → Venus
  Gemini → Mercury
  Cancer → Moon
  Leo → Sun
  Virgo → Mercury
  Libra → Venus
  Scorpio → Mars (modern: Pluto)
  Sagittarius → Jupiter
  Capricorn → Saturn
  Aquarius → Uranus (traditional: Saturn)
  Pisces → Neptune (traditional: Jupiter)
═══════════════════════════════════════════════════════════════
"""


def create_aspect_safety_block(planet1: str, planet2: str, aspect: str, language: str = 'pt') -> str:
    """
    Cria bloco de segurança para interpretação de aspectos.
    Valida que o aspecto é astronomicamente possível.
    
    Args:
        planet1: Primeiro planeta
        planet2: Segundo planeta
        aspect: Tipo de aspecto
        language: 'pt' ou 'en'
    
    Returns:
        Bloco formatado com validação do aspecto
    """
    # Verificar aspectos impossíveis
    forbidden_aspects = []
    
    if (planet1 in ['Mercúrio', 'Mercury'] and planet2 in ['Sol', 'Sun']) or \
       (planet2 in ['Mercúrio', 'Mercury'] and planet1 in ['Sol', 'Sun']):
        forbidden_aspects = ['quadratura', 'square', 'trígono', 'trine', 'oposição', 'opposition', 'sextil', 'sextile']
    
    if (planet1 in ['Vênus', 'Venus'] and planet2 in ['Sol', 'Sun']) or \
       (planet2 in ['Vênus', 'Venus'] and planet1 in ['Sol', 'Sun']):
        forbidden_aspects = ['sextil', 'sextile', 'quadratura', 'square', 'trígono', 'trine', 'oposição', 'opposition']
    
    is_forbidden = aspect.lower() in [f.lower() for f in forbidden_aspects]
    
    if language == 'pt':
        validation = "❌ ASPECTO ASTRONOMICAMENTE IMPOSSÍVEL" if is_forbidden else "✅ Aspecto possível"
        return f"""
═══════════════════════════════════════════════════════════════
🔒 VALIDAÇÃO DE ASPECTO
═══════════════════════════════════════════════════════════════

⚠️ ATENÇÃO IA: Verifique regras astronômicas antes de interpretar.

ASPECTO: {planet1} {aspect} {planet2}
STATUS: {validation}

REGRAS ASTRONÔMICAS CRÍTICAS:
• Mercúrio x Sol: Máximo 28° de distância
  PERMITIDO: Conjunção (0-10°) ou Sem Aspecto
  PROIBIDO: Quadratura, Trígono, Oposição, Sextil
  
• Vênus x Sol: Máximo 48° de distância
  PERMITIDO: Conjunção (0-10°), Semi-Sextil (30°), Semi-Quadratura (45°)
  PROIBIDO: Sextil, Quadratura, Trígono, Oposição
  
• Vênus x Mercúrio: Máximo 76° de distância
  PERMITIDO: Conjunção, Sextil
  PROIBIDO: Quadratura, Trígono, Oposição

{f"⚠️ AVISO: Este aspecto ({planet1} {aspect} {planet2}) é ASTRONOMICAMENTE IMPOSSÍVEL. Não pode ser interpretado como válido." if is_forbidden else ""}
═══════════════════════════════════════════════════════════════
"""
    else:
        validation = "❌ ASTRONOMICALLY IMPOSSIBLE ASPECT" if is_forbidden else "✅ Possible aspect"
        return f"""
═══════════════════════════════════════════════════════════════
🔒 ASPECT VALIDATION
═══════════════════════════════════════════════════════════════

⚠️ AI ATTENTION: Check astronomical rules before interpreting.

ASPECT: {planet1} {aspect} {planet2}
STATUS: {validation}

CRITICAL ASTRONOMICAL RULES:
• Mercury x Sun: Maximum 28° distance
  ALLOWED: Conjunction (0-10°) or No Aspect
  FORBIDDEN: Square, Trine, Opposition, Sextile
  
• Venus x Sun: Maximum 48° distance
  ALLOWED: Conjunction (0-10°), Semi-Sextile (30°), Semi-Square (45°)
  FORBIDDEN: Sextile, Square, Trine, Opposition
  
• Venus x Mercury: Maximum 76° distance
  ALLOWED: Conjunction, Sextile
  FORBIDDEN: Square, Trine, Opposition

{f"⚠️ WARNING: This aspect ({planet1} {aspect} {planet2}) is ASTRONOMICALLY IMPOSSIBLE. Cannot be interpreted as valid." if is_forbidden else ""}
═══════════════════════════════════════════════════════════════
"""

