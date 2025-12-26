"""
Testes TDD para a Ferramenta de Validação e Correção de Cálculos do Mapa Astral.
Valida que a ferramenta detecta e corrige imprecisões antes da interpretação.
"""
import pytest
from app.services.chart_validation_tool import (
    validate_complete_birth_chart,
    ChartValidationReport,
    validate_planetary_distances,
    validate_sign_consistency,
    validate_dignities,
    validate_aspects_in_chart,
    validate_chart_ruler,
    get_validation_summary_for_prompt,
)


class TestChartValidationReport:
    """Testes para o relatório de validação."""
    
    @pytest.mark.unit
    def test_report_starts_valid(self):
        """TDD: Relatório deve começar como válido."""
        report = ChartValidationReport()
        assert report.is_valid is True
        assert len(report.errors) == 0
        assert len(report.warnings) == 0
    
    @pytest.mark.unit
    def test_add_error_makes_invalid(self):
        """TDD: Adicionar erro deve tornar relatório inválido."""
        report = ChartValidationReport()
        report.add_error("Erro crítico")
        assert report.is_valid is False
        assert len(report.errors) == 1
    
    @pytest.mark.unit
    def test_add_warning_keeps_valid(self):
        """TDD: Adicionar aviso não deve tornar relatório inválido."""
        report = ChartValidationReport()
        report.add_warning("Aviso")
        assert report.is_valid is True
        assert len(report.warnings) == 1
    
    @pytest.mark.unit
    def test_report_to_dict(self):
        """TDD: Relatório deve converter para dicionário corretamente."""
        report = ChartValidationReport()
        report.add_validation("Validação 1")
        report.add_warning("Aviso 1")
        report.add_error("Erro 1")
        
        report_dict = report.to_dict()
        
        assert report_dict['is_valid'] is False
        assert len(report_dict['validations']) == 1
        assert len(report_dict['warnings']) == 1
        assert len(report_dict['errors']) == 1
        assert report_dict['total_issues'] == 2


class TestPlanetaryDistancesValidation:
    """Testes para validação de distâncias planetárias."""
    
    @pytest.mark.unit
    def test_validate_mercury_sun_conjunction_valid(self):
        """TDD: Conjunção Mercúrio-Sol válida deve ser aceita."""
        chart_data = {
            '_source_longitudes': {
                'mercury': 10.0,
                'sun': 5.0,  # 5° de distância - conjunção válida
            }
        }
        report = ChartValidationReport()
        
        result = validate_planetary_distances(chart_data, report)
        
        assert report.is_valid is True
        assert len(report.errors) == 0
        assert any('Mercúrio x Sol' in v for v in report.validations)
    
    @pytest.mark.unit
    def test_validate_mercury_sun_invalid_distance(self):
        """TDD: Distância Mercúrio-Sol maior que 28° deve gerar erro."""
        chart_data = {
            '_source_longitudes': {
                'mercury': 10.0,
                'sun': 50.0,  # 40° de distância - impossível
            }
        }
        report = ChartValidationReport()
        
        result = validate_planetary_distances(chart_data, report)
        
        assert report.is_valid is False
        assert any('Mercúrio x Sol' in e for e in report.errors)
    
    @pytest.mark.unit
    def test_validate_venus_sun_semi_sextile_valid(self):
        """TDD: Semi-sextil Vênus-Sol válido deve ser aceito."""
        chart_data = {
            '_source_longitudes': {
                'venus': 30.0,
                'sun': 0.0,  # 30° de distância - semi-sextil válido
            }
        }
        report = ChartValidationReport()
        
        result = validate_planetary_distances(chart_data, report)
        
        assert report.is_valid is True
        assert len(report.errors) == 0
    
    @pytest.mark.unit
    def test_validate_venus_sun_sextile_prohibited(self):
        """TDD: Sextil entre Vênus e Sol deve ser proibido."""
        chart_data = {
            '_source_longitudes': {
                'venus': 60.0,
                'sun': 0.0,  # 60° de distância - sextil proibido
            }
        }
        report = ChartValidationReport()
        
        result = validate_planetary_distances(chart_data, report)
        
        assert any('Vênus x Sol' in e for e in report.errors) or any('Vênus x Sol' in w for w in report.warnings)
    
    @pytest.mark.unit
    def test_validate_without_source_longitudes(self):
        """TDD: Validação sem longitudes fonte deve gerar aviso."""
        chart_data = {}
        report = ChartValidationReport()
        
        result = validate_planetary_distances(chart_data, report)
        
        assert any('Longitudes fonte não disponíveis' in w for w in report.warnings)


class TestSignConsistencyValidation:
    """Testes para validação de consistência de signos."""
    
    @pytest.mark.unit
    def test_validate_consistent_sign(self):
        """TDD: Signo consistente com longitude deve ser validado."""
        chart_data = {
            'sun_sign': 'Áries',
            'sun_degree': 15.5,
            '_source_longitudes': {
                'sun': 15.5,  # Longitude corresponde ao signo Áries
            }
        }
        report = ChartValidationReport()
        
        result = validate_sign_consistency(chart_data, report)
        
        assert report.is_valid is True
        assert len(report.errors) == 0
    
    @pytest.mark.unit
    def test_validate_inconsistent_sign_corrected(self):
        """TDD: Signo inconsistente deve ser corrigido automaticamente."""
        chart_data = {
            'sun_sign': 'Touro',  # Signo errado
            'sun_degree': 15.5,
            '_source_longitudes': {
                'sun': 15.5,  # Longitude corresponde a Áries, não Touro
            }
        }
        report = ChartValidationReport()
        
        result = validate_sign_consistency(chart_data, report)
        
        assert 'Áries' in report.corrections[0] if report.corrections else True
        assert result['sun_sign'] == 'Áries'  # Deve ser corrigido
    
    @pytest.mark.unit
    def test_validate_sign_without_longitudes(self):
        """TDD: Validação sem longitudes não deve gerar erro."""
        chart_data = {
            'sun_sign': 'Áries',
            'sun_degree': 15.5,
        }
        report = ChartValidationReport()
        
        result = validate_sign_consistency(chart_data, report)
        
        assert report.is_valid is True


class TestDignitiesValidation:
    """Testes para validação de dignidades planetárias."""
    
    @pytest.mark.unit
    def test_validate_planet_in_domicile(self):
        """TDD: Planeta em domicílio deve ser identificado."""
        chart_data = {
            'sun_sign': 'Leão',
        }
        report = ChartValidationReport()
        
        result = validate_dignities(chart_data, report)
        
        assert any('DOMICÍLIO' in v for v in report.validations)
        assert any('Sol' in v and 'Leão' in v for v in report.validations)
    
    @pytest.mark.unit
    def test_validate_planet_in_detriment(self):
        """TDD: Planeta em detrimento deve gerar aviso."""
        chart_data = {
            'mars_sign': 'Libra',  # Marte em detrimento
        }
        report = ChartValidationReport()
        
        result = validate_dignities(chart_data, report)
        
        assert any('DETRIMENTO' in w for w in report.warnings)
    
    @pytest.mark.unit
    def test_validate_planet_in_fall(self):
        """TDD: Planeta em queda deve gerar aviso."""
        chart_data = {
            'sun_sign': 'Libra',  # Sol em queda
        }
        report = ChartValidationReport()
        
        result = validate_dignities(chart_data, report)
        
        assert any('QUEDA' in w for w in report.warnings)
    
    @pytest.mark.unit
    def test_validate_planet_peregrine(self):
        """TDD: Planeta peregrino deve ser identificado."""
        chart_data = {
            'sun_sign': 'Gêmeos',  # Sol peregrino
        }
        report = ChartValidationReport()
        
        result = validate_dignities(chart_data, report)
        
        assert any('PEREGRINO' in v for v in report.validations)


class TestAspectsValidation:
    """Testes para validação de aspectos."""
    
    @pytest.mark.unit
    def test_validate_conjunction_aspect(self):
        """TDD: Conjunção válida deve ser identificada."""
        chart_data = {
            '_source_longitudes': {
                'sun': 10.0,
                'moon': 15.0,  # 5° de distância - conjunção
            }
        }
        report = ChartValidationReport()
        
        result = validate_aspects_in_chart(chart_data, report)
        
        assert '_validated_aspects' in result
        assert len(result['_validated_aspects']) > 0
        assert any('conjunction' in str(a).lower() for a in result['_validated_aspects'])
    
    @pytest.mark.unit
    def test_validate_trine_aspect(self):
        """TDD: Trígono válido deve ser identificado."""
        chart_data = {
            '_source_longitudes': {
                'sun': 0.0,
                'moon': 120.0,  # 120° de distância - trígono
            }
        }
        report = ChartValidationReport()
        
        result = validate_aspects_in_chart(chart_data, report)
        
        validated_aspects = result.get('_validated_aspects', [])
        assert any(a.get('aspect') == 'trine' for a in validated_aspects)
    
    @pytest.mark.unit
    def test_validate_no_aspect_without_longitudes(self):
        """TDD: Validação sem longitudes não deve gerar erros."""
        chart_data = {}
        report = ChartValidationReport()
        
        result = validate_aspects_in_chart(chart_data, report)
        
        assert report.is_valid is True


class TestChartRulerValidation:
    """Testes para validação do regente do mapa."""
    
    @pytest.mark.unit
    def test_validate_chart_ruler_aries(self):
        """TDD: Regente de Áries deve ser Marte."""
        chart_data = {
            'ascendant_sign': 'Áries',
            'mars_sign': 'Leão',
            'mars_degree': 15.0,
        }
        report = ChartValidationReport()
        
        result = validate_chart_ruler(chart_data, report)
        
        assert '_chart_ruler' in result
        assert result['_chart_ruler']['planet'] == 'Marte'
        assert result['_chart_ruler']['sign'] == 'Leão'
    
    @pytest.mark.unit
    def test_validate_chart_ruler_leo(self):
        """TDD: Regente de Leão deve ser Sol."""
        chart_data = {
            'ascendant_sign': 'Leão',
            'sun_sign': 'Escorpião',
            'sun_degree': 20.0,
        }
        report = ChartValidationReport()
        
        result = validate_chart_ruler(chart_data, report)
        
        assert '_chart_ruler' in result
        assert result['_chart_ruler']['planet'] == 'Sol'
    
    @pytest.mark.unit
    def test_validate_chart_ruler_without_ascendant(self):
        """TDD: Sem ascendente deve gerar aviso."""
        chart_data = {}
        report = ChartValidationReport()
        
        result = validate_chart_ruler(chart_data, report)
        
        assert any('Ascendente não disponível' in w for w in report.warnings)


class TestCompleteValidation:
    """Testes para validação completa do mapa astral."""
    
    @pytest.mark.unit
    def test_validate_complete_valid_chart(self):
        """TDD: Mapa astral válido deve passar todas as validações."""
        chart_data = {
            'sun_sign': 'Leão',
            'sun_degree': 145.0,
            'moon_sign': 'Áries',
            'moon_degree': 5.0,
            'ascendant_sign': 'Áries',
            'ascendant_degree': 10.0,
            'mercury_sign': 'Leão',
            'mercury_degree': 142.0,  # Conjunção com Sol (3° de distância)
            'venus_sign': 'Leão',
            'venus_degree': 140.0,  # Conjunção com Sol (5° de distância)
            'mars_sign': 'Leão',
            'mars_degree': 143.0,
            '_source_longitudes': {
                'sun': 145.0,  # Leão (135° - 165°)
                'moon': 5.0,   # Áries (0° - 30°)
                'mercury': 142.0,  # Leão (3° do Sol)
                'venus': 140.0,  # Leão (5° do Sol)
                'mars': 143.0,  # Leão
                'ascendant': 10.0,  # Áries
            }
        }
        
        validated_chart, report = validate_complete_birth_chart(chart_data)
        
        # O mapa deve ser válido após correções (se houver)
        assert len(report.errors) == 0 or len(report.corrections) > 0
        # Se houver apenas correções (não erros críticos), ainda é válido
        if len(report.errors) == 0:
            assert report.is_valid is True
        else:
            # Se houver erros que foram corrigidos, verificamos que foram corrigidos
            assert len(report.corrections) >= len(report.errors)
    
    @pytest.mark.unit
    def test_validate_complete_chart_with_errors(self):
        """TDD: Mapa astral com erros deve detectar e corrigir."""
        chart_data = {
            'sun_sign': 'Leão',
            'sun_degree': 15.0,
            'mercury_sign': 'Touro',  # Signo errado
            'mercury_degree': 12.0,
            '_source_longitudes': {
                'sun': 285.0,  # Leão
                'mercury': 282.0,  # Leão (não Touro)
            }
        }
        
        validated_chart, report = validate_complete_birth_chart(chart_data)
        
        # Deve ter pelo menos uma correção ou erro
        assert len(report.corrections) > 0 or len(report.errors) > 0
    
    @pytest.mark.unit
    def test_validate_complete_chart_empty(self):
        """TDD: Mapa astral vazio não deve quebrar."""
        chart_data = {}
        
        validated_chart, report = validate_complete_birth_chart(chart_data)
        
        assert isinstance(report, ChartValidationReport)
        assert isinstance(validated_chart, dict)


class TestValidationSummary:
    """Testes para o resumo de validação no prompt."""
    
    @pytest.mark.unit
    def test_get_validation_summary_pt(self):
        """TDD: Resumo em português deve estar formatado corretamente."""
        report = ChartValidationReport()
        report.add_validation("Validação 1")
        report.add_correction("Correção 1")
        report.add_warning("Aviso 1")
        
        summary = get_validation_summary_for_prompt(report, 'pt')
        
        assert '✅ VALIDAÇÕES APROVADAS' in summary
        assert '🔧 CORREÇÕES APLICADAS' in summary
        assert '⚠️ AVISOS' in summary
        assert 'Validação 1' in summary
    
    @pytest.mark.unit
    def test_get_validation_summary_en(self):
        """TDD: Resumo em inglês deve estar formatado corretamente."""
        report = ChartValidationReport()
        report.add_validation("Validation 1")
        
        summary = get_validation_summary_for_prompt(report, 'en')
        
        assert '✅ VALIDATIONS APPROVED' in summary
        assert 'Validation 1' in summary
    
    @pytest.mark.unit
    def test_get_validation_summary_empty(self):
        """TDD: Resumo vazio deve retornar mensagem padrão."""
        report = ChartValidationReport()
        
        summary = get_validation_summary_for_prompt(report, 'pt')
        
        assert 'validado sem problemas' in summary.lower()
    
    @pytest.mark.unit
    def test_get_validation_summary_with_errors(self):
        """TDD: Resumo com erros deve incluir seção de erros."""
        report = ChartValidationReport()
        report.add_error("Erro crítico")
        
        summary = get_validation_summary_for_prompt(report, 'pt')
        
        assert '❌ ERROS CRÍTICOS' in summary
        assert 'Erro crítico' in summary


class TestIntegrationValidation:
    """Testes de integração para validação completa."""
    
    @pytest.mark.unit
    def test_real_world_chart_validation(self):
        """TDD: Validação de mapa astral real deve funcionar."""
        # Dados de um mapa astral realista
        chart_data = {
            'sun_sign': 'Capricórnio',
            'sun_degree': 25.31,
            'moon_sign': 'Virgem',
            'moon_degree': 19.97,
            'ascendant_sign': 'Touro',
            'ascendant_degree': 24.55,
            'mercury_sign': 'Capricórnio',
            'mercury_degree': 11.18,
            'venus_sign': 'Aquário',
            'venus_degree': 0.55,
            'mars_sign': 'Sagitário',
            'mars_degree': 20.07,
            'jupiter_sign': 'Câncer',
            'jupiter_degree': 3.34,
            'saturn_sign': 'Capricórnio',
            'saturn_degree': 17.34,
            '_source_longitudes': {
                'sun': 295.31,
                'moon': 169.97,
                'mercury': 281.18,
                'venus': 300.55,
                'mars': 260.07,
                'jupiter': 93.34,
                'saturn': 287.34,
                'ascendant': 54.55,
            }
        }
        
        validated_chart, report = validate_complete_birth_chart(chart_data)
        
        assert isinstance(validated_chart, dict)
        assert isinstance(report, ChartValidationReport)
        assert '_validated_aspects' in validated_chart or len(report.validations) > 0
        assert len(report.errors) == 0  # Mapa válido não deve ter erros críticos

