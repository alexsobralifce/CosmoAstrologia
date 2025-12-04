"""
Formatador de Análise Astrológica Completa.
Organiza e formata a análise astrológica de forma clara e didática.
"""

from typing import Dict, List, Any, Optional
from collections import defaultdict


def format_dignities_explanation(language: str = 'pt') -> str:
    """
    Retorna explicação sobre dignidades planetárias.
    """
    if language == 'pt':
        return """
**O QUE SÃO DIGNIDADES PLANETÁRIAS:**

As dignidades indicam a força e facilidade de expressão de um planeta em um signo:

• **DOMICÍLIO**: O planeta está em "casa", onde se sente mais confortável e expressa sua energia naturalmente. É a posição mais forte e harmoniosa.

• **EXALTAÇÃO**: O planeta está em sua melhor performance, com energia elevada e expressão refinada. É uma posição muito favorável.

• **DETRIMENTO**: O planeta está em signo oposto ao seu domicílio, precisando de mais esforço para se expressar. A energia pode ser desafiadora.

• **QUEDA**: O planeta está em signo oposto à sua exaltação, com energia mais difícil de expressar. Requer consciência e trabalho para integrar.

• **PEREGRINO**: O planeta não está em nenhuma dignidade específica. Sua expressão depende dos aspectos que recebe de outros planetas. É uma posição neutra que pode variar.
"""
    else:
        return """
**WHAT ARE PLANETARY DIGNITIES:**

Dignities indicate the strength and ease of expression of a planet in a sign:

• **DOMICILE**: The planet is in its "home", where it feels most comfortable and expresses its energy naturally. It's the strongest and most harmonious position.

• **EXALTATION**: The planet is at its best performance, with elevated energy and refined expression. It's a very favorable position.

• **DETRIMENT**: The planet is in the sign opposite to its domicile, needing more effort to express itself. The energy can be challenging.

• **FALL**: The planet is in the sign opposite to its exaltation, with energy more difficult to express. Requires awareness and work to integrate.

• **PEREGRINE**: The planet is not in any specific dignity. Its expression depends on the aspects it receives from other planets. It's a neutral position that can vary.
"""


def format_aspects_compact(aspects: List[Dict[str, Any]], language: str = 'pt') -> str:
    """
    Formata aspectos de forma compacta, agrupando por tipo.
    Remove aspectos redundantes e organiza melhor.
    """
    if not aspects:
        return "Nenhum aspecto validado encontrado." if language == 'pt' else "No validated aspects found."
    
    # Agrupar aspectos por tipo
    aspects_by_type = defaultdict(list)
    for asp in aspects:
        aspect_type = asp.get('aspect', '').lower()
        planet1 = asp.get('planet1', '')
        planet2 = asp.get('planet2', '')
        
        # Criar chave única para evitar duplicatas
        key = tuple(sorted([planet1, planet2]))
        aspects_by_type[aspect_type].append({
            'planet1': planet1,
            'planet2': planet2,
            'distance': asp.get('distance', 0),
            'key': key
        })
    
    # Remover duplicatas dentro de cada tipo
    for aspect_type in aspects_by_type:
        seen = set()
        unique = []
        for asp in aspects_by_type[aspect_type]:
            if asp['key'] not in seen:
                seen.add(asp['key'])
                unique.append(asp)
        aspects_by_type[aspect_type] = unique
    
    # Ordenar tipos de aspectos por importância
    aspect_order = {
        'conjunção': 1, 'conjunction': 1,
        'oposição': 2, 'opposition': 2,
        'quadratura': 3, 'square': 3,
        'trígono': 4, 'trine': 4,
        'sextil': 5, 'sextile': 5,
        'quincúncio': 6, 'quincunx': 6,
        'semissextil': 7, 'semisextile': 7,
    }
    
    # Formatar saída
    if language == 'pt':
        lines = ["**ASPECTOS PRINCIPAIS:**\n"]
        
        # Agrupar por tipo e mostrar apenas os mais importantes
        for aspect_type in sorted(aspects_by_type.keys(), key=lambda x: aspect_order.get(x.lower(), 99)):
            aspect_list = aspects_by_type[aspect_type]
            if not aspect_list:
                continue
            
            # Limitar a 10 aspectos por tipo para não ficar muito longo
            aspect_list = aspect_list[:10]
            
            # Formatar nome do aspecto
            aspect_name = aspect_type.capitalize()
            if aspect_name == 'Conjunção':
                aspect_name = 'Conjunções'
            elif aspect_name == 'Oposição':
                aspect_name = 'Oposições'
            elif aspect_name == 'Quadratura':
                aspect_name = 'Quadraturas'
            elif aspect_name == 'Trígono':
                aspect_name = 'Trígonos'
            elif aspect_name == 'Sextil':
                aspect_name = 'Sextis'
            
            lines.append(f"**{aspect_name}:**")
            for asp in aspect_list:
                lines.append(f"  • {asp['planet1']} ↔ {asp['planet2']}")
            
            lines.append("")  # Linha em branco entre tipos
        
        # Se houver muitos aspectos, adicionar nota
        total_aspects = sum(len(v) for v in aspects_by_type.values())
        if total_aspects > 15:
            lines.append(f"\n*Total de {total_aspects} aspectos validados. Apenas os principais são mostrados acima.*")
        
        return "\n".join(lines)
    else:
        lines = ["**MAIN ASPECTS:**\n"]
        
        for aspect_type in sorted(aspects_by_type.keys(), key=lambda x: aspect_order.get(x.lower(), 99)):
            aspect_list = aspects_by_type[aspect_type]
            if not aspect_list:
                continue
            
            aspect_list = aspect_list[:10]
            
            aspect_name = aspect_type.capitalize()
            if aspect_name == 'Conjunction':
                aspect_name = 'Conjunctions'
            elif aspect_name == 'Opposition':
                aspect_name = 'Oppositions'
            elif aspect_name == 'Square':
                aspect_name = 'Squares'
            elif aspect_name == 'Trine':
                aspect_name = 'Trines'
            elif aspect_name == 'Sextile':
                aspect_name = 'Sextiles'
            
            lines.append(f"**{aspect_name}:**")
            for asp in aspect_list:
                lines.append(f"  • {asp['planet1']} ↔ {asp['planet2']}")
            
            lines.append("")
        
        total_aspects = sum(len(v) for v in aspects_by_type.values())
        if total_aspects > 15:
            lines.append(f"\n*Total of {total_aspects} validated aspects. Only the main ones are shown above.*")
        
        return "\n".join(lines)


def format_astrological_analysis(
    chart_data: Dict[str, Any],
    precomputed_data: str,
    language: str = 'pt'
) -> str:
    """
    Formata análise astrológica completa de forma organizada e didática.
    
    Args:
        chart_data: Dados do mapa astral
        precomputed_data: Bloco de dados pré-calculados
        language: 'pt' ou 'en'
    
    Returns:
        Análise formatada e organizada
    """
    from app.services.precomputed_chart_engine import (
        calculate_temperament_from_chart,
        get_planet_dignity,
        get_validated_aspects
    )
    
    if language == 'pt':
        # Calcular dados necessários
        temperament = calculate_temperament_from_chart(chart_data, 'pt')
        aspects = get_validated_aspects(chart_data, 'pt')
        
        # Identificar dignidades
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
                dignities_list.append({
                    'planet': planet_name,
                    'sign': sign,
                    'dignity': dignity_names[dignity]
                })
        
        # Construir análise formatada
        analysis = []
        
        # 1. Temperamento
        analysis.append("## TEMPERAMENTO\n")
        points = temperament['points']
        dominant = temperament['dominant']
        lacking = temperament.get('lacking')
        
        analysis.append(f"O mapa apresenta predominância do elemento **{dominant}**, com {points.get(dominant, 0)} pontos.")
        
        # Listar outros elementos em ordem decrescente
        other_elements = [(elem, pts) for elem, pts in points.items() if elem != dominant]
        other_elements.sort(key=lambda x: x[1], reverse=True)
        
        if other_elements:
            other_text = ", ".join([f"{elem} com {pts} pontos" for elem, pts in other_elements if pts > 0])
            if other_text:
                analysis.append(f"Outros elementos: {other_text}.")
        
        if lacking:
            analysis.append(f"O elemento ausente é **{lacking}**, com 0 pontos.")
        else:
            analysis.append("Todos os elementos estão presentes no mapa.")
        
        analysis.append("")
        
        # 2. Dignidades com explicação
        analysis.append("## DIGNIDADES PLANETÁRIAS\n")
        analysis.append(format_dignities_explanation('pt'))
        analysis.append("\n**Dignidades no Mapa:**\n")
        
        for d in dignities_list:
            analysis.append(f"- **{d['planet']} em {d['sign']}**: {d['dignity']}")
        
        analysis.append("")
        
        # 3. Aspectos (compacto)
        if aspects:
            analysis.append("## ASPECTOS VALIDADOS\n")
            analysis.append(format_aspects_compact(aspects, 'pt'))
            analysis.append("")
        
        return "\n".join(analysis)
    
    else:
        # English version
        temperament = calculate_temperament_from_chart(chart_data, 'en')
        aspects = get_validated_aspects(chart_data, 'en')
        
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
                dignities_list.append({
                    'planet': planet_name,
                    'sign': sign,
                    'dignity': dignity_names[dignity]
                })
        
        analysis = []
        
        analysis.append("## TEMPERAMENT\n")
        points = temperament['points']
        dominant = temperament['dominant']
        lacking = temperament.get('lacking')
        
        analysis.append(f"The chart shows predominance of the **{dominant}** element, with {points.get(dominant, 0)} points.")
        
        other_elements = [(elem, pts) for elem, pts in points.items() if elem != dominant]
        other_elements.sort(key=lambda x: x[1], reverse=True)
        
        if other_elements:
            other_text = ", ".join([f"{elem} with {pts} points" for elem, pts in other_elements if pts > 0])
            if other_text:
                analysis.append(f"Other elements: {other_text}.")
        
        if lacking:
            analysis.append(f"The lacking element is **{lacking}**, with 0 points.")
        else:
            analysis.append("All elements are present in the chart.")
        
        analysis.append("")
        
        analysis.append("## PLANETARY DIGNITIES\n")
        analysis.append(format_dignities_explanation('en'))
        analysis.append("\n**Dignities in the Chart:**\n")
        
        for d in dignities_list:
            analysis.append(f"- **{d['planet']} in {d['sign']}**: {d['dignity']}")
        
        analysis.append("")
        
        if aspects:
            analysis.append("## VALIDATED ASPECTS\n")
            analysis.append(format_aspects_compact(aspects, 'en'))
            analysis.append("")
        
        return "\n".join(analysis)

