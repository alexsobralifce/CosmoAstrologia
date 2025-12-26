"""
Testes Unitários para Travas de Segurança do Sistema
Garante que a IA NÃO invente dados - apenas interprete dados pré-calculados.
"""
import pytest
from app.services.precomputed_chart_engine import (
    SIGN_TO_ELEMENT,
    SIGN_TO_MODALITY,
    SIGN_TO_RULER,
    PLANET_DIGNITIES,
    calculate_temperament_from_chart,
    get_planet_dignity,
    get_chart_ruler,
    create_precomputed_data_block,
    create_planet_safety_block,
    create_chart_ruler_safety_block,
    create_aspect_safety_block,
)


class TestSignToElementMapping:
    """Testa que signos são mapeados corretamente para elementos."""
    
    def test_libra_is_air(self):
        """Libra DEVE ser AR, NÃO Fogo."""
        # Libra pode estar mapeado como 'Ar' (PT) ou 'Air' (EN) dependendo da chave
        libra_element_pt = SIGN_TO_ELEMENT.get('Libra')
        assert libra_element_pt in ['Ar', 'Air'], f"Libra deve ser Ar ou Air, mas é {libra_element_pt}"
        assert libra_element_pt not in ['Fogo', 'Terra', 'Fire', 'Earth']
    
    def test_leo_is_fire(self):
        """Leão DEVE ser FOGO, NÃO Água."""
        leo_element_pt = SIGN_TO_ELEMENT.get('Leão', SIGN_TO_ELEMENT.get('Leo'))
        assert leo_element_pt in ['Fogo', 'Fire']
        assert leo_element_pt not in ['Água', 'Water']
    
    def test_all_fire_signs(self):
        """Valida todos os signos de Fogo."""
        fire_signs_pt = ['Áries', 'Leão', 'Sagitário']
        fire_signs_en = ['Aries', 'Leo', 'Sagittarius']
        
        for sign in fire_signs_pt:
            element = SIGN_TO_ELEMENT.get(sign)
            assert element in ['Fogo', 'Fire'], f"{sign} deve ser Fogo/Fire, mas é {element}"
        for sign in fire_signs_en:
            element = SIGN_TO_ELEMENT.get(sign)
            assert element in ['Fogo', 'Fire'], f"{sign} deve ser Fogo/Fire, mas é {element}"
    
    def test_all_earth_signs(self):
        """Valida todos os signos de Terra."""
        earth_signs_pt = ['Touro', 'Virgem', 'Capricórnio']
        earth_signs_en = ['Taurus', 'Virgo', 'Capricorn']
        
        for sign in earth_signs_pt:
            element = SIGN_TO_ELEMENT.get(sign)
            assert element in ['Terra', 'Earth'], f"{sign} deve ser Terra/Earth, mas é {element}"
        for sign in earth_signs_en:
            element = SIGN_TO_ELEMENT.get(sign)
            assert element in ['Terra', 'Earth'], f"{sign} deve ser Terra/Earth, mas é {element}"
    
    def test_all_air_signs(self):
        """Valida todos os signos de Ar."""
        air_signs_pt = ['Gêmeos', 'Libra', 'Aquário']
        air_signs_en = ['Gemini', 'Libra', 'Aquarius']
        
        for sign in air_signs_pt:
            element = SIGN_TO_ELEMENT.get(sign)
            assert element in ['Ar', 'Air'], f"{sign} deve ser Ar/Air, mas é {element}"
        for sign in air_signs_en:
            element = SIGN_TO_ELEMENT.get(sign)
            assert element in ['Ar', 'Air'], f"{sign} deve ser Ar/Air, mas é {element}"
    
    def test_all_water_signs(self):
        """Valida todos os signos de Água."""
        water_signs_pt = ['Câncer', 'Escorpião', 'Peixes']
        water_signs_en = ['Cancer', 'Scorpio', 'Pisces']
        
        for sign in water_signs_pt:
            element = SIGN_TO_ELEMENT.get(sign)
            assert element in ['Água', 'Water'], f"{sign} deve ser Água/Water, mas é {element}"
        for sign in water_signs_en:
            element = SIGN_TO_ELEMENT.get(sign)
            assert element in ['Água', 'Water'], f"{sign} deve ser Água/Water, mas é {element}"


class TestSignToRulerMapping:
    """Testa que regentes são identificados corretamente."""
    
    def test_aquarius_ruler_is_uranus_not_chiron(self):
        """Aquário DEVE ter Urano como regente, NUNCA Quíron."""
        assert SIGN_TO_RULER['Aquário'] == 'Urano'
        assert SIGN_TO_RULER['Aquarius'] == 'Uranus'
        assert SIGN_TO_RULER['Aquário'] != 'Quíron'
        assert SIGN_TO_RULER['Aquarius'] != 'Chiron'
    
    def test_all_rulers_correct(self):
        """Valida todos os regentes."""
        expected_rulers_pt = {
            'Áries': ['Marte', 'Mars'],
            'Touro': ['Vênus', 'Venus'],
            'Gêmeos': ['Mercúrio', 'Mercury'],
            'Câncer': ['Lua', 'Moon'],
            'Leão': ['Sol', 'Sun'],
            'Virgem': ['Mercúrio', 'Mercury'],
            'Libra': ['Vênus', 'Venus'],
            'Escorpião': ['Marte', 'Mars'],
            'Sagitário': ['Júpiter', 'Jupiter'],
            'Capricórnio': ['Saturno', 'Saturn'],
            'Aquário': ['Urano', 'Uranus'],
            'Peixes': ['Netuno', 'Neptune'],
        }
        
        for sign, possible_rulers in expected_rulers_pt.items():
            ruler = SIGN_TO_RULER.get(sign)
            assert ruler in possible_rulers, f"{sign} deve ter regente em {possible_rulers}, mas é {ruler}"
    
    def test_chiron_never_a_ruler(self):
        """Quíron NUNCA deve aparecer como regente."""
        all_rulers = set(SIGN_TO_RULER.values())
        assert 'Quíron' not in all_rulers
        assert 'Chiron' not in all_rulers


class TestTemperamentCalculation:
    """Testa que o temperamento é calculado matematicamente."""
    
    def test_temperament_with_fire_dominant(self):
        """Testa cálculo com Fogo dominante."""
        chart_data = {
            'sun_sign': 'Áries',       # 3 pontos Fogo
            'moon_sign': 'Leão',       # 3 pontos Fogo
            'ascendant_sign': 'Sagitário',  # 3 pontos Fogo
            'mercury_sign': 'Áries',   # 1 ponto Fogo
            'venus_sign': 'Touro',     # 1 ponto Terra
            'mars_sign': 'Leão',       # 1 ponto Fogo
        }
        
        result = calculate_temperament_from_chart(chart_data, 'pt')
        
        assert result['points']['Fogo'] == 11  # 3+3+3+1+1
        assert result['points']['Terra'] == 1
        assert result['points']['Ar'] == 0
        assert result['points']['Água'] == 0
        assert result['dominant'] == 'Fogo'
        assert result['lacking'] == 'Ar' or result['lacking'] == 'Água'
    
    def test_temperament_calculation_is_deterministic(self):
        """O cálculo de temperamento deve ser sempre o mesmo para os mesmos dados."""
        chart_data = {
            'sun_sign': 'Libra',       # 3 pontos AR
            'moon_sign': 'Gêmeos',     # 3 pontos AR
            'ascendant_sign': 'Aquário',  # 3 pontos AR
            'mercury_sign': 'Libra',   # 1 ponto AR
        }
        
        result1 = calculate_temperament_from_chart(chart_data, 'pt')
        result2 = calculate_temperament_from_chart(chart_data, 'pt')
        
        assert result1['points'] == result2['points']
        assert result1['dominant'] == result2['dominant']
    
    def test_temperament_never_invents_data(self):
        """Temperamento só conta planetas fornecidos."""
        chart_data = {
            'sun_sign': 'Áries',  # 3 pontos
        }
        
        result = calculate_temperament_from_chart(chart_data, 'pt')
        
        # Deve ter apenas 3 pontos total (só o Sol foi fornecido)
        assert result['total_points'] == 3


class TestPlanetDignity:
    """Testa identificação de dignidades planetárias."""
    
    def test_sun_in_leo_is_domicile(self):
        """Sol em Leão é DOMICÍLIO."""
        assert get_planet_dignity('Sol', 'Leão') == 'domicile'
        assert get_planet_dignity('Sun', 'Leo') == 'domicile'
    
    def test_sun_in_aries_is_exaltation(self):
        """Sol em Áries é EXALTAÇÃO."""
        assert get_planet_dignity('Sol', 'Áries') == 'exaltation'
        assert get_planet_dignity('Sun', 'Aries') == 'exaltation'
    
    def test_sun_in_libra_is_fall(self):
        """Sol em Libra é QUEDA."""
        assert get_planet_dignity('Sol', 'Libra') == 'fall'
        assert get_planet_dignity('Sun', 'Libra') == 'fall'
    
    def test_moon_in_scorpio_is_fall(self):
        """Lua em Escorpião é QUEDA."""
        assert get_planet_dignity('Lua', 'Escorpião') == 'fall'
        assert get_planet_dignity('Moon', 'Scorpio') == 'fall'


class TestChartRuler:
    """Testa identificação do regente do mapa."""
    
    def test_aquarius_ascendant_ruler_is_uranus(self):
        """Ascendente Aquário = Regente Urano."""
        result = get_chart_ruler('Aquário', {})
        assert result['planet'] == 'Urano'
        assert result['ascendant'] == 'Aquário'
    
    def test_leo_ascendant_ruler_is_sun(self):
        """Ascendente Leão = Regente Sol."""
        result = get_chart_ruler('Leão', {})
        assert result['planet'] == 'Sol'
        assert result['ascendant'] == 'Leão'
    
    def test_never_returns_chiron_as_ruler(self):
        """Nenhum signo deve ter Quíron como regente."""
        all_signs = ['Áries', 'Touro', 'Gêmeos', 'Câncer', 'Leão', 'Virgem',
                     'Libra', 'Escorpião', 'Sagitário', 'Capricórnio', 'Aquário', 'Peixes']
        
        for sign in all_signs:
            result = get_chart_ruler(sign, {})
            assert result['planet'] != 'Quíron'
            assert result['planet'] != 'Chiron'


class TestSafetyBlocks:
    """Testa que blocos de segurança contêm instruções corretas."""
    
    def test_precomputed_block_forbids_calculation(self):
        """Bloco pré-calculado deve proibir IA de calcular."""
        chart_data = {
            'sun_sign': 'Libra',
            'moon_sign': 'Leão',
            'ascendant_sign': 'Aquário',
        }
        
        block = create_precomputed_data_block(chart_data, 'pt')
        
        assert 'NÃO deve calcular NADA' in block
        assert 'NÃO invente' in block
        assert 'PROIBIDO' in block
        assert 'Libra' in block  # Deve mencionar os signos
        assert 'AR' in block.upper()  # Deve mencionar que Libra é AR
    
    def test_planet_safety_block_includes_element(self):
        """Bloco de planeta deve incluir elemento correto."""
        block = create_planet_safety_block('Sol', 'Libra', 5, 'pt')
        
        assert 'Libra' in block
        assert 'Ar' in block or 'AR' in block
        assert 'NÃO invente' in block
    
    def test_chart_ruler_safety_block_validates_ruler(self):
        """Bloco de regente deve validar o regente correto."""
        block = create_chart_ruler_safety_block('Aquário', 'Urano', None, None, 'pt')
        
        assert 'Aquário' in block
        assert 'Urano' in block
        assert 'CORRETO' in block
        assert 'Quíron NÃO é regente' in block
    
    def test_chart_ruler_safety_block_detects_wrong_ruler(self):
        """Bloco deve detectar regente errado."""
        block = create_chart_ruler_safety_block('Aquário', 'Quíron', None, None, 'pt')
        
        assert 'ERRO' in block
        assert 'Deveria ser Urano' in block
    
    def test_aspect_safety_block_forbids_impossible_aspects(self):
        """Bloco de aspecto deve proibir aspectos impossíveis."""
        block = create_aspect_safety_block('Mercúrio', 'Sol', 'quadratura', 'pt')
        
        assert 'IMPOSSÍVEL' in block.upper()
        assert 'Mercúrio x Sol: Máximo 28°' in block


class TestCriticalSafetyRules:
    """Testes críticos que NUNCA devem falhar."""
    
    @pytest.mark.critical
    def test_libra_never_fire_or_earth(self):
        """CRÍTICO: Libra NUNCA pode ser Fogo ou Terra."""
        assert SIGN_TO_ELEMENT['Libra'] not in ['Fogo', 'Terra', 'Fire', 'Earth']
        assert SIGN_TO_ELEMENT['Libra'] in ['Ar', 'Air']
    
    @pytest.mark.critical
    def test_leo_never_water(self):
        """CRÍTICO: Leão NUNCA pode ser Água."""
        assert SIGN_TO_ELEMENT['Leão'] not in ['Água', 'Water']
        assert SIGN_TO_ELEMENT['Leão'] in ['Fogo', 'Fire']
    
    @pytest.mark.critical
    def test_chiron_never_ruler(self):
        """CRÍTICO: Quíron NUNCA pode ser regente."""
        all_rulers = set(SIGN_TO_RULER.values())
        assert 'Quíron' not in all_rulers
        assert 'Chiron' not in all_rulers
    
    @pytest.mark.critical
    def test_temperament_calculation_never_invents_planets(self):
        """CRÍTICO: Temperamento só conta planetas fornecidos."""
        chart_data = {'sun_sign': 'Áries'}
        result = calculate_temperament_from_chart(chart_data, 'pt')
        
        # Deve ter exatamente 3 pontos (só Sol = 3 pontos)
        assert result['total_points'] == 3

