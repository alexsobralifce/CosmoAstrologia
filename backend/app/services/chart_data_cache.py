"""
Cache de Dados do Mapa Astral - Fonte Única de Verdade

Este módulo garante que uma vez calculado, o mapa astral seja armazenado
e reutilizado, evitando recálculos que podem gerar inconsistências.
"""
from datetime import datetime
from typing import Dict, Optional, Tuple
import hashlib
import json


class ChartDataCache:
    """
    Cache simples em memória para armazenar mapas astrais calculados.
    Garante que o mesmo mapa não seja recalculado múltiplas vezes.
    """
    _cache: Dict[str, Dict] = {}
    _max_cache_size = 100  # Limitar tamanho do cache
    
    @staticmethod
    def _generate_cache_key(
        birth_date: datetime,
        birth_time: str,
        latitude: float,
        longitude: float
    ) -> str:
        """Gera uma chave única para o cache baseada nos dados de nascimento."""
        # Normalizar dados para garantir chave consistente
        date_str = birth_date.isoformat() if isinstance(birth_date, datetime) else str(birth_date)
        lat = round(latitude, 6)  # Precisão suficiente para coordenadas
        lon = round(longitude, 6)
        
        # Criar hash único
        key_data = f"{date_str}|{birth_time}|{lat}|{lon}"
        key_hash = hashlib.md5(key_data.encode()).hexdigest()
        
        return f"chart_{key_hash}"
    
    @staticmethod
    def get(
        birth_date: datetime,
        birth_time: str,
        latitude: float,
        longitude: float
    ) -> Optional[Dict]:
        """Obtém dados do cache se existirem."""
        cache_key = ChartDataCache._generate_cache_key(birth_date, birth_time, latitude, longitude)
        return ChartDataCache._cache.get(cache_key)
    
    @staticmethod
    def set(
        birth_date: datetime,
        birth_time: str,
        latitude: float,
        longitude: float,
        chart_data: Dict
    ) -> None:
        """Armazena dados do mapa no cache."""
        cache_key = ChartDataCache._generate_cache_key(birth_date, birth_time, latitude, longitude)
        
        # Limpar cache se estiver muito grande
        if len(ChartDataCache._cache) >= ChartDataCache._max_cache_size:
            # Remover item mais antigo (simples - remover primeiro)
            if ChartDataCache._cache:
                first_key = next(iter(ChartDataCache._cache))
                del ChartDataCache._cache[first_key]
        
        # Armazenar dados
        ChartDataCache._cache[cache_key] = chart_data.copy()
    
    @staticmethod
    def clear() -> None:
        """Limpa o cache."""
        ChartDataCache._cache.clear()
    
    @staticmethod
    def size() -> int:
        """Retorna o tamanho atual do cache."""
        return len(ChartDataCache._cache)


def get_or_calculate_chart(
    birth_date: datetime,
    birth_time: str,
    latitude: float,
    longitude: float,
    calculate_func
) -> Dict:
    """
    Obtém dados do cache ou calcula se não existirem.
    Garante que o mapa seja calculado apenas uma vez.
    
    Args:
        birth_date: Data de nascimento
        birth_time: Hora de nascimento
        latitude: Latitude
        longitude: Longitude
        calculate_func: Função que calcula o mapa (calculate_birth_chart)
    
    Returns:
        Dados do mapa astral (sempre os mesmos para os mesmos inputs)
    """
    # Tentar obter do cache
    cached = ChartDataCache.get(birth_date, birth_time, latitude, longitude)
    if cached is not None:
        return cached
    
    # Calcular se não estiver no cache
    chart_data = calculate_func(birth_date, birth_time, latitude, longitude)
    
    # Armazenar no cache
    ChartDataCache.set(birth_date, birth_time, latitude, longitude, chart_data)
    
    return chart_data

