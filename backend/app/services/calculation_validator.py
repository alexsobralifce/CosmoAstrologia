"""
Validador de Parâmetros para Cálculos Astrológicos.
Garante que todos os parâmetros estejam dentro dos limites válidos antes de calcular.
"""
from datetime import datetime, timezone
from typing import Tuple, Optional, Dict, Any


def validate_birth_date(birth_date: datetime) -> Tuple[bool, Optional[str]]:
    """
    Valida data de nascimento.
    
    Args:
        birth_date: Data de nascimento
    
    Returns:
        Tuple (is_valid, error_message)
    """
    if not birth_date:
        return (False, "Data de nascimento é obrigatória")
    
    # Normalizar datetime para comparação (remover timezone se presente)
    # Converter ambos para naive datetime para evitar erro de comparação
    if birth_date.tzinfo is not None:
        # Se tiver timezone, converter para UTC e remover timezone
        birth_date_naive = birth_date.astimezone(timezone.utc).replace(tzinfo=None)
    else:
        # Se já for naive, usar diretamente
        birth_date_naive = birth_date
    
    # Usar datetime naive para comparação
    now_naive = datetime.now()
    
    # Verificar se a data não é no futuro
    if birth_date_naive > now_naive:
        return (False, "Data de nascimento não pode ser no futuro")
    
    # Verificar se a data não é muito antiga (antes de 1800)
    if birth_date.year < 1800:
        return (False, "Data de nascimento muito antiga (antes de 1800)")
    
    # Verificar se a data não é muito futura (mais de 100 anos no futuro)
    max_future = datetime.now().year + 100
    if birth_date.year > max_future:
        return (False, f"Data de nascimento muito futura (após {max_future})")
    
    return (True, None)


def validate_birth_time(birth_time: str) -> Tuple[bool, Optional[str]]:
    """
    Valida hora de nascimento.
    
    Args:
        birth_time: Hora no formato "HH:MM"
    
    Returns:
        Tuple (is_valid, error_message)
    """
    if not birth_time:
        return (False, "Hora de nascimento é obrigatória")
    
    try:
        time_parts = birth_time.split(":")
        if len(time_parts) != 2:
            return (False, "Formato de hora inválido. Use HH:MM")
        
        hour = int(time_parts[0])
        minute = int(time_parts[1])
        
        if hour < 0 or hour > 23:
            return (False, "Hora deve estar entre 00 e 23")
        
        if minute < 0 or minute > 59:
            return (False, "Minuto deve estar entre 00 e 59")
        
        return (True, None)
    except ValueError:
        return (False, "Hora de nascimento inválida. Use formato HH:MM")


def validate_coordinates(latitude: float, longitude: float) -> Tuple[bool, Optional[str]]:
    """
    Valida coordenadas geográficas.
    
    Args:
        latitude: Latitude (-90 a 90)
        longitude: Longitude (-180 a 180)
    
    Returns:
        Tuple (is_valid, error_message)
    """
    if latitude is None or longitude is None:
        return (False, "Latitude e longitude são obrigatórias")
    
    if not isinstance(latitude, (int, float)) or not isinstance(longitude, (int, float)):
        return (False, "Latitude e longitude devem ser números")
    
    if latitude < -90 or latitude > 90:
        return (False, "Latitude deve estar entre -90 e 90 graus")
    
    if longitude < -180 or longitude > 180:
        return (False, "Longitude deve estar entre -180 e 180 graus")
    
    return (True, None)


def validate_target_year(target_year: Optional[int], birth_year: int) -> Tuple[bool, Optional[str]]:
    """
    Valida ano alvo para cálculos futuros (ex: Revolução Solar).
    
    Args:
        target_year: Ano alvo
        birth_year: Ano de nascimento
    
    Returns:
        Tuple (is_valid, error_message)
    """
    if target_year is None:
        return (True, None)  # None é válido (usa ano atual)
    
    current_year = datetime.now().year
    
    # Ano alvo não pode ser antes do nascimento
    if target_year < birth_year:
        return (False, f"Ano alvo ({target_year}) não pode ser antes do nascimento ({birth_year})")
    
    # Ano alvo não pode ser muito no futuro (máximo 100 anos após nascimento)
    max_year = birth_year + 100
    if target_year > max_year:
        return (False, f"Ano alvo ({target_year}) muito distante (máximo {max_year})")
    
    return (True, None)


def validate_astrological_parameters(
    birth_date: Optional[datetime] = None,
    birth_time: Optional[str] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    target_year: Optional[int] = None
) -> Tuple[bool, Optional[str], Dict[str, Any]]:
    """
    Valida todos os parâmetros astrológicos de uma vez.
    
    Args:
        birth_date: Data de nascimento
        birth_time: Hora de nascimento (HH:MM)
        latitude: Latitude
        longitude: Longitude
        target_year: Ano alvo (opcional)
    
    Returns:
        Tuple (is_valid, error_message, validated_params)
    """
    errors = []
    validated_params = {}
    
    # Validar data
    if birth_date:
        is_valid, error = validate_birth_date(birth_date)
        if not is_valid:
            errors.append(error)
        else:
            validated_params['birth_date'] = birth_date
            validated_params['birth_year'] = birth_date.year
    
    # Validar hora
    if birth_time:
        is_valid, error = validate_birth_time(birth_time)
        if not is_valid:
            errors.append(error)
        else:
            validated_params['birth_time'] = birth_time
    
    # Validar coordenadas
    if latitude is not None and longitude is not None:
        is_valid, error = validate_coordinates(latitude, longitude)
        if not is_valid:
            errors.append(error)
        else:
            validated_params['latitude'] = latitude
            validated_params['longitude'] = longitude
    
    # Validar ano alvo
    if target_year is not None and 'birth_year' in validated_params:
        is_valid, error = validate_target_year(target_year, validated_params['birth_year'])
        if not is_valid:
            errors.append(error)
        else:
            validated_params['target_year'] = target_year
    
    if errors:
        return (False, "; ".join(errors), validated_params)
    
    return (True, None, validated_params)


def validate_calculated_chart_data(chart_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Valida que os dados calculados do mapa estão completos e corretos.
    
    Args:
        chart_data: Dados do mapa calculado
    
    Returns:
        Tuple (is_valid, error_message)
    """
    if not chart_data:
        return (False, "Dados do mapa não foram calculados")
    
    # Validar campos essenciais
    required_fields = [
        'sun_sign', 'moon_sign', 'ascendant_sign'
    ]
    
    missing_fields = []
    for field in required_fields:
        if field not in chart_data or not chart_data[field]:
            missing_fields.append(field)
    
    if missing_fields:
        return (False, f"Campos obrigatórios não calculados: {', '.join(missing_fields)}")
    
    # Validar que signos são válidos
    valid_signs = [
        'Áries', 'Touro', 'Gêmeos', 'Câncer', 'Leão', 'Virgem',
        'Libra', 'Escorpião', 'Sagitário', 'Capricórnio', 'Aquário', 'Peixes'
    ]
    
    for field in required_fields:
        sign = chart_data.get(field)
        if sign and sign not in valid_signs:
            return (False, f"Signo inválido em {field}: {sign}")
    
    return (True, None)


def ensure_calculation_before_interpretation(
    calculation_func,
    validation_func,
    *args,
    **kwargs
) -> Tuple[Dict[str, Any], Optional[str]]:
    """
    Garante que o cálculo seja feito e validado antes de usar para interpretação.
    
    Args:
        calculation_func: Função de cálculo (ex: calculate_solar_return)
        validation_func: Função de validação (ex: validate_calculated_chart_data)
        *args, **kwargs: Argumentos para a função de cálculo
    
    Returns:
        Tuple (calculated_data, error_message)
    """
    try:
        # 1. Calcular usando biblioteca
        calculated_data = calculation_func(*args, **kwargs)
        
        # 2. Validar dados calculados
        is_valid, error = validation_func(calculated_data)
        if not is_valid:
            return (None, f"Dados calculados inválidos: {error}")
        
        return (calculated_data, None)
    except Exception as e:
        return (None, f"Erro ao calcular: {str(e)}")
