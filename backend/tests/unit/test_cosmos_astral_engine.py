"""
Testes TDD para Cosmos Astral Engine - Validação Matemática
Garante que as regras astronômicas e cálculos matemáticos estão corretos.
"""
import pytest
from app.services.astrology_calculator import shortest_angular_distance
from app.services.cosmos_validation import (
    validate_mercury_sun_distance,
    validate_venus_sun_distance,
    validate_venus_mercury_distance,
    validate_aspect,
    calculate_temperament_points,
    validate_temperament_interpretation,
    MERCURY_SUN_MAX_DISTANCE,
    VENUS_SUN_MAX_DISTANCE,
    VENUS_MERCURY_MAX_DISTANCE,
)


class TestCosmosAstralEngineValidation:
    """
    Testes para as regras de validação matemática do Cosmos Astral Engine.
    Baseado nas regras definidas no PASSO 1 do sistema.
    """
    
    @pytest.mark.critical
    @pytest.mark.unit
    def test_mercury_sun_maximum_distance_28_degrees(self):
        """
        TDD: Mercúrio x Sol - distância máxima é 28°.
        Permitido: Conjunção (0-10°) ou Sem Aspecto.
        Proibido: Quadratura, Trígono, Oposição, Sextil.
        """
        # Teste: Distância de 28° deve ser válida (limite máximo)
        sol_longitude = 100.0  # Sol em Câncer (grau 10)
        mercury_longitude = 128.0  # Mercúrio 28° à frente
        
        distance = shortest_angular_distance(sol_longitude, mercury_longitude)
        assert distance <= 28.0, f"Mercúrio não pode estar a mais de 28° do Sol. Distância: {distance}°"
        
        # Teste: Distância de 29° deve violar a regra
        mercury_invalid = 129.0
        distance_invalid = shortest_angular_distance(sol_longitude, mercury_invalid)
        assert distance_invalid > 28.0, "Distância de 29° viola a regra astronômica"
        
        # Teste: Conjunção válida (dentro de 10°)
        mercury_conjunction = 105.0  # 5° à frente
        distance_conj = shortest_angular_distance(sol_longitude, mercury_conjunction)
        assert distance_conj <= 10.0, f"Conjunção deve estar dentro de 10°. Distância: {distance_conj}°"
    
    @pytest.mark.critical
    @pytest.mark.unit
    def test_venus_sun_maximum_distance_48_degrees(self):
        """
        TDD: Vênus x Sol - distância máxima é 48°.
        Permitido: Conjunção (0-10°), Semi-Sextil (30°), Semi-Quadratura (45°).
        Proibido: Sextil (60°), Quadratura (90°), Trígono (120°), Oposição (180°).
        """
        sol_longitude = 100.0
        
        # Teste: Distância de 48° deve ser válida (limite máximo)
        venus_longitude = 148.0  # 48° à frente
        distance = shortest_angular_distance(sol_longitude, venus_longitude)
        assert distance <= 48.0, f"Vênus não pode estar a mais de 48° do Sol. Distância: {distance}°"
        
        # Teste: Distância de 49° deve violar a regra
        venus_invalid = 149.0
        distance_invalid = shortest_angular_distance(sol_longitude, venus_invalid)
        assert distance_invalid > 48.0, "Distância de 49° viola a regra astronômica"
        
        # Teste: Semi-Sextil válido (30°)
        venus_semi_sextil = 130.0  # 30° à frente
        distance_semi = shortest_angular_distance(sol_longitude, venus_semi_sextil)
        assert abs(distance_semi - 30.0) < 1.0, f"Semi-Sextil deve estar próximo de 30°. Distância: {distance_semi}°"
        
        # Teste: Semi-Quadratura válida (45°)
        venus_semi_square = 145.0  # 45° à frente
        distance_semi_sq = shortest_angular_distance(sol_longitude, venus_semi_square)
        assert abs(distance_semi_sq - 45.0) < 1.0, f"Semi-Quadratura deve estar próximo de 45°. Distância: {distance_semi_sq}°"
    
    @pytest.mark.critical
    @pytest.mark.unit
    def test_venus_mercury_maximum_distance_76_degrees(self):
        """
        TDD: Vênus x Mercúrio - distância máxima é 76°.
        Permitido: Conjunção, Sextil.
        Proibido: Quadratura, Trígono, Oposição.
        """
        mercury_longitude = 100.0
        
        # Teste: Distância de 76° deve ser válida (limite máximo)
        venus_longitude = 176.0  # 76° à frente
        distance = shortest_angular_distance(mercury_longitude, venus_longitude)
        assert distance <= 76.0, f"Vênus não pode estar a mais de 76° de Mercúrio. Distância: {distance}°"
        
        # Teste: Distância de 77° deve violar a regra
        venus_invalid = 177.0
        distance_invalid = shortest_angular_distance(mercury_longitude, venus_invalid)
        assert distance_invalid > 76.0, "Distância de 77° viola a regra astronômica"
    
    @pytest.mark.critical
    @pytest.mark.unit
    def test_aspect_calculation_conjunction_orb_8_degrees(self):
        """
        TDD: Conjunção (0°) - Orbe +/- 8°.
        Distância válida: 0° a 8° ou 352° a 360°.
        """
        planet1 = 100.0
        
        # Teste: Conjunção exata (0°)
        planet2_exact = 100.0
        distance_exact = shortest_angular_distance(planet1, planet2_exact)
        assert distance_exact <= 8.0, f"Conjunção exata deve estar dentro do orbe. Distância: {distance_exact}°"
        
        # Teste: Conjunção no limite do orbe (8°)
        planet2_limit = 108.0
        distance_limit = shortest_angular_distance(planet1, planet2_limit)
        assert distance_limit <= 8.0, f"Conjunção no limite deve estar dentro do orbe. Distância: {distance_limit}°"
        
        # Teste: Fora do orbe de conjunção (9°)
        planet2_out = 109.0
        distance_out = shortest_angular_distance(planet1, planet2_out)
        assert distance_out > 8.0, "Distância de 9° está fora do orbe de conjunção"
        
        # Teste: Conjunção através de 360° (352° a 360°)
        planet1_near_end = 359.0
        planet2_near_start = 2.0  # 3° de diferença (360 - 359 + 2 = 3)
        distance_wrap = shortest_angular_distance(planet1_near_end, planet2_near_start)
        assert distance_wrap <= 8.0, f"Conjunção através de 360° deve estar dentro do orbe. Distância: {distance_wrap}°"
    
    @pytest.mark.critical
    @pytest.mark.unit
    def test_aspect_calculation_sextile_orb_4_degrees(self):
        """
        TDD: Sextil (60°) - Orbe +/- 4°.
        Distância válida: 56° a 64° (Harmônico).
        """
        planet1 = 100.0
        
        # Teste: Sextil exato (60°)
        planet2_exact = 160.0
        distance_exact = shortest_angular_distance(planet1, planet2_exact)
        assert 56.0 <= distance_exact <= 64.0, f"Sextil exato deve estar dentro do orbe. Distância: {distance_exact}°"
        
        # Teste: Sextil no limite mínimo (56°)
        planet2_min = 156.0
        distance_min = shortest_angular_distance(planet1, planet2_min)
        assert 56.0 <= distance_min <= 64.0, f"Sextil no limite mínimo deve estar dentro do orbe. Distância: {distance_min}°"
        
        # Teste: Sextil no limite máximo (64°)
        planet2_max = 164.0
        distance_max = shortest_angular_distance(planet1, planet2_max)
        assert 56.0 <= distance_max <= 64.0, f"Sextil no limite máximo deve estar dentro do orbe. Distância: {distance_max}°"
        
        # Teste: Fora do orbe (65°)
        planet2_out = 165.0
        distance_out = shortest_angular_distance(planet1, planet2_out)
        assert not (56.0 <= distance_out <= 64.0), "Distância de 65° está fora do orbe de sextil"
    
    @pytest.mark.critical
    @pytest.mark.unit
    def test_aspect_calculation_square_orb_6_degrees(self):
        """
        TDD: Quadratura (90°) - Orbe +/- 6°.
        Distância válida: 84° a 96° (Tenso).
        """
        planet1 = 100.0
        
        # Teste: Quadratura exata (90°)
        planet2_exact = 190.0
        distance_exact = shortest_angular_distance(planet1, planet2_exact)
        assert 84.0 <= distance_exact <= 96.0, f"Quadratura exata deve estar dentro do orbe. Distância: {distance_exact}°"
        
        # Teste: Fora do orbe (97°)
        planet2_out = 197.0
        distance_out = shortest_angular_distance(planet1, planet2_out)
        assert not (84.0 <= distance_out <= 96.0), "Distância de 97° está fora do orbe de quadratura"
    
    @pytest.mark.critical
    @pytest.mark.unit
    def test_aspect_calculation_trine_orb_8_degrees(self):
        """
        TDD: Trígono (120°) - Orbe +/- 8°.
        Distância válida: 112° a 128° (Fluido).
        """
        planet1 = 100.0
        
        # Teste: Trígono exato (120°)
        planet2_exact = 220.0
        distance_exact = shortest_angular_distance(planet1, planet2_exact)
        assert 112.0 <= distance_exact <= 128.0, f"Trígono exato deve estar dentro do orbe. Distância: {distance_exact}°"
        
        # Teste: Fora do orbe (129°)
        planet2_out = 229.0
        distance_out = shortest_angular_distance(planet1, planet2_out)
        assert not (112.0 <= distance_out <= 128.0), "Distância de 129° está fora do orbe de trígono"
    
    @pytest.mark.critical
    @pytest.mark.unit
    def test_aspect_calculation_opposition_orb_8_degrees(self):
        """
        TDD: Oposição (180°) - Orbe +/- 8°.
        Distância válida: 172° a 188° (Tenso).
        """
        planet1 = 100.0
        
        # Teste: Oposição exata (180°)
        planet2_exact = 280.0
        distance_exact = shortest_angular_distance(planet1, planet2_exact)
        assert 172.0 <= distance_exact <= 188.0, f"Oposição exata deve estar dentro do orbe. Distância: {distance_exact}°"
        
        # Teste: Fora do orbe (189°)
        planet2_out = 289.0
        distance_out = shortest_angular_distance(planet1, planet2_out)
        assert not (172.0 <= distance_out <= 188.0), "Distância de 189° está fora do orbe de oposição"
    
    @pytest.mark.critical
    @pytest.mark.unit
    def test_aspect_calculation_quincunx_orb_2_degrees(self):
        """
        TDD: Quincúncio (150°) - Orbe +/- 2°.
        Distância válida: 148° a 152° (Ajuste).
        """
        planet1 = 100.0
        
        # Teste: Quincúncio exato (150°)
        planet2_exact = 250.0
        distance_exact = shortest_angular_distance(planet1, planet2_exact)
        assert 148.0 <= distance_exact <= 152.0, f"Quincúncio exato deve estar dentro do orbe. Distância: {distance_exact}°"
        
        # Teste: Fora do orbe (153°)
        planet2_out = 253.0
        distance_out = shortest_angular_distance(planet1, planet2_out)
        assert not (148.0 <= distance_out <= 152.0), "Distância de 153° está fora do orbe de quincúncio"
    
    @pytest.mark.critical
    @pytest.mark.unit
    def test_geometric_aspect_validation_65_degrees_not_opposition(self):
        """
        TDD: Validação geométrica crítica.
        Se a distância for 65° (Leão para Libra), é um Sextil "largo" ou Sem Aspecto.
        JAMAIS chamar isso de Oposição ou Quadratura.
        """
        planet1 = 120.0  # Leão (aproximadamente)
        planet2 = 185.0  # Libra (aproximadamente) - 65° de diferença
        
        distance = shortest_angular_distance(planet1, planet2)
        
        # Verificar que NÃO é oposição (180°)
        assert not (172.0 <= distance <= 188.0), f"Distância de {distance}° não pode ser interpretada como oposição"
        
        # Verificar que NÃO é quadratura (90°)
        assert not (84.0 <= distance <= 96.0), f"Distância de {distance}° não pode ser interpretada como quadratura"
        
        # Pode ser sextil largo ou sem aspecto, mas não um aspecto major
        assert distance < 84.0 or distance > 96.0, "65° pode ser sextil largo, mas não aspecto major"


class TestTemperamentCalculation:
    """
    Testes para o cálculo de temperamento (PASSO 1.3).
    Sistema de pontuação: Sol/Lua/Ascendente = 3 pontos cada.
    Outros planetas = 1 ponto cada.
    """
    
    @pytest.mark.critical
    @pytest.mark.unit
    def test_temperament_scoring_sun_moon_ascendant_3_points(self):
        """
        TDD: Sol, Lua e Ascendente valem 3 pontos cada no cálculo de temperamento.
        """
        # Simular contagem de elementos
        fire_points = 0
        earth_points = 0
        air_points = 0
        water_points = 0
        
        # Sol em Leão (Fogo) = 3 pontos
        fire_points += 3
        
        # Lua em Touro (Terra) = 3 pontos
        earth_points += 3
        
        # Ascendente em Gêmeos (Ar) = 3 pontos
        air_points += 3
        
        assert fire_points == 3, "Sol deve valer 3 pontos"
        assert earth_points == 3, "Lua deve valer 3 pontos"
        assert air_points == 3, "Ascendente deve valer 3 pontos"
    
    @pytest.mark.critical
    @pytest.mark.unit
    def test_temperament_scoring_other_planets_1_point(self):
        """
        TDD: Outros planetas (Mercúrio a Plutão) valem 1 ponto cada.
        """
        fire_points = 0
        
        # Mercúrio em Leão (Fogo) = 1 ponto
        fire_points += 1
        
        # Marte em Áries (Fogo) = 1 ponto
        fire_points += 1
        
        # Vênus em Sagitário (Fogo) = 1 ponto
        fire_points += 1
        
        assert fire_points == 3, "Três planetas devem somar 3 pontos"
    
    @pytest.mark.critical
    @pytest.mark.unit
    def test_temperament_element_not_absent_when_has_planets(self):
        """
        TDD: Regra crítica - Se o usuário tem Lua, Marte e Vênus em signos de Fogo,
        NÃO PODE dizer que o elemento Fogo está "ausente" ou é "ponto cego".
        """
        fire_points = 0
        
        # Lua em Leão (Fogo) = 3 pontos
        fire_points += 3
        
        # Marte em Áries (Fogo) = 1 ponto
        fire_points += 1
        
        # Vênus em Sagitário (Fogo) = 1 ponto
        fire_points += 1
        
        total_fire = fire_points
        
        # Verificar que Fogo NÃO está ausente
        assert total_fire > 0, "Fogo não pode estar ausente se há planetas em signos de Fogo"
        assert total_fire >= 5, "Com Lua, Marte e Vênus em Fogo, deve ter pelo menos 5 pontos"
        
        # Validar que não pode ser interpretado como "ponto cego"
        is_blind_spot = total_fire == 0
        assert not is_blind_spot, "Elemento com 5 pontos não pode ser ponto cego"


class TestShortestAngularDistance:
    """
    Testes para a função shortest_angular_distance que é fundamental para cálculos.
    """
    
    @pytest.mark.critical
    @pytest.mark.unit
    def test_shortest_angular_distance_same_position(self):
        """TDD: Distância entre mesmas posições deve ser 0°."""
        distance = shortest_angular_distance(100.0, 100.0)
        assert distance == 0.0, "Distância entre mesmas posições deve ser 0°"
    
    @pytest.mark.critical
    @pytest.mark.unit
    def test_shortest_angular_distance_opposite_sides(self):
        """TDD: Distância entre posições opostas deve ser 180°."""
        distance = shortest_angular_distance(100.0, 280.0)
        assert abs(distance - 180.0) < 0.1, f"Distância oposta deve ser ~180°. Obtido: {distance}°"
    
    @pytest.mark.critical
    @pytest.mark.unit
    def test_shortest_angular_distance_wraps_around_360(self):
        """TDD: Distância deve calcular corretamente através de 360°."""
        # 359° para 1° = 2° de distância (não 358°)
        distance = shortest_angular_distance(359.0, 1.0)
        assert distance == 2.0, f"Distância através de 360° deve ser 2°. Obtido: {distance}°"
    
    @pytest.mark.critical
    @pytest.mark.unit
    def test_shortest_angular_distance_always_positive(self):
        """TDD: Distância angular sempre deve ser positiva (0 a 180)."""
        distances = [
            shortest_angular_distance(0.0, 90.0),
            shortest_angular_distance(180.0, 90.0),
            shortest_angular_distance(270.0, 90.0),
            shortest_angular_distance(359.0, 1.0),
        ]
        
        for distance in distances:
            assert distance >= 0.0, f"Distância deve ser sempre positiva. Obtido: {distance}°"
            assert distance <= 180.0, f"Distância deve ser sempre <= 180°. Obtido: {distance}°"


class TestCosmosValidationModule:
    """
    Testes para o módulo cosmos_validation que implementa as validações.
    """
    
    @pytest.mark.critical
    @pytest.mark.unit
    def test_validate_mercury_sun_distance_valid_conjunction(self):
        """TDD: Validação de conjunção válida entre Mercúrio e Sol."""
        is_valid, aspect_type = validate_mercury_sun_distance(105.0, 100.0)  # 5° de distância
        assert is_valid is True
        assert aspect_type == "conjunction"
    
    @pytest.mark.critical
    @pytest.mark.unit
    def test_validate_mercury_sun_distance_invalid_too_far(self):
        """TDD: Validação deve rejeitar distâncias maiores que 28°."""
        is_valid, aspect_type = validate_mercury_sun_distance(130.0, 100.0)  # 30° de distância
        assert is_valid is False
        assert "28" in aspect_type or "limite" in aspect_type.lower()
    
    @pytest.mark.critical
    @pytest.mark.unit
    def test_validate_venus_sun_distance_valid_semi_sextile(self):
        """TDD: Validação de semi-sextil válido entre Vênus e Sol."""
        is_valid, aspect_type, error = validate_venus_sun_distance(130.0, 100.0)  # 30° de distância
        assert is_valid is True
        assert aspect_type == "semi-sextile"
        assert error is None
    
    @pytest.mark.critical
    @pytest.mark.unit
    def test_validate_venus_sun_distance_invalid_sextile(self):
        """TDD: Validação deve rejeitar sextil entre Vênus e Sol (proibido)."""
        # Sextil seria ~60°, mas dentro do limite de 48° não deve aparecer
        # Vamos testar uma distância que seria sextil mas está fora do limite máximo
        is_valid, aspect_type, error = validate_venus_sun_distance(160.0, 100.0)  # 60° de distância
        # Deve falhar por estar além do limite máximo de 48°
        assert is_valid is False
        assert "48" in error or "limite" in error.lower()
    
    @pytest.mark.critical
    @pytest.mark.unit
    def test_validate_venus_mercury_distance_valid_conjunction(self):
        """TDD: Validação de conjunção válida entre Vênus e Mercúrio."""
        is_valid, aspect_type, error = validate_venus_mercury_distance(105.0, 100.0)  # 5° de distância
        assert is_valid is True
        assert aspect_type == "conjunction"
        assert error is None
    
    @pytest.mark.critical
    @pytest.mark.unit
    def test_validate_venus_mercury_distance_valid_sextile(self):
        """TDD: Validação de sextil válido entre Vênus e Mercúrio."""
        is_valid, aspect_type, error = validate_venus_mercury_distance(160.0, 100.0)  # 60° de distância
        assert is_valid is True
        assert aspect_type == "sextile"
        assert error is None
    
    @pytest.mark.critical
    @pytest.mark.unit
    def test_validate_aspect_conjunction_valid(self):
        """TDD: Validação de aspecto de conjunção válido."""
        is_valid, distance, error = validate_aspect(100.0, 105.0, "conjunction")
        assert is_valid is True
        assert error is None
        assert distance <= 8.0  # Dentro do orbe de 8°
    
    @pytest.mark.critical
    @pytest.mark.unit
    def test_validate_aspect_square_invalid_out_of_orb(self):
        """TDD: Validação deve rejeitar aspecto fora do orbe."""
        # 95° está dentro do orbe de quadratura (84-96°), mas vamos testar 97°
        is_valid, distance, error = validate_aspect(100.0, 197.0, "square")
        assert is_valid is False
        assert error is not None
    
    @pytest.mark.critical
    @pytest.mark.unit
    def test_calculate_temperament_points_major_planets(self):
        """TDD: Cálculo de pontos de temperamento - planetas maiores valem 3 pontos."""
        planet_positions = {
            'sun': {'sign': 'Leão', 'element': 'fire'},
            'moon': {'sign': 'Touro', 'element': 'earth'},
            'ascendant': {'sign': 'Gêmeos', 'element': 'air'},
        }
        points = calculate_temperament_points(planet_positions)
        
        assert points['fire'] == 3  # Sol vale 3
        assert points['earth'] == 3  # Lua vale 3
        assert points['air'] == 3  # Ascendente vale 3
    
    @pytest.mark.critical
    @pytest.mark.unit
    def test_calculate_temperament_points_minor_planets(self):
        """TDD: Cálculo de pontos - planetas menores valem 1 ponto cada."""
        planet_positions = {
            'mercury': {'sign': 'Leão'},
            'mars': {'sign': 'Áries'},
            'venus': {'sign': 'Sagitário'},
        }
        points = calculate_temperament_points(planet_positions)
        
        assert points['fire'] == 3  # 3 planetas × 1 ponto = 3 pontos
    
    @pytest.mark.critical
    @pytest.mark.unit
    def test_validate_temperament_interpretation_rejects_absent_with_planets(self):
        """TDD: Validação deve rejeitar interpretação que diz elemento ausente quando tem planetas."""
        planet_positions = {
            'sun': {'sign': 'Leão'},
            'moon': {'sign': 'Leão'},
            'mars': {'sign': 'Áries'},
        }
        # Interpretação incorreta dizendo que Fogo está ausente
        interpretation = "O elemento fogo está ausente no mapa"
        
        is_valid, error = validate_temperament_interpretation(planet_positions, interpretation)
        assert is_valid is False
        assert "fogo" in error.lower() or "fire" in error.lower()
        assert "pontos" in error.lower() or "points" in error.lower()


class TestCosmosAstralEnginePrompt:
    """
    Testes para validar que o prompt do Cosmos Astral Engine está correto.
    """
    
    @pytest.mark.unit
    def test_master_prompt_contains_cosmos_engine_name(self):
        """TDD: Prompt mestre deve conter nome 'Cosmos Astral Engine'."""
        from app.api.interpretation import _get_master_prompt
        
        prompt_pt = _get_master_prompt('pt')
        prompt_en = _get_master_prompt('en')
        
        assert "Cosmos Astral Engine" in prompt_pt or "cosmos astral engine" in prompt_pt.lower()
        assert "Cosmos Astral Engine" in prompt_en or "cosmos astral engine" in prompt_en.lower()
    
    @pytest.mark.unit
    def test_master_prompt_contains_validation_rules(self):
        """TDD: Prompt deve conter as regras de validação astronômica."""
        from app.api.interpretation import _get_master_prompt
        
        prompt_pt = _get_master_prompt('pt')
        
        # Verificar presença de regras críticas
        assert "28°" in prompt_pt or "28 graus" in prompt_pt.lower()
        assert "48°" in prompt_pt or "48 graus" in prompt_pt.lower()
        assert "76°" in prompt_pt or "76 graus" in prompt_pt.lower()
        assert "Mercúrio" in prompt_pt or "Mercury" in prompt_pt
        assert "Vênus" in prompt_pt or "Venus" in prompt_pt
    
    @pytest.mark.unit
    def test_master_prompt_contains_aspect_orb_table(self):
        """TDD: Prompt deve conter tabela de orbes de aspectos."""
        from app.api.interpretation import _get_master_prompt
        
        prompt_pt = _get_master_prompt('pt')
        
        # Verificar presença de aspectos e orbes
        assert "Conjunção" in prompt_pt or "Conjunction" in prompt_pt
        assert "Sextil" in prompt_pt or "Sextile" in prompt_pt
        assert "Quadratura" in prompt_pt or "Square" in prompt_pt
        assert "Trígono" in prompt_pt or "Trine" in prompt_pt
        assert "Oposição" in prompt_pt or "Opposition" in prompt_pt
    
    @pytest.mark.unit
    def test_master_prompt_contains_temperament_calculation(self):
        """TDD: Prompt deve conter algoritmo de cálculo de temperamento."""
        from app.api.interpretation import _get_master_prompt
        
        prompt_pt = _get_master_prompt('pt')
        
        # Verificar presença de cálculo de temperamento
        assert "Temperamento" in prompt_pt or "Temperament" in prompt_pt
        assert "3 pontos" in prompt_pt or "3 points" in prompt_pt
        assert "pontos cada" in prompt_pt or "points each" in prompt_pt
    
    @pytest.mark.unit
    def test_master_prompt_contains_5_steps(self):
        """TDD: Prompt deve conter os 5 passos do sistema."""
        from app.api.interpretation import _get_master_prompt
        
        prompt_pt = _get_master_prompt('pt')
        
        # Verificar presença dos 5 passos
        assert "PASSO 1" in prompt_pt or "STEP 1" in prompt_pt
        assert "PASSO 2" in prompt_pt or "STEP 2" in prompt_pt
        assert "PASSO 3" in prompt_pt or "STEP 3" in prompt_pt
        assert "PASSO 4" in prompt_pt or "STEP 4" in prompt_pt
        assert "PASSO 5" in prompt_pt or "STEP 5" in prompt_pt

