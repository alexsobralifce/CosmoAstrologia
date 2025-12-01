"""
Ferramenta de Validação e Correção de Cálculos do Mapa Astral
Atua em conjunto com o prompt para detectar e corrigir imprecisões.

Esta ferramenta:
1. Valida todos os cálculos do mapa astral
2. Detecta inconsistências matemáticas
3. Corrige erros automaticamente quando possível
4. Retorna dados validados para uso no prompt
"""
from typing import Dict, List, Tuple, Optional, Any
from app.services.astrology_calculator import shortest_angular_distance, get_zodiac_sign
from app.services.cosmos_validation import (
    validate_mercury_sun_distance,
    validate_venus_sun_distance,
    validate_venus_mercury_distance,
    validate_aspect,
    MERCURY_SUN_MAX_DISTANCE,
    VENUS_SUN_MAX_DISTANCE,
    VENUS_MERCURY_MAX_DISTANCE,
)
import math


# Mapeamento de signos para planetas regentes
SIGN_RULERS = {
    'Áries': 'Marte',
    'Touro': 'Vênus',
    'Gêmeos': 'Mercúrio',
    'Câncer': 'Lua',
    'Leão': 'Sol',
    'Virgem': 'Mercúrio',
    'Libra': 'Vênus',
    'Escorpião': 'Marte',
    'Sagitário': 'Júpiter',
    'Capricórnio': 'Saturno',
    'Aquário': 'Urano',
    'Peixes': 'Netuno',
    # Inglês também
    'Aries': 'Mars',
    'Taurus': 'Venus',
    'Gemini': 'Mercury',
    'Cancer': 'Moon',
    'Leo': 'Sun',
    'Virgo': 'Mercury',
    'Libra': 'Venus',
    'Scorpio': 'Mars',
    'Sagittarius': 'Jupiter',
    'Capricorn': 'Saturn',
    'Aquarius': 'Uranus',
    'Pisces': 'Neptune',
}

# Dignidades planetárias
PLANET_DIGNITIES = {
    'Sol': {
        'domicile': ['Leão', 'Leo'],
        'exaltation': ['Áries', 'Aries'],
        'detriment': ['Aquário', 'Aquarius'],
        'fall': ['Libra', 'Libra'],
    },
    'Lua': {
        'domicile': ['Câncer', 'Cancer'],
        'exaltation': ['Touro', 'Taurus'],
        'detriment': ['Capricórnio', 'Capricorn'],
        'fall': ['Escorpião', 'Scorpio'],
    },
    'Mercúrio': {
        'domicile': ['Gêmeos', 'Gemini', 'Virgem', 'Virgo'],
        'exaltation': ['Virgem', 'Virgo'],
        'detriment': ['Sagitário', 'Sagittarius', 'Peixes', 'Pisces'],
        'fall': ['Peixes', 'Pisces'],
    },
    'Vênus': {
        'domicile': ['Touro', 'Taurus', 'Libra', 'Libra'],
        'exaltation': ['Peixes', 'Pisces'],
        'detriment': ['Áries', 'Aries', 'Escorpião', 'Scorpio'],
        'fall': ['Virgem', 'Virgo'],
    },
    'Marte': {
        'domicile': ['Áries', 'Aries', 'Escorpião', 'Scorpio'],
        'exaltation': ['Capricórnio', 'Capricorn'],
        'detriment': ['Libra', 'Libra', 'Touro', 'Taurus'],
        'fall': ['Câncer', 'Cancer'],
    },
    'Júpiter': {
        'domicile': ['Sagitário', 'Sagittarius', 'Peixes', 'Pisces'],
        'exaltation': ['Câncer', 'Cancer'],
        'detriment': ['Gêmeos', 'Gemini', 'Virgem', 'Virgo'],
        'fall': ['Capricórnio', 'Capricorn'],
    },
    'Saturno': {
        'domicile': ['Capricórnio', 'Capricorn', 'Aquário', 'Aquarius'],
        'exaltation': ['Libra', 'Libra'],
        'detriment': ['Câncer', 'Cancer', 'Leão', 'Leo'],
        'fall': ['Áries', 'Aries'],
    },
    'Urano': {
        'domicile': ['Aquário', 'Aquarius'],
        'exaltation': ['Escorpião', 'Scorpio'],
        'detriment': ['Leão', 'Leo'],
        'fall': ['Touro', 'Taurus'],
    },
    'Netuno': {
        'domicile': ['Peixes', 'Pisces'],
        'exaltation': ['Leão', 'Leo'],
        'detriment': ['Virgem', 'Virgo'],
        'fall': ['Aquário', 'Aquarius'],
    },
    'Plutão': {
        'domicile': ['Escorpião', 'Scorpio'],
        'exaltation': ['Áries', 'Aries'],
        'detriment': ['Touro', 'Taurus'],
        'fall': ['Libra', 'Libra'],
    },
}


class ChartValidationReport:
    """Relatório de validação do mapa astral."""
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.corrections: List[str] = []
        self.validations: List[str] = []
        self.is_valid: bool = True
    
    def add_error(self, message: str):
        """Adiciona um erro crítico."""
        self.errors.append(message)
        self.is_valid = False
    
    def add_warning(self, message: str):
        """Adiciona um aviso."""
        self.warnings.append(message)
    
    def add_correction(self, message: str):
        """Adiciona uma correção aplicada."""
        self.corrections.append(message)
    
    def add_validation(self, message: str):
        """Adiciona uma validação bem-sucedida."""
        self.validations.append(message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte o relatório para dicionário."""
        return {
            'is_valid': self.is_valid,
            'errors': self.errors,
            'warnings': self.warnings,
            'corrections': self.corrections,
            'validations': self.validations,
            'total_issues': len(self.errors) + len(self.warnings),
        }


def validate_planetary_distances(chart_data: Dict[str, Any], report: ChartValidationReport) -> Dict[str, Any]:
    """
    Valida distâncias entre planetas internos.
    
    Args:
        chart_data: Dados do mapa astral
        report: Relatório de validação
    
    Returns:
        Dicionário com dados corrigidos (se necessário)
    """
    corrected_data = chart_data.copy()
    
    # Obter longitudes da fonte única
    source_longitudes = chart_data.get('_source_longitudes', {})
    
    if not source_longitudes:
        report.add_warning("Longitudes fonte não disponíveis para validação completa")
        return corrected_data
    
    # Validar Mercúrio x Sol
    if 'mercury' in source_longitudes and 'sun' in source_longitudes:
        mercury_lon = source_longitudes['mercury']
        sun_lon = source_longitudes['sun']
        
        is_valid, aspect_or_error = validate_mercury_sun_distance(mercury_lon, sun_lon)
        
        if not is_valid:
            report.add_error(f"Mercúrio x Sol: {aspect_or_error}")
        elif aspect_or_error:
            report.add_validation(f"Mercúrio x Sol: {aspect_or_error} válido (distância: {shortest_angular_distance(mercury_lon, sun_lon):.1f}°)")
    
    # Validar Vênus x Sol
    if 'venus' in source_longitudes and 'sun' in source_longitudes:
        venus_lon = source_longitudes['venus']
        sun_lon = source_longitudes['sun']
        
        is_valid, aspect_or_none, error_msg = validate_venus_sun_distance(venus_lon, sun_lon)
        
        if not is_valid:
            if error_msg:
                report.add_error(f"Vênus x Sol: {error_msg}")
            else:
                report.add_warning(f"Vênus x Sol: Configuração incomum detectada")
        elif aspect_or_none:
            distance = shortest_angular_distance(venus_lon, sun_lon)
            report.add_validation(f"Vênus x Sol: {aspect_or_none} válido (distância: {distance:.1f}°)")
        else:
            distance = shortest_angular_distance(venus_lon, sun_lon)
            report.add_validation(f"Vênus x Sol: Sem aspecto específico (distância: {distance:.1f}°)")
    
    # Validar Vênus x Mercúrio
    if 'venus' in source_longitudes and 'mercury' in source_longitudes:
        venus_lon = source_longitudes['venus']
        mercury_lon = source_longitudes['mercury']
        
        is_valid, aspect_or_none, error_msg = validate_venus_mercury_distance(venus_lon, mercury_lon)
        
        if not is_valid:
            if error_msg:
                report.add_error(f"Vênus x Mercúrio: {error_msg}")
        elif aspect_or_none:
            distance = shortest_angular_distance(venus_lon, mercury_lon)
            report.add_validation(f"Vênus x Mercúrio: {aspect_or_none} válido (distância: {distance:.1f}°)")
        else:
            distance = shortest_angular_distance(venus_lon, mercury_lon)
            report.add_validation(f"Vênus x Mercúrio: Sem aspecto específico (distância: {distance:.1f}°)")
    
    return corrected_data


def validate_sign_consistency(chart_data: Dict[str, Any], report: ChartValidationReport) -> Dict[str, Any]:
    """
    Valida consistência entre signos calculados e longitudes.
    
    Args:
        chart_data: Dados do mapa astral
        report: Relatório de validação
    
    Returns:
        Dicionário com dados corrigidos (se necessário)
    """
    corrected_data = chart_data.copy()
    source_longitudes = chart_data.get('_source_longitudes', {})
    
    if not source_longitudes:
        return corrected_data
    
    # Validar cada planeta
    planet_fields = {
        'sun': ('sun_sign', 'sun_degree'),
        'moon': ('moon_sign', 'moon_degree'),
        'mercury': ('mercury_sign', 'mercury_degree'),
        'venus': ('venus_sign', 'venus_degree'),
        'mars': ('mars_sign', 'mars_degree'),
        'jupiter': ('jupiter_sign', 'jupiter_degree'),
        'saturn': ('saturn_sign', 'saturn_degree'),
        'uranus': ('uranus_sign', 'uranus_degree'),
        'neptune': ('neptune_sign', 'neptune_degree'),
        'pluto': ('pluto_sign', 'pluto_degree'),
    }
    
    for planet_key, (sign_field, degree_field) in planet_fields.items():
        if planet_key not in source_longitudes:
            continue
        
        longitude = source_longitudes[planet_key]
        calculated_sign_data = get_zodiac_sign(longitude)
        
        # Verificar se o signo calculado coincide com o armazenado
        stored_sign = chart_data.get(sign_field)
        stored_degree = chart_data.get(degree_field)
        
        if stored_sign and stored_sign != calculated_sign_data['sign']:
            report.add_error(
                f"Inconsistência detectada em {planet_key}: "
                f"Signo armazenado '{stored_sign}' não corresponde ao calculado '{calculated_sign_data['sign']}' "
                f"(longitude: {longitude:.2f}°)"
            )
            # Corrigir automaticamente
            corrected_data[sign_field] = calculated_sign_data['sign']
            corrected_data[degree_field] = calculated_sign_data['degree']
            report.add_correction(f"{planet_key.capitalize()}: Signo corrigido de '{stored_sign}' para '{calculated_sign_data['sign']}'")
        elif stored_sign:
            report.add_validation(f"{planet_key.capitalize()}: Signo '{stored_sign}' consistente com longitude {longitude:.2f}°")
    
    return corrected_data


def validate_dignities(chart_data: Dict[str, Any], report: ChartValidationReport) -> Dict[str, Any]:
    """
    Valida e identifica dignidades planetárias.
    
    Args:
        chart_data: Dados do mapa astral
        report: Relatório de validação
    
    Returns:
        Dicionário com dados corrigidos (se necessário)
    """
    corrected_data = chart_data.copy()
    
    # Mapear planetas em português para inglês
    planet_map = {
        'Sol': 'Sun', 'Lua': 'Moon', 'Mercúrio': 'Mercury', 'Vênus': 'Venus',
        'Marte': 'Mars', 'Júpiter': 'Jupiter', 'Saturno': 'Saturn',
        'Urano': 'Uranus', 'Netuno': 'Neptune', 'Plutão': 'Pluto',
    }
    
    # Verificar dignidades de cada planeta
    for planet_pt, planet_en in planet_map.items():
        sign_field = f"{planet_en.lower()}_sign"
        sign = chart_data.get(sign_field)
        
        if not sign:
            continue
        
        # Verificar se planeta tem dignidades definidas
        if planet_pt in PLANET_DIGNITIES:
            dignities = PLANET_DIGNITIES[planet_pt]
            
            # Verificar domicílio
            if sign in dignities.get('domicile', []):
                report.add_validation(f"{planet_pt} em {sign}: DOMICÍLIO (energia forte e natural)")
            
            # Verificar exaltação
            elif sign in dignities.get('exaltation', []):
                report.add_validation(f"{planet_pt} em {sign}: EXALTAÇÃO (energia em melhor performance)")
            
            # Verificar detrimento
            elif sign in dignities.get('detriment', []):
                report.add_warning(f"{planet_pt} em {sign}: DETRIMENTO (energia desconfortável, precisa agir de forma indireta)")
            
            # Verificar queda
            elif sign in dignities.get('fall', []):
                report.add_warning(f"{planet_pt} em {sign}: QUEDA (energia inadequada, precisa de muito esforço)")
            
            # Peregrino
            else:
                report.add_validation(f"{planet_pt} em {sign}: PEREGRINO (depende dos aspectos recebidos)")
    
    return corrected_data


def validate_aspects_in_chart(chart_data: Dict[str, Any], report: ChartValidationReport) -> Dict[str, Any]:
    """
    Valida aspectos entre planetas principais.
    
    Args:
        chart_data: Dados do mapa astral
        report: Relatório de validação
    
    Returns:
        Dicionário com dados corrigidos (se necessário)
    """
    corrected_data = chart_data.copy()
    source_longitudes = chart_data.get('_source_longitudes', {})
    
    if not source_longitudes:
        return corrected_data
    
    # Planetas principais para validar aspectos
    main_planets = ['sun', 'moon', 'mercury', 'venus', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune', 'pluto']
    
    validated_aspects = []
    
    # Validar aspectos entre todos os pares de planetas principais
    for i, planet1 in enumerate(main_planets):
        if planet1 not in source_longitudes:
            continue
        
        for planet2 in main_planets[i+1:]:
            if planet2 not in source_longitudes:
                continue
            
            lon1 = source_longitudes[planet1]
            lon2 = source_longitudes[planet2]
            distance = shortest_angular_distance(lon1, lon2)
            
            # Verificar cada tipo de aspecto
            aspect_types = ['conjunction', 'sextile', 'square', 'trine', 'opposition', 'quincunx']
            
            for aspect_type in aspect_types:
                is_valid, calculated_distance, error = validate_aspect(lon1, lon2, aspect_type)
                
                if is_valid:
                    validated_aspects.append({
                        'planet1': planet1,
                        'planet2': planet2,
                        'aspect': aspect_type,
                        'distance': calculated_distance,
                    })
                    report.add_validation(
                        f"{planet1.capitalize()} {aspect_type} {planet2.capitalize()}: "
                        f"Válido (distância: {calculated_distance:.1f}°)"
                    )
                    break  # Apenas um aspecto por par
    
    # Adicionar aspectos validados aos dados
    corrected_data['_validated_aspects'] = validated_aspects
    
    return corrected_data


def validate_chart_ruler(chart_data: Dict[str, Any], report: ChartValidationReport) -> Dict[str, Any]:
    """
    Valida o regente do mapa astral.
    
    Args:
        chart_data: Dados do mapa astral
        report: Relatório de validação
    
    Returns:
        Dicionário com dados corrigidos (se necessário)
    """
    corrected_data = chart_data.copy()
    
    ascendant_sign = chart_data.get('ascendant_sign')
    if not ascendant_sign:
        report.add_warning("Ascendente não disponível para validar regente do mapa")
        return corrected_data
    
    # Encontrar regente do ascendente
    ruler = SIGN_RULERS.get(ascendant_sign)
    
    if not ruler:
        report.add_warning(f"Regente não encontrado para ascendente '{ascendant_sign}'")
        return corrected_data
    
    # Verificar onde está o regente
    planet_map_pt_to_en = {
        'Sol': 'sun', 'Lua': 'moon', 'Mercúrio': 'mercury', 'Vênus': 'venus',
        'Marte': 'mars', 'Júpiter': 'jupiter', 'Saturno': 'saturn',
        'Urano': 'uranus', 'Netuno': 'neptune', 'Plutão': 'pluto',
    }
    
    ruler_en = planet_map_pt_to_en.get(ruler)
    
    if ruler_en:
        ruler_sign_field = f"{ruler_en}_sign"
        ruler_degree_field = f"{ruler_en}_degree"
        
        ruler_sign = chart_data.get(ruler_sign_field)
        ruler_degree = chart_data.get(ruler_degree_field)
        
        if ruler_sign:
            report.add_validation(
                f"Regente do mapa: {ruler} em {ruler_sign} "
                f"(grau {ruler_degree:.1f}°)" if ruler_degree else f"Regente do mapa: {ruler} em {ruler_sign}"
            )
            corrected_data['_chart_ruler'] = {
                'planet': ruler,
                'sign': ruler_sign,
                'degree': ruler_degree,
            }
        else:
            report.add_warning(f"Regente {ruler} não encontrado no mapa")
    
    return corrected_data


def validate_complete_birth_chart(chart_data: Dict[str, Any]) -> Tuple[Dict[str, Any], ChartValidationReport]:
    """
    Valida completamente um mapa astral e retorna dados corrigidos.
    
    Args:
        chart_data: Dados do mapa astral a validar
    
    Returns:
        Tuple[Dict, ChartValidationReport]: (dados_corrigidos, relatório)
    """
    report = ChartValidationReport()
    
    # 1. Validar distâncias planetárias
    chart_data = validate_planetary_distances(chart_data, report)
    
    # 2. Validar consistência de signos
    chart_data = validate_sign_consistency(chart_data, report)
    
    # 3. Validar dignidades
    chart_data = validate_dignities(chart_data, report)
    
    # 4. Validar aspectos
    chart_data = validate_aspects_in_chart(chart_data, report)
    
    # 5. Validar regente do mapa
    chart_data = validate_chart_ruler(chart_data, report)
    
    return chart_data, report


def get_validation_summary_for_prompt(report: ChartValidationReport, language: str = 'pt') -> str:
    """
    Gera um resumo de validação formatado para uso no prompt.
    
    Args:
        report: Relatório de validação
        language: Idioma ('pt' ou 'en')
    
    Returns:
        String formatada com o resumo de validação
    """
    if language == 'pt':
        summary_parts = []
        
        if report.validations:
            summary_parts.append("✅ VALIDAÇÕES APROVADAS:")
            for validation in report.validations[:10]:  # Limitar a 10 para não sobrecarregar
                summary_parts.append(f"  • {validation}")
        
        if report.corrections:
            summary_parts.append("\n🔧 CORREÇÕES APLICADAS:")
            for correction in report.corrections:
                summary_parts.append(f"  • {correction}")
        
        if report.warnings:
            summary_parts.append("\n⚠️ AVISOS:")
            for warning in report.warnings[:5]:  # Limitar a 5
                summary_parts.append(f"  • {warning}")
        
        if report.errors:
            summary_parts.append("\n❌ ERROS CRÍTICOS:")
            for error in report.errors:
                summary_parts.append(f"  • {error}")
        
        return "\n".join(summary_parts) if summary_parts else "✅ Mapa astral validado sem problemas."
    else:
        summary_parts = []
        
        if report.validations:
            summary_parts.append("✅ VALIDATIONS APPROVED:")
            for validation in report.validations[:10]:
                summary_parts.append(f"  • {validation}")
        
        if report.corrections:
            summary_parts.append("\n🔧 CORRECTIONS APPLIED:")
            for correction in report.corrections:
                summary_parts.append(f"  • {correction}")
        
        if report.warnings:
            summary_parts.append("\n⚠️ WARNINGS:")
            for warning in report.warnings[:5]:
                summary_parts.append(f"  • {warning}")
        
        if report.errors:
            summary_parts.append("\n❌ CRITICAL ERRORS:")
            for error in report.errors:
                summary_parts.append(f"  • {error}")
        
        return "\n".join(summary_parts) if summary_parts else "✅ Birth chart validated without issues."

